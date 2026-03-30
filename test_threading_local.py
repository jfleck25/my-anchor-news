import threading

_worker_locals = threading.local()

def get_client(creds_dict, project_id):
    if not hasattr(_worker_locals, 'tts_client'):
        print(f"Creating TTS client in thread {threading.current_thread().name}")
        from google.oauth2.credentials import Credentials
        from google.cloud import texttospeech
        from google.api_core import client_options

        creds = Credentials(**creds_dict)
        client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
        _worker_locals.tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
    else:
        print(f"Reusing TTS client in thread {threading.current_thread().name}")
    return _worker_locals.tts_client
