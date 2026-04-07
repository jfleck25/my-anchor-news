import unittest
from unittest.mock import patch
import main

class TestFetchEmailsRoute(unittest.TestCase):
    def setUp(self):
        self.app = main.app
        self.app.testing = True
        self.client = self.app.test_client()

    def test_fetch_emails_no_credentials(self):
        # Request /api/fetch_emails without any credentials in the session
        with self.client as c:
            with c.session_transaction() as sess:
                if 'credentials' in sess:
                    del sess['credentials']

            response = c.get('/api/fetch_emails')

            # Verify response is 401
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertEqual(data.get('error'), 'Please log in to generate your briefing.')

    @patch('main.get_user_info')
    def test_fetch_emails_credentials_popped(self, mock_get_user_info):
        # The key issue is that get_user_email_for_rate_limit() is called by the @limiter decorator
        # before the fetch_emails() function is even executed. It calls get_user_info().
        # So we need mock_get_user_info to pop credentials on the FIRST call (during ratelimit checking)
        # OR we can bypass the limiter by mocking get_user_email_for_rate_limit, but it's simpler
        # to just understand what gets called.

        # Actually, if get_user_info() pops credentials during the limiter check,
        # then when the route actually executes, 'credentials' not in session
        # and it returns "Please log in to generate your briefing."
        # This explains why the test was returning "Please log in" instead of "Your session expired".

        # To hit the code path returning "Your session expired", credentials MUST be in session
        # when fetch_emails() begins, and then get_user_info() must pop it during the body of fetch_emails.

        call_count = [0]

        def side_effect_get_user_info():
            call_count[0] += 1
            if call_count[0] == 1:
                # First call happens in get_user_email_for_rate_limit()
                # Return dummy user info so credentials are NOT popped yet
                return {'email': 'test@example.com'}
            elif call_count[0] == 2:
                # Second call happens in fetch_emails()
                # Pop credentials to simulate expiration
                from flask import session
                session.pop('credentials', None)
                return None
            return None

        mock_get_user_info.side_effect = side_effect_get_user_info

        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = {'token': 'dummy'}

            response = c.get('/api/fetch_emails')

            # Verify response is 401
            self.assertEqual(response.status_code, 401)
            data = response.get_json()
            self.assertEqual(data.get('error'), 'Your session expired. Please log in again.')

if __name__ == '__main__':
    unittest.main()
