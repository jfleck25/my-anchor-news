import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing main
sys.modules['flask'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.api_core'] = MagicMock()
sys.modules['google.api_core.exceptions'] = MagicMock()
sys.modules['google.api_core.client_options'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.credentials'] = MagicMock()
sys.modules['google.auth'] = MagicMock()
sys.modules['google.auth.transport'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google_auth_oauthlib'] = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = MagicMock()
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()
sys.modules['sentry_sdk.integrations'] = MagicMock()
sys.modules['sentry_sdk.integrations.flask'] = MagicMock()
sys.modules['posthog'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()
sys.modules['werkzeug'] = MagicMock()
sys.modules['werkzeug.middleware'] = MagicMock()
sys.modules['werkzeug.middleware.proxy_fix'] = MagicMock()
sys.modules['bs4'] = MagicMock()

import main
import hashlib

class TestAnonymizeUser(unittest.TestCase):
    def test_anonymize_user_none(self):
        """Test anonymize_user with None email returns 'anonymous'"""
        self.assertEqual(main.anonymize_user(None), 'anonymous')

    def test_anonymize_user_empty_string(self):
        """Test anonymize_user with empty string returns 'anonymous'"""
        self.assertEqual(main.anonymize_user(''), 'anonymous')

    def test_anonymize_user_valid_email(self):
        """Test anonymize_user with a valid email"""
        email = "test@example.com"
        # Since flask is mocked, app.secret_key is a mock.
        # We need to explicitly set or mock app.secret_key for testing
        main.app = MagicMock()
        main.app.secret_key = "test_secret_key"

        salt = str(main.app.secret_key or "default_salt")
        expected_hash = hashlib.sha256((email + salt).encode()).hexdigest()

        self.assertEqual(main.anonymize_user(email), expected_hash)

    def test_anonymize_user_consistency(self):
        """Test that same email returns same hash"""
        email = "test@example.com"
        main.app = MagicMock()
        main.app.secret_key = "test_secret_key"

        result1 = main.anonymize_user(email)
        result2 = main.anonymize_user(email)

        self.assertEqual(result1, result2)


    def test_anonymize_user_missing_secret_key(self):
        """Test anonymize_user raises RuntimeError when secret_key is missing"""
        email = "test@example.com"
        main.app = MagicMock()
        main.app.secret_key = None

        with self.assertRaises(RuntimeError) as context:
            main.anonymize_user(email)

        self.assertTrue("app.secret_key is required" in str(context.exception))

if __name__ == '__main__':

    unittest.main()
