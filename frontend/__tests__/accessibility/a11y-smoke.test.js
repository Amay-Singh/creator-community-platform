import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Accessibility Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await injectAxe(page);
  });

  test('login page should be accessible', async ({ page }) => {
    await page.goto('/auth/login');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('register page should be accessible', async ({ page }) => {
    await page.goto('/auth/register');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('search page should be accessible', async ({ page }) => {
    // Mock authentication
    await page.goto('/search');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('profile view should be accessible', async ({ page }) => {
    await page.goto('/profile/1');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('profile edit should be accessible', async ({ page }) => {
    await page.goto('/profile/edit');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('chat interface should be accessible', async ({ page }) => {
    await page.goto('/chat/thread-123');
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    });
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();
  });

  test('should have proper focus indicators', async ({ page }) => {
    await page.goto('/auth/login');
    
    const emailInput = page.locator('input[name="email"]');
    await emailInput.focus();
    
    // Check that focus-visible styles are applied
    const focusStyles = await emailInput.evaluate(el => {
      return window.getComputedStyle(el, ':focus-visible').outline;
    });
    
    expect(focusStyles).toBeTruthy();
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/auth/login');
    
    await checkA11y(page, null, {
      rules: {
        'color-contrast': { enabled: true }
      }
    });
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/search');
    
    await checkA11y(page, null, {
      rules: {
        'heading-order': { enabled: true }
      }
    });
  });

  test('should have accessible form labels', async ({ page }) => {
    await page.goto('/auth/register');
    
    await checkA11y(page, null, {
      rules: {
        'label': { enabled: true },
        'label-title-only': { enabled: true }
      }
    });
  });

  test('should support screen reader navigation', async ({ page }) => {
    await page.goto('/profile/1');
    
    // Check for proper ARIA landmarks
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('aside')).toBeVisible();
  });

  test('should have accessible interactive elements', async ({ page }) => {
    await page.goto('/search');
    
    await checkA11y(page, null, {
      rules: {
        'button-name': { enabled: true },
        'link-name': { enabled: true }
      }
    });
  });
});
