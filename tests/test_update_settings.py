import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules['google.auth'] = MagicMock()
sys.modules['google.auth.transport'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.cloud.texttospeech'] = MagicMock()

google_oauth2 = types.ModuleType('google.oauth2')
sys.modules['google.oauth2'] = google_oauth2
google_oauth2_credentials = types.ModuleType('google.oauth2.credentials')
sys.modules['google.oauth2.credentials'] = google_oauth2_credentials
google_oauth2_credentials.Credentials = MagicMock()
sys.modules['google.oauth2.id_token'] = MagicMock()

sys.modules['google_auth_oauthlib'] = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = MagicMock()

psycopg2 = types.ModuleType('psycopg2')
sys.modules['psycopg2'] = psycopg2
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()

import main

class TestUpdateSettingsRoute(unittest.TestCase):
    def setUp(self):
        self.app = main.app
        self.app.testing = True
        self.client = self.app.test_client()

    @patch('main.save_settings')
    @patch('main.get_user_info')
    def test_update_settings_success(self, mock_get_user_info, mock_save_settings):
        mock_get_user_info.return_value = {'email': 'test@example.com'}
        mock_save_settings.return_value = True

        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'sources': ['test.com'],
                'time_window_hours': 12,
                'personality': 'anchor'
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['status'], 'success')

            mock_save_settings.assert_called_once_with(
                {'sources': ['test.com'], 'time_window_hours': 12, 'personality': 'anchor'},
                'test@example.com'
            )

    def test_update_settings_unauthorized(self):
        with self.client as c:
            response = c.post('/api/settings', json={'sources': ['test.com']})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.get_json()['error'], 'Please log in to save your settings.')

    def test_update_settings_invalid_json(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json=[])
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], 'Invalid request.')

    def test_update_settings_invalid_type_sources(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'sources': 'not_a_list'
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], 'Invalid type for sources. Expected a list.')

    def test_update_settings_invalid_type_time_window(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'time_window_hours': 'not_a_number'
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], 'Invalid type for time_window_hours. Expected a number.')

    def test_update_settings_invalid_type_personality(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'personality': 123
            })

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()['error'], 'Invalid type for personality. Expected a string.')

    @patch('main.save_settings')
    @patch('main.get_user_info')
    def test_update_settings_sanitization(self, mock_get_user_info, mock_save_settings):
        mock_get_user_info.return_value = {'email': 'test@example.com'}
        mock_save_settings.return_value = True

        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'sources': ['test.com'],
                'personality': 'anchor',
                'malicious_key': 'drop_table'
            })

            self.assertEqual(response.status_code, 200)

            mock_save_settings.assert_called_once_with(
                {'sources': ['test.com'], 'personality': 'anchor'},
                'test@example.com'
            )

    @patch('main.save_settings')
    @patch('main.get_user_info')
    def test_update_settings_save_failure(self, mock_get_user_info, mock_save_settings):
        mock_get_user_info.return_value = {'email': 'test@example.com'}
        mock_save_settings.return_value = False

        with self.client as c:
            with c.session_transaction() as sess:
                sess['credentials'] = 'dummy_token'

            response = c.post('/api/settings', json={
                'sources': ['test.com']
            })

            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.get_json()['error'], 'Unable to save settings. Please try again or contact support if the issue persists.')

if __name__ == '__main__':
    unittest.main()
