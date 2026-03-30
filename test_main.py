import unittest
from unittest.mock import MagicMock, patch
import sys
import threading

sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.texttospeech'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['google.oauth2.credentials'] = MagicMock()

import main

class TestOptimization(unittest.TestCase):
    def test_worker_thread_locals(self):
        self.assertTrue(hasattr(main, '_worker_thread_locals'))
        self.assertIsInstance(main._worker_thread_locals, type(threading.local()))

if __name__ == '__main__':
    unittest.main()
