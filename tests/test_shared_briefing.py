import sys
import unittest
from unittest.mock import MagicMock, patch
import importlib

MOCKED_MODULES = [
    'flask', 'flask_cors', 'google_auth_oauthlib', 'google_auth_oauthlib.flow',
    'google', 'google.oauth2', 'google.oauth2.credentials', 'googleapiclient',
    'googleapiclient.discovery', 'google.generativeai', 'google.cloud',
    'google.api_core', 'google.api_core.exceptions', 'bs4', 'google.auth', 'google.auth.transport',
    'google.auth.transport.requests', 'werkzeug', 'werkzeug.middleware',
    'werkzeug.middleware.proxy_fix', 'psycopg2', 'psycopg2.extras',
    'psycopg2.pool',
    'flask_limiter', 'flask_limiter.util', 'sentry_sdk',
    'sentry_sdk.integrations', 'sentry_sdk.integrations.flask', 'dotenv', 'posthog'
]

class TestSharedBriefing(unittest.TestCase):
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

        # We need to mock Limiter properly so its decorators don't fail during import
        mock_limiter = MagicMock()
        def limit_decorator(*args, **kwargs):
            def decorator(f):
                return f
            return decorator
        mock_limiter.limit = limit_decorator

        mock_flask_limiter = MagicMock()
        mock_flask_limiter.Limiter.return_value = mock_limiter
        self.mocks['flask_limiter'] = mock_flask_limiter

        self.patcher = patch.dict('sys.modules', self.mocks)
        self.patcher.start()

        import main
        importlib.reload(main)
        self.main_module = main

        self.main_module.DATABASE_URL = "postgres://dummy"
        self.mock_flask.jsonify.reset_mock()
        self.mock_flask.jsonify.side_effect = lambda x: x

    def tearDown(self):
        self.patcher.stop()

    def test_get_shared_briefing_exception(self):
        with patch.object(self.main_module.psycopg2, 'connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")

            result = self.main_module.get_shared_briefing("test_id")

            self.assertEqual(result, ({'error': 'Unable to load shared briefing. Please try again.'}, 500))
            self.mock_flask.jsonify.assert_called_once_with({'error': 'Unable to load shared briefing. Please try again.'})

    def test_share_briefing_no_data(self):
        self.main_module.session = {'credentials': 'dummy_creds'}
        self.main_module.request = MagicMock()
        self.main_module.request.get_json.return_value = None

        result = self.main_module.share_briefing()

        self.assertEqual(result, ({'error': 'Invalid data format. Expected a JSON object.'}, 400))
        self.mock_flask.jsonify.assert_called_with({'error': 'Invalid data format. Expected a JSON object.'})

if __name__ == '__main__':
    unittest.main()
