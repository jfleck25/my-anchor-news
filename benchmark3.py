import time
from unittest.mock import MagicMock, patch
import threading
from concurrent.futures import ThreadPoolExecutor
from google.oauth2.credentials import Credentials
from google.cloud import texttospeech
from google.api_core import client_options

def synthesize_mock_worker(i, creds_dict, project_id):
    creds = Credentials(**creds_dict)
    client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
    tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
    # Simulate a little work
    time.sleep(0.01)
    return i

_worker_locals = threading.local()

def synthesize_mock_worker_optimized(i, creds_dict, project_id):
    if not hasattr(_worker_locals, 'tts_client'):
        creds = Credentials(**creds_dict)
        client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
        _worker_locals.tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")

    tts_client = _worker_locals.tts_client
    # Simulate a little work
    time.sleep(0.01)
    return i

def run_benchmarks():
    creds_dict = {
        "token": "fake_token",
        "refresh_token": "fake_refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "fake_client_id",
        "client_secret": "fake_secret",
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
    }
    project_id = "fake-project-id"
    chunks = 100

    start = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda i: synthesize_mock_worker(i, creds_dict, project_id), range(chunks)))
    unoptimized_time = time.time() - start
    print(f"Unoptimized time (100 tasks, 8 workers): {unoptimized_time:.4f} seconds")

    start = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda i: synthesize_mock_worker_optimized(i, creds_dict, project_id), range(chunks)))
    optimized_time = time.time() - start
    print(f"Optimized time (100 tasks, 8 workers): {optimized_time:.4f} seconds")

run_benchmarks()
