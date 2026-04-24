import sys
import unittest
from unittest.mock import MagicMock, patch
import io

# When run via pytest, main module uses real flask. We need to handle both environments.
# To avoid RuntimeError: Working outside of application context.
import main

class TestErrorHandler(unittest.TestCase):
    def test_handle_500_error(self):
        exception = Exception("Test 500 API Error")

        with main.app.app_context():
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                # We call the main module's actual function instead of a route
                response, status_code = main.handle_500_error(exception)

                self.assertEqual(status_code, 500)

                # We need to handle both FakeFlask (which returns dict directly) and real Flask (which returns a Response object)
                if isinstance(response, dict):
                    data = response
                else:
                    data = response.get_json()

                self.assertEqual(data['error'], "Something went wrong. Please try again or log in again.")
                self.assertIsNone(data['details'])

                output = mock_stdout.getvalue()
                self.assertIn("Unhandled 500 error: Test 500 API Error", output)
                self.assertIn("Test 500 API Error", output)

if __name__ == '__main__':
    unittest.main()
