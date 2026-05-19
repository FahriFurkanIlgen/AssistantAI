"""
AI Eval Harness — regression tests for grounding, anti-hallucination, citations.

Usage (from backend/):
    .\\venv\\Scripts\\python.exe -m eval.run_eval
    .\\venv\\Scripts\\python.exe -m eval.run_eval --fixtures akdeniz-sifa
    .\\venv\\Scripts\\python.exe -m eval.run_eval --verbose

Loads JSON fixtures from eval/fixtures/*.json and runs each case against the
live FastAPI app (using httpx AsyncClient + ASGI transport). Requires the
configured MongoDB to contain the referenced business slugs.

Fixture format (eval/fixtures/<slug>.json):
{
  "business_slug": "akdeniz-sifa",
  "cases": [
    {
      "name": "phone fact",
      "message": "Telefon numaranız nedir?",
      "must_include": ["444 7 606"],          // case-insensitive substrings
      "must_not_include": ["bilmiyorum"],     // anti-hallucination guards
      "must_include_any": ["randevu", "ara"], // at least one must appear
      "expect_citation": ["SSS"],             // citation doc-title substrings
      "no_citation": false,                   // if true, asserts zero citations
      "language": "tr"                        // optional, default "tr"
    }
  ]
}
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.main import app
from app.models.business import Business
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.otp_code import OtpCode
from app.models.staff_member import StaffMember
from app.models.demo_request import DemoRequest
from app.models.knowledge import KnowledgeDocument, KnowledgeGap


FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Lightweight ANSI colors (no extra deps).
class C:
    OK = "\033[92m"
    FAIL = "\033[91m"
    WARN = "\033[93m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


async def init_db() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Business, Appointment, Customer, Conversation, OtpCode,
            StaffMember, DemoRequest, KnowledgeDocument, KnowledgeGap,
        ],
    )
    return client


def _check_case(reply: str, citations: list[dict], case: dict) -> tuple[bool, list[str]]:
    """Return (passed, failure_reasons)."""
    fails: list[str] = []
    lower = reply.lower()

    for needle in case.get("must_include", []):
        if needle.lower() not in lower:
            fails.append(f"must_include missing: {needle!r}")

    for needle in case.get("must_not_include", []):
        if needle.lower() in lower:
            fails.append(f"must_not_include present: {needle!r}")

    any_set = case.get("must_include_any", [])
    if any_set and not any(n.lower() in lower for n in any_set):
        fails.append(f"must_include_any: none of {any_set} present")

    expect_cites = case.get("expect_citation", [])
    if expect_cites:
        cite_titles = [c.get("title", "").lower() for c in citations]
        for needle in expect_cites:
            if not any(needle.lower() in t for t in cite_titles):
                fails.append(
                    f"expect_citation missing: {needle!r} (got: {cite_titles or 'none'})"
                )

    if case.get("no_citation"):
        if citations:
            fails.append(
                f"no_citation violated: got {[c.get('title') for c in citations]}"
            )

    return (len(fails) == 0, fails)


async def run_fixture(
    client: httpx.AsyncClient,
    fixture: dict,
    verbose: bool,
    case_filter: Optional[list[str]] = None,
) -> tuple[int, int]:
    slug = fixture["business_slug"]
    biz = await Business.find_one(Business.slug == slug, Business.is_active == True)
    if not biz:
        print(f"{C.FAIL}✗ business not found: {slug}{C.RESET}")
        return (0, len(fixture.get("cases", [])))

    cases = fixture.get("cases", [])
    if case_filter:
        needles = [n.lower() for n in case_filter]
        cases = [
            c for c in cases
            if any(n in c.get("name", "").lower() for n in needles)
        ]
        if not cases:
            return (0, 0)

    print(f"\n{C.BOLD}── {slug} ({biz.name}) ──{C.RESET}")
    passed = failed = 0

    for case in cases:
        name = case.get("name", case["message"][:40])
        # Fresh session per case → isolation from prior turns
        session_id = str(uuid.uuid4())
        t0 = time.perf_counter()
        attempt = 0
        data = None
        last_err: Optional[Exception] = None
        while attempt < 3:
            attempt += 1
            try:
                resp = await client.post(
                    f"/api/chat/{slug}",
                    json={
                        "message": case["message"],
                        "session_id": session_id,
                        "language": case.get("language", "tr"),
                    },
                    timeout=90.0,
                )
                if resp.status_code == 429:
                    await asyncio.sleep(8 * attempt)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                last_err = e
                # Only retry on transient 429-ish; otherwise bail.
                if "429" not in str(e):
                    break
                await asyncio.sleep(8 * attempt)

        if data is None:
            failed += 1
            print(f"  {C.FAIL}✗{C.RESET} {name} — request error: {last_err}")
            continue

        elapsed_ms = (time.perf_counter() - t0) * 1000
        reply = data.get("reply", "")
        citations = data.get("citations", [])
        ok, reasons = _check_case(reply, citations, case)

        if ok:
            passed += 1
            mark = f"{C.OK}✓{C.RESET}"
            print(f"  {mark} {name}  {C.DIM}({elapsed_ms:.0f}ms){C.RESET}")
            if verbose:
                print(f"     {C.DIM}Q:{C.RESET} {case['message']}")
                print(f"     {C.DIM}A:{C.RESET} {reply[:200]}")
                if citations:
                    print(
                        f"     {C.DIM}cites:{C.RESET} "
                        + ", ".join(f"{c['title']}({c['score']})" for c in citations)
                    )
        else:
            failed += 1
            print(f"  {C.FAIL}✗{C.RESET} {name}  {C.DIM}({elapsed_ms:.0f}ms){C.RESET}")
            print(f"     {C.DIM}Q:{C.RESET} {case['message']}")
            print(f"     {C.DIM}A:{C.RESET} {reply[:300]}")
            for r in reasons:
                print(f"     {C.WARN}→ {r}{C.RESET}")
            if citations:
                print(
                    f"     {C.DIM}cites:{C.RESET} "
                    + ", ".join(f"{c['title']}({c['score']})" for c in citations)
                )

    return (passed, failed)


def _load_fixtures(only: Optional[list[str]]) -> list[dict]:
    if not FIXTURES_DIR.exists():
        print(f"{C.FAIL}fixtures dir not found: {FIXTURES_DIR}{C.RESET}")
        return []
    out: list[dict] = []
    for p in sorted(FIXTURES_DIR.glob("*.json")):
        if only and p.stem not in only:
            continue
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"{C.FAIL}failed to parse {p.name}: {e}{C.RESET}")
    return out


async def main_async(args) -> int:
    fixtures = _load_fixtures(args.fixtures)
    if not fixtures:
        print(f"{C.WARN}no fixtures to run{C.RESET}")
        return 1

    mongo_client = await init_db()
    total_p = total_f = 0
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://eval") as client:
            for fx in fixtures:
                p, f = await run_fixture(client, fx, args.verbose, args.case)
                total_p += p
                total_f += f
    finally:
        mongo_client.close()

    total = total_p + total_f
    print(f"\n{C.BOLD}══ Eval Summary ══{C.RESET}")
    print(
        f"  {C.OK}passed:{C.RESET} {total_p}/{total}   "
        f"{C.FAIL}failed:{C.RESET} {total_f}/{total}"
    )
    return 0 if total_f == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixtures",
        nargs="*",
        help="Only run these fixture stems (e.g. akdeniz-sifa). Default: all.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--case",
        nargs="*",
        help="Only run cases whose name contains any of these substrings (case-insensitive).",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
