import time
from unittest.mock import patch
import json
from google.oauth2.credentials import Credentials


def benchmark_instantiation():
    args = (
        0,
        "Hello world, this is a test chunk to measure the time it takes "
        "to create the TTS client. " * 10,
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
    from google.api_core import client_options
    client_opts = client_options.ClientOptions(quota_project_id=args[4])

    from google.cloud import texttospeech

    start = time.time()
    for _ in range(50):
        _ = texttospeech.TextToSpeechClient(
            credentials=creds,
            client_options=client_opts,
            transport="rest"
        )
    end = time.time()
    print(f"50 instantiations took {end - start:.4f} seconds")


if __name__ == "__main__":
    benchmark_instantiation()
