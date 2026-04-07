import unittest
from unittest.mock import patch, mock_open
import json
import main

class TestCache(unittest.TestCase):

    @patch('os.path.exists')
    def test_load_cache_no_file(self, mock_exists):
        mock_exists.return_value = False
        result = main.load_cache()
        self.assertEqual(result, {})

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_cache_valid_json(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = main.load_cache()
        self.assertEqual(result, {"key": "value"})
        mock_file.assert_called_once_with(main.CACHE_FILE, 'r')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_cache_invalid_json(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = main.load_cache()
        self.assertEqual(result, {})
        mock_file.assert_called_once_with(main.CACHE_FILE, 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_cache_success(self, mock_file):
        data = {"key": "value"}
        main.save_cache(data)
        mock_file.assert_called_once_with(main.CACHE_FILE, 'w')
        # Check that json.dump was called correctly.
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(written, '{"key": "value"}')

    @patch('builtins.open', side_effect=Exception("Permission denied"))
    def test_save_cache_exception(self, mock_file):
        data = {"key": "value"}
        # This shouldn't raise an exception because save_cache catches it
        main.save_cache(data)
        mock_file.assert_called_once_with(main.CACHE_FILE, 'w')

if __name__ == '__main__':
    unittest.main()
