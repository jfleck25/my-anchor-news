🎯 **What:**
Refactored the overly complex `_fetch_one_message` function by extracting four logical blocks into smaller helper functions (`_extract_email_body`, `_decode_and_sanitize_body`, `_matches_keywords`, and `_is_priority_sender`).

💡 **Why:**
The original function was nearly 60 lines long, making it difficult to read, test, and maintain. By isolating pure logic blocks into dedicated helper functions, we improve modularity and reduce cognitive load for developers working within the concurrent fetch cycle. It also slightly improves robustness by using `.get()` for dictionary lookups on the payload headers.

✅ **Verification:**
Verified using `py_compile main.py`, unit tested with mock configurations on the extracted helper blocks, and ran `test_security.py` successfully.

✨ **Result:**
`_fetch_one_message` is now much shorter, linear, and explicitly conveys its data flow.
