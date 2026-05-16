/* AssistantAI Service Worker
 * Cache stratejisi:
 *  - Statik varlıklar (Next /_next/static, /icons, /manifest): cache-first
 *  - Sayfa navigasyonları: network-first + offline fallback
 *  - API çağrıları (/api): network-only (cache yok — taze veri zorunlu)
 */
const VERSION = "v2";
const STATIC_CACHE = `assistantai-static-${VERSION}`;
const PAGE_CACHE = `assistantai-pages-${VERSION}`;
const OFFLINE_URL = "/offline.html";

const PRECACHE_URLS = [
  "/",
  "/offline.html",
  "/manifest.webmanifest",
  "/icon.svg",
  "/icon-192.png",
  "/icon-512.png",
  "/apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS).catch(() => undefined))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => ![STATIC_CACHE, PAGE_CACHE].includes(k))
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // API'yi cacheleme
  if (url.pathname.startsWith("/api/")) return;

  // Next.js HMR / sıcak güncellemeleri atla
  if (url.pathname.startsWith("/_next/webpack-hmr")) return;

  // Statik varlıklar → cache-first
  if (
    url.pathname.startsWith("/_next/static/") ||
    url.pathname.startsWith("/icons/") ||
    /\.(?:svg|png|jpg|jpeg|webp|gif|ico|woff2?|ttf|css|js)$/i.test(url.pathname)
  ) {
    event.respondWith(
      caches.match(req).then(
        (cached) =>
          cached ||
          fetch(req)
            .then((res) => {
              const copy = res.clone();
              caches.open(STATIC_CACHE).then((c) => c.put(req, copy));
              return res;
            })
            .catch(() => cached)
      )
    );
    return;
  }

  // Sayfa navigasyonları → network-first, offline fallback
  if (req.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          const fresh = await fetch(req);
          const copy = fresh.clone();
          caches.open(PAGE_CACHE).then((c) => c.put(req, copy));
          return fresh;
        } catch {
          const cached = await caches.match(req);
          return cached || (await caches.match(OFFLINE_URL));
        }
      })()
    );
  }
});

self.addEventListener("message", (event) => {
  if (event.data === "SKIP_WAITING") self.skipWaiting();
});
