/**
 * Debug Screenshot Script - Test Authentication Bypass
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = '/Users/amays/Desktop/Work/Colab/Testing screenshots';
const BASE_URL = 'http://localhost:3001';

async function testAuthenticationBypass() {
  console.log('🔍 Testing authentication bypass...');
  
  const browser = await chromium.launch({ 
    headless: false, // Run in visible mode to see what's happening
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  try {
    // Set viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    
    // Test 1: Check if frontend is accessible
    console.log('1. Testing frontend accessibility...');
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 10000 });
    console.log(`✅ Frontend accessible at: ${page.url()}`);
    
    // Test 2: Set mock authentication in localStorage
    console.log('2. Setting mock authentication...');
    await page.evaluate(() => {
      localStorage.setItem('token', 'mock-jwt-token-for-screenshots');
      const mockUser = {
        id: 'test-user-123',
        email: 'test@example.com',
        username: 'testuser'
      };
      localStorage.setItem('user', JSON.stringify(mockUser));
    });
    
    // Test 3: Try to access dashboard with screenshot parameter
    console.log('3. Testing dashboard access with screenshot mode...');
    await page.goto(`${BASE_URL}/dashboard?screenshot=true`, { 
      waitUntil: 'networkidle', 
      timeout: 15000 
    });
    
    console.log(`Current URL: ${page.url()}`);
    
    // Check if we're still on login page or successfully on dashboard
    const isOnLogin = page.url().includes('/login');
    const isOnDashboard = page.url().includes('/dashboard');
    
    if (isOnLogin) {
      console.log('❌ Still redirected to login page');
      
      // Check console errors
      const logs = await page.evaluate(() => {
        return window.console._logs || [];
      });
      console.log('Console logs:', logs);
      
      // Take a debug screenshot
      await page.screenshot({ 
        path: path.join(SCREENSHOT_DIR, 'DEBUG_login_redirect.png'),
        fullPage: true
      });
      
    } else if (isOnDashboard) {
      console.log('✅ Successfully accessed dashboard!');
      
      // Take a success screenshot
      await page.screenshot({ 
        path: path.join(SCREENSHOT_DIR, 'DEBUG_dashboard_success.png'),
        fullPage: false
      });
      
      // Test tab navigation
      console.log('4. Testing tab navigation...');
      try {
        await page.click('button:has-text("AI Tools")');
        await page.waitForTimeout(2000);
        console.log('✅ AI Tools tab clicked successfully');
        
        await page.screenshot({ 
          path: path.join(SCREENSHOT_DIR, 'DEBUG_ai_tools_tab.png'),
          fullPage: false
        });
        
      } catch (error) {
        console.log('❌ Tab navigation failed:', error.message);
      }
    }
    
    // Test 4: Check authentication context state
    console.log('5. Checking authentication context state...');
    const authState = await page.evaluate(() => {
      return {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user'),
        hasAuthContext: !!window.React
      };
    });
    
    console.log('Auth state:', authState);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    // Take error screenshot
    try {
      await page.screenshot({ 
        path: path.join(SCREENSHOT_DIR, 'DEBUG_error_state.png'),
        fullPage: true
      });
    } catch (e) {
      console.log('Could not capture error screenshot');
    }
  } finally {
    await browser.close();
  }
}

async function main() {
  console.log('🚀 Starting authentication bypass debug...');
  
  // Ensure screenshot directory exists
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }
  
  await testAuthenticationBypass();
  
  console.log('🔍 Debug complete. Check screenshots in:', SCREENSHOT_DIR);
}

main().catch(console.error);
