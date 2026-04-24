import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
import main

class TestGetUserEmailForRateLimit(unittest.TestCase):
    def setUp(self):
        self.app = main.app
        self.app.testing = True

    def test_email_in_session(self):
        with self.app.test_request_context():
            session['user_email'] = 'session@example.com'
            result = main.get_user_email_for_rate_limit()
            self.assertEqual(result, 'session@example.com')

    @patch('main.get_user_info')
    def test_email_from_user_info(self, mock_get_user_info):
        mock_get_user_info.return_value = {'email': 'userinfo@example.com'}
        with self.app.test_request_context():
            # Ensure session is empty initially
            session.clear()
            result = main.get_user_email_for_rate_limit()
            self.assertEqual(result, 'userinfo@example.com')
            self.assertEqual(session.get('user_email'), 'userinfo@example.com')

    @patch('main.get_user_info')
    @patch('main.get_remote_address')
    def test_fallback_user_info_none(self, mock_get_remote_address, mock_get_user_info):
        mock_get_user_info.return_value = None
        mock_get_remote_address.return_value = '127.0.0.1'
        with self.app.test_request_context():
            session.clear()
            result = main.get_user_email_for_rate_limit()
            self.assertEqual(result, '127.0.0.1')
            self.assertNotIn('user_email', session)
            mock_get_remote_address.assert_called_once()

    @patch('main.get_user_info')
    @patch('main.get_remote_address')
    def test_fallback_user_info_no_email(self, mock_get_remote_address, mock_get_user_info):
        mock_get_user_info.return_value = {'name': 'No Email User'}
        mock_get_remote_address.return_value = '192.168.1.1'
        with self.app.test_request_context():
            session.clear()
            result = main.get_user_email_for_rate_limit()
            self.assertEqual(result, '192.168.1.1')
            self.assertNotIn('user_email', session)
            mock_get_remote_address.assert_called_once()

    @patch('main.get_user_info')
    @patch('main.get_remote_address')
    def test_fallback_exception(self, mock_get_remote_address, mock_get_user_info):
        mock_get_user_info.side_effect = Exception("API Error")
        mock_get_remote_address.return_value = '10.0.0.1'
        with self.app.test_request_context():
            session.clear()
            result = main.get_user_email_for_rate_limit()
            self.assertEqual(result, '10.0.0.1')
            self.assertNotIn('user_email', session)
            mock_get_remote_address.assert_called_once()

if __name__ == '__main__':
    unittest.main()
