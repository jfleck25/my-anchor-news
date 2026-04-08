cat << 'PATCH' > tts.patch
--- main.py
+++ main.py
@@ -380,9 +380,12 @@
     byte_limit = 4800
     if len(chunk_text.encode('utf-8')) > byte_limit:
         chunk_text = chunk_text.encode('utf-8')[:byte_limit].decode('utf-8', 'ignore')
-    creds = Credentials(**creds_dict)
-    client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
-    tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
+
+    if not hasattr(_worker_thread_locals, 'tts_client'):
+        creds = Credentials(**creds_dict)
+        client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
+        _worker_thread_locals.tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
+    tts_client = _worker_thread_locals.tts_client
     persona_config = PERSONAS.get(style, PERSONAS['anchor'])
     voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=persona_config['voice_name'], ssml_gender=persona_config['gender'])
     audio_config = texttospeech.AudioConfig(
PATCH
patch main.py < tts.patch
