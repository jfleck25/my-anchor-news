import unittest
import sys
import os
from unittest.mock import MagicMock

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock heavy dependencies
sys.modules['dotenv'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.api_core'] = MagicMock()
sys.modules['google.auth'] = MagicMock()
sys.modules['google.auth.transport'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['google_auth_oauthlib'] = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = MagicMock()
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.credentials'] = MagicMock()
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()
sys.modules['sentry_sdk.integrations'] = MagicMock()
sys.modules['sentry_sdk.integrations.flask'] = MagicMock()
sys.modules['posthog'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['authlib'] = MagicMock()
sys.modules['authlib.integrations'] = MagicMock()
sys.modules['authlib.integrations.flask_client'] = MagicMock()
sys.modules['werkzeug'] = MagicMock()
sys.modules['werkzeug.middleware'] = MagicMock()
sys.modules['werkzeug.middleware.proxy_fix'] = MagicMock()
sys.modules['google.cloud.texttospeech'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()


from main import sanitize_for_llm

class TestSanitizeForLLM(unittest.TestCase):
    def test_sanitize_normal_text(self):
        self.assertEqual(sanitize_for_llm("Hello World"), "Hello World")

    def test_sanitize_escape_quotes(self):
        self.assertEqual(sanitize_for_llm('Hello "World"'), 'Hello \\"World\\"')

    def test_sanitize_escape_backslashes(self):
        self.assertEqual(sanitize_for_llm(r'Path C:\Temp'), r'Path C:\\Temp')

    def test_sanitize_control_characters(self):
        self.assertEqual(sanitize_for_llm("Hello\x00World"), "HelloWorld")
        self.assertEqual(sanitize_for_llm("Tab\tIs\tKept"), "Tab\tIs\tKept")
        self.assertEqual(sanitize_for_llm("Newline\nIs\nKept"), "Newline\nIs\nKept")
        self.assertEqual(sanitize_for_llm("Carriage\rReturn\rKept"), "Carriage\rReturn\rKept")
        self.assertEqual(sanitize_for_llm("Bell\x07Rings"), "BellRings")
        self.assertEqual(sanitize_for_llm("Vertical\x0BTab"), "VerticalTab")
        self.assertEqual(sanitize_for_llm("Delete\x7FChar"), "DeleteChar")

    def test_sanitize_combined(self):
        self.assertEqual(sanitize_for_llm('A "quote" \\ \x00 null'), 'A \\"quote\\" \\\\  null')

if __name__ == '__main__':
    unittest.main()
