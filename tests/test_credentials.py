import unittest
from unittest.mock import patch, MagicMock
import main

class TestGetCredentialsFromSession(unittest.TestCase):

    @patch('main.get_client_secrets_config')
    @patch('main.Credentials')
    def test_get_credentials_from_session_exception(self, mock_credentials, mock_get_client_secrets_config):
        creds_data = {'token': 'test_token', 'refresh_token': 'test_refresh_token'}

        # Make get_client_secrets_config raise an exception
        mock_get_client_secrets_config.side_effect = Exception("Simulated config error")

        # Expected fallback credentials object
        mock_fallback_creds = MagicMock()
        mock_credentials.return_value = mock_fallback_creds

        result = main.get_credentials_from_session(creds_data)

        # Verify the exception branch was taken and Credentials was called with creds_data
        mock_credentials.assert_called_once_with(**creds_data)
        self.assertEqual(result, mock_fallback_creds)

if __name__ == '__main__':
    unittest.main()
