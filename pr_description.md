🧪 [testing improvement description]

🎯 **What:**
Added unit tests for the `/api/check_auth` API route in `main.py` which was previously untested. The tests patch `main.get_user_info` to isolate the logic.

📊 **Coverage:**
- Tested the scenario where a user is logged in (mocked `get_user_info` returns a populated user dictionary), validating the JSON response contains `logged_in: True` and the `user` data.
- Tested the scenario where a user is logged out (mocked `get_user_info` returns `None`), validating the JSON response contains `logged_in: False` and lacks user data.

✨ **Result:**
Increased test coverage by ensuring the authentication check endpoint correctly maps the application's internal state to the corresponding JSON API response, catching potential regressions in API responses.
