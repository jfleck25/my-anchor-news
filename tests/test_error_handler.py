import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Mimic the exact working setup from test_security.py
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

# Store the global mocks to ensure we don't clobber things unexpectedly
# Setup flask specific mock to capture the error handler
mock_flask = MagicMock()
mock_jsonify = MagicMock(side_effect=lambda x: x)
mock_flask.jsonify = mock_jsonify

# Bypassing the errorhandler decorator so we can retrieve the wrapped function
error_handlers = {}
def mock_errorhandler(code):
    def decorator(f):
        error_handlers[code] = f
        return f
    return decorator

mock_app = MagicMock()
mock_app.errorhandler = mock_errorhandler
mock_flask.Flask.return_value = mock_app

sys.modules.update({
    'dotenv': MagicMock(),
    'flask': mock_flask,
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

class TestErrorHandler(unittest.TestCase):
    @patch('builtins.print')
    @patch('traceback.format_exc')
    def test_handle_500_error(self, mock_format_exc, mock_print):
        mock_format_exc.return_value = "Mock Traceback: ValueError at line 42"
        test_exception = ValueError("Something failed completely")

        # We need to manually set the jsonify mock back on main because main imported it
        main.jsonify = mock_jsonify

        # Grab the error handler directly because Flask app is a MagicMock
        # main.py does: @app.errorhandler(500) def handle_500_error(e): ...
        # which our mock interceptor stores in `error_handlers[500]`
        handle_500_error = error_handlers.get(500)

        # If it wasn't intercepted because `main` was already loaded in memory
        # (e.g. running in pytest suite), fallback to direct function access
        if not handle_500_error:
            handle_500_error = getattr(main, 'handle_500_error', None)

        self.assertIsNotNone(handle_500_error, "Failed to locate handle_500_error")

        response_tuple = handle_500_error(test_exception)

        self.assertEqual(len(response_tuple), 2)
        response_data, status_code = response_tuple

        mock_print.assert_any_call("Unhandled 500 error: Something failed completely")
        mock_print.assert_any_call("Mock Traceback: ValueError at line 42")

        self.assertEqual(status_code, 500)
        self.assertEqual(response_data, {
            'error': "Something went wrong. Please try again or log in again.",
            'details': None
        })

if __name__ == '__main__':
    unittest.main()
