const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to quick-chart page...');
    await page.goto('http://localhost:3000/quick-chart');
    await page.waitForLoadState('networkidle');

    console.log('Page loaded, taking screenshot 1...');
    await page.screenshot({ path: 'screenshot1-initial.png', fullPage: true });

    // Step 1: Fill birth data
    console.log('Step 1: Filling birth data...');
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="birthDate"]', '1990-04-15');
    await page.fill('input[name="birthTime"]', '14:30');
    await page.fill('input[name="birthCity"]', 'Buenos Aires');
    await page.fill('input[name="birthCountry"]', 'AR');
    await page.fill('input[name="birthTimezone"]', 'America/Argentina/Buenos_Aires');

    await page.screenshot({ path: 'screenshot2-step1-filled.png', fullPage: true });

    console.log('Clicking Next button...');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(1000);

    await page.screenshot({ path: 'screenshot3-step2-loaded.png', fullPage: true });

    // Step 2: Additional options (planets and house system)
    console.log('Step 2: On additional options page');

    // Try to find checkboxes and selects
    const checkboxes = await page.locator('input[type="checkbox"]').count();
    console.log(`Found ${checkboxes} checkboxes`);

    const selects = await page.locator('select').count();
    console.log(`Found ${selects} select elements`);

    // Check for any error messages
    const errors = await page.locator('[role="alert"], .error, .MuiAlert-root').count();
    console.log(`Found ${errors} error messages`);

    if (errors > 0) {
      const errorText = await page.locator('[role="alert"], .error, .MuiAlert-root').first().textContent();
      console.log('Error message:', errorText);
    }

    // Try to interact with planet checkboxes
    console.log('Looking for Chiron checkbox...');
    const chironCheckbox = page.locator('input[type="checkbox"][name*="chiron"], input[type="checkbox"][value="chiron"]');
    const chironCount = await chironCheckbox.count();
    console.log(`Found ${chironCount} Chiron checkboxes`);

    if (chironCount > 0) {
      console.log('Clicking Chiron checkbox...');
      await chironCheckbox.first().click();
      await page.waitForTimeout(500);
    }

    // Try to find house system select
    console.log('Looking for house system select...');
    const houseSystemSelect = page.locator('select[name*="house"], select[name*="houseSystem"]');
    const houseSelectCount = await houseSystemSelect.count();
    console.log(`Found ${houseSelectCount} house system selects`);

    if (houseSelectCount > 0) {
      console.log('Changing house system...');
      await houseSystemSelect.first().selectOption('koch');
      await page.waitForTimeout(500);
    }

    await page.screenshot({ path: 'screenshot4-step2-interacted.png', fullPage: true });

    console.log('Clicking Next button (step 2)...');
    const nextButton = page.locator('button:has-text("Next")');
    const nextCount = await nextButton.count();
    console.log(`Found ${nextCount} Next buttons`);

    if (nextCount > 0) {
      await nextButton.first().click();
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'screenshot5-step3-loaded.png', fullPage: true });
    }

    // Check if we're on step 3 (review)
    const calculateButton = page.locator('button:has-text("Calculate")');
    const calculateCount = await calculateButton.count();
    console.log(`Found ${calculateCount} Calculate buttons`);

    if (calculateCount > 0) {
      console.log('On review step, clicking Calculate...');
      await calculateButton.first().click();

      // Wait for response
      await page.waitForTimeout(5000);
      await page.screenshot({ path: 'screenshot6-results.png', fullPage: true });

      // Check for results or errors
      const svgCount = await page.locator('svg').count();
      console.log(`Found ${svgCount} SVG elements`);

      const resultErrors = await page.locator('[role="alert"], .error').count();
      if (resultErrors > 0) {
        const resultErrorText = await page.locator('[role="alert"], .error').first().textContent();
        console.log('Result error:', resultErrorText);
      }
    }

    console.log('Test completed!');
    console.log('Screenshots saved. Press Ctrl+C to close browser.');
    await page.waitForTimeout(60000); // Wait 1 minute to inspect

  } catch (error) {
    console.error('Error during test:', error);
    await page.screenshot({ path: 'screenshot-error.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
