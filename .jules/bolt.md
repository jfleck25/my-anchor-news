
## 2026-04-06 - Optimize inner loops with lowercase string comparisons
**Learning:** Found multiple O(n) calls to `.lower()` string methods when comparing arrays of keywords against a main body string and subject string in inner worker threads (`_fetch_one_message`). This issue drastically affects performance, specifically when analyzing many text emails, as Python forces a recomputation of `.lower()` for every element in the keyword list during list comprehensions inside loops.
**Action:** When scanning lists of target keywords in text bodies, pre-compute `.lower()` arrays and strings outside the main scanning loop to avoid redundant allocations and recalculations.

## 2024-04-01 - BeautifulSoup default get_text() behavior
**Learning:** `BeautifulSoup.get_text()` silently extracts the raw JavaScript and CSS text contents embedded inside `<script>` and `<style>` tags by default (for both `lxml` and `html.parser`). This leads to massive unexpected payloads and wasted LLM tokens when parsing raw HTML newsletters, destroying performance and increasing API latency/costs.
**Action:** Always call `.decompose()` on `<script>` and `<style>` elements found by BeautifulSoup before running `.get_text()` if the goal is to extract clean, human-readable text for LLM prompts.
