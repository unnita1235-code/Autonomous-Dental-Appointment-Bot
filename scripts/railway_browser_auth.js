#!/usr/bin/env node
/**
 * Automate Railway browserless login using system Chrome.
 * 1. Starts `railway login --browserless` to get a user_code
 * 2. Opens Chrome via Puppeteer to the activate URL
 * 3. Enters the code and waits for auth completion
 */
const { execSync, spawn } = require('child_process');
const puppeteer = require('puppeteer');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
// Use the user's existing Chrome profile so they're already logged in
const USER_DATA_DIR = 'C:\\Users\\unnit\\AppData\\Local\\Google\\Chrome\\User Data';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log('=== Starting Railway browserless login ===\n');

    // Step 1: Start railway login --browserless and capture output
    const output = execSync('railway.cmd login --browserless', { timeout: 15000 }).toString();
    console.log(output);

    // Parse user_code from output
    const match = output.match(/user_code=([A-Z0-9-]+)/);
    if (!match) {
        console.error('Could not find user_code in output');
        process.exit(1);
    }
    const userCode = match[1];
    console.log(`Found user_code: ${userCode}`);

    const activateUrl = `https://railway.com/activate?user_code=${userCode}`;

    // Step 2: Launch Chrome with existing profile
    console.log('\n=== Launching Chrome ===');
    const browser = await puppeteer.launch({
        executablePath: CHROME_PATH,
        userDataDir: USER_DATA_DIR,
        headless: false,
        defaultViewport: null,
        args: [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            `--window-size=1280,900`,
        ],
    });

    const page = await browser.newPage();

    // Navigate to the activate URL
    console.log(`Navigating to ${activateUrl}...`);
    await page.goto(activateUrl, { waitUntil: 'networkidle2', timeout: 30000 });

    await sleep(3000);

    // Check if we're on the activate page
    const pageTitle = await page.title();
    const pageUrl = page.url();
    console.log(`Page title: ${pageTitle}`);
    console.log(`Page URL: ${pageUrl}`);

    // Check if already logged in by looking for the activate form
    const pageContent = await page.content();
    
    // If there's an "Enter code" input, the code might already be pre-filled from the URL
    // Look for the submit button or continue button
    const buttons = await page.$$('button');
    console.log(`Found ${buttons.length} buttons`);
    for (const btn of buttons) {
        const text = await btn.evaluate(el => el.textContent.trim());
        console.log(`  Button: "${text}"`);
    }

    // Try to click "Continue" or "Activate" button if present
    for (const btn of buttons) {
        const text = await btn.evaluate(el => el.textContent.trim().toLowerCase());
        if (text.includes('continue') || text.includes('activate') || text.includes('submit') || text.includes('enter')) {
            console.log(`Clicking button: ${text}`);
            await btn.click();
            await sleep(3000);
            break;
        }
    }

    // Wait and check the new URL
    const newUrl = page.url();
    console.log(`After click URL: ${newUrl}`);

    // Check if we're now on a sign-in page
    if (newUrl.includes('sign-in') || newUrl.includes('login') || newUrl.includes('clerk')) {
        console.log('\n=== On sign-in page ===');
        // Look for email/password fields and sign-in button
        const inputs = await page.$$('input');
        for (const input of inputs) {
            const type = await input.evaluate(el => el.type);
            const name = await input.evaluate(el => el.name);
            const placeholder = await input.evaluate(el => el.placeholder);
            console.log(`  Input: type="${type}" name="${name}" placeholder="${placeholder}"`);
        }
    }

    // Wait for the auth to complete (up to 2 minutes)
    console.log('\n=== Waiting for authentication to complete... ===');
    for (let i = 0; i < 120; i++) {
        await sleep(1000);
        const currentUrl = page.url();
        if (currentUrl.includes('success') || currentUrl.includes('dashboard') || currentUrl.includes('activate/success')) {
            console.log(`Auth completed! Redirected to: ${currentUrl}`);
            break;
        }
        if (i % 10 === 0) {
            console.log(`Still waiting... (${i}s) URL: ${currentUrl}`);
        }
    }

    // Wait a bit more for Railway CLI to pick up the auth
    await sleep(5000);

    console.log('\n=== Checking Railway login status ===');
    try {
        const whoami = execSync('railway.cmd whoami', { timeout: 5000 }).toString();
        console.log(`Logged in as: ${whoami.trim()}`);
    } catch (e) {
        console.log('Not authenticated yet');
    }

    await browser.close();
    console.log('\n=== Done ===');
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
