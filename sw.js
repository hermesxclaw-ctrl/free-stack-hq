// Free-Stack HQ service worker — cache-first for assets, network-first for data.
const CACHE = 'fs-hq-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => e.waitUntil(clients.claim()));
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // data: never cache (health.json must be fresh-ish — still cache-busted anyway)
  if (e.request.method !== 'GET' || url.pathname.includes('health.json')) return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      if (res.ok) caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }))
  );
});
