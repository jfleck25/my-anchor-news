import time
from unittest.mock import MagicMock, patch
import threading
from google.oauth2.credentials import Credentials
from google.cloud import texttospeech
from google.api_core import client_options

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

    creds = Credentials(**args[2])
    client_opts = client_options.ClientOptions(quota_project_id=args[4])

    start = time.time()
    for _ in range(500):
        client = texttospeech.TextToSpeechClient(
            credentials=creds,
            client_options=client_opts,
            transport="rest"
        )
    end = time.time()
    print(f"500 instantiations took {end - start:.4f} seconds")

benchmark_instantiation()
