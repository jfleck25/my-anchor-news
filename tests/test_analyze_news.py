import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock out heavy dependencies before importing main.py
sys.modules['dotenv'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.auth'] = MagicMock()
sys.modules['google_auth_oauthlib'] = MagicMock()
sys.modules['google_auth_oauthlib.flow'] = MagicMock()
sys.modules['google.oauth2'] = MagicMock()
sys.modules['google.oauth2.credentials'] = MagicMock()
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.api_core'] = MagicMock()
sys.modules['google.api_core.exceptions'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['google.auth.transport'] = MagicMock()
sys.modules['google.auth.transport.requests'] = MagicMock()
sys.modules['werkzeug'] = MagicMock()
sys.modules['werkzeug.middleware'] = MagicMock()
sys.modules['werkzeug.middleware.proxy_fix'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()
sys.modules['sentry_sdk.integrations'] = MagicMock()
sys.modules['sentry_sdk.integrations.flask'] = MagicMock()
sys.modules['posthog'] = MagicMock()

import main

# Define custom exception classes for testing
class DummyResourceExhausted(Exception): pass
class DummyInvalidArgument(Exception): pass

class TestAnalyzeNewsWithLLM(unittest.TestCase):
    def setUp(self):
        # We need to mock main.model and main.genai for these tests
        self.patcher_model = patch('main.model')
        self.mock_model = self.patcher_model.start()

        self.patcher_genai = patch('main.genai')
        self.mock_genai = self.patcher_genai.start()

        # Patch the exceptions in main.py to be our dummy exceptions
        self.patcher_ResourceExhausted = patch('main.ResourceExhausted', DummyResourceExhausted)
        self.mock_ResourceExhausted = self.patcher_ResourceExhausted.start()

        self.patcher_InvalidArgument = patch('main.InvalidArgument', DummyInvalidArgument)
        self.mock_InvalidArgument = self.patcher_InvalidArgument.start()

    def tearDown(self):
        self.patcher_model.stop()
        self.patcher_genai.stop()
        self.patcher_ResourceExhausted.stop()
        self.patcher_InvalidArgument.stop()

    def test_missing_model(self):
        main.model = None
        with self.assertRaises(Exception) as context:
            main.analyze_news_with_llm("some text")
        self.assertTrue("Gemini API model is not configured" in str(context.exception))

    def test_too_large_content(self):
        # Length > 800000
        large_text = "a" * 800001
        main.model = self.mock_model
        result = main.analyze_news_with_llm(large_text)
        self.assertEqual(result.get("error"), "Too much newsletter content to process at once. Please reduce your lookback window in settings.")

    def test_successful_analysis(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 1 # STOP

        expected_json = {
            "story_groups": [],
            "remaining_stories": []
        }
        mock_response.text = f"Here is the analysis: {json.dumps(expected_json)}"
        self.mock_model.generate_content.return_value = mock_response

        result = main.analyze_news_with_llm("Valid newsletter text")
        self.assertEqual(result, expected_json)
        self.mock_model.generate_content.assert_called_once()

    def test_finish_reason_max_tokens(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 2 # MAX_TOKENS
        self.mock_model.generate_content.return_value = mock_response

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "The briefing was too long to generate. Try reducing your sources or lookback period.")

    def test_finish_reason_safety(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 3 # SAFETY
        self.mock_model.generate_content.return_value = mock_response

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "The analysis was blocked due to safety filters.")

    def test_finish_reason_unexpected(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        # Using a mock for an unexpected reason that isn't 0, 1, 2, or 3
        mock_reason = MagicMock()
        mock_reason.value = 4
        mock_response.candidates[0].finish_reason = mock_reason
        self.mock_model.generate_content.return_value = mock_response

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "The AI encountered an unexpected interruption. Please try again.")

    def test_no_text_in_response(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 1
        # text is None or empty
        mock_response.text = None
        self.mock_model.generate_content.return_value = mock_response

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "AI analysis failed.")

    def test_no_json_in_text(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 1
        mock_response.text = "This text does not contain any JSON."
        self.mock_model.generate_content.return_value = mock_response

        with patch('main.json.loads') as mock_loads:
            # Should raise ValueError inside the try block, caught by general Exception block
            result = main.analyze_news_with_llm("Valid text")
            self.assertEqual(result.get("error"), "AI analysis failed.")

    def test_invalid_json(self):
        main.model = self.mock_model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].finish_reason = 1
        mock_response.text = "Here is bad json: { this is not valid }"
        self.mock_model.generate_content.return_value = mock_response

        with patch('main.json.loads', side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            result = main.analyze_news_with_llm("Valid text")
            self.assertEqual(result.get("error"), "The AI failed to format the analysis correctly. Please try again.")

    def test_resource_exhausted(self):
        main.model = self.mock_model
        self.mock_model.generate_content.side_effect = DummyResourceExhausted()
        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "AI service is currently overloaded. Please wait a minute before trying again.")

    def test_invalid_argument(self):
        main.model = self.mock_model
        self.mock_model.generate_content.side_effect = DummyInvalidArgument()
        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "The newsletter content is too large for the current AI model capacity.")

    def test_quota_exception(self):
        main.model = self.mock_model
        self.mock_model.generate_content.side_effect = Exception("Some quota error")

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "AI rate limit reached. Please try again in a few minutes.")

    def test_generic_exception(self):
        main.model = self.mock_model
        self.mock_model.generate_content.side_effect = Exception("Some random error")

        result = main.analyze_news_with_llm("Valid text")
        self.assertEqual(result.get("error"), "AI analysis failed.")

if __name__ == '__main__':
    unittest.main()
