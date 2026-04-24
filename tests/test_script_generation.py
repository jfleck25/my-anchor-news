import unittest
from unittest.mock import patch, MagicMock
import sys
import os

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
sys.modules['posthog'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2.extras'] = MagicMock()
sys.modules['psycopg2.pool'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()
sys.modules['sentry_sdk'] = MagicMock()
sys.modules['sentry_sdk.integrations'] = MagicMock()
sys.modules['sentry_sdk.integrations.flask'] = MagicMock()

import main
import re

class TestGenerateScriptFromAnalysis(unittest.TestCase):
    def setUp(self):
        # We need to mock random.choice to have deterministic tests
        self.patcher = patch('random.choice')
        self.mock_choice = self.patcher.start()
        # Make random.choice just return the first element
        self.mock_choice.side_effect = lambda x: x[0] if isinstance(x, (list, tuple)) else x

    def tearDown(self):
        self.patcher.stop()

    def normalize_spaces(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def test_generate_script_empty(self):
        analysis_json = {}
        # Since empty, it should just be intro + outro
        script = main.generate_script_from_analysis(analysis_json, style="anchor")

        intro = main.PERSONAS["anchor"]["intro"][0]
        outro = main.PERSONAS["anchor"]["outro"]
        expected = f"{intro} {outro}"
        self.assertEqual(self.normalize_spaces(script), self.normalize_spaces(expected))

    def test_generate_script_with_stories(self):
        analysis_json = {
            "story_groups": [
                {
                    "group_headline": "Tech Giant Releases New Gadget",
                    "group_summary": "A major technology company has announced their latest device",
                    "stories": [
                        {
                            "source": "TechCrunch.com",
                            "angle": "reports that the device has amazing battery life"
                        },
                        {
                            "source": "The Verge",
                            "angle": "notes the high price point"
                        }
                    ]
                },
                {
                    "group_headline": "Local Sports Team Wins Championship",
                    "group_summary": "The city is celebrating after a dramatic victory",
                    "stories": [
                        {
                            "source": "ESPN <a href='...'>",
                            "angle": "highlights the star player's performance"
                        }
                    ]
                }
            ],
            "remaining_stories": [
                {
                    "headline": "Weather to get colder this weekend"
                },
                {
                    "headline": "New park opening downtown"
                }
            ]
        }

        script = main.generate_script_from_analysis(analysis_json, style="anchor")

        # Check elements are present
        self.assertIn("Tech Giant Releases New Gadget", script)
        self.assertIn("reports that the device has amazing battery life", script)
        self.assertIn("The TechCrunch", script) # The source cleaning logic removes .com
        self.assertIn("The The Verge", script)
        self.assertIn("Local Sports Team Wins Championship", script)
        # Note: both groups should be present now
        self.assertIn("The ESPN", script)
        self.assertIn("Weather to get colder this weekend", script)
        self.assertIn("Briefly:", script)

        # Test transition
        transition = main.PERSONAS["anchor"]["transition"][0]
        self.assertIn(transition, script)

    def test_perspectives_with_multiple_stories(self):
        analysis_json = {
            "story_groups": [
                {
                    "group_headline": "Group 1",
                    "group_summary": "Summary 1",
                    "stories": [
                        {"source": "Source 1", "angle": "Angle 1"},
                        {"source": "Source 2", "angle": "Angle 2"}
                    ]
                }
            ]
        }
        script = main.generate_script_from_analysis(analysis_json, style="anchor")
        self.assertIn("Differing perspectives:", script)
        self.assertIn("The Source 1 Angle 1.", script)
        self.assertIn("The Source 2 Angle 2.", script)

    def test_source_cleaning(self):
        analysis_json = {
            "story_groups": [
                {
                    "group_headline": "Group 1",
                    "group_summary": "Summary 1",
                    "stories": [
                        {"source": "Site.com <a href='link'>", "angle": "Angle 1"},
                        {"source": "NewsOrg", "angle": "Angle 2"}
                    ]
                }
            ]
        }
        script = main.generate_script_from_analysis(analysis_json, style="anchor")
        # Site.com <a href='link'> should become "Site"
        self.assertIn("The Site Angle 1.", script)

if __name__ == '__main__':
    unittest.main()
