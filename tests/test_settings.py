import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock heavy dependencies before importing main to prevent side effects and errors
sys.modules['google.auth'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['google.oauth2.id_token'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.cloud.texttospeech'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()

import main

def test_save_settings_db_exception(monkeypatch):
    """Test that save_settings handles database connection errors gracefully and returns False."""
    # Ensure DATABASE_URL is set so the DB path is taken
    monkeypatch.setattr(main, 'DATABASE_URL', 'postgres://mock')

    # Mock get_db_connection to raise an exception
    mock_get_db = MagicMock(side_effect=Exception("Database Connection Failed"))
    monkeypatch.setattr(main, 'get_db_connection', mock_get_db)

    # Call the function
    result = main.save_settings({"theme": "dark"}, user_email="test@example.com")

    # Assertions
    assert result is False
    mock_get_db.assert_called_once()
