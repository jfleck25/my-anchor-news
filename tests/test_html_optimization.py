import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestOptimizeNewsletterForLlm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need to test the actual function without having global mocked dependencies
        # interfere with bs4 being executed by other tests that ran previously.
        # Since bs4 was being mocked by `test_script_generation.py`, let's reload main
        # without that mock.

        # Keep original bs4 mock if it exists so we can restore it later
        cls.original_bs4_mock = sys.modules.get('bs4')

        if 'bs4' in sys.modules and hasattr(sys.modules['bs4'], 'MagicMock'):
            del sys.modules['bs4']

        import bs4
        sys.modules['bs4'] = bs4

        # Now import main which will use the real bs4
        import main
        # Force reload beautiful soup in main
        main.BeautifulSoup = bs4.BeautifulSoup
        cls.main = main

    @classmethod
    def tearDownClass(cls):
        # Restore the original state to not break other tests
        if cls.original_bs4_mock:
            sys.modules['bs4'] = cls.original_bs4_mock

    def test_basic_html_removal(self):
        html_content = "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>"
        result = self.main.optimize_newsletter_for_llm(html_content)
        self.assertEqual(result, "Hello World This is a test.")

    def test_script_style_removal(self):
        html_content = """
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>alert('Hello');</script>
            </head>
            <body>
                <p>Visible content</p>
                <script type="text/javascript">console.log('Hidden');</script>
            </body>
        </html>
        """
        result = self.main.optimize_newsletter_for_llm(html_content)
        self.assertEqual(result, "Visible content")

    def test_whitespace_normalization(self):
        html_content = "<html><body><p>Word1   Word2\n\nWord3\tWord4</p></body></html>"
        result = self.main.optimize_newsletter_for_llm(html_content)
        self.assertEqual(result, "Word1 Word2 Word3 Word4")

    def test_max_chars_truncation(self):
        html_content = "<p>1234567890</p>"
        result = self.main.optimize_newsletter_for_llm(html_content, max_chars=5)
        self.assertEqual(result, "12345")

        result_full = self.main.optimize_newsletter_for_llm(html_content, max_chars=20)
        self.assertEqual(result_full, "1234567890")

if __name__ == '__main__':
    unittest.main()
