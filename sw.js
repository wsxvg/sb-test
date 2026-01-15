const CACHE_NAME = 'shibiao-static-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './products_db.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
