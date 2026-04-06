import unittest
from unittest.mock import patch
import main

# Add the route globally before any request is made
@main.app.route('/force_500')
def force_500():
    raise Exception("Simulated server error")

class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = main.app
        self.app.testing = True
        self.client = self.app.test_client()

    def test_handle_500_error_debug_false(self):
        # Set DEBUG to False
        self.app.config['DEBUG'] = False
        self.app.config['PROPAGATE_EXCEPTIONS'] = False

        # Make a request that triggers a 500 error
        response = self.client.get('/force_500')

        # Verify response status code
        self.assertEqual(response.status_code, 500)

        # Verify JSON payload
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('error'), "Something went wrong. Please try again or log in again.")
        self.assertIsNone(data.get('details'))

    def test_handle_500_error_debug_true(self):
        # Set DEBUG to True
        self.app.config['DEBUG'] = True
        self.app.config['PROPAGATE_EXCEPTIONS'] = False

        # Make a request that triggers a 500 error
        response = self.client.get('/force_500')

        # Verify response status code
        self.assertEqual(response.status_code, 500)

        # Verify JSON payload
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data.get('error'), "Something went wrong. Please try again or log in again.")
        # 🛡️ Sentinel: Details should now be None even in DEBUG mode to prevent info leaks
        self.assertIsNone(data.get('details'))

if __name__ == '__main__':
    unittest.main()
