🚨 **Severity**: MEDIUM
💡 **Vulnerability**: The `/api/settings` POST endpoint lacked strict data type validation when extracting allowed keys from incoming JSON payloads. This exposed the application to type mismatches.
🎯 **Impact**: An attacker or errant client could inject unexpected types (like a string instead of a list of sources) causing a persistent Denial of Service state, as downstream functions (`fetch_emails`) would crash while trying to process the malformed configuration.
🔧 **Fix**: Enhanced the key-plucking mechanism in `update_settings` to explicitly validate the types of `sources`, `time_window_hours`, `personality`, `priority_sources`, and `keywords` using `isinstance()`, rejecting mismatches with a 400 Bad Request error.
✅ **Verification**: Run `python3 test_security.py` and `python3 -m pytest tests/` to confirm that valid JSON structures succeed while type mismatches are correctly rejected without overwriting the settings payload.
