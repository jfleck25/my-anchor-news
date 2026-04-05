import re
from playwright.sync_api import Page, expect

def test_pdf_xss_mitigation(page: Page, mocker):
    """
    Verifies that the PDF generation mitigates XSS by escaping HTML entities.
    We mock the API response to return a malicious payload, trigger the PDF download,
    and intercept the newly opened window to check its content.
    """

    malicious_headline = 'Top Story <script>alert("XSS_HEADLINE")</script>'
    escaped_headline = 'Top Story &lt;script&gt;alert("XSS_HEADLINE")&lt;/script&gt;'

    malicious_summary = 'Summary <img src=x onerror=alert("XSS_SUMMARY")>'
    escaped_summary = 'Summary &lt;img src=x onerror=alert("XSS_SUMMARY")&gt;'

    mock_analysis_data = {
        "story_groups": [
            {
                "group_headline": malicious_headline,
                "group_summary": malicious_summary,
                "stories": [
                    {
                        "source": "MaliciousSource",
                        "angle": "Malicious Angle <script>alert(1)</script>"
                    }
                ]
            }
        ],
        "remaining_stories": []
    }

    # Route interception for auth and settings
    page.route("**/api/check_auth", lambda route: route.fulfill(
        status=200, json={"logged_in": True, "user": {"email": "test@example.com", "name": "Test User"}}
    ))
    page.route("**/api/settings", lambda route: route.fulfill(
        status=200, json={"sources": ["wsj.com"], "personality": "anchor"}
    ))

    # Route interception for fetching emails
    page.route("**/api/fetch_emails", lambda route: route.fulfill(
        status=200, json=mock_analysis_data
    ))

    # Route for audio generation to prevent errors
    page.route("**/api/generate_audio", lambda route: route.fulfill(
        status=200, json={"audio_content": "dummy_base64"}
    ))

    # Load the app
    page.goto("http://localhost:3000/")

    # Dismiss tour if it appears
    tour_skip_button = page.locator("text=Skip")
    if tour_skip_button.is_visible():
        tour_skip_button.click()

    # Click the refresh button to trigger data fetch
    refresh_button = page.locator("button[title='Refresh briefing (R)']")
    refresh_button.wait_for()
    refresh_button.click()

    # Wait for the data to be rendered (wait for Top Story tag)
    page.locator("text=Top Story").first.wait_for()

    # Dismiss tour if it appears after data loads
    tour_skip_button = page.locator("text=Skip")
    if tour_skip_button.is_visible():
        tour_skip_button.click()

    # Intercept the new window opened for PDF generation
    with page.context.expect_page() as new_page_info:
        pdf_button = page.locator("button[title='Download as PDF']")
        pdf_button.click(force=True)

    new_page = new_page_info.value

    # Wait for the new page to load its content
    new_page.wait_for_load_state()

    # Get the raw HTML content of the new page
    html_content = new_page.content()

    # Verify that the malicious payloads are not present in their unescaped form
    assert "<script>alert(\"XSS_HEADLINE\")</script>" not in html_content, "XSS vulnerability found in headline!"
    assert "<img src=x onerror=alert(\"XSS_SUMMARY\")>" not in html_content, "XSS vulnerability found in summary!"

    # Verify that the escaped versions are present
    assert escaped_headline in html_content, f"Escaped headline not found. HTML: {html_content[:500]}"
    assert escaped_summary in html_content, "Escaped summary not found"
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_content, "Escaped angle not found"

    print("XSS mitigation test passed!")
