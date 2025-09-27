import { test, expect } from '@playwright/test';

test.describe('Creator Matching Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        email: 'creator@example.com',
        username: 'creator1',
        profile: {
          skills: ['JavaScript', 'React', 'Node.js'],
          location: 'San Francisco, CA'
        }
      }));
    });
  });

  test('should display matching dashboard', async ({ page }) => {
    // Mock matching API responses
    await page.route('**/api/ai/matches/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          matches: [
            {
              id: 1,
              matched_user: {
                id: 2,
                username: 'designer1',
                profile: {
                  skills: ['UI/UX', 'Figma', 'Adobe Creative Suite'],
                  location: 'Los Angeles, CA',
                  bio: 'Passionate UI/UX designer with 5 years of experience'
                }
              },
              match_score: 0.85,
              compatibility_reasons: ['Complementary skills', 'Similar location']
            },
            {
              id: 2,
              matched_user: {
                id: 3,
                username: 'developer2',
                profile: {
                  skills: ['Python', 'Django', 'Machine Learning'],
                  location: 'Seattle, WA',
                  bio: 'Full-stack developer specializing in AI applications'
                }
              },
              match_score: 0.78,
              compatibility_reasons: ['Technical expertise', 'Project experience']
            }
          ],
          total: 2,
          page: 1
        })
      });
    });

    await page.goto('/matching');

    // Check if matching dashboard loads
    await expect(page.locator('h1')).toContainText('Find Your Perfect Collaborator');
    
    // Check if matches are displayed
    await expect(page.locator('[data-testid="match-card"]')).toHaveCount(2);
    
    // Check match details
    await expect(page.locator('text=designer1')).toBeVisible();
    await expect(page.locator('text=developer2')).toBeVisible();
    await expect(page.locator('text=85% Match')).toBeVisible();
    await expect(page.locator('text=78% Match')).toBeVisible();
  });

  test('should filter matches by skills', async ({ page }) => {
    await page.goto('/matching');
    
    // Wait for initial load
    await page.waitForSelector('[data-testid="match-card"]');
    
    // Open filters
    await page.click('[data-testid="filter-button"]');
    
    // Select skill filter
    await page.click('input[name="skills"][value="UI/UX"]');
    
    // Mock filtered API response
    await page.route('**/api/ai/matches/**', async route => {
      const url = new URL(route.request().url());
      if (url.searchParams.get('skills')?.includes('UI/UX')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            matches: [
              {
                id: 1,
                matched_user: {
                  id: 2,
                  username: 'designer1',
                  profile: {
                    skills: ['UI/UX', 'Figma', 'Adobe Creative Suite'],
                    location: 'Los Angeles, CA'
                  }
                },
                match_score: 0.85
              }
            ],
            total: 1
          })
        });
      }
    });
    
    // Apply filters
    await page.click('button[data-testid="apply-filters"]');
    
    // Check filtered results
    await expect(page.locator('[data-testid="match-card"]')).toHaveCount(1);
    await expect(page.locator('text=designer1')).toBeVisible();
  });

  test('should send collaboration invite', async ({ page }) => {
    await page.goto('/matching');
    
    // Wait for matches to load
    await page.waitForSelector('[data-testid="match-card"]');
    
    // Click on first match
    await page.click('[data-testid="match-card"]:first-child');
    
    // Check if match details modal opens
    await expect(page.locator('[data-testid="match-modal"]')).toBeVisible();
    
    // Click invite button
    await page.click('button[data-testid="send-invite"]');
    
    // Fill invite form
    await page.fill('textarea[name="message"]', 'Hi! I\'d love to collaborate on a project with you.');
    await page.selectOption('select[name="project_type"]', 'Web Application');
    
    // Mock invite API response
    await page.route('**/api/collaborations/invites/send/', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          message: 'Collaboration invite sent successfully',
          invite: {
            id: 1,
            recipient: { username: 'designer1' },
            status: 'pending'
          }
        })
      });
    });
    
    // Send invite
    await page.click('button[data-testid="confirm-invite"]');
    
    // Check success message
    await expect(page.locator('text=Invite sent successfully')).toBeVisible();
    
    // Check if modal closes
    await expect(page.locator('[data-testid="match-modal"]')).not.toBeVisible();
  });

  test('should handle match rejection', async ({ page }) => {
    await page.goto('/matching');
    
    // Wait for matches to load
    await page.waitForSelector('[data-testid="match-card"]');
    
    // Click reject button on first match
    await page.click('[data-testid="reject-match"]:first-child');
    
    // Mock rejection API response
    await page.route('**/api/ai/matches/*/reject/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Match rejected' })
      });
    });
    
    // Confirm rejection
    await page.click('button[data-testid="confirm-reject"]');
    
    // Check if match is removed
    await expect(page.locator('[data-testid="match-card"]')).toHaveCount(1);
  });

  test('should display match analytics', async ({ page }) => {
    // Mock analytics API response
    await page.route('**/api/analytics/matching/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user_stats: {
            total_matches: 25,
            invites_sent: 8,
            invites_received: 12,
            successful_collaborations: 3,
            match_acceptance_rate: 0.65
          },
          recent_activity: [
            { type: 'match_found', date: '2025-09-24', count: 3 },
            { type: 'invite_sent', date: '2025-09-23', count: 1 },
            { type: 'invite_received', date: '2025-09-22', count: 2 }
          ]
        })
      });
    });

    await page.goto('/matching/analytics');

    // Check analytics display
    await expect(page.locator('text=25')).toBeVisible(); // Total matches
    await expect(page.locator('text=65%')).toBeVisible(); // Acceptance rate
    await expect(page.locator('text=3')).toBeVisible(); // Successful collaborations
  });

  test('should search for specific creators', async ({ page }) => {
    await page.goto('/matching');
    
    // Use search functionality
    await page.fill('input[data-testid="search-input"]', 'UI designer');
    
    // Mock search API response
    await page.route('**/api/ai/search/**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              id: 4,
              username: 'ui_expert',
              profile: {
                skills: ['UI Design', 'Prototyping', 'User Research'],
                location: 'New York, NY',
                bio: 'Senior UI designer with expertise in user-centered design'
              },
              relevance_score: 0.92
            }
          ],
          total: 1
        })
      });
    });
    
    // Trigger search
    await page.press('input[data-testid="search-input"]', 'Enter');
    
    // Check search results
    await expect(page.locator('text=ui_expert')).toBeVisible();
    await expect(page.locator('text=92% Relevance')).toBeVisible();
  });

  test('should handle geolocation-based matching', async ({ page }) => {
    // Mock geolocation
    await page.context().grantPermissions(['geolocation']);
    await page.setGeolocation({ latitude: 37.7749, longitude: -122.4194 }); // San Francisco
    
    await page.goto('/matching');
    
    // Enable location-based matching
    await page.click('[data-testid="location-toggle"]');
    
    // Mock location-based matches
    await page.route('**/api/ai/matches/**', async route => {
      const url = new URL(route.request().url());
      if (url.searchParams.get('use_location') === 'true') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            matches: [
              {
                id: 5,
                matched_user: {
                  username: 'local_creator',
                  profile: {
                    location: 'San Francisco, CA',
                    distance: 2.5
                  }
                },
                match_score: 0.80
              }
            ]
          })
        });
      }
    });
    
    // Check location-based results
    await expect(page.locator('text=2.5 miles away')).toBeVisible();
  });

  test('should save favorite matches', async ({ page }) => {
    await page.goto('/matching');
    
    // Wait for matches to load
    await page.waitForSelector('[data-testid="match-card"]');
    
    // Click favorite button
    await page.click('[data-testid="favorite-button"]:first-child');
    
    // Mock favorite API response
    await page.route('**/api/ai/favorites/', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Added to favorites' })
      });
    });
    
    // Check favorite status
    await expect(page.locator('[data-testid="favorite-button"]:first-child')).toHaveClass(/favorited/);
    
    // Navigate to favorites
    await page.click('a[href="/matching/favorites"]');
    
    // Check favorites page
    await expect(page.locator('h1')).toContainText('Favorite Creators');
    await expect(page.locator('[data-testid="match-card"]')).toHaveCount(1);
  });
});
