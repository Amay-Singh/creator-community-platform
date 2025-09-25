import { test, expect } from '@playwright/test';

test.describe('Performance Regression Tests', () => {
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
  });

  test('should load dashboard within performance budget', async ({ page }) => {
    // Start measuring performance
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    
    // Wait for main content to load
    await page.waitForSelector('[data-testid="dashboard-content"]');
    
    const loadTime = Date.now() - startTime;
    
    // Assert load time is under 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Check Core Web Vitals
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const metrics = {};
          
          entries.forEach((entry) => {
            if (entry.entryType === 'navigation') {
              metrics.loadTime = entry.loadEventEnd - entry.loadEventStart;
              metrics.domContentLoaded = entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart;
            }
            if (entry.entryType === 'paint') {
              if (entry.name === 'first-contentful-paint') {
                metrics.fcp = entry.startTime;
              }
              if (entry.name === 'largest-contentful-paint') {
                metrics.lcp = entry.startTime;
              }
            }
          });
          
          resolve(metrics);
        }).observe({ entryTypes: ['navigation', 'paint'] });
      });
    });
    
    // Assert Core Web Vitals thresholds
    if (metrics.fcp) expect(metrics.fcp).toBeLessThan(1800); // FCP < 1.8s
    if (metrics.lcp) expect(metrics.lcp).toBeLessThan(2500); // LCP < 2.5s
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    // Mock large dataset
    await page.route('**/api/ai/matches/**', async route => {
      const largeDataset = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        matched_user: {
          id: i + 100,
          username: `user${i}`,
          profile: {
            skills: ['JavaScript', 'React', 'Node.js'],
            location: 'San Francisco, CA',
            bio: `Bio for user ${i}`
          }
        },
        match_score: Math.random() * 0.4 + 0.6
      }));

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          matches: largeDataset,
          total: 100
        })
      });
    });

    const startTime = Date.now();
    
    await page.goto('/matching');
    
    // Wait for all match cards to render
    await page.waitForSelector('[data-testid="match-card"]');
    
    const renderTime = Date.now() - startTime;
    
    // Assert rendering time is reasonable for large dataset
    expect(renderTime).toBeLessThan(5000);
    
    // Check if virtual scrolling or pagination is working
    const visibleCards = await page.locator('[data-testid="match-card"]').count();
    
    // Should not render all 100 items at once (virtual scrolling)
    expect(visibleCards).toBeLessThanOrEqual(20);
  });

  test('should maintain performance during real-time updates', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Mock WebSocket for real-time updates
    await page.addInitScript(() => {
      window.performanceMetrics = [];
      
      // Override WebSocket to simulate high-frequency updates
      class MockWebSocket {
        constructor(url) {
          this.url = url;
          this.readyState = WebSocket.OPEN;
          
          // Simulate high-frequency notifications
          setInterval(() => {
            const startTime = performance.now();
            
            if (this.onmessage) {
              this.onmessage({
                data: JSON.stringify({
                  type: 'notification',
                  data: {
                    id: Date.now(),
                    title: 'Test notification',
                    message: 'Performance test message'
                  }
                })
              });
            }
            
            const endTime = performance.now();
            window.performanceMetrics.push(endTime - startTime);
          }, 100); // 10 updates per second
        }
      }
      
      window.WebSocket = MockWebSocket;
    });
    
    // Wait for several updates
    await page.waitForTimeout(2000);
    
    // Check performance metrics
    const avgUpdateTime = await page.evaluate(() => {
      const metrics = window.performanceMetrics;
      return metrics.reduce((sum, time) => sum + time, 0) / metrics.length;
    });
    
    // Assert average update time is under 16ms (60fps)
    expect(avgUpdateTime).toBeLessThan(16);
  });

  test('should optimize bundle size and loading', async ({ page }) => {
    // Enable network monitoring
    const responses = [];
    
    page.on('response', response => {
      if (response.url().includes('.js') || response.url().includes('.css')) {
        responses.push({
          url: response.url(),
          size: response.headers()['content-length'],
          type: response.url().includes('.js') ? 'js' : 'css'
        });
      }
    });
    
    await page.goto('/dashboard');
    
    // Wait for all resources to load
    await page.waitForLoadState('networkidle');
    
    // Calculate total bundle size
    const totalJSSize = responses
      .filter(r => r.type === 'js')
      .reduce((sum, r) => sum + parseInt(r.size || 0), 0);
    
    const totalCSSSize = responses
      .filter(r => r.type === 'css')
      .reduce((sum, r) => sum + parseInt(r.size || 0), 0);
    
    // Assert bundle size limits
    expect(totalJSSize).toBeLessThan(500 * 1024); // JS bundle < 500KB
    expect(totalCSSSize).toBeLessThan(100 * 1024); // CSS bundle < 100KB
    
    // Check for code splitting
    const jsFiles = responses.filter(r => r.type === 'js');
    expect(jsFiles.length).toBeGreaterThan(1); // Should have multiple JS chunks
  });

  test('should handle memory usage efficiently', async ({ page }) => {
    await page.goto('/matching');
    
    // Simulate heavy interaction
    for (let i = 0; i < 10; i++) {
      // Navigate between pages
      await page.click('a[href="/dashboard"]');
      await page.waitForSelector('[data-testid="dashboard-content"]');
      
      await page.click('a[href="/matching"]');
      await page.waitForSelector('[data-testid="match-card"]');
      
      // Trigger re-renders
      await page.click('[data-testid="filter-button"]');
      await page.click('[data-testid="close-filter"]');
    }
    
    // Check memory usage
    const memoryUsage = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        };
      }
      return null;
    });
    
    if (memoryUsage) {
      // Assert memory usage is reasonable
      const usageRatio = memoryUsage.usedJSHeapSize / memoryUsage.jsHeapSizeLimit;
      expect(usageRatio).toBeLessThan(0.5); // Using less than 50% of heap limit
    }
  });

  test('should optimize API response times', async ({ page }) => {
    const apiTimes = [];
    
    // Monitor API requests
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        const timing = response.timing();
        apiTimes.push({
          url: response.url(),
          responseTime: timing.responseEnd - timing.requestStart
        });
      }
    });
    
    await page.goto('/dashboard');
    
    // Navigate to different sections to trigger API calls
    await page.click('a[href="/matching"]');
    await page.waitForSelector('[data-testid="match-card"]');
    
    await page.click('a[href="/notifications"]');
    await page.waitForSelector('[data-testid="notification-item"]');
    
    // Check API response times
    const avgResponseTime = apiTimes.reduce((sum, api) => sum + api.responseTime, 0) / apiTimes.length;
    
    // Assert average API response time is under 500ms
    expect(avgResponseTime).toBeLessThan(500);
    
    // Check that no individual API call takes more than 2 seconds
    const slowAPIs = apiTimes.filter(api => api.responseTime > 2000);
    expect(slowAPIs.length).toBe(0);
  });

  test('should handle concurrent users simulation', async ({ browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts = await Promise.all(
      Array.from({ length: 5 }, () => browser.newContext())
    );
    
    const pages = await Promise.all(
      contexts.map(context => context.newPage())
    );
    
    // Set up each page with authentication
    await Promise.all(
      pages.map(page => 
        page.addInitScript(() => {
          localStorage.setItem('token', 'mock-jwt-token');
          localStorage.setItem('user', JSON.stringify({
            id: Math.floor(Math.random() * 1000),
            email: 'user@example.com',
            username: 'testuser'
          }));
        })
      )
    );
    
    // Simulate concurrent navigation
    const startTime = Date.now();
    
    await Promise.all(
      pages.map(async (page, index) => {
        await page.goto('/dashboard');
        await page.waitForSelector('[data-testid="dashboard-content"]');
        
        // Simulate different user behaviors
        if (index % 2 === 0) {
          await page.click('a[href="/matching"]');
          await page.waitForSelector('[data-testid="match-card"]');
        } else {
          await page.click('a[href="/notifications"]');
          await page.waitForSelector('[data-testid="notification-item"]');
        }
      })
    );
    
    const totalTime = Date.now() - startTime;
    
    // Assert concurrent operations complete within reasonable time
    expect(totalTime).toBeLessThan(10000); // 10 seconds for 5 concurrent users
    
    // Clean up
    await Promise.all(contexts.map(context => context.close()));
  });

  test('should maintain performance with large notification history', async ({ page }) => {
    // Mock large notification dataset
    await page.route('**/api/notifications/**', async route => {
      const largeNotifications = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        title: `Notification ${i + 1}`,
        message: `This is a test notification message ${i + 1}`,
        notification_type: ['collaboration_invite', 'match_found', 'message'][i % 3],
        read_at: i % 3 === 0 ? new Date().toISOString() : null,
        created_at: new Date(Date.now() - i * 60000).toISOString()
      }));

      // Simulate pagination
      const page_num = parseInt(new URL(route.request().url()).searchParams.get('page') || '1');
      const page_size = 20;
      const start = (page_num - 1) * page_size;
      const end = start + page_size;

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: largeNotifications.slice(start, end),
          count: largeNotifications.length,
          next: end < largeNotifications.length ? `?page=${page_num + 1}` : null,
          previous: page_num > 1 ? `?page=${page_num - 1}` : null
        })
      });
    });

    const startTime = Date.now();
    
    await page.goto('/notifications');
    
    // Wait for initial load
    await page.waitForSelector('[data-testid="notification-item"]');
    
    const initialLoadTime = Date.now() - startTime;
    expect(initialLoadTime).toBeLessThan(2000);
    
    // Test pagination performance
    const paginationStartTime = Date.now();
    
    await page.click('[data-testid="next-page"]');
    await page.waitForSelector('[data-testid="notification-item"]');
    
    const paginationTime = Date.now() - paginationStartTime;
    expect(paginationTime).toBeLessThan(1000);
  });

  test('should optimize image loading and rendering', async ({ page }) => {
    // Mock profile images in matching results
    await page.route('**/api/ai/matches/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          matches: Array.from({ length: 20 }, (_, i) => ({
            id: i + 1,
            matched_user: {
              id: i + 100,
              username: `user${i}`,
              profile: {
                avatar: `https://picsum.photos/200/200?random=${i}`,
                skills: ['JavaScript', 'React'],
                location: 'San Francisco, CA'
              }
            },
            match_score: 0.8
          }))
        })
      });
    });

    await page.goto('/matching');
    
    // Wait for images to start loading
    await page.waitForSelector('img[data-testid="user-avatar"]');
    
    // Check for lazy loading implementation
    const images = await page.locator('img[data-testid="user-avatar"]').all();
    
    // Not all images should be loaded immediately (lazy loading)
    const loadedImages = await Promise.all(
      images.map(img => img.evaluate(el => el.complete))
    );
    
    const immediatelyLoaded = loadedImages.filter(Boolean).length;
    expect(immediatelyLoaded).toBeLessThan(images.length);
    
    // Scroll to trigger lazy loading
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    
    // Wait for more images to load
    await page.waitForTimeout(1000);
    
    // Check that more images are now loaded
    const loadedAfterScroll = await Promise.all(
      images.map(img => img.evaluate(el => el.complete))
    );
    
    const totalLoaded = loadedAfterScroll.filter(Boolean).length;
    expect(totalLoaded).toBeGreaterThan(immediatelyLoaded);
  });
});
