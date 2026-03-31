# My Anchor Model Analysis: Token Optimization Script Review

## Agent Review Notes
I have reviewed the provided Python snippet for optimizing newsletter tokens before sending them to Gemini.

### The Original Snippet:
```python
import re
def optimize_newsletter_for_llm(html_content: str, max_chars: int = 15000) -> str:
    """Strips HTML tags and extra whitespace to massively reduce LLM token usage."""
    # Strip HTML tags
    text_only = re.sub('<[^<]+?>', ' ', html_content)
    # Remove extra whitespace (newline, tabs)
    clean_text = ' '.join(text_only.split())
    # Truncate to save tokens if it's too long
    return clean_text[:max_chars]
```

### Review Feedback
While the regex approach `re.sub('<[^<]+?>', ' ', html_content)` removes HTML tags, it fails to remove the **contents** of `<script>` and `<style>` blocks. Because newsletters frequently contain massive CSS blocks, this regex would leave raw CSS code in the payload, unnecessarily burning through tokens.

Because the My Anchor backend codebase already imports and uses `BeautifulSoup`, I have updated the function to leverage `BeautifulSoup` instead of regex to accurately strip styles, scripts, and format the final text compactly.

### Implementation Details
I injected the improved function directly into `main.py` and modified `_fetch_one_message`, completely replacing the old 4,000 character limit implementation with this new 15,000 character threshold as specified. The codebase is now successfully using `optimize_newsletter_for_llm()` to clean tokens cleanly before passing the result to Gemini.
