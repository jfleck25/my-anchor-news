import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import importlib

MOCKED_MODULES = [
    'flask_cors', 'google_auth_oauthlib', 'google_auth_oauthlib.flow',
    'google', 'google.oauth2', 'google.oauth2.credentials', 'googleapiclient',
    'googleapiclient.discovery', 'google.generativeai', 'google.cloud',
    'google.api_core', 'bs4', 'google.auth', 'google.auth.transport',
    'google.auth.transport.requests', 'psycopg2', 'psycopg2.extras',
    'sentry_sdk', 'sentry_sdk.integrations', 'sentry_sdk.integrations.flask'
]

class TestShareBriefing(unittest.TestCase):
    def setUp(self):
        self.mocks = {mod: MagicMock() for mod in MOCKED_MODULES}

        # We need to mock Limiter properly so its decorators don't fail during import
        mock_limiter = MagicMock()
        def limit_decorator(*args, **kwargs):
            def decorator(f):
                return f
            return decorator
        mock_limiter.limit.return_value = limit_decorator
        mock_flask_limiter = MagicMock()
        mock_flask_limiter.Limiter.return_value = mock_limiter
        self.mocks['flask_limiter'] = mock_flask_limiter
        self.mocks['flask_limiter.util'] = MagicMock()

        self.patcher = patch.dict('sys.modules', self.mocks)
        self.patcher.start()

        import main
        importlib.reload(main)
        self.main_module = main

        self.app = self.main_module.app
        self.app.config['TESTING'] = True
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.app.secret_key = 'test_secret'
        self.client = self.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def test_share_briefing_not_authenticated(self):
        response = self.client.post('/api/share', json={"story_groups": []})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {'error': 'User not authenticated'})

    def test_share_briefing_invalid_type(self):
        with self.client.session_transaction() as sess:
            sess['credentials'] = {'token': 'fake_token'}

        response = self.client.post('/api/share', json=["not", "a", "dict"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Invalid data format. Expected a JSON object.'})

        response = self.client.post('/api/share', json="string data")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Invalid data format. Expected a JSON object.'})

    def test_share_briefing_missing_keys(self):
        with self.client.session_transaction() as sess:
            sess['credentials'] = {'token': 'fake_token'}

        response = self.client.post('/api/share', json={"wrong_key": "value"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Invalid data content. Required fields missing.'})

    @patch('main.get_db_connection')
    @patch('main.release_db_connection')
    def test_share_briefing_success(self, mock_release, mock_get):
        self.main_module.DATABASE_URL = "postgres://dummy"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get.return_value = mock_conn

        with self.client.session_transaction() as sess:
            sess['credentials'] = {'token': 'fake_token'}

        with patch('uuid.uuid4', return_value="fake_uuid"):
            response = self.client.post('/api/share', json={"story_groups": [{"group_headline": "Test"}]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'share_id': 'fake_uuid'})

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_release.assert_called_once_with(mock_conn)

if __name__ == '__main__':
    unittest.main()
