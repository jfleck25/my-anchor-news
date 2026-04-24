1. **Compile Regex Patterns in `main.py`**
   - The function `optimize_newsletter_for_llm` uses `re.sub` for HTML parsing heavily, calling it repeatedly for each fetched email block in parallel background threads.
   - Using uncompiled regex patterns repeatedly within functions can introduce overhead.
   - We will pre-compile `SCRIPT_STYLE_RE = re.compile(r'<(script|style).*?>.*?</\1>', flags=re.IGNORECASE | re.DOTALL)` and `HTML_TAGS_RE = re.compile(r'<[^>]+>')` at the module level in `main.py`.
   - Update `optimize_newsletter_for_llm` to use these pre-compiled regex objects.
   - We will pre-compile `CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')` at the module level.
   - Update `sanitize_for_llm` to use this pre-compiled regex object.

2. **Remove Unnecessary `.encode('ASCII')` on Base64 Decode**
   - In `_fetch_one_message` function, there is `decoded_data = base64.urlsafe_b64decode(body_data.encode('ASCII'))`
   - `body_data` is a string. `base64.urlsafe_b64decode` accepts string objects. Calling `.encode('ASCII')` introduces an unnecessary, repetitive encoding step in a loop.
   - Update it to `decoded_data = base64.urlsafe_b64decode(body_data)`.

3. **Complete Pre-Commit Steps**
   - Run tests using `python3 -m pytest tests/` to ensure no functionality is broken.
   - Add a journal entry to `.jules/bolt.md` about the learnings (compiling regex patterns and unnecessary encode overhead).

4. **Submit PR**
   - Create a PR titled "⚡ Bolt: [performance improvement] Pre-compile regex and remove redundant encode for email parsing" with a description of the impact.
