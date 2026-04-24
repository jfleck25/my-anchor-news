🚨 Severity: CRITICAL
💡 Vulnerability: The `/api/share` endpoint failed to explicitly construct a sanitized payload using the allowed keys, choosing instead to store the non-existent `sanitized_data` variable which caused a `NameError` server failure and bypassed mass assignment protection.
🎯 Impact: Attackers could cause application crashes by submitting valid share requests (DoS) or exploit the missing validation pattern to bloat the database if raw payloads were improperly stored instead.
🔧 Fix: Correctly substituted the bugged `sanitized_data` parameter with the cleanly constructed `validated_data` mapping.
✅ Verification: Ran `pytest test_main.py tests/test_ui.py` and `unittest test_security.py` locally and verified correct behavior.
