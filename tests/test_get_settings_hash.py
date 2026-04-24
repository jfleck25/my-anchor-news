import sys
import json
import hashlib
import unittest
from unittest.mock import MagicMock, patch
import importlib

MOCKED_MODULES = [
    'flask', 'flask_cors', 'google_auth_oauthlib', 'google_auth_oauthlib.flow',
    'google', 'google.oauth2', 'google.oauth2.credentials', 'googleapiclient',
    'googleapiclient.discovery', 'google.generativeai', 'google.cloud',
    'google.api_core', 'bs4', 'google.auth', 'google.auth.transport',
    'google.auth.transport.requests', 'werkzeug', 'werkzeug.middleware',
    'werkzeug.middleware.proxy_fix', 'psycopg2', 'psycopg2.extras',
    'flask_limiter', 'flask_limiter.util', 'sentry_sdk',
    'sentry_sdk.integrations', 'sentry_sdk.integrations.flask', 'dotenv'
]

class TestGetSettingsHash(unittest.TestCase):
    def setUp(self):
        self.mocks = {mod: MagicMock() for mod in MOCKED_MODULES}

        self.mock_flask = self.mocks['flask']
        self.mock_app = MagicMock()
        self.mock_flask.Flask.return_value = self.mock_app

        def mock_route(*args, **kwargs):
            def decorator(f):
                return f
            return decorator
        self.mock_app.route = mock_route

        self.patcher = patch.dict('sys.modules', self.mocks)
        self.patcher.start()

        import main
        importlib.reload(main)
        self.main_module = main

    def tearDown(self):
        self.patcher.stop()

    def test_get_settings_hash_consistency(self):
        dict1 = {"b": 2, "a": 1, "c": 3}
        dict2 = {"a": 1, "c": 3, "b": 2}

        hash1 = self.main_module.get_settings_hash(dict1)
        hash2 = self.main_module.get_settings_hash(dict2)

        self.assertEqual(hash1, hash2, "Hashes should be identical for dictionaries with same content but different key order.")

    def test_get_settings_hash_correctness(self):
        settings = {"theme": "dark", "notifications": True}

        # Expected manual hash
        expected_json = json.dumps(settings, sort_keys=True)
        expected_hash = hashlib.sha256(expected_json.encode()).hexdigest()

        result_hash = self.main_module.get_settings_hash(settings)

        self.assertEqual(result_hash, expected_hash, "Hash output should match the SHA256 of the sorted JSON string.")

    def test_get_settings_hash_type(self):
        settings = {"a": 1}
        result_hash = self.main_module.get_settings_hash(settings)

        self.assertIsInstance(result_hash, str, "The returned hash should be a string.")

if __name__ == '__main__':
    unittest.main()
