
## $(date +%Y-%m-%d) - Optimize inner loops with lowercase string comparisons
**Learning:** Found multiple O(n) calls to `.lower()` string methods when comparing arrays of keywords against a main body string and subject string in inner worker threads (`_fetch_one_message`). This issue drastically affects performance, specifically when analyzing many text emails, as Python forces a recomputation of `.lower()` for every element in the keyword list during list comprehensions inside loops.
**Action:** When scanning lists of target keywords in text bodies, pre-compute `.lower()` arrays and strings outside the main scanning loop to avoid redundant allocations and recalculations.
## 2024-05-19 - Use string builder pattern for building large texts in a loop
**Learning:** Using `+=` for string concatenation in a loop over many strings creates a new string object and copies the memory every iteration, resulting in O(N^2) time complexity. Using an array and calling `.append()` each iteration, then `"".join(array)` at the end reduces this to O(N) operations and gives significant speedups.
**Action:** Whenever generating strings in a loop by accumulating parts, always use the `.append()` and `"".join()` pattern to prevent O(N^2) memory and execution overhead.
