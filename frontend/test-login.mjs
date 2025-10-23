import { chromium } from '@playwright/test';

async function testLogin() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to the app
    console.log('Navigating to http://localhost:5000...');
    await page.goto('http://localhost:5000');

    // Wait for page to load
    await page.waitForTimeout(2000);

    // Take a screenshot of initial state
    console.log('Taking screenshot of initial page...');
    await page.screenshot({ path: 'screenshot-1-initial.png' });

    // Get page title
    const title = await page.title();
    console.log('Page title:', title);

    // Try to find email/username input
    console.log('\nLooking for login form...');

    // Check for common input selectors
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[name="username"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"]').first();

    if (await emailInput.count() > 0) {
      console.log('Found email/username input');

      // Fill in credentials
      console.log('Filling in credentials...');
      await emailInput.fill('consultant@astrojoy.com');
      await passwordInput.fill('Consultant123!');

      // Take screenshot before clicking login
      await page.screenshot({ path: 'screenshot-2-before-login.png' });

      // Look for submit button
      const loginButton = await page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first();

      if (await loginButton.count() > 0) {
        console.log('Found login button, clicking...');

        // Listen for network requests
        page.on('request', request => {
          if (request.url().includes('auth') || request.url().includes('login')) {
            console.log('REQUEST:', request.method(), request.url());
            console.log('POST DATA:', request.postData());
          }
        });

        page.on('response', async response => {
          if (response.url().includes('auth') || response.url().includes('login')) {
            console.log('RESPONSE:', response.status(), response.url());
            try {
              const body = await response.text();
              console.log('RESPONSE BODY:', body);
            } catch (e) {
              console.log('Could not read response body');
            }
          }
        });

        await loginButton.click();

        // Wait for response
        await page.waitForTimeout(3000);

        // Take screenshot after login attempt
        await page.screenshot({ path: 'screenshot-3-after-login.png' });

        // Check for error messages
        const errorSelectors = [
          '.error',
          '.alert',
          '[role="alert"]',
          '.MuiAlert-root',
          'text="Invalid"',
          'text="Error"'
        ];

        for (const selector of errorSelectors) {
          const errorElement = await page.locator(selector).first();
          if (await errorElement.count() > 0) {
            const errorText = await errorElement.textContent();
            console.log('ERROR MESSAGE FOUND:', errorText);
          }
        }

        // Get current URL
        const currentUrl = page.url();
        console.log('Current URL after login:', currentUrl);

      } else {
        console.log('Login button not found!');
      }
    } else {
      console.log('Login form not found!');
      console.log('Page HTML:');
      const html = await page.content();
      console.log(html.substring(0, 500) + '...');
    }

  } catch (error) {
    console.error('ERROR:', error.message);
    await page.screenshot({ path: 'screenshot-error.png' });
  } finally {
    await page.waitForTimeout(2000);
    await browser.close();
    console.log('\nTest completed. Check screenshots for details.');
  }
}

testLogin();
