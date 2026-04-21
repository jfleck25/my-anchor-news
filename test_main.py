import pytest
import sys
from unittest.mock import MagicMock, patch, ANY

# Mock out heavy external dependencies before importing main

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

# Now import main which will use the real Flask
import main

@pytest.fixture
def client():
    """A test client for the app."""
    # Configure the app for testing
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def test_app_created():
    """Test that the Flask app was created successfully."""
    assert main.app is not None

def test_index_route(client):
    """Test that the index route returns a valid response."""
    response = client.get('/')
    # The main.py index route handles session tokens or returns a template/redirect
    # Depending on exact implementation it might be a redirect (302) or 200.
    # At minimum, asserting we get a response object without blowing up.
    assert response.status_code in [200, 302, 401]


def test_index_environment_variables_set(client, monkeypatch):
    """Test that the index route correctly parses environment variables when set."""
    test_sentry_dsn = 'https://test@sentry.io/123'
    test_posthog_key = 'phc_testkey123'

    monkeypatch.setenv('SENTRY_DSN_FRONTEND', test_sentry_dsn)
    monkeypatch.setenv('POSTHOG_API_KEY', test_posthog_key)

    with patch('main.render_template') as mock_render:
        mock_render.return_value = "Mocked Response"

        response = client.get('/')

        assert response.status_code == 200
        mock_render.assert_called_once_with(
            'index.html',
            sentry_dsn_frontend=test_sentry_dsn,
            posthog_api_key=test_posthog_key,
            react_production=ANY
        )

def test_index_environment_variables_missing(client, monkeypatch):
    """Test that the index route correctly defaults to empty strings when env vars are missing."""
    monkeypatch.delenv('SENTRY_DSN_FRONTEND', raising=False)
    monkeypatch.delenv('POSTHOG_API_KEY', raising=False)

    with patch('main.render_template') as mock_render:
        mock_render.return_value = "Mocked Response"

        response = client.get('/')

        assert response.status_code == 200
        mock_render.assert_called_once_with(
            'index.html',
            sentry_dsn_frontend='',
            posthog_api_key='',
            react_production=ANY
        )

import unittest
from unittest.mock import MagicMock
import sys
import threading

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.texttospeech'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.oauth2.credentials'] = MagicMock()

import main

class TestOptimization(unittest.TestCase):
    def test_worker_thread_locals(self):
        self.assertTrue(hasattr(main, '_worker_thread_locals'))
        self.assertIsInstance(main._worker_thread_locals, type(threading.local()))

if __name__ == '__main__':
    unittest.main()
