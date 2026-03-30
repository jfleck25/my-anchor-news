import time
from unittest.mock import MagicMock, patch
import json
from google.oauth2.credentials import Credentials

# Mock the module before importing main
import sys

# Try to import main.py, but mock the decorators and Flask stuff if needed
sys.path.append('.')
import main

def benchmark_instantiation():
    args = (
        0,
        "Hello world, this is a test chunk to measure the time it takes to create the TTS client. " * 10,
        {
            "token": "fake_token",
            "refresh_token": "fake_refresh",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "fake_client_id",
            "client_secret": "fake_secret",
            "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
        },
        "anchor",
        "fake-project-id"
    )

    # Mock synthesize_speech so we only measure setup and not network request
    with patch('google.cloud.texttospeech.TextToSpeechClient') as MockClient:
        # Actually we WANT to measure TextToSpeechClient instantiation, so we shouldn't mock the whole class
        pass

    # Let's mock the actual network request or synthesize_speech inside the instantiated client
    # Or just time the instantiation directly:
    creds = Credentials(**args[2])
    from google.api_core import client_options
    client_opts = client_options.ClientOptions(quota_project_id=args[4])

    from google.cloud import texttospeech

    start = time.time()
    for _ in range(50):
        # We need to mock google.auth to prevent actual creds validation if any,
        # but Credentials(**dict) just creates a local object.
        client = texttospeech.TextToSpeechClient(
            credentials=creds,
            client_options=client_opts,
            transport="rest"
        )
    end = time.time()
    print(f"50 instantiations took {end - start:.4f} seconds")

benchmark_instantiation()
