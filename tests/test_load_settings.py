import sys
import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
import importlib
import json

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

class TestLoadSettings(unittest.TestCase):
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

        # Disable the database so we only test file operations
        self.main_module.DATABASE_URL = None

    def tearDown(self):
        self.patcher.stop()

    @patch('os.path.exists')
    def test_load_settings_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        settings = self.main_module.load_settings()

        self.assertEqual(settings['sources'], ["wsj.com", "nytimes.com", "axios.com", "theguardian.com", "techcrunch.com"])
        self.assertEqual(settings['time_window_hours'], 24)
        self.assertEqual(settings['personality'], "anchor")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_settings_read_exception(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.side_effect = Exception("Permission denied")

        settings = self.main_module.load_settings()

        # Verify defaults are returned when there is an exception
        self.assertEqual(settings['sources'], ["wsj.com", "nytimes.com", "axios.com", "theguardian.com", "techcrunch.com"])
        self.assertEqual(settings['time_window_hours'], 24)
        self.assertEqual(settings['personality'], "anchor")

    @patch('os.path.getmtime')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"sources": ["test.com"], "time_window_hours": 12, "personality": "funny"}')
    def test_load_settings_success(self, mock_file, mock_exists, mock_getmtime):
        mock_exists.return_value = True
        mock_getmtime.return_value = 12345.0

        # Reset cache for testing
        self.main_module._file_settings_cache = None
        self.main_module._file_settings_mtime = 0

        settings = self.main_module.load_settings()

        # Verify specific settings are loaded correctly
        self.assertEqual(settings['sources'], ["test.com"])
        self.assertEqual(settings['time_window_hours'], 12)
        self.assertEqual(settings['personality'], "funny")

if __name__ == '__main__':
    unittest.main()
