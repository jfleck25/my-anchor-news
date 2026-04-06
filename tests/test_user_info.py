import unittest
from unittest.mock import patch, MagicMock
from flask import session
import main

class TestGetUserInfo(unittest.TestCase):
    def setUp(self):
        self.app = main.app
        self.app.testing = True

    def test_no_credentials(self):
        with self.app.test_request_context():
            session.clear()
            result = main.get_user_info()
            self.assertIsNone(result)

    def test_with_user_info_in_session(self):
        with self.app.test_request_context():
            session['credentials'] = 'test_creds'
            session['user_info'] = {'email': 'test@example.com'}
            result = main.get_user_info()
            self.assertEqual(result, {'email': 'test@example.com'})

    @patch('main.get_credentials_from_session')
    @patch('main.build')
    def test_fetch_user_info_success(self, mock_build, mock_get_credentials):
        mock_credentials = MagicMock()
        mock_get_credentials.return_value = mock_credentials

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_user_info = {'email': 'fetched@example.com'}
        mock_service.userinfo().get().execute.return_value = mock_user_info

        with self.app.test_request_context():
            session['credentials'] = 'test_creds'
            result = main.get_user_info()

            self.assertEqual(result, mock_user_info)
            self.assertEqual(session['user_info'], mock_user_info)

    @patch('main.get_credentials_from_session')
    @patch('main.build')
    def test_fetch_user_info_exception(self, mock_build, mock_get_credentials):
        mock_get_credentials.side_effect = Exception("Failed to get credentials")

        with self.app.test_request_context():
            session['credentials'] = 'test_creds'
            session['user_email'] = 'old@example.com'

            result = main.get_user_info()
            self.assertIsNone(result)
            self.assertNotIn('credentials', session)
            self.assertNotIn('user_email', session)
            self.assertNotIn('user_info', session)

    @patch('main.get_credentials_from_session')
    @patch('main.build')
    def test_fetch_user_info_exception_pops(self, mock_build, mock_get_credentials):
        mock_credentials = MagicMock()
        mock_get_credentials.return_value = mock_credentials

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_service.userinfo().get().execute.side_effect = Exception("API error")

        with self.app.test_request_context():
            session['credentials'] = 'test_creds'
            session['user_email'] = 'old@example.com'

            result = main.get_user_info()
            self.assertIsNone(result)
            self.assertNotIn('credentials', session)
            self.assertNotIn('user_email', session)
            self.assertNotIn('user_info', session)

if __name__ == '__main__':
    unittest.main()
