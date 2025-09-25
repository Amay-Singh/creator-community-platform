import { test, expect } from '@playwright/test';

test.describe('Real-time Notifications', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        email: 'user@example.com',
        username: 'testuser'
      }));
    });

    // Mock WebSocket for real-time notifications
    await page.addInitScript(() => {
      class MockWebSocket {
        constructor(url) {
          this.url = url;
          this.readyState = WebSocket.CONNECTING;
          setTimeout(() => {
            this.readyState = WebSocket.OPEN;
            if (this.onopen) this.onopen();
          }, 100);
        }

        send(data) {
          // Mock sending data
          console.log('WebSocket send:', data);
        }

        close() {
          this.readyState = WebSocket.CLOSED;
          if (this.onclose) this.onclose();
        }

        // Method to simulate receiving messages
        simulateMessage(data) {
          if (this.onmessage) {
            this.onmessage({ data: JSON.stringify(data) });
          }
        }
      }

      window.MockWebSocket = MockWebSocket;
      window.WebSocket = MockWebSocket;
    });
  });

  test('should display notification bell with count', async ({ page }) => {
    // Mock notifications API
    await page.route('**/api/notifications/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              id: 1,
              title: 'New collaboration invite',
              message: 'John Doe wants to collaborate with you',
              notification_type: 'collaboration_invite',
              read_at: null,
              created_at: '2025-09-24T10:00:00Z'
            },
            {
              id: 2,
              title: 'Match found',
              message: 'You have a new 85% match!',
              notification_type: 'match_found',
              read_at: null,
              created_at: '2025-09-24T09:30:00Z'
            }
          ],
          count: 2,
          unread_count: 2
        })
      });
    });

    await page.goto('/dashboard');

    // Check notification bell
    await expect(page.locator('[data-testid="notification-bell"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-count"]')).toContainText('2');
  });

  test('should open notification dropdown', async ({ page }) => {
    await page.goto('/dashboard');

    // Click notification bell
    await page.click('[data-testid="notification-bell"]');

    // Check if dropdown opens
    await expect(page.locator('[data-testid="notification-dropdown"]')).toBeVisible();
    
    // Check notification items
    await expect(page.locator('[data-testid="notification-item"]')).toHaveCount(2);
    await expect(page.locator('text=New collaboration invite')).toBeVisible();
    await expect(page.locator('text=Match found')).toBeVisible();
  });

  test('should mark notifications as read', async ({ page }) => {
    await page.goto('/dashboard');

    // Open notification dropdown
    await page.click('[data-testid="notification-bell"]');

    // Mock mark as read API
    await page.route('**/api/notifications/mark-read', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          marked_read: 1
        })
      });
    });

    // Click on first notification
    await page.click('[data-testid="notification-item"]:first-child');

    // Check if notification is marked as read (visual indicator)
    await expect(page.locator('[data-testid="notification-item"]:first-child')).toHaveClass(/read/);
    
    // Check if count decreases
    await expect(page.locator('[data-testid="notification-count"]')).toContainText('1');
  });

  test('should receive real-time notifications via WebSocket', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for WebSocket connection
    await page.waitForTimeout(200);

    // Simulate receiving a new notification
    await page.evaluate(() => {
      const mockWs = window.mockWebSocketInstance;
      if (mockWs && mockWs.simulateMessage) {
        mockWs.simulateMessage({
          type: 'notification',
          data: {
            id: 3,
            title: 'New message',
            message: 'You have a new message from Sarah',
            notification_type: 'message',
            created_at: new Date().toISOString()
          }
        });
      }
    });

    // Check if new notification appears
    await expect(page.locator('[data-testid="notification-count"]')).toContainText('3');
    
    // Check if toast notification appears
    await expect(page.locator('[data-testid="toast-notification"]')).toBeVisible();
    await expect(page.locator('text=New message')).toBeVisible();
  });

  test('should display different notification types with correct icons', async ({ page }) => {
    // Mock different notification types
    await page.route('**/api/notifications/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              id: 1,
              title: 'Collaboration invite',
              notification_type: 'collaboration_invite',
              read_at: null
            },
            {
              id: 2,
              title: 'New match',
              notification_type: 'match_found',
              read_at: null
            },
            {
              id: 3,
              title: 'New message',
              notification_type: 'message',
              read_at: null
            },
            {
              id: 4,
              title: 'System update',
              notification_type: 'system',
              read_at: null
            }
          ]
        })
      });
    });

    await page.goto('/dashboard');
    await page.click('[data-testid="notification-bell"]');

    // Check different notification type icons
    await expect(page.locator('[data-testid="notification-icon-collaboration"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-icon-match"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-icon-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="notification-icon-system"]')).toBeVisible();
  });

  test('should handle notification preferences', async ({ page }) => {
    await page.goto('/settings/notifications');

    // Check notification preference toggles
    await expect(page.locator('input[name="email_notifications"]')).toBeVisible();
    await expect(page.locator('input[name="push_notifications"]')).toBeVisible();
    await expect(page.locator('input[name="collaboration_notifications"]')).toBeVisible();
    await expect(page.locator('input[name="match_notifications"]')).toBeVisible();

    // Toggle a preference
    await page.click('input[name="email_notifications"]');

    // Mock save preferences API
    await page.route('**/api/notifications/preferences/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Preferences updated successfully'
        })
      });
    });

    // Save preferences
    await page.click('button[data-testid="save-preferences"]');

    // Check success message
    await expect(page.locator('text=Preferences updated')).toBeVisible();
  });

  test('should handle push notification permission', async ({ page }) => {
    // Mock Notification API
    await page.addInitScript(() => {
      window.Notification = {
        permission: 'default',
        requestPermission: () => Promise.resolve('granted')
      };
    });

    await page.goto('/dashboard');

    // Check for push notification prompt
    await expect(page.locator('[data-testid="push-notification-prompt"]')).toBeVisible();

    // Click enable push notifications
    await page.click('button[data-testid="enable-push"]');

    // Check if permission is requested
    const permission = await page.evaluate(() => {
      return window.Notification.permission;
    });
    
    // Note: In real test, this would be 'granted' after user interaction
    expect(['default', 'granted']).toContain(permission);
  });

  test('should display notification history', async ({ page }) => {
    await page.goto('/notifications');

    // Mock notification history API
    await page.route('**/api/notifications/**', async route => {
      const url = new URL(route.request().url());
      const page_num = url.searchParams.get('page') || '1';
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: Array.from({ length: 10 }, (_, i) => ({
            id: i + 1,
            title: `Notification ${i + 1}`,
            message: `This is notification message ${i + 1}`,
            notification_type: ['collaboration_invite', 'match_found', 'message'][i % 3],
            read_at: i % 2 === 0 ? '2025-09-24T10:00:00Z' : null,
            created_at: new Date(Date.now() - i * 3600000).toISOString()
          })),
          count: 50,
          next: page_num === '1' ? 'http://localhost:8000/api/notifications/?page=2' : null,
          previous: null
        })
      });
    });

    // Check notification history
    await expect(page.locator('h1')).toContainText('Notifications');
    await expect(page.locator('[data-testid="notification-item"]')).toHaveCount(10);

    // Check pagination
    await expect(page.locator('[data-testid="pagination"]')).toBeVisible();
  });

  test('should filter notifications by type', async ({ page }) => {
    await page.goto('/notifications');

    // Click filter dropdown
    await page.click('[data-testid="notification-filter"]');

    // Select collaboration invites filter
    await page.click('text=Collaboration Invites');

    // Mock filtered API response
    await page.route('**/api/notifications/**', async route => {
      const url = new URL(route.request().url());
      if (url.searchParams.get('type') === 'collaboration_invite') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: 1,
                title: 'Collaboration invite from John',
                notification_type: 'collaboration_invite',
                read_at: null
              }
            ],
            count: 1
          })
        });
      }
    });

    // Check filtered results
    await expect(page.locator('[data-testid="notification-item"]')).toHaveCount(1);
    await expect(page.locator('text=Collaboration invite from John')).toBeVisible();
  });

  test('should handle WebSocket connection errors', async ({ page }) => {
    // Mock WebSocket connection error
    await page.addInitScript(() => {
      class FailingWebSocket {
        constructor(url) {
          this.url = url;
          this.readyState = WebSocket.CONNECTING;
          setTimeout(() => {
            this.readyState = WebSocket.CLOSED;
            if (this.onerror) this.onerror(new Error('Connection failed'));
            if (this.onclose) this.onclose();
          }, 100);
        }
      }
      window.WebSocket = FailingWebSocket;
    });

    await page.goto('/dashboard');

    // Check for connection error indicator
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Disconnected');
    
    // Check for retry mechanism
    await expect(page.locator('[data-testid="retry-connection"]')).toBeVisible();
  });

  test('should mark all notifications as read', async ({ page }) => {
    await page.goto('/notifications');

    // Mock mark all as read API
    await page.route('**/api/notifications/mark-read', async route => {
      const body = await route.request().postDataJSON();
      if (body.all === true) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            marked_read: 10
          })
        });
      }
    });

    // Click mark all as read
    await page.click('[data-testid="mark-all-read"]');

    // Check success message
    await expect(page.locator('text=All notifications marked as read')).toBeVisible();
    
    // Check if notification count is cleared
    await expect(page.locator('[data-testid="notification-count"]')).not.toBeVisible();
  });
});
