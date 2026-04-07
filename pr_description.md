🎯 What:
Fixed an Insufficient Data Validation vulnerability in the `/api/share` endpoint (`main.py`). The endpoint previously accepted any arbitrary JSON payload and stored it directly in the database as long as one of the expected keys (`story_groups` or `remaining_stories`) was present. The fix introduces strict schema enforcement by explicitly constructing a `sanitized_data` dictionary containing only the allowed keys before database insertion.

⚠️ Risk:
By failing to strictly filter incoming JSON data before storage, the application was vulnerable to Mass Assignment and abusive storage attacks. An attacker could inject enormous, arbitrary, or malicious JSON blobs into the database alongside valid data. This could lead to resource exhaustion (database bloat), denial of service, or potentially exploit downstream parsers/consumers that read the `shared_briefings` data.

🛡️ Solution:
Updated `share_briefing()` in `main.py` to extract only the specific keys required for the feature (`story_groups` and `remaining_stories`) into a new dictionary. Any other injected keys in the request payload are safely discarded before being serialized to JSON and inserted into PostgreSQL. Added comprehensive unit tests in `test_share_briefing.py` and `test_shared_briefing.py` to verify the isolation and safety of the endpoint.
