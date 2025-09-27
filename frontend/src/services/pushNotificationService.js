import { notificationAPI } from './notificationAPI';

class PushNotificationService {
  constructor() {
    this.registration = null;
    this.subscription = null;
    this.vapidPublicKey = null;
    this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
  }

  async initialize() {
    if (!this.isSupported) {
      console.warn('Push notifications not supported');
      return false;
    }

    try {
      // Register service worker
      this.registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered:', this.registration);

      // Get VAPID public key
      const response = await notificationAPI.getVapidPublicKey();
      this.vapidPublicKey = response.public_key;

      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage);

      return true;
    } catch (error) {
      console.error('Error initializing push notifications:', error);
      return false;
    }
  }

  handleServiceWorkerMessage = (event) => {
    const { data } = event;
    
    switch (data.type) {
      case 'NOTIFICATION_CLICKED':
        // Handle notification click from service worker
        if (data.targetUrl && data.targetUrl !== window.location.pathname) {
          window.location.href = data.targetUrl;
        }
        break;
    }
  };

  async requestPermission() {
    if (!this.isSupported) {
      return 'not-supported';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission === 'denied') {
      return 'denied';
    }

    const permission = await Notification.requestPermission();
    return permission;
  }

  async subscribe() {
    if (!this.registration || !this.vapidPublicKey) {
      throw new Error('Service worker not registered or VAPID key not available');
    }

    const permission = await this.requestPermission();
    if (permission !== 'granted') {
      throw new Error('Push notification permission not granted');
    }

    try {
      // Check if already subscribed
      this.subscription = await this.registration.pushManager.getSubscription();
      
      if (!this.subscription) {
        // Create new subscription
        this.subscription = await this.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
        });
      }

      // Send subscription to server
      await notificationAPI.subscribePush(this.subscription);
      
      console.log('Push notification subscription successful');
      return this.subscription;

    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      throw error;
    }
  }

  async unsubscribe() {
    if (!this.subscription) {
      return true;
    }

    try {
      await this.subscription.unsubscribe();
      await notificationAPI.unsubscribePush();
      this.subscription = null;
      
      console.log('Push notification unsubscription successful');
      return true;

    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
      throw error;
    }
  }

  async getSubscriptionStatus() {
    if (!this.registration) {
      return { subscribed: false, supported: this.isSupported };
    }

    try {
      this.subscription = await this.registration.pushManager.getSubscription();
      return {
        subscribed: !!this.subscription,
        supported: this.isSupported,
        permission: Notification.permission
      };
    } catch (error) {
      console.error('Error getting subscription status:', error);
      return { subscribed: false, supported: this.isSupported };
    }
  }

  async sendTestNotification() {
    try {
      await notificationAPI.sendTestPushNotification();
      console.log('Test push notification sent');
    } catch (error) {
      console.error('Error sending test push notification:', error);
      throw error;
    }
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Utility methods for checking support and permission
  static isSupported() {
    return 'serviceWorker' in navigator && 'PushManager' in window;
  }

  static getPermissionStatus() {
    if (!PushNotificationService.isSupported()) {
      return 'not-supported';
    }
    return Notification.permission;
  }
}

// Singleton instance
const pushNotificationService = new PushNotificationService();

export default pushNotificationService;
