import unittest
from unittest.mock import patch, MagicMock
import sys
import types

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

mock_genai = MagicMock()
sys.modules['google.generativeai'] = mock_genai

mock_psycopg2 = types.ModuleType('psycopg2')
mock_psycopg2_extras = types.ModuleType('psycopg2.extras')
mock_psycopg2_extras.RealDictCursor = MagicMock()
mock_psycopg2.extras = mock_psycopg2_extras
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = mock_psycopg2_extras
mock_psycopg2_pool = types.ModuleType('psycopg2.pool')
mock_psycopg2_pool.ThreadedConnectionPool = MagicMock()
sys.modules['psycopg2.pool'] = mock_psycopg2_pool

sys.modules.update({
    'dotenv': MagicMock(),
    'flask': MagicMock(),
    'flask_cors': MagicMock(),
    'flask_limiter': MagicMock(),
    'flask_limiter.util': MagicMock(),
    'werkzeug.middleware.proxy_fix': MagicMock(),
    'sentry_sdk': MagicMock(),
    'sentry_sdk.integrations.flask': MagicMock(),
    'bs4': MagicMock(),
    'posthog': MagicMock(),
})

import main
from main import get_credentials_from_session

class TestSecurityFix(unittest.TestCase):
    @patch('main.get_client_secrets_config')
    def test_get_credentials_from_session_adds_secret(self, mock_get_config):
        mock_get_config.return_value = {
            'web': {
                'client_id': 'test_id',
                'client_secret': 'super_secret'
            }
        }

        session_data = {
            'token': 'test_token',
            'refresh_token': 'test_refresh',
            'token_uri': 'test_uri',
            'client_id': 'test_id',
            'scopes': ['test_scope']
        }

        main.Credentials.reset_mock()
        creds = get_credentials_from_session(session_data)

        main.Credentials.assert_called_once()
        kwargs = main.Credentials.call_args[1]
        self.assertEqual(kwargs['client_secret'], 'super_secret')
        self.assertEqual(kwargs['token'], 'test_token')

    def test_global_payload_size_limit(self):
        """Test that requests exceeding the 2MB limit are rejected."""
        # Due to testing constraints where flask is completely mocked in test_security.py,
        # we can only verify that the MAX_CONTENT_LENGTH config is properly set on the mock's dictionary.
        # Since it is a MagicMock, assigning app.config['key'] = value sets it in a mocked dictionary way.

        # When main.py does app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024, it uses the __setitem__ method on the config mock
        # We can extract the call args.
        config_mock = main.app.config
        found = False
        for call in config_mock.__setitem__.call_args_list:
            if call[0][0] == 'MAX_CONTENT_LENGTH' and call[0][1] == 2 * 1024 * 1024:
                found = True
                break
        self.assertTrue(found, "MAX_CONTENT_LENGTH should be set to 2MB in app config")

if __name__ == '__main__':
    unittest.main()
