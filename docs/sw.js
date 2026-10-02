/* ModuLaser Battery Calculator — service worker */
const CACHE_VERSION = 'modulaser-calc-v41';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Runtime-cache cross-origin assets (SheetJS CDN, Google Fonts) so
  // Excel export and typography keep working offline after first load.
  if (url.origin !== self.location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((resp) => {
          if (resp && resp.ok) {
            const copy = resp.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(event.request, copy));
          }
          return resp;
        }).catch(() => cached);
      })
    );
    return;
  }

  // Same-origin: network-first so updates land, cache fallback for offline.
  event.respondWith(
    fetch(event.request).then((resp) => {
      if (resp && resp.ok) {
        const copy = resp.clone();
        caches.open(CACHE_VERSION).then((cache) => cache.put(event.request, copy));
      }
      return resp;
    }).catch(() => caches.match(event.request).then((c) => c || caches.match('./index.html')))
  );
});
