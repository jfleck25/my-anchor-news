import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import types

# Ensure werkzeug acts as a package
werkzeug = types.ModuleType('werkzeug')
sys.modules['werkzeug'] = werkzeug
sys.modules['werkzeug.middleware'] = types.ModuleType('werkzeug.middleware')
sys.modules['werkzeug.middleware.proxy_fix'] = MagicMock()
sys.modules['werkzeug.utils'] = MagicMock()

# Sentry
sentry_sdk = types.ModuleType('sentry_sdk')
sys.modules['sentry_sdk'] = sentry_sdk
sys.modules['sentry_sdk.integrations'] = types.ModuleType('sentry_sdk.integrations')
sys.modules['sentry_sdk.integrations.flask'] = MagicMock()

# Other mocks
google = types.ModuleType('google')
sys.modules['google'] = google

google_auth = types.ModuleType('google.auth')
sys.modules['google.auth'] = google_auth
sys.modules['google.auth.transport'] = types.ModuleType('google.auth.transport')
mock_requests = types.ModuleType('google.auth.transport.requests')
mock_requests.Request = MagicMock()
mock_requests.AuthorizedSession = MagicMock()
sys.modules['google.auth.transport.requests'] = mock_requests

google_oauth2 = types.ModuleType('google.oauth2')
sys.modules['google.oauth2'] = google_oauth2
mock_credentials = MagicMock()
mock_credentials_mod = types.ModuleType('google.oauth2.credentials')
mock_credentials_mod.Credentials = mock_credentials
sys.modules['google.oauth2.credentials'] = mock_credentials_mod

sys.modules['google_auth_oauthlib'] = types.ModuleType('google_auth_oauthlib')
mock_flow_mod = types.ModuleType('google_auth_oauthlib.flow')
mock_flow_mod.Flow = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = mock_flow_mod

sys.modules['googleapiclient'] = types.ModuleType('googleapiclient')
mock_discovery_mod = types.ModuleType('googleapiclient.discovery')
mock_discovery_mod.build = MagicMock()
sys.modules['googleapiclient.discovery'] = mock_discovery_mod

sys.modules['google.cloud'] = types.ModuleType('google.cloud')
mock_texttospeech = MagicMock()
sys.modules['google.cloud.texttospeech'] = mock_texttospeech

sys.modules['google.api_core'] = types.ModuleType('google.api_core')
mock_client_options = MagicMock()
sys.modules['google.api_core.client_options'] = mock_client_options

sys.modules['google.api_core.exceptions'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()

# --- Extra mocks ---
sys.modules.setdefault('dotenv', MagicMock())
sys.modules.setdefault('flask', MagicMock())
sys.modules.setdefault('flask_cors', MagicMock())
sys.modules.setdefault('posthog', MagicMock())
sys.modules.setdefault('psycopg2', MagicMock())
sys.modules.setdefault('psycopg2.pool', MagicMock())
sys.modules.setdefault('psycopg2.extras', MagicMock())
sys.modules.setdefault('requests', MagicMock())
sys.modules.setdefault('bs4', MagicMock())

# specifically mock out the decorator to do nothing
flask_limiter = types.ModuleType('flask_limiter')
sys.modules['flask_limiter'] = flask_limiter
class MockLimiter:
    def __init__(self, *args, **kwargs):
        pass
    def limit(self, *args, **kwargs):
        return lambda f: f
flask_limiter.Limiter = MockLimiter
sys.modules['flask_limiter.util'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestGetDBConnection(unittest.TestCase):

    @patch('main.db_pool')
    def test_get_db_connection_with_db_pool(self, mock_db_pool):
        import main
        # Setup
        mock_conn = MagicMock()
        mock_db_pool.getconn.return_value = mock_conn

        # Execute
        result = main.get_db_connection()

        # Assert
        self.assertEqual(result, mock_conn)
        mock_db_pool.getconn.assert_called_once()

    @patch('main.db_pool', new=None)
    @patch('main.DATABASE_URL', new='mock_db_url')
    @patch('main.psycopg2.connect')
    def test_get_db_connection_no_pool_with_url(self, mock_connect):
        import main
        # Setup
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Execute
        result = main.get_db_connection()

        # Assert
        self.assertEqual(result, mock_conn)
        mock_connect.assert_called_once_with('mock_db_url')

    @patch('main.db_pool', new=None)
    @patch('main.DATABASE_URL', new=None)
    @patch('main.psycopg2.connect')
    def test_get_db_connection_no_pool_no_url(self, mock_connect):
        import main
        # Execute
        result = main.get_db_connection()

        # Assert
        self.assertIsNone(result)
        mock_connect.assert_not_called()

if __name__ == '__main__':
    unittest.main()
