// WeatherGPT Service Worker for PWA Installation & Caching
const CACHE_NAME = 'weathergpt-v2.0';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/chat.js',
  '/static/js/charts.js',
  '/static/js/map.js',
  '/static/js/voice.js',
  '/static/js/i18n.js',
  '/static/js/advisories.js',
  '/static/assets/icons/icon.svg',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Let live API calls pass through to network
  if (event.request.url.includes('/api/') || event.request.url.includes('/ws/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Network first with cache fallback for UI shell
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
