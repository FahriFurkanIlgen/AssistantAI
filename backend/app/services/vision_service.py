"""
Vision Service - Extract images from Instagram post URLs and analyze via GPT-4o Vision.
Also supports fetching a business's own Instagram portfolio posts.
"""
import re
import json
import httpx
from typing import Optional, List

# Regex to detect Instagram post links
INSTAGRAM_POST_RE = re.compile(r"https?://(?:www\.)?instagram\.com/p/[\w-]+")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}


def is_instagram_url(text: str) -> bool:
    return bool(INSTAGRAM_POST_RE.search(text))


def extract_instagram_url(text: str) -> Optional[str]:
    m = INSTAGRAM_POST_RE.search(text)
    return m.group(0) if m else None


async def extract_og_image(url: str) -> Optional[str]:
    """
    Fetch a webpage and extract the og:image meta tag value.
    Works for Instagram public posts (returns the post's main image URL).
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=12) as client:
            resp = await client.get(url, headers=BROWSER_HEADERS)
            resp.raise_for_status()
        html = resp.text
        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](https?://[^"\']+)["\']',
            r'<meta[^>]+content=["\'](https?://[^"\']+)["\'][^>]+property=["\']og:image["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None


async def fetch_instagram_portfolio(handle: str, max_posts: int = 9) -> List[dict]:
    """
    Fetch recent posts from a public Instagram account.
    Returns a list of dicts: [{url: str, thumbnail: str, shortcode: str}]
    Falls back to empty list if Instagram blocks the request.
    """
    profile_url = f"https://www.instagram.com/{handle}/"
    posts: List[dict] = []

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(profile_url, headers=BROWSER_HEADERS)
            if resp.status_code != 200:
                return posts
            html = resp.text

        # Try to find embedded JSON with post data
        # Instagram embeds post shortcodes in meta tags and scripts
        # Method 1: og:image from profile (profile picture, skip)
        # Method 2: Find all post shortcodes from page source
        shortcode_pattern = re.compile(r'"shortcode"\s*:\s*"([\w-]+)"')
        thumbnail_pattern = re.compile(r'"display_url"\s*:\s*"(https://[^"]+)"')
        
        shortcodes = shortcode_pattern.findall(html)
        thumbnails = thumbnail_pattern.findall(html)

        # Unescape unicode in URLs
        def unescape(s: str) -> str:
            return s.encode().decode('unicode_escape') if '\\u' in s else s

        for i, sc in enumerate(shortcodes[:max_posts]):
            thumb = unescape(thumbnails[i]) if i < len(thumbnails) else None
            posts.append({
                "shortcode": sc,
                "url": f"https://www.instagram.com/p/{sc}/",
                "thumbnail": thumb,
            })

        # If no structured data found, try alternate JSON pattern
        if not posts:
            # Try to find image URLs directly
            img_pattern = re.compile(
                r'https://[^"\']+(?:cdninstagram|fbcdn)[^"\']+\.(?:jpg|jpeg|webp)'
            )
            imgs = img_pattern.findall(html)
            for img in imgs[:max_posts]:
                posts.append({"shortcode": None, "url": None, "thumbnail": unescape(img)})

    except Exception:
        pass

    return posts
