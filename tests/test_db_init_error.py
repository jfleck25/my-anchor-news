import unittest
from unittest.mock import patch
import io
import sys

class TestDBInitError(unittest.TestCase):
    def test_db_init_exception_handling(self):
        """
        Verify that if database initialization raises an exception (e.g. invalid URL, network issue),
        the error is caught and logged appropriately without crashing the application.
        """
        import main

        # Save original db_pool to restore later
        original_db_pool = main.db_pool

        with patch('main.DATABASE_URL', new='mock_database_url'), \
             patch('main.psycopg2.pool.ThreadedConnectionPool') as mock_pool, \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:

            # Configure the mock to simulate a connection failure
            mock_pool.side_effect = Exception("Simulated connection failure")

            # Call init_db directly to test its error handling
            main.init_db()

            # Verify the exception was caught and printed
            output = mock_stdout.getvalue()
            self.assertIn(" * DB Init Error: Simulated connection failure", output)

        # Restore original db_pool
        main.db_pool = original_db_pool

if __name__ == '__main__':
    unittest.main()
