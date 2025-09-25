// Service Worker for Push Notifications
const CACHE_NAME = 'creator-platform-v1';
const urlsToCache = [
  '/',
  '/static/icons/notification-icon.png',
  '/static/icons/badge-icon.png'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
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

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
  // Only handle GET requests for caching
  if (event.request.method !== 'GET') {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      })
  );
});
