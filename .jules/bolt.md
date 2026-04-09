## 2024-04-07 - Avoid Google API Discovery Document for Simple Calls
**Learning:** Initializing a Google API service via `googleapiclient.discovery.build()` introduces substantial network latency because it fetches and parses the API's discovery document before making the actual request. This is particularly problematic for simple REST operations like fetching user info during authentication checks.
**Action:** Replace `build('oauth2', 'v2')` with direct REST API requests using `google.auth.transport.requests.AuthorizedSession(credentials)` for simple operations. This avoids the discovery overhead while preserving automatic OAuth2 token refreshment.

## $(date +%Y-%m-%d) - Optimize inner loops with lowercase string comparisons
**Learning:** Found multiple O(n) calls to `.lower()` string methods when comparing arrays of keywords against a main body string and subject string in inner worker threads (`_fetch_one_message`). This issue drastically affects performance, specifically when analyzing many text emails, as Python forces a recomputation of `.lower()` for every element in the keyword list during list comprehensions inside loops.
**Action:** When scanning lists of target keywords in text bodies, pre-compute `.lower()` arrays and strings outside the main scanning loop to avoid redundant allocations and recalculations.

## 2024-05-19 - Use string builder pattern for building large texts in a loop
**Learning:** Using `+=` for string concatenation in a loop over many strings creates a new string object and copies the memory every iteration, resulting in O(N^2) time complexity. Using an array and calling `.append()` each iteration, then `"".join(array)` at the end reduces this to O(N) operations and gives significant speedups.
**Action:** Whenever generating strings in a loop by accumulating parts, always use the `.append()` and `"".join()` pattern to prevent O(N^2) memory and execution overhead.

## $(date +%Y-%m-%d) - Prevent repeated UTF-8 encoding in loops
**Learning:** Found an O(N^2) performance bottleneck in the text-to-speech chunk generation logic. A loop was repeatedly checking `len(current_chunk.encode('utf-8'))` while `current_chunk` was growing, causing Python to repeatedly allocate and encode the entire accumulating string on every iteration.
**Action:** When accumulating strings with a byte limit, calculate the byte length of only the new addition (`len(sentence.encode('utf-8'))`) and maintain a running sum (`current_chunk_byte_len`). Combine this with the string builder pattern (`"".join(array)`) to completely eliminate the O(N^2) overhead.
