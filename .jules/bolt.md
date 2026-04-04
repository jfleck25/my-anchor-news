
## $(date +%Y-%m-%d) - Optimize inner loops with lowercase string comparisons
**Learning:** Found multiple O(n) calls to `.lower()` string methods when comparing arrays of keywords against a main body string and subject string in inner worker threads (`_fetch_one_message`). This issue drastically affects performance, specifically when analyzing many text emails, as Python forces a recomputation of `.lower()` for every element in the keyword list during list comprehensions inside loops.
**Action:** When scanning lists of target keywords in text bodies, pre-compute `.lower()` arrays and strings outside the main scanning loop to avoid redundant allocations and recalculations.

## 2024-11-06 - Avoid BeautifulSoup in worker threads for simple HTML stripping
**Learning:** Parsing and extracting text from large HTML newsletters using `BeautifulSoup` creates a severe performance bottleneck inside worker threads. The DOM parsing is too slow and heavy when only simple text extraction is needed.
**Action:** Use regex-based replacement (e.g., `re.sub`) to strip HTML and `<script>`/`<style>` blocks when precise DOM manipulation is unnecessary to massively improve speed.
