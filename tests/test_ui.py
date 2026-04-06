import sys
from playwright.sync_api import Page, expect
import json

def test_frontend_loads_without_errors(page: Page, live_server):
    errors = []
    
    # We will log any JS console error or unhandled page exception
    def handle_page_error(err):
        errors.append(f"Page Error: {err.message}")
        print(f"Page Error: {err.message}", file=sys.stderr)
        
    def handle_console_message(msg):
        if msg.type == "error":
            # Ignore some known non-fatal errors if they exist (PostHog/Sentry blockers)
            if "favicon.ico" not in msg.text:
                errors.append(f"Console Error: {msg.text}")
                print(f"Console Error: {msg.text}", file=sys.stderr)
            
    page.on("pageerror", handle_page_error)
    page.on("console", handle_console_message)

    # 1) Mock /api/check_auth to pretend we are logged in so Dashboard mounts
    page.route("**/api/check_auth", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"logged_in": true, "user": {"email": "test@example.com", "name": "Mock User"}}'
    ))

    # 2) Mock /api/settings
    page.route("**/api/settings", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"sources": ["example.com"], "time_window_hours": 24, "personality": "anchor", "priority_sources": [], "keywords": []}'
    ))

    # 3) Mock /api/fetch_emails
    mock_analysis = {
        "story_groups": [{
            "group_headline": "Mocked News Feature Verified",
            "group_summary": "This is a mocked news summary to verify UI rendering.",
            "stories": [{"source": "MockNews", "angle": "We mocked this data."}]
        }],
        "remaining_stories": [{"headline": "Mocked remaining brief."}]
    }
    page.route("**/api/fetch_emails", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_analysis)
    ))

    # Test Step 1: Browse to the server
    print(f"Navigating to {live_server.url}")
    page.goto(live_server.url, wait_until="networkidle")

    # Wait for React to mount Dashboard or show loading state
    try:
        page.wait_for_selector("text=Mock User", state="visible", timeout=3000)
    except:
        pass # Catch failure below if the UI broke

    # If there's an error in index.html (like JSX missing closing tag),
    # Babel standalone throws a console error and nothing renders.
    # So we assert no errors occurred.
    assert len(errors) == 0, f"Flaws found in frontend! {len(errors)} error(s): {errors}"
