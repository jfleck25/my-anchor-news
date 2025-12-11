# main.py
import os
import base64
import json
import re
import time
import hashlib
import flask
from flask import request, redirect, session, url_for, jsonify, send_from_directory
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.generativeai as genai
from google.cloud import texttospeech
from google.api_core import client_options 
from bs4 import BeautifulSoup
import google.auth.transport.requests 
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg2 
from psycopg2.extras import RealDictCursor

# --- Configuration & Constants ---
app = flask.Flask(__name__, static_folder='.', static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app, supports_credentials=True)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key_for_development")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/cloud-platform'
]

CLIENT_SECRETS_FILE = "client_secrets.json"
SETTINGS_FILE = "user_settings.json"
CACHE_FILE = "cache.json"
CACHE_TTL_SECONDS = 900 

DATABASE_URL = os.environ.get("DATABASE_URL")

# --- Database Setup (Postgres) ---
def init_db():
    if not DATABASE_URL: 
        print(" * Running in Local Mode (No Database URL found)")
        return
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_email VARCHAR(255) PRIMARY KEY,
                settings JSONB
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print(" * Database connection successful. Table initialized.")
    except Exception as e:
        print(f" * DB Init Error: {e}")

init_db()

# --- Helper Functions ---

def get_user_info():
    if 'credentials' not in session: return None
    credentials = Credentials(**session['credentials'])
    try:
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        return user_info_service.userinfo().get().execute()
    except: return None

def load_settings(user_email=None):
    defaults = {
        "sources": ["wsj.com", "nytimes.com", "axios.com", "theguardian.com", "techcrunch.com"],
        "time_window_hours": 24
    }

    if DATABASE_URL and user_email:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT settings FROM user_settings WHERE user_email = %s", (user_email,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                user_settings = defaults.copy()
                user_settings.update(row['settings'])
                return user_settings
            else:
                return defaults
        except Exception as e:
            print(f"DB Read Error: {e}")
            return defaults

    if not os.path.exists(SETTINGS_FILE): return defaults
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except: return defaults

def save_settings(new_settings, user_email=None):
    if DATABASE_URL and user_email:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_settings (user_email, settings)
                VALUES (%s, %s)
                ON CONFLICT (user_email) 
                DO UPDATE SET settings = EXCLUDED.settings;
            """, (user_email, json.dumps(new_settings)))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Write Error: {e}")
            return False

    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(new_settings, f, indent=2)
        return True
    except: return False

# --- Secrets & AI Config ---
def get_client_secrets_config():
    env_secrets = os.environ.get("GOOGLE_CLIENT_SECRETS_JSON")
    if env_secrets:
        try: return json.loads(env_secrets)
        except json.JSONDecodeError: pass
    if os.path.exists(CLIENT_SECRETS_FILE): return CLIENT_SECRETS_FILE
    raise FileNotFoundError("Client secrets not found.")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    try:
        config = get_client_secrets_config()
        if isinstance(config, dict): secrets = config
        else:
            with open(config, 'r') as f: secrets = json.load(f)
        data = secrets.get('web') or secrets.get('installed')
        if data: PROJECT_ID = data.get('project_id')
    except: pass

api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except: model = None

def sanitize_for_llm(text):
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return text.replace('\\', '\\\\').replace('"', '\\"')

def generate_script_from_analysis(analysis_json):
    script = "Good morning. Here is your deeper look at today's news. "
    story_groups = analysis_json.get('story_groups', [])
    for i, group in enumerate(story_groups):
        script += f"{group.get('group_headline', '')}. {group.get('group_summary', '')}. "
        stories = group.get('stories', [])
        if len(stories) > 1:
            script += "Here is how the coverage differs: "
            for story in stories:
                source = story.get('source', 'One source').split('<')[0].strip().replace('.com', '')
                script += f"The {source} {story.get('angle', '')}. "
        if i < len(story_groups) - 1: script += " Moving on... "
    remaining = analysis_json.get('remaining_stories', [])
    if remaining:
        script += "In brief: "
        for story in remaining: script += f"{story.get('headline', '')}. "
    script += "That concludes your briefing."
    return script

def analyze_news_with_llm(newsletters_text):
    if not model: raise Exception("Gemini API model is not configured.")
    prompt = """
    You are an elite media analyst. Provide raw text from multiple newsletters.
    Task:
    1. Group distinct news events.
    2. Create neutral headlines.
    3. Write 3-4 sentence summary of facts.
    4. **DEEP ANGLE ANALYSIS**: 1-2 sentences per article. Include specific facts/data/quotes. Start with verb (e.g. "Cites...").
    5. **Remaining Stories**: Top 5 only. One-sentence summary.
    6. **Filter**: Ignore ads/fluff.
    7. **Limit**: Top 10 groups max.
    
    Output JSON: { "story_groups": [ { "group_headline": "...", "group_summary": "...", "stories": [ { "headline": "...", "source": "...", "angle": "..." } ] } ], "remaining_stories": [ { "headline": "..." } ] }
    
    Content: ---
    """ + newsletters_text
    try:
        generation_config = genai.types.GenerationConfig(max_output_tokens=8192, temperature=0.2)
        response = model.generate_content(prompt, generation_config=generation_config)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match: return json.loads(match.group(0))
        else: raise ValueError("No valid JSON found.")
    except json.JSONDecodeError: return {"error": "Analysis failed due to volume."}
    except Exception as e: return {"error": "AI analysis failed."}

# --- Caching Helpers ---
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_cache(data):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def get_settings_hash(settings):
    s = json.dumps(settings, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()

# --- Routes ---

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login():
    config = get_client_secrets_config()
    if isinstance(config, dict):
        flow = Flow.from_client_config(config, scopes=SCOPES)
        flow.redirect_uri = url_for('oauth2callback', _external=True)
    else:
        flow = Flow.from_client_secrets_file(config, scopes=SCOPES, redirect_uri=url_for('oauth2callback', _external=True))
        
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    config = get_client_secrets_config()
    if isinstance(config, dict):
        flow = Flow.from_client_config(config, scopes=SCOPES)
        flow.redirect_uri = url_for('oauth2callback', _external=True)
    else:
        flow = Flow.from_client_secrets_file(config, scopes=SCOPES, state=state, redirect_uri=url_for('oauth2callback', _external=True))
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri, 'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scopes': credentials.scopes}
    return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'logged_out'})

@app.route('/api/check_auth')
def check_auth():
    user_info = get_user_info()
    return jsonify({'logged_in': True, 'user': user_info}) if user_info else jsonify({'logged_in': False})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    if 'credentials' not in session: return jsonify({'error': 'User not authenticated'}), 401
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    return jsonify(load_settings(email))

@app.route('/api/settings', methods=['POST'])
def update_settings():
    if 'credentials' not in session: return jsonify({'error': 'User not authenticated'}), 401
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    if save_settings(request.get_json(), email):
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to save settings'}), 500

@app.route('/api/fetch_emails')
def fetch_emails():
    if 'credentials' not in session: return jsonify({'error': 'User not authenticated'}), 401
    
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    settings = load_settings(email)
    
    current_hash = get_settings_hash(settings)
    cache = load_cache()
    
    if (cache.get('timestamp', 0) + CACHE_TTL_SECONDS > time.time()) and \
       (cache.get('settings_hash') == current_hash) and \
       (cache.get('analysis')):
        return jsonify(cache['analysis'])
    
    creds = Credentials(**session['credentials'])
    try:
        service = build('gmail', 'v1', credentials=creds)
        sources = settings.get('sources', []) or ["wsj.com", "nytimes.com"]
        hours = settings.get('time_window_hours', 24)
        sources_query = " OR ".join([f"from:{s}" for s in sources])
        query = f"({sources_query}) newer_than:{hours}h"
        
        results = service.users().messages().list(userId='me', q=query, maxResults=25).execute()
        messages = results.get('messages', [])

        if not messages: return jsonify({'story_groups': [], 'remaining_stories': [{'headline': f'No newsletters found in last {hours}h.'}]})
        
        consolidated_text = ""
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')
            
            body_data = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        body_data = part['body']['data']
                        break
            else: body_data = msg['payload'].get('body', {}).get('data', '')
            
            if not body_data: continue
            decoded_data = base64.urlsafe_b64decode(body_data.encode('ASCII'))
            soup = BeautifulSoup(decoded_data, "lxml")
            clean_text = soup.get_text(separator='\n', strip=True)
            sanitized_text = sanitize_for_llm(clean_text)
            if len(sanitized_text) > 4000: sanitized_text = sanitized_text[:4000] + "... [TRUNCATED]"
            consolidated_text += f"\n\n--- Newsletter from: {sender} ---\n--- Subject: {subject} ---\n{sanitized_text}\n"

        if not consolidated_text: return jsonify({'story_groups': [], 'remaining_stories': [{'headline': 'No text found.'}]})

        analysis_result = analyze_news_with_llm(consolidated_text)
        
        cache['timestamp'] = time.time()
        cache['settings_hash'] = current_hash
        cache['analysis'] = analysis_result
        if 'audio' in cache: del cache['audio']
        if 'script_hash' in cache: del cache['script_hash']
        save_cache(cache)
        
        return jsonify(analysis_result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_audio', methods=['POST'])
def generate_audio():
    if 'credentials' not in session: return jsonify({'error': 'User not authenticated'}), 401
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    try:
        auth_req = google.auth.transport.requests.Request()
        if creds.expired:
            creds.refresh(auth_req)
            session['credentials']['token'] = creds.token
            session.modified = True
    except Exception as e: print(f"Token Refresh Error: {e}")

    client_opts = None
    if PROJECT_ID: client_opts = client_options.ClientOptions(quota_project_id=PROJECT_ID)
    tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
    
    analysis_data = request.get_json()
    if not analysis_data: return jsonify({"error": "No analysis data provided."}), 400
    
    try:
        script_text = generate_script_from_analysis(analysis_data)
        script_hash = hashlib.md5(script_text.encode()).hexdigest()
        
        cache = load_cache()
        if cache.get('script_hash') == script_hash and cache.get('audio'):
            return jsonify({"audio_content": cache['audio']})
        
        sentences = re.split(r'(?<=[.!?])\s+', script_text)
        chunks = []
        current_chunk = ""
        byte_limit = 4800 
        for sentence in sentences:
            if len(current_chunk.encode('utf-8')) + len(sentence.encode('utf-8')) + 1 < byte_limit:
                current_chunk += sentence + " "
            else:
                if current_chunk: chunks.append(current_chunk)
                current_chunk = sentence + " "
        if current_chunk: chunks.append(current_chunk)
        
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        all_audio_content = b""
        
        for chunk_text in chunks:
            if len(chunk_text.encode('utf-8')) > byte_limit: chunk_text = chunk_text.encode('utf-8')[:byte_limit].decode('utf-8', 'ignore')
            synthesis_input = texttospeech.SynthesisInput(text=chunk_text)
            response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            all_audio_content += response.audio_content
        
        audio_base64 = base64.b64encode(all_audio_content).decode('utf-8')
        
        cache['script_hash'] = script_hash
        cache['audio'] = audio_base64
        save_cache(cache)
        
        return jsonify({"audio_content": audio_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # In production, we don't run with debug=True
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))