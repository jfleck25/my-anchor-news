const puppeteer = require('puppeteer');
const express = require('express');
const path = require('path');

const app = express();
// Serve the main directory so /templates/index.html is accessible
app.use(express.static(path.join(__dirname, '..')));

const server = app.listen(5002, async () => {
    console.log("Start headless test server on port 5002");

    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-web-security']
        });
        const page = await browser.newPage();
        let errors = [];

        page.on('pageerror', err => {
            errors.push(`PageError: ${err.message}`);
        });

        page.on('console', msg => {
            const text = msg.text();
            if (msg.type() === 'error' && !text.includes('favicon') && !text.includes('failed to load') && !text.includes('Sentry SDK failed') && !text.includes('404') && !text.includes('React DevTools')) {
                errors.push(`ConsoleError: ${text}`);
            }
        });

        // Intercept API calls to mock backend
        await page.setRequestInterception(true);
        page.on('request', req => {
            const url = req.url();
            if (url.includes('/api/check_auth')) {
                req.respond({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ logged_in: true, user: { email: "test@example.com", name: "MockUser" } })
                });
            } else if (url.includes('/api/settings')) {
                req.respond({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ sources: [], time_window_hours: 24, personality: "anchor", priority_sources: [], keywords: [] })
                });
            } else if (url.includes('/api/fetch_emails')) {
                req.respond({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        story_groups: [{ group_headline: "Testing Success", group_summary: "Test UI logic" }],
                        remaining_stories: []
                    })
                });
            } else if (url.includes('posthog') || url.includes('sentry')) {
                req.respond({ status: 200, body: '' }); // stub trackers
            } else {
                req.continue();
            }
        });

        console.log("Navigating to index.html...");
        await page.goto('http://localhost:5002/templates/index.html', { waitUntil: 'networkidle0' });

        try {
            console.log("Waiting for user to login via mock...");
            await page.waitForFunction(() => document.body.innerText.includes("Good"));

            console.log("Testing skip link focus via keyboard...");
            await page.keyboard.press("Tab");
            await new Promise(r => setTimeout(r, 500));

            await page.screenshot({ path: '/home/jules/verification/screenshots/verification.png' });

            await page.keyboard.press("Enter");
            await new Promise(r => setTimeout(r, 500));

            await page.keyboard.press("Tab");
            await new Promise(r => setTimeout(r, 500));

            // Wait to capture errors
            await new Promise(r => setTimeout(r, 1000));
        } catch(e) { console.error("Could not complete test", e); }

        if (errors.length > 0) {
            console.error("FLAWS DETECTED:");
            console.error(errors.join("\n"));
            process.exit(1);
        } else {
            console.log("Success! No rendering or compilation flaws detected.");
            process.exit(0);
        }
    } catch (err) {
        console.error("Test execution failed:", err);
        process.exit(1);
    } finally {
        if (browser) await browser.close();
        server.close();
    }
});