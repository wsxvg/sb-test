const CACHE_NAME = 'huiyou-shop-v1';
const DATA_CACHE_NAME = 'huiyou-data-v1';
const IMAGE_CACHE_NAME = 'huiyou-images-v1';

// 核心文件立即缓存
const urlsToCache = [
  './',
  './index.html',
  './manifest.json',
  './placeholder.svg'
];

// 安装事件 - 缓存核心文件
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: 缓存核心文件');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting()) // 立即激活新的 SW
  );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== DATA_CACHE_NAME && 
              cacheName !== IMAGE_CACHE_NAME) {
            console.log('Service Worker: 删除旧缓存', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // 立即控制所有页面
  );
});

// Fetch 事件 - 智能缓存策略
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. products_db.json 和 home_config.json - 缓存优先，后台更新
  if (url.pathname.endsWith('products_db.json') || url.pathname.endsWith('home_config.json')) {
    event.respondWith(
      caches.open(DATA_CACHE_NAME).then(cache => {
        return cache.match(request).then(cachedResponse => {
          const fetchPromise = fetch(request).then(networkResponse => {
            // 后台更新缓存
            if (networkResponse && networkResponse.status === 200) {
              cache.put(request, networkResponse.clone());
            }
            return networkResponse;
          }).catch(() => cachedResponse); // 网络失败时返回缓存
          
          // 如果有缓存，立即返回缓存，同时后台更新
          return cachedResponse || fetchPromise;
        });
      })
    );
    return;
  }

  // 2. 图片文件 - 缓存优先
  if (request.destination === 'image' || 
      url.pathname.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)) {
    event.respondWith(
      caches.open(IMAGE_CACHE_NAME).then(cache => {
        return cache.match(request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          return fetch(request).then(networkResponse => {
            // 只缓存成功的图片响应
            if (networkResponse && networkResponse.status === 200) {
              cache.put(request, networkResponse.clone());
            }
            return networkResponse;
          }).catch(() => {
            // 图片加载失败，返回占位图
            return caches.match('./placeholder.svg');
          });
        });
      })
    );
    return;
  }

  // 3. HTML/CSS/JS - 网络优先，失败时使用缓存
  if (request.destination === 'document' || 
      request.destination === 'script' || 
      request.destination === 'style') {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }

  // 4. 其他请求 - 网络优先
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
