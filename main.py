# main.py
import os
import base64
import json
import re
import time
import hashlib
import uuid
import random
from dotenv import load_dotenv
import flask

# Load environment variables from .env file
load_dotenv()
from flask import request, redirect, session, url_for, jsonify, render_template
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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# --- Sentry Configuration ---
# Get Sentry DSN from environment variable
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
        profiles_sample_rate=1.0,  # Capture 100% of profiles
        environment=os.environ.get("FLASK_ENV", "development"),
        release=os.environ.get("APP_VERSION", "1.0.0")
    )
    print(" * Sentry error tracking enabled")
else:
    print(" * Sentry DSN not found - error tracking disabled (set SENTRY_DSN environment variable)")

# --- Configuration & Constants ---
app = flask.Flask(__name__, static_folder='.', static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app, supports_credentials=True)

# --- Rate Limiting ---
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key_for_development")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Enable detailed error messages in development
if os.environ.get("FLASK_ENV") != "production":
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True

# Global error handler to catch all unhandled exceptions
@app.errorhandler(500)
def handle_500_error(e):
    import traceback
    error_trace = traceback.format_exc()
    path = request.path if request else "unknown"
    print(f"[500] path={path} error={e}")
    print(error_trace)
    # Don't expose raw upstream (Google/Gemini) errors to client
    safe_msg = "Something went wrong. Please try again or log in again."
    return jsonify({'error': safe_msg, 'endpoint': path, 'details': error_trace[:500] if app.config.get('DEBUG') else None}), 500

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

# --- PERSONA CONFIGURATION ---
PERSONAS = {
    "anchor": {
        "voice_name": "en-US-Journey-D",
        "gender": texttospeech.SsmlVoiceGender.MALE,
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "intro": ["Good morning. Here is your daily briefing.", "This is My Anchor. Let's look at the news."],
        "transition": ["Next up...", "Moving on...", "In other news...", "Turning to..."],
        "outro": "That concludes your briefing. Have a good day."
    },
    "analyst": {
        "voice_name": "en-US-Neural2-J",
        "gender": texttospeech.SsmlVoiceGender.MALE,
        "speaking_rate": 1.20,
        "pitch": -2.0,
        "intro": ["Market update.", "Here is the data.", "Let's look at the numbers."],
        "transition": ["Next sector:", "Analysis:", "Data point:", "Moving to:"],
        "outro": "Briefing complete."
    },
    "dj": {
        "voice_name": "en-US-Neural2-F",
        "gender": texttospeech.SsmlVoiceGender.FEMALE,
        "speaking_rate": 1.15,
        "pitch": 1.5,
        "intro": ["Rise and shine! Here's what's happening.", "Yo! Let's get you caught up."],
        "transition": ["Check this out...", "Switching gears...", "And get this...", "Next story..."],
        "outro": "That's the wrap! Catch you later."
    }
}

# --- Database Setup ---
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shared_briefings (
                share_id UUID PRIMARY KEY,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print(" * Database connection successful.")
    except Exception as e:
        print(f" * DB Init Error: {e}")

init_db()

# --- Helper Functions ---

def get_user_info():
    if 'credentials' not in session:
        return None
    try:
        credentials = Credentials(**session['credentials'])
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        return user_info_service.userinfo().get().execute()
    except Exception as ex:
        print(f"get_user_info error: {ex}")
        return None

def load_settings(user_email=None):
    defaults = {
        "sources": ["wsj.com", "nytimes.com", "axios.com", "theguardian.com", "techcrunch.com"],
        "time_window_hours": 24,
        "personality": "anchor",
        "priority_sources": [],
        "keywords": []
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
        except Exception:
            pass

    if not os.path.exists(SETTINGS_FILE):
        return defaults
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return defaults

def save_settings(new_settings, user_email=None):
    if DATABASE_URL and user_email:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_settings (user_email, settings) VALUES (%s, %s)
                ON CONFLICT (user_email) DO UPDATE SET settings = EXCLUDED.settings;
            """, (user_email, json.dumps(new_settings)))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception:
            return False
            
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(new_settings, f, indent=2)
        return True
    except Exception:
        return False

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
    except Exception:
        model = None

def sanitize_for_llm(text):
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return text.replace('\\', '\\\\').replace('"', '\\"')

def generate_script_from_analysis(analysis_json, style="anchor"):
    persona = PERSONAS.get(style, PERSONAS["anchor"])
    script = f"{random.choice(persona['intro'])} "
    
    story_groups = analysis_json.get('story_groups', [])
    for i, group in enumerate(story_groups):
        script += f"{group.get('group_headline', '')}. {group.get('group_summary', '')}. "
        stories = group.get('stories', [])
        if len(stories) > 1:
            script += "Perspectives: "
            for story in stories:
                source = story.get('source', 'One source').split('<')[0].strip().replace('.com', '')
                script += f"The {source} {story.get('angle', '')}. "
        if i < len(story_groups) - 1: script += f" {random.choice(persona['transition'])} "
            
    remaining = analysis_json.get('remaining_stories', [])
    if remaining:
        script += "Briefly: "
        for story in remaining: script += f"{story.get('headline', '')}. "
    script += f" {persona['outro']}"
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
    except json.JSONDecodeError:
        return {"error": "Analysis failed due to volume."}
    except Exception as e:
        print(f"LLM analysis error: {e}")
        return {"error": "AI analysis failed."}

# --- Caching Helpers ---
def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache(data):
    try: 
        with open(CACHE_FILE, 'w') as f: json.dump(data, f)
    except Exception as e:
        pass

def get_settings_hash(settings):
    s = json.dumps(settings, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html',
        sentry_dsn_frontend=os.environ.get('SENTRY_DSN_FRONTEND', ''),
        posthog_api_key=os.environ.get('POSTHOG_API_KEY', '')
    )

@app.route('/login')
def login():
    try:
        config = get_client_secrets_config()
        if isinstance(config, dict):
            flow = Flow.from_client_config(config, scopes=SCOPES)
            flow.redirect_uri = url_for('oauth2callback', _external=True)
        else:
            flow = Flow.from_client_secrets_file(config, scopes=SCOPES, redirect_uri=url_for('oauth2callback', _external=True))
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
        session['state'] = state
        return redirect(authorization_url)
    except FileNotFoundError as e:
        print(f"ERROR in login route: Client secrets not found: {e}")
        return jsonify({'error': 'OAuth configuration not found. Please set GOOGLE_CLIENT_SECRETS_JSON environment variable or create client_secrets.json file.'}), 500
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in login route: {e}")
        print(error_trace)
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/oauth2callback')
def oauth2callback():
    try:
        if 'state' not in session:
            print("ERROR: State missing from session")
            return jsonify({'error': 'Invalid session state'}), 400
        state = session['state']
        
        try:
            config = get_client_secrets_config()
        except FileNotFoundError as config_err:
            print(f"ERROR: Client secrets not found: {config_err}")
            return jsonify({'error': 'OAuth configuration not found. Please check GOOGLE_CLIENT_SECRETS_JSON environment variable or client_secrets.json file.'}), 500
        
        if isinstance(config, dict):
            flow = Flow.from_client_config(config, scopes=SCOPES)
            flow.redirect_uri = url_for('oauth2callback', _external=True)
        else:
            flow = Flow.from_client_secrets_file(config, scopes=SCOPES, state=state, redirect_uri=url_for('oauth2callback', _external=True))
        
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        session['credentials'] = {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri, 'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scopes': credentials.scopes}
        return redirect("/")
    except Exception as e:
        import traceback
        print(f"OAuth callback error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'logged_out'})

@app.route('/api/check_auth')
def check_auth():
    # #region agent log
    _log = {"sessionId":"4b162f","location":"main.py:check_auth","data":{"has_credentials":"credentials" in session}}
    print(f"[DEBUG 4b162f] {json.dumps(_log)}", flush=True)
    # #endregion
    user_info = get_user_info()
    # #region agent log
    _log2 = {"sessionId":"4b162f","location":"main.py:check_auth","message":"result","data":{"has_user_info":user_info is not None}}
    print(f"[DEBUG 4b162f] {json.dumps(_log2)}", flush=True)
    # #endregion
    return jsonify({'logged_in': True, 'user': user_info}) if user_info else jsonify({'logged_in': False})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    if 'credentials' not in session:
        return jsonify({'error': 'Please log in to view your settings.'}), 401
    try:
        user_info = get_user_info()
        email = user_info.get('email') if user_info else None
        return jsonify(load_settings(email))
    except Exception as ex:
        print(f"get_settings error: {ex}")
        return jsonify({'error': 'Unable to load settings. Please try again.'}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    if 'credentials' not in session: 
        return jsonify({'error': 'Please log in to save your settings.'}), 401
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    if save_settings(request.get_json(), email):
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Unable to save settings. Please try again or contact support if the issue persists.'}), 500

def get_user_email_for_rate_limit():
    """Get user email from session or use IP address as fallback"""
    if 'user_email' in session:
        return session['user_email']
    # Try to get from user info if available
    try:
        user_info = get_user_info()
        if user_info and user_info.get('email'):
            session['user_email'] = user_info['email']
            return user_info['email']
    except Exception as e:
        pass
    return get_remote_address()

@app.route('/api/fetch_emails')
@limiter.limit("3 per day", key_func=get_user_email_for_rate_limit, error_message="You've reached your daily limit of 3 briefings. Upgrade to Pro for unlimited briefings or try again tomorrow!")
def fetch_emails():
    if 'credentials' not in session: 
        return jsonify({'error': 'Please log in to generate your briefing.'}), 401
    
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    # Store email in session for rate limiting
    if email: session['user_email'] = email
    settings = load_settings(email)
    
    current_hash = get_settings_hash(settings)
    cache = load_cache()
    if (cache.get('timestamp', 0) + CACHE_TTL_SECONDS > time.time()) and (cache.get('settings_hash') == current_hash) and (cache.get('analysis')):
        return jsonify(cache['analysis'])
    
    creds = Credentials(**session['credentials'])
    try:
        service = build('gmail', 'v1', credentials=creds)
        sources = settings.get('sources', []) or ["wsj.com", "nytimes.com"]
        hours = settings.get('time_window_hours', 24)
        
        # --- NEW: Get Watchlist & Priority ---
        keywords = settings.get('keywords', [])
        priority_sources = settings.get('priority_sources', [])
        
        sources_query = " OR ".join([f"from:{s}" for s in sources])
        query = f"({sources_query}) newer_than:{hours}h"
        
        # Increase maxResults to account for filtering
        results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        messages = results.get('messages', [])
        if not messages: return jsonify({'story_groups': [], 'remaining_stories': [{'headline': f'No newsletters found in last {hours}h.'}]})
        
        priority_text = ""
        normal_text = ""
        
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')
            
            body_data = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/html': body_data = part['body']['data']; break
            else: body_data = msg['payload'].get('body', {}).get('data', '')
            if not body_data: continue
            
            decoded_data = base64.urlsafe_b64decode(body_data.encode('ASCII'))
            soup = BeautifulSoup(decoded_data, "lxml")
            clean_text = soup.get_text(separator='\n', strip=True)
            sanitized_text = sanitize_for_llm(clean_text)
            
            # --- FEATURE: Watchlist Filtering ---
            # If keywords are set, skip emails that don't match ANY keyword
            if keywords:
                has_keyword = any(k.lower() in sanitized_text.lower() or k.lower() in subject.lower() for k in keywords)
                if not has_keyword:
                    continue

            if len(sanitized_text) > 4000: sanitized_text = sanitized_text[:4000] + "... [TRUNCATED]"
            
            email_block = f"\n\n--- Newsletter from: {sender} ---\n--- Subject: {subject} ---\n{sanitized_text}\n"
            
            # --- FEATURE: Source Prioritization ---
            # If sender is in priority list, add to priority block
            is_priority = any(p.lower() in sender.lower() for p in priority_sources)
            if is_priority:
                priority_text += f"*** PRIORITY SOURCE ***\n{email_block}"
            else:
                normal_text += email_block

        # Put priority text FIRST so LLM sees it
        consolidated_text = priority_text + normal_text

        if not consolidated_text: 
            reason = "No text found matching your watchlist." if keywords else "No text found."
            return jsonify({'story_groups': [], 'remaining_stories': [{'headline': reason}]})
        
        analysis_result = analyze_news_with_llm(consolidated_text)
        
        cache['timestamp'] = time.time()
        cache['settings_hash'] = current_hash
        cache['analysis'] = analysis_result
        if 'audio' in cache: del cache['audio']
        if 'script_hash' in cache: del cache['script_hash']
        save_cache(cache)
        return jsonify(analysis_result)
    except Exception as e:
        err_msg = str(e).lower()
        if 'quota' in err_msg or 'rate' in err_msg or '429' in err_msg:
            return jsonify({'error': "Gmail rate limit reached. Please try again in a few minutes."}), 429
        if 'credentials' in err_msg or 'token' in err_msg or '401' in err_msg:
            return jsonify({'error': "Your session expired. Please log in again."}), 401
        print(f"fetch_emails error: {e}")
        return jsonify({'error': "Unable to fetch newsletters. Please check your connection and try again."}), 500

@app.route('/api/generate_audio', methods=['POST'])
def generate_audio():
    if 'credentials' not in session: 
        return jsonify({'error': 'Please log in to generate audio.'}), 401
    
    # --- Load Settings to get Persona ---
    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    settings = load_settings(email)
    style = settings.get('personality', 'anchor')
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    try:
        auth_req = google.auth.transport.requests.Request()
        if creds.expired: creds.refresh(auth_req); session['credentials']['token'] = creds.token; session.modified = True
    except Exception:
        pass
    try:
        client_opts = None
        if PROJECT_ID: client_opts = client_options.ClientOptions(quota_project_id=PROJECT_ID)
        tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")

        analysis_data = request.get_json()
        if not analysis_data:
            return jsonify({'error': 'No briefing data to convert to audio.'}), 400
        script_text = generate_script_from_analysis(analysis_data, style)
        script_hash = hashlib.md5((script_text + style).encode()).hexdigest()
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

        persona_config = PERSONAS.get(style, PERSONAS['anchor'])
        voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=persona_config['voice_name'], ssml_gender=persona_config['gender'])
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=persona_config.get('speaking_rate', 1.0), pitch=persona_config.get('pitch', 0.0))
        all_audio_content = b""
        for chunk_text in chunks:
            if len(chunk_text.encode('utf-8')) > byte_limit: chunk_text = chunk_text.encode('utf-8')[:byte_limit].decode('utf-8', 'ignore')
            response = tts_client.synthesize_speech(input=texttospeech.SynthesisInput(text=chunk_text), voice=voice, audio_config=audio_config)
            all_audio_content += response.audio_content
        audio_base64 = base64.b64encode(all_audio_content).decode('utf-8')
        cache['script_hash'] = script_hash
        cache['audio'] = audio_base64
        save_cache(cache)
        return jsonify({"audio_content": audio_base64})
    except Exception as e:
        err_msg = str(e).lower()
        if 'quota' in err_msg or '429' in err_msg:
            return jsonify({'error': 'Text-to-speech quota exceeded. Please try again later.'}), 429
        if 'credentials' in err_msg or 'token' in err_msg or '401' in err_msg:
            return jsonify({'error': 'Your session expired. Please log in again.'}), 401
        print(f"generate_audio error: {e}")
        return jsonify({'error': 'Unable to generate audio. Please try again.'}), 500

# --- Share Endpoints ---
@app.route('/api/share', methods=['POST'])
def share_briefing():
    if 'credentials' not in session: return jsonify({'error': 'User not authenticated'}), 401
    data = request.get_json()
    if not data: return jsonify({'error': 'No data'}), 400
    share_id = str(uuid.uuid4())
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO shared_briefings (share_id, data) VALUES (%s, %s)", (share_id, json.dumps(data)))
            conn.commit(); cur.close(); conn.close()
            return jsonify({'share_id': share_id})
        except Exception:
            return jsonify({'error': 'Unable to save shared briefing. Please try again.'}), 500
    return jsonify({'error': 'DB not configured'}), 500

@app.route('/api/shared/<share_id>', methods=['GET'])
def get_shared_briefing(share_id):
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT data FROM shared_briefings WHERE share_id = %s", (share_id,))
            row = cur.fetchone(); cur.close(); conn.close()
            if row: return jsonify(row['data'])
            return jsonify({'error': 'This shared briefing could not be found. The link may be invalid or expired.'}), 404
        except Exception:
            return jsonify({'error': 'Unable to load shared briefing. Please try again.'}), 500
    return jsonify({'error': 'Shared briefings are not available. Database connection required.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))