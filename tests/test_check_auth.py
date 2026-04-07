import unittest
from unittest.mock import patch
import main

class TestCheckAuth(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = main.app
        self.app.testing = True
        self.client = self.app.test_client()

    @patch('main.get_user_info')
    def test_check_auth_logged_in(self, mock_get_user_info):
        # Set up the mock to return a fake user info dict
        mock_user_info = {'email': 'test@example.com', 'name': 'Test User'}
        mock_get_user_info.return_value = mock_user_info

        # Make request to /api/check_auth
        response = self.client.get('/api/check_auth')

        # Verify response status code
        self.assertEqual(response.status_code, 200)

        # Verify JSON payload
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertTrue(data.get('logged_in'))
        self.assertEqual(data.get('user'), mock_user_info)

    @patch('main.get_user_info')
    def test_check_auth_logged_out(self, mock_get_user_info):
        # Set up the mock to return None, simulating logged out state
        mock_get_user_info.return_value = None

        # Make request to /api/check_auth
        response = self.client.get('/api/check_auth')

        # Verify response status code
        self.assertEqual(response.status_code, 200)

        # Verify JSON payload
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertFalse(data.get('logged_in'))
        self.assertNotIn('user', data)

if __name__ == '__main__':
    unittest.main()
