// Service Worker for PWA and Push Notifications
const CACHE_NAME = 'creator-platform-v2';
const STATIC_CACHE = 'static-v2';
const DYNAMIC_CACHE = 'dynamic-v2';

// Static assets to cache
const STATIC_ASSETS = [
  '/',
  '/offline',
  '/static/icons/notification-icon.png',
  '/static/icons/badge-icon.png',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/manifest.json'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  '/api/notifications/',
  '/api/ai/matches/',
  '/api/collaborations/invites/'
];

// Install event
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS)),
      caches.open(DYNAMIC_CACHE).then(() => console.log('Dynamic cache opened'))
    ]).then(() => {
      console.log('Service Worker installed successfully');
      self.skipWaiting();
    })
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    Promise.all([
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (![STATIC_CACHE, DYNAMIC_CACHE].includes(cacheName)) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      clients.claim()
    ]).then(() => {
      console.log('Service Worker activated successfully');
    })
  );
});

// Push event - handle incoming push notifications
self.addEventListener('push', (event) => {
  console.log('Push event received:', event);
  
  let notificationData = {};
  
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'New Notification',
        body: event.data.text() || 'You have a new notification',
        icon: '/static/icons/notification-icon.png',
        badge: '/static/icons/badge-icon.png'
      };
    }
  }

  const options = {
    body: notificationData.body || 'You have a new notification',
    icon: notificationData.icon || '/static/icons/notification-icon.png',
    badge: notificationData.badge || '/static/icons/badge-icon.png',
    data: notificationData.data || {},
    actions: notificationData.actions || [],
    requireInteraction: notificationData.requireInteraction || false,
    tag: notificationData.tag || 'default',
    timestamp: notificationData.timestamp || Date.now(),
    vibrate: [200, 100, 200],
    sound: '/static/sounds/notification.mp3'
  };

  event.waitUntil(
    self.registration.showNotification(
      notificationData.title || 'Creator Community Platform',
      options
    )
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  const data = event.notification.data || {};
  let targetUrl = '/';
  
  // Handle different notification types
  switch (data.type) {
    case 'new_match':
      targetUrl = data.url || `/matching?highlight=${data.match_id}`;
      break;
    case 'collaboration_invite':
      targetUrl = data.url || `/collaborations/invites/${data.invite_id}`;
      break;
    case 'match_accepted':
      targetUrl = data.url || `/collaborations/new?match=${data.match_id}`;
      break;
    default:
      targetUrl = data.url || '/notifications';
  }
  
  // Handle action clicks
  if (event.action) {
    switch (event.action) {
      case 'view_match':
        targetUrl = `/matching?highlight=${data.match_id}`;
        break;
      case 'view_invite':
        targetUrl = `/collaborations/invites/${data.invite_id}`;
        break;
      case 'start_collaboration':
        targetUrl = `/collaborations/new?match=${data.match_id}`;
        break;
      case 'dismiss':
        return; // Just close the notification
    }
  }
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if there's already a window/tab open
        for (const client of clientList) {
          if (client.url.includes(self.location.origin)) {
            client.focus();
            client.postMessage({
              type: 'NOTIFICATION_CLICKED',
              data: data,
              targetUrl: targetUrl
            });
            return;
          }
        }
        
        // No existing window, open a new one
        return clients.openWindow(targetUrl);
      })
  );
});

// Background sync for offline notification handling
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync-notifications') {
    event.waitUntil(syncNotifications());
  }
});

async function syncNotifications() {
  try {
    // Sync any pending notifications when back online
    const response = await fetch('/api/notifications/unread-count/');
    if (response.ok) {
      const data = await response.json();
      if (data.unread_count > 0) {
        // Show a summary notification for missed notifications
        self.registration.showNotification('Missed Notifications', {
          body: `You have ${data.unread_count} unread notifications`,
          icon: '/static/icons/notification-icon.png',
          badge: '/static/icons/badge-icon.png',
          tag: 'missed-notifications',
          data: { type: 'missed', url: '/notifications' }
        });
      }
    }
  } catch (error) {
    console.error('Error syncing notifications:', error);
  }
}

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
  console.log('Service worker received message:', event.data);
  
  switch (event.data.type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    case 'GET_VERSION':
      event.ports[0].postMessage({ version: CACHE_NAME });
      break;
  }
});

// Fetch event - handle network requests with offline support
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension requests
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }

  // Handle API requests with cache-first strategy for specific endpoints
  if (url.pathname.startsWith('/api/')) {
    const shouldCache = API_CACHE_PATTERNS.some(pattern => 
      url.pathname.startsWith(pattern)
    );
    
    if (shouldCache) {
      event.respondWith(handleAPIRequest(request));
    }
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request));
    return;
  }

  // Handle static assets
  event.respondWith(handleStaticRequest(request));
});

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Return offline response for API requests
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'This content is not available offline'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle navigation requests with cache-first strategy
async function handleNavigationRequest(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log('Navigation failed, serving offline page:', error);
    const cachedResponse = await caches.match('/offline');
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

// Handle static assets with cache-first strategy
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Static asset failed to load:', error);
    return new Response('Resource not available offline', { status: 503 });
  }
}
