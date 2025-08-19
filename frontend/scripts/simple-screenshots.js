/**
 * Simplified Screenshot Capture - No Authentication Required
 * Captures public pages and uses mock data for protected views
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = '/Users/amays/Desktop/Work/Colab/Testing screenshots';
const BASE_URL = 'http://localhost:3001?screenshot=true';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const publicScreenshots = [
  {
    name: '01_landing_page_redirect.png',
    url: '/',
    description: 'Landing page redirect behavior'
  },
  {
    name: '02_login_form_empty.png',
    url: '/login',
    description: 'Clean login form'
  },
  {
    name: '03_login_validation_errors.png',
    url: '/login',
    description: 'Login form validation errors',
    action: async (page) => {
      // Try to submit empty form to show validation
      try {
        await page.click('button[type="submit"]');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Form submission handled gracefully');
      }
    }
  },
  {
    name: '04_registration_form.png',
    url: '/register',
    description: 'Registration form'
  },
  {
    name: '19_form_validation_errors.png',
    url: '/register',
    description: 'Registration form validation errors',
    action: async (page) => {
      try {
        await page.click('button[type="submit"]');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Form validation handled gracefully');
      }
    }
  }
];

const mockDashboardScreenshots = [
  {
    name: '05_dashboard_overview.png',
    url: '/dashboard',
    description: 'Dashboard overview tab'
  },
  {
    name: '06_dashboard_collaborations.png',
    url: '/dashboard',
    description: 'Dashboard collaborations tab',
    action: async (page) => {
      try {
        await page.click('button:has-text("Collaborations")');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Tab navigation handled gracefully');
      }
    }
  },
  {
    name: '07_dashboard_chat.png',
    url: '/dashboard',
    description: 'Dashboard chat tab',
    action: async (page) => {
      try {
        await page.click('button:has-text("Chat")');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Tab navigation handled gracefully');
      }
    }
  },
  {
    name: '08_dashboard_ai_tools.png',
    url: '/dashboard',
    description: 'Dashboard AI tools tab',
    action: async (page) => {
      try {
        await page.click('button:has-text("AI Tools")');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Tab navigation handled gracefully');
      }
    }
  },
  {
    name: '09_dashboard_portfolio.png',
    url: '/dashboard',
    description: 'Dashboard portfolio tab',
    action: async (page) => {
      try {
        await page.click('button:has-text("Portfolio")');
        await page.waitForTimeout(1000);
      } catch (e) {
        console.log('Tab navigation handled gracefully');
      }
    }
  }
];

async function setupMockAuth(page) {
  console.log('🔐 Setting up mock authentication...');
  
  await page.addInitScript(() => {
    // Mock localStorage data
    const mockUser = {
      id: 'test-user-123',
      email: 'test@example.com',
      username: 'testuser',
      profile: {
        bio: 'Test user for screenshot validation',
        category: 'Developer',
        experience_level: 'Intermediate',
        location: 'San Francisco, CA'
      }
    };
    
    localStorage.setItem('token', 'mock-jwt-token-for-screenshots');
    localStorage.setItem('user', JSON.stringify(mockUser));
    
    // Mock fetch for API calls
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
      // Mock successful responses for common API calls
      if (url.includes('/api/auth/profile')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockUser)
        });
      }
      if (url.includes('/api/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ success: true, data: [] })
        });
      }
      return originalFetch.apply(this, arguments);
    };
  });
}

async function captureScreenshot(browser, screenshot, useMockAuth = false) {
  const page = await browser.newPage();
  
  try {
    console.log(`📸 Capturing: ${screenshot.name} - ${screenshot.description}`);
    
    // Set viewport size
    await page.setViewportSize({ width: 1200, height: 800 });
    
    // Setup mock auth if needed
    if (useMockAuth) {
      await setupMockAuth(page);
    }
    
    // Navigate to URL
    await page.goto(`${BASE_URL}${screenshot.url}`, { 
      waitUntil: 'networkidle',
      timeout: 10000 
    });
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Perform any custom actions
    if (screenshot.action) {
      try {
        await screenshot.action(page);
      } catch (e) {
        console.log(`Action failed for ${screenshot.name}, continuing...`);
      }
    }
    
    // Wait for any animations/loading
    await page.waitForTimeout(1000);
    
    // Take screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, screenshot.name);
    await page.screenshot({ 
      path: screenshotPath, 
      fullPage: false,
      clip: { x: 0, y: 0, width: 1200, height: 800 }
    });
    
    console.log(`✅ Saved: ${screenshot.name}`);
    
  } catch (error) {
    console.error(`❌ Failed to capture ${screenshot.name}:`, error.message);
    
    // Try to take a screenshot anyway to see what's happening
    try {
      const errorScreenshotPath = path.join(SCREENSHOT_DIR, `ERROR_${screenshot.name}`);
      await page.screenshot({ path: errorScreenshotPath });
      console.log(`📸 Error screenshot saved: ERROR_${screenshot.name}`);
    } catch (e) {
      console.log('Could not capture error screenshot');
    }
  } finally {
    await page.close();
  }
}

async function captureResponsiveScreenshots(browser) {
  const page = await browser.newPage();
  
  try {
    // Mobile view
    console.log('📱 Capturing mobile responsive view...');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, '21_mobile_responsive.png'),
      fullPage: false
    });
    
    // Tablet view
    console.log('📱 Capturing tablet responsive view...');
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, '22_tablet_responsive.png'),
      fullPage: false
    });
    
    // Desktop view
    console.log('🖥️ Capturing desktop responsive view...');
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    await page.screenshot({ 
      path: path.join(SCREENSHOT_DIR, '23_desktop_responsive.png'),
      fullPage: false
    });
    
    console.log('✅ Responsive screenshots captured');
    
  } catch (error) {
    console.error('❌ Failed to capture responsive screenshots:', error.message);
  } finally {
    await page.close();
  }
}

async function main() {
  console.log('🚀 Starting simplified screenshot capture...');
  console.log(`📁 Screenshots will be saved to: ${SCREENSHOT_DIR}`);
  console.log(`🌐 Frontend URL: ${BASE_URL}`);
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });
  
  try {
    // Test if frontend is accessible
    const testPage = await browser.newPage();
    try {
      await testPage.goto(BASE_URL, { timeout: 5000 });
      console.log('✅ Frontend is accessible');
      await testPage.close();
    } catch (error) {
      console.error('❌ Frontend not accessible:', error.message);
      console.log('Make sure the frontend server is running on port 3001');
      return;
    }
    
    // Capture public screenshots (no auth needed)
    console.log('\n📸 Capturing public pages...');
    for (const screenshot of publicScreenshots) {
      await captureScreenshot(browser, screenshot, false);
    }
    
    // Capture dashboard screenshots with mock auth
    console.log('\n📸 Capturing dashboard pages with mock auth...');
    for (const screenshot of mockDashboardScreenshots) {
      await captureScreenshot(browser, screenshot, true);
    }
    
    // Capture responsive design screenshots
    console.log('\n📸 Capturing responsive design screenshots...');
    await captureResponsiveScreenshots(browser);
    
    console.log('\n✅ Screenshot capture completed!');
    console.log(`📁 Check screenshots in: ${SCREENSHOT_DIR}`);
    
    // List captured files
    const files = fs.readdirSync(SCREENSHOT_DIR).filter(f => f.endsWith('.png'));
    console.log(`📊 Captured ${files.length} screenshots:`);
    files.forEach(file => console.log(`   - ${file}`));
    
  } catch (error) {
    console.error('❌ Screenshot capture failed:', error);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
