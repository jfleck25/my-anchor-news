🎯 **What:** The `analyze_news_with_llm` function was heavily bloated, containing both the massive, multi-line string for constructing the AI prompt and the complex logic necessary to extract and validate JSON responses from the raw Gemini API output. These concerns have been extracted into two private helper functions: `_build_analysis_prompt` and `_parse_llm_response`.

💡 **Why:** This refactoring significantly improves the readability and maintainability of the main module. By separating the string construction and output parsing logic, the core `analyze_news_with_llm` function becomes much shorter and is now solely focused on handling high-level API orchestration, validation, and error management. This makes it easier to test prompt changes or JSON parsing rules independently in the future.

✅ **Verification:**
1. Manually verified the helper extractions via `grep` and source code inspection.
2. The core unit tests (`test_main.py` and `test_security.py`) were executed and verified to pass, confirming that application routing and global mocks continue to work properly. All previous exception-catching blocks and API behaviors are preserved intact.

✨ **Result:** The `analyze_news_with_llm` function is significantly cleaner, reducing cognitive load for future maintenance while fully preserving its existing capability and error-handling flow.
