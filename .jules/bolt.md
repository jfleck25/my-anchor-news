
## 2026-04-06 - Optimize inner loops with lowercase string comparisons
**Learning:** Found multiple O(n) calls to `.lower()` string methods when comparing arrays of keywords against a main body string and subject string in inner worker threads (`_fetch_one_message`). This issue drastically affects performance, specifically when analyzing many text emails, as Python forces a recomputation of `.lower()` for every element in the keyword list during list comprehensions inside loops.
**Action:** When scanning lists of target keywords in text bodies, pre-compute `.lower()` arrays and strings outside the main scanning loop to avoid redundant allocations and recalculations.

## 2024-04-01 - BeautifulSoup default get_text() behavior
**Learning:** `BeautifulSoup.get_text()` silently extracts the raw JavaScript and CSS text contents embedded inside `<script>` and `<style>` tags by default (for both `lxml` and `html.parser`). This leads to massive unexpected payloads and wasted LLM tokens when parsing raw HTML newsletters, destroying performance and increasing API latency/costs.
**Action:** Always call `.decompose()` on `<script>` and `<style>` elements found by BeautifulSoup before running `.get_text()` if the goal is to extract clean, human-readable text for LLM prompts.
## 2024-05-15 - Fast HTML parsing in worker threads
**Learning:** Parsing and extracting text from large HTML newsletters using `BeautifulSoup` creates a severe performance bottleneck inside worker threads.
**Action:** Use regex-based replacement (e.g., `re.sub`) to strip HTML and `<script>`/`<style>` blocks when precise DOM manipulation is unnecessary to massively improve speed.

## 2024-05-15 - Rejected BeautifulSoup regression
**Learning:** Reverting to regex-based HTML parsing for script/style removal was rejected because HTML is notoriously malformed, and regex fails on edge cases like missing closing tags or tags in comments.
**Action:** Always maintain robust tools like BeautifulSoup when reliability is paramount, even if memory suggests a faster regex option. Do not sacrifice correctness for micro-optimizations in string parsing.

## 2024-05-15 - Fast header extraction in worker loop
**Learning:** Multiple generator expressions on the same dataset (like `next((h for h in headers if h['name'] == 'X'))`) cause redundant iterations and slow down execution, especially when operations like string lowercasing are involved inside the generator.
**Action:** For Python optimizations, replace multiple list comprehensions or generator expressions that iterate over the same dataset with a single `for` loop. This avoids redundant allocations and allows expensive operations to be evaluated only once per item while enabling early short-circuits.
