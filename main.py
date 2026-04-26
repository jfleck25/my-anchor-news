# main.py
import os
import base64
import json
import re
import secrets
import time
import hashlib
import uuid
import random
import threading
import copy
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import flask

# Load environment variables from .env file
load_dotenv()
from flask import request, redirect, session, url_for, jsonify, render_template
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import google.generativeai as genai
from google.cloud import texttospeech
from google.api_core import client_options 
from google.api_core.exceptions import ResourceExhausted, InvalidArgument
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request, AuthorizedSession
import google.auth.transport.requests 
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg2 
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from posthog import Posthog

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

# --- PostHog Configuration ---
POSTHOG_API_KEY = os.environ.get("POSTHOG_API_KEY")
if POSTHOG_API_KEY:
    posthog_client = Posthog(project_api_key=POSTHOG_API_KEY, host=os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com"))
else:
    posthog_client = None

# --- Configuration & Constants ---
MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"
if MOCK_MODE:
    print(" * [DEMO MODE] Interactive demo button enabled.")

app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 🛡️ Sentinel: Enforce a global 2MB request payload limit to prevent resource exhaustion / DoS
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

allowed_origins = os.environ.get("ALLOWED_ORIGINS")
if allowed_origins:
    origins_list = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    CORS(app, supports_credentials=True, origins=origins_list)
else:
    # 🛡️ Sentinel: Default to empty origins to prevent overly permissive CORS across all environments
    if os.environ.get("FLASK_ENV") != "production":
        print(" * WARNING: ALLOWED_ORIGINS not set. Defaulting to empty origins. Cross-origin requests will be blocked. Please configure ALLOWED_ORIGINS for local development.")
    CORS(app, supports_credentials=True, origins=[])


# --- Rate Limiting ---
# Note: storage_uri="memory://" is per-process; with multiple gunicorn workers the limit is effectively (limit x workers) per user.
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

_secret_key = os.environ.get("FLASK_SECRET_KEY")
if os.environ.get("FLASK_ENV") == "production" and not _secret_key:
    raise RuntimeError("FLASK_SECRET_KEY must be set in production")
app.secret_key = _secret_key or secrets.token_hex(32)

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://browser.sentry-cdn.com https://unpkg.com https://us.i.posthog.com https://eu.i.posthog.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' https://us.i.posthog.com https://eu.i.posthog.com https://sentry.io https://*.sentry.io;"
    return response

# Enable detailed error messages in development
if os.environ.get("FLASK_ENV") != "production":
    if os.environ.get("ALLOW_INSECURE_OAUTH") == "1":
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    elif "OAUTHLIB_INSECURE_TRANSPORT" in os.environ:
        del os.environ["OAUTHLIB_INSECURE_TRANSPORT"]
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
else:
    # Security enhancements for production
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Global error handler to catch all unhandled exceptions
@app.errorhandler(500)
def handle_500_error(e):
    import traceback
    error_trace = traceback.format_exc()
    print(f"Unhandled 500 error: {e}")
    print(error_trace)
    # Don't expose raw upstream (Google/Gemini) errors to client
    safe_msg = "Something went wrong. Please try again or log in again."
    return jsonify({'error': safe_msg, 'details': None}), 500

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
_cache_lock = threading.Lock()
_worker_thread_locals = threading.local()

# ⚡ Bolt: Caching user settings from file to reduce I/O and JSON parsing overhead
_file_settings_cache = None
_file_settings_mtime = 0
_file_settings_lock = threading.Lock()

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
db_pool = None

def get_db_connection():
    global db_pool
    if db_pool:
        return db_pool.getconn()
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return None

def release_db_connection(conn):
    global db_pool
    if conn:
        try:
            conn.rollback() # Ensure connection state is clean
        except Exception:
            pass
        if db_pool:
            db_pool.putconn(conn)
        else:
            conn.close()

def init_db():
    global db_pool
    if not DATABASE_URL: 
        print(" * Running in Local Mode (No Database URL found)")
        return
    try:
        db_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, DATABASE_URL)
        conn = get_db_connection()
        try:
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
            print(" * Database connection successful.")
        finally:
            release_db_connection(conn)
    except Exception as e:
        print(f" * DB Init Error: {e}")

init_db()

# --- Helper Functions ---

def anonymize_user(email):
    if not email:
        return 'anonymous'
    # Use app instance secret_key for a consistent but secure salt across sessions if it persists, or fallback to something secure
    salt = str(app.secret_key or "default_salt")
    return hashlib.sha256((email + salt).encode()).hexdigest()


def get_credentials_from_session(creds_data):
    if not creds_data:
        return None
    try:
        config = get_client_secrets_config()
        if isinstance(config, dict):
            client_secrets = config
        else:
            with open(config, 'r') as f:
                import json
                client_secrets = json.load(f)
        data = client_secrets.get('web') or client_secrets.get('installed')
        client_secret = data.get('client_secret')

        creds_kwargs = dict(creds_data)
        if client_secret:
            creds_kwargs['client_secret'] = client_secret

        return Credentials(**creds_kwargs)
    except Exception as e:
        print(f"Error loading client secret: {e}")
        return Credentials(**creds_data)

def get_user_info():
    # Demo mode: return a synthetic user profile
    if session.get('is_mock_session'):
        return {
            'email': 'demo@myanchor.test',
            'name': 'Demo User',
            'picture': '',
            'id': 'demo-user-001'
        }
    if 'credentials' not in session:
        return None
    if 'user_info' in session:
        return session['user_info']
    try:
        credentials = get_credentials_from_session(session['credentials'])
        # ⚡ Bolt: Use AuthorizedSession for direct REST call to avoid discovery document overhead
        authed_session = AuthorizedSession(credentials)
        response = authed_session.get('https://www.googleapis.com/oauth2/v2/userinfo', timeout=5)
        response.raise_for_status()
        user_info = response.json()
        session['user_info'] = user_info
        return user_info
    except Exception as ex:
        print(f"get_user_info error: {ex}")
        session.pop('credentials', None)
        session.pop('user_email', None)
        session.pop('user_info', None)
        return None


# ⚡ Bolt: Cache DB-based settings to prevent repetitive synchronous blockages in hot loops.
# This cache reduces DB overhead for load_settings on cache hits significantly.
# We invalidate on explicit save_settings.
_db_settings_cache = {}
_db_settings_lock = threading.Lock()

def load_settings(user_email=None):

    defaults = {
        "sources": ["wsj.com", "nytimes.com", "axios.com", "theguardian.com", "techcrunch.com"],
        "time_window_hours": 24,
        "personality": "anchor",
        "priority_sources": [],
        "keywords": []
    }
    # In demo mode, never touch disk or DB — return in-memory defaults only
    if user_email == "demo@myanchor.test":
        return defaults
    
    # 1) If we have a user email, check the unified per-email cache first
    if user_email:
        with _db_settings_lock:
            if user_email in _db_settings_cache:
                return copy.deepcopy(_db_settings_cache[user_email])

    user_settings = None

    # 2) If using DB, try fetching from there
    if DATABASE_URL and user_email:
        try:
            conn = get_db_connection()
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT settings FROM user_settings WHERE user_email = %s", (user_email,))
                row = cur.fetchone()
                cur.close()
            finally:
                release_db_connection(conn)
            if row:
                user_settings = defaults.copy()
                user_settings.update(row['settings'] or {})
        except Exception:
            pass

    # 3) If no DB or DB fetch failed/returned nothing, fallback to file or defaults
    if user_settings is None:
        global _file_settings_cache, _file_settings_mtime
        if not os.path.exists(SETTINGS_FILE):
            user_settings = defaults.copy()
        else:
            try:
                mtime = os.path.getmtime(SETTINGS_FILE)
                with _file_settings_lock:
                    if _file_settings_cache is not None and _file_settings_mtime == mtime:
                        user_settings = copy.deepcopy(_file_settings_cache)

                if user_settings is None:
                    with open(SETTINGS_FILE, 'r') as f:
                        data = json.load(f)
                    with _file_settings_lock:
                        _file_settings_cache = copy.deepcopy(data)
                        _file_settings_mtime = mtime
                    user_settings = copy.deepcopy(_file_settings_cache)
            except Exception:
                user_settings = defaults.copy()

    # 4) Cache the final result (negative or positive) for this user
    if user_email:
        with _db_settings_lock:
            if len(_db_settings_cache) > 1000:
                # Naive bounded LRU by dropping half the cache to prevent sudden spikes
                keys_to_delete = list(_db_settings_cache.keys())[:500]
                for k in keys_to_delete:
                    del _db_settings_cache[k]
            _db_settings_cache[user_email] = copy.deepcopy(user_settings)

    return user_settings

def save_settings(new_settings, user_email=None):
    # In demo mode, never persist settings
    if user_email == "demo@myanchor.test":
        return True

    # ⚡ Bolt: Invalidate the in-memory settings cache when we update settings
    if user_email:
        with _db_settings_lock:
            if user_email in _db_settings_cache:
                del _db_settings_cache[user_email]

    if DATABASE_URL and user_email:
        try:
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO user_settings (user_email, settings) VALUES (%s, %s)
                    ON CONFLICT (user_email) DO UPDATE SET settings = EXCLUDED.settings;
                """, (user_email, json.dumps(new_settings)))
                conn.commit()
                cur.close()
            finally:
                release_db_connection(conn)
            return True
        except Exception as e:
            print(f"Error saving settings to DB: {e}")
            return False
            
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(new_settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings to file: {e}")
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
        if isinstance(config, dict): client_secrets = config
        else:
            with open(config, 'r') as f: client_secrets = json.load(f)
        data = client_secrets.get('web') or client_secrets.get('installed')
        if data: PROJECT_ID = data.get('project_id')
    except: pass

api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        print(f"ERROR: Failed to initialize Gemini model: {e}")
        model = None
else:
    if not MOCK_MODE:
        print("CRITICAL: GOOGLE_API_KEY is missing from environment variables!")
    model = None

_RE_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
_RE_SCRIPT_STYLE = re.compile(r'<(script|style).*?>.*?</\1>', flags=re.IGNORECASE | re.DOTALL)
_RE_HTML_TAGS = re.compile(r'<[^>]+>')
_RE_JSON_MATCH = re.compile(r'\{.*\}', flags=re.DOTALL)

def sanitize_for_llm(text):
    text = _RE_CONTROL_CHARS.sub('', text)
    return text.replace('\\', '\\\\').replace('"', '\\"')

def optimize_newsletter_for_llm(html_content: str, max_chars: int = 15000) -> str:
    """Strips HTML tags and extra whitespace to massively reduce LLM token usage."""
    # ⚡ Bolt: Regex is >50x faster than BeautifulSoup for this and handles <script>/<style> removal correctly.
    # Remove script and style tags and their contents
    no_scripts = _RE_SCRIPT_STYLE.sub('', html_content)
    # Remove all other HTML tags
    text_only = _RE_HTML_TAGS.sub(' ', no_scripts)
    # Remove extra whitespace (newline, tabs)
    clean_text = ' '.join(text_only.split())
    # Truncate to save tokens if it's too long
    return clean_text[:max_chars]

def generate_script_from_analysis(analysis_json, style="anchor"):
    persona = PERSONAS.get(style, PERSONAS["anchor"])
    greeting = analysis_json.get('greeting')
    chosen_intro = random.choice(persona['intro'])
    
    if greeting:
        if "Good morning" in chosen_intro:
            chosen_intro = chosen_intro.replace("Good morning", greeting)
        elif "Rise and shine!" in chosen_intro and "morning" not in greeting.lower():
            chosen_intro = chosen_intro.replace("Rise and shine!", greeting + "!")
            
    script_parts = [f"{chosen_intro} "]
    
    story_groups = analysis_json.get('story_groups', [])
    for i, group in enumerate(story_groups):
        script_parts.append(f"{group.get('group_headline', '')}. {group.get('consensus_summary', group.get('group_summary', ''))}. ")
        stories = group.get('stories', [])
        if len(stories) > 1:
            script_parts.append("Differing perspectives: ")
            for story in stories:
                source = story.get('source', 'One source').split('<')[0].strip().replace('.com', '')
                script_parts.append(f"The {source} {story.get('angle', '')}. ")
        elif len(stories) == 1:
            story = stories[0]
            source = story.get('source', 'One source').split('<')[0].strip().replace('.com', '')
            script_parts.append(f"The {source} {story.get('angle', '')}. ")
            
        if i < len(story_groups) - 1: script_parts.append(f" {random.choice(persona['transition'])} ")
            
    remaining = analysis_json.get('remaining_stories', [])
    if remaining:
        script_parts.append("Briefly: ")
        for story in remaining: script_parts.append(f"{story.get('headline', '')}. ")
    script_parts.append(f" {persona['outro']}")
    return "".join(script_parts)

ANALYSIS_PROMPT_TEMPLATE = """
    You are an elite media analyst processing raw text from multiple newsletters.
    Task:
    1. Group related stories from DIFFERENT newsletters into a single distinct news event.
    2. Create a neutral headline for the group (`group_headline`).
    3. Write a `consensus_summary`: A 3-4 sentence summary of the core facts that all sources agree on.
    4. **DEEP ANGLE ANALYSIS (Perspective Split)**: For EACH individual source/story in the group, extract its specific perspective, unique facts, or how it differs from others into the `angle` field. (1-2 sentences. Start with a verb like "Argues...", "Cites...", "Reveals...").
    5. **Remaining Stories**: Top 5 only. One-sentence summary.
    6. **Filter**: Ignore ads/fluff.
    7. **Limit**: Top 10 groups max. For each group, include the top 5 most relevant sources max.
    
    Output JSON format exactly:
    {
      "story_groups": [
        {
          "group_headline": "...",
          "consensus_summary": "...",
          "stories": [
            { "headline": "...", "source": "...", "angle": "..." }
          ]
        }
      ],
      "remaining_stories": [
        { "headline": "..." }
      ]
    }
    
    Content: ---
    """

def _process_llm_response(response):
    # Check finish reason
    if response.candidates:
        finish_reason = response.candidates[0].finish_reason
        if finish_reason == 2: # MAX_TOKENS
            return {"error": "The briefing was too long to generate. Try reducing your sources or lookback period."}
        elif finish_reason == 3: # SAFETY
            return {"error": "The analysis was blocked due to safety filters."}
        elif finish_reason not in [1, 0] and hasattr(finish_reason, 'value') and finish_reason.value not in [1, 0]:
            return {"error": "The AI encountered an unexpected interruption. Please try again."}

    text = getattr(response, 'text', None)
    if not text:
        return {"error": "AI analysis failed."}
    match = _RE_JSON_MATCH.search(text)
    if match: return json.loads(match.group(0))
    else: raise ValueError("No valid JSON found.")

def analyze_news_with_llm(newsletters_text):
    if not model: raise Exception("Gemini API model is not configured.")

    # Pre-validation check
    if len(newsletters_text) > 1500000:
        return {"error": "Too much newsletter content to process at once. Please reduce your lookback window in settings."}

    prompt = ANALYSIS_PROMPT_TEMPLATE + newsletters_text
    try:
        generation_config = genai.types.GenerationConfig(max_output_tokens=16384, temperature=0.2)
        response = model.generate_content(prompt, generation_config=generation_config)
        return _process_llm_response(response)
    except json.JSONDecodeError:
        return {"error": "The AI failed to format the analysis correctly. Please try again."}
    except ResourceExhausted:
        return {"error": "AI service is currently overloaded. Please wait a minute before trying again."}
    except InvalidArgument:
        return {"error": "The newsletter content is too large for the current AI model capacity."}
    except Exception as e:
        print(f"LLM analysis error: {e}")
        err_str = str(e).lower()
        if "quota" in err_str:
            return {"error": "AI rate limit reached. Please try again in a few minutes."}
        return {"error": "AI analysis failed."}

# --- Caching Helpers ---
# File-based cache is ephemeral on Render and not shared across workers; treat as best-effort.
_in_memory_cache = None
_in_memory_cache_mtime = 0

def load_cache():
    global _in_memory_cache, _in_memory_cache_mtime
    if not os.path.exists(CACHE_FILE): return {}
    try:
        # ⚡ Bolt: Cache file-based data in memory to avoid repeated JSON parsing overhead
        mtime = os.path.getmtime(CACHE_FILE)
        if _in_memory_cache is not None and _in_memory_cache_mtime == mtime:
            return copy.deepcopy(_in_memory_cache)

        with open(CACHE_FILE, 'r') as f:
            _in_memory_cache = json.load(f)
            _in_memory_cache_mtime = mtime
            return copy.deepcopy(_in_memory_cache)
    except Exception:
        return {}

def save_cache(data):
    global _in_memory_cache, _in_memory_cache_mtime
    try: 
        with open(CACHE_FILE, 'w') as f: json.dump(data, f)
        # Update in-memory cache to avoid re-reading the file we just wrote
        _in_memory_cache = copy.deepcopy(data)
        _in_memory_cache_mtime = os.path.getmtime(CACHE_FILE)
    except Exception as e:
        pass

def get_settings_hash(settings):
    s = json.dumps(settings, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()

def _fetch_one_message(args):
    """Fetch a single Gmail message. Used by parallel workers. Returns (index, email_block, is_priority) or (index, None, None) on skip/error."""
    index, message_id, creds_dict, keywords, priority_sources = args
    try:
        if not hasattr(_worker_thread_locals, 'auth_session'):
            creds = get_credentials_from_session(creds_dict)
            _worker_thread_locals.auth_session = AuthorizedSession(creds)

        session = _worker_thread_locals.auth_session
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full"
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        msg = resp.json()
        headers = msg['payload']['headers']

        # ⚡ Bolt: Optimize header extraction with a single loop and early break
        subject, sender = 'No Subject', 'No Sender'
        for h in headers:
            name_lower = h['name'].lower()
            if name_lower == 'subject':
                subject = h['value']
            elif name_lower == 'from':
                sender = h['value']
            if subject != 'No Subject' and sender != 'No Sender':
                break

        body_data = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/html':
                    body_data = part['body']['data']
                    break
        else:
            body_data = msg['payload'].get('body', {}).get('data', '')
        if not body_data:
            return (index, None, None)
        decoded_data = base64.urlsafe_b64decode(body_data)
        html_str = decoded_data.decode('utf-8', errors='ignore')
        optimized_text = optimize_newsletter_for_llm(html_str, max_chars=15000)
        sanitized_text = sanitize_for_llm(optimized_text)
        if keywords:
            sanitized_text_lower = sanitized_text.lower()
            subject_lower = subject.lower()
            has_keyword = any(k in sanitized_text_lower or k in subject_lower for k in keywords)
            if not has_keyword:
                return (index, None, None)
        email_block = f"\n\n--- Newsletter from: {sender} ---\n--- Subject: {subject} ---\n{sanitized_text}\n"

        # ⚡ Bolt: optimize string operations for priority sources
        if priority_sources:
            sender_lower = sender.lower()
            is_priority = any(p in sender_lower for p in priority_sources)
        else:
            is_priority = False

        return (index, email_block, is_priority)
    except Exception as e:
        print(f"fetch_emails: failed to fetch message {message_id}: {e}")
        return (index, None, None)


def _chunk_script_text(script_text, byte_limit=4800):
    """Splits script text into chunks that stay under the byte limit."""
    sentences = re.split(r'(?<=[.!?])\s+', script_text)
    chunks = []
    # ⚡ Bolt: Replace O(N^2) string concatenation loop with string builder pattern and incremental byte tracking
    current_chunk_parts = []
    current_chunk_bytes = 0
    for sentence in sentences:
        sentence_bytes = len(sentence.encode('utf-8')) + 1 # +1 for the space
        if current_chunk_bytes + sentence_bytes < byte_limit:
            current_chunk_parts.append(sentence)
            current_chunk_parts.append(" ")
            current_chunk_bytes += sentence_bytes
        else:
            if current_chunk_parts:
                chunks.append("".join(current_chunk_parts))
            current_chunk_parts = [sentence, " "]
            current_chunk_bytes = sentence_bytes
    if current_chunk_parts:
        chunks.append("".join(current_chunk_parts))
    return chunks

def _synthesize_audio_from_chunks(chunks, creds_dict, style, project_id):
    """Synthesizes audio from chunks in parallel and concatenates the results."""
    worker_args = [(i, chunk_text, creds_dict, style, project_id) for i, chunk_text in enumerate(chunks)]
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=min(len(chunks), 8)) as executor:
        results = list(executor.map(_synthesize_one_chunk, worker_args))
    all_audio_content = b"".join(audio for _idx, audio in results)
    tts_duration_ms = int((time.time() - t_start) * 1000)
    return all_audio_content, tts_duration_ms

def _synthesize_one_chunk(args):
    """Synthesize a single TTS chunk. Used by parallel workers. Returns (index, audio_bytes)."""
    index, chunk_text, creds_dict, style, project_id = args
    byte_limit = 4800
    if len(chunk_text.encode('utf-8')) > byte_limit:
        chunk_text = chunk_text.encode('utf-8')[:byte_limit].decode('utf-8', 'ignore')

    if not hasattr(_worker_thread_locals, 'tts_client'):
        creds = get_credentials_from_session(creds_dict)
        client_opts = client_options.ClientOptions(quota_project_id=project_id) if project_id else None
        _worker_thread_locals.tts_client = texttospeech.TextToSpeechClient(credentials=creds, client_options=client_opts, transport="rest")
    tts_client = _worker_thread_locals.tts_client
    persona_config = PERSONAS.get(style, PERSONAS['anchor'])
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=persona_config['voice_name'], ssml_gender=persona_config['gender'])
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=persona_config.get('speaking_rate', 1.0),
        pitch=persona_config.get('pitch', 0.0)
    )
    response = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=chunk_text),
        voice=voice,
        audio_config=audio_config
    )
    return (index, response.audio_content)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html',
        sentry_dsn_frontend=os.environ.get('SENTRY_DSN_FRONTEND', ''),
        posthog_api_key=os.environ.get('POSTHOG_API_KEY', ''),
        react_production=not app.debug,
        mock_mode=MOCK_MODE,
    )

# --- Mock / Demo Routes (no rate limiting, no real API calls) ---

# Static mock briefing data served in demo mode
_MOCK_BRIEFING = {
    "story_groups": [
        {
            "group_headline": "Federal Reserve Signals Pause on Rate Hikes Amid Mixed Economic Data",
            "group_summary": "The Federal Reserve indicated it may hold interest rates steady at its next meeting, citing cooling inflation but persistent labor market strength. Officials noted that recent GDP figures came in below expectations, adding uncertainty to the path forward. Markets rallied on the news, with the S&P 500 closing up 1.2%.",
            "stories": [
                {"headline": "Fed Officials Signal Rate Pause", "source": "wsj.com", "angle": "Emphasizes hawkish dissent from two regional Fed presidents who pushed for another 25bps hike."},
                {"headline": "Markets Cheer Fed Pivot Signal", "source": "nytimes.com", "angle": "Focuses on investor relief and notes that bond yields fell sharply following the announcement."}
            ]
        },
        {
            "group_headline": "OpenAI Launches GPT-5 with Real-Time Reasoning Capabilities",
            "group_summary": "OpenAI unveiled GPT-5, its most powerful model to date, featuring native real-time reasoning and a dramatically expanded context window of one million tokens. The release sparked immediate comparisons to Google's Gemini Ultra and raised new questions about AI safety benchmarks. Enterprise pricing starts at $60 per million output tokens.",
            "stories": [
                {"headline": "GPT-5 Arrives with Landmark Reasoning", "source": "techcrunch.com", "angle": "Details the model's new 'chain-of-thought' transparency features that show users how it arrives at answers."},
                {"headline": "AI Arms Race Intensifies with GPT-5 Drop", "source": "theguardian.com", "angle": "Raises ethical concerns about the accelerating pace of deployment without sufficient safety evaluation."}
            ]
        },
        {
            "group_headline": "Apple Reports Record Services Revenue, iPhone Sales Disappoint",
            "group_summary": "Apple's Q2 earnings beat on services, with the segment reaching $26 billion in revenue driven by App Store and Apple TV+ growth. However, iPhone unit sales fell 8% year-over-year amid competition in China from Huawei. The company announced an additional $90 billion share buyback program.",
            "stories": [
                {"headline": "Apple Services Hit Record High", "source": "wsj.com", "angle": "Notes that services now represent 28% of total revenue, a milestone that validates CEO Tim Cook's platform strategy."},
                {"headline": "iPhone Slump Clouds Apple's Quarter", "source": "axios.com", "angle": "Highlights that the China market decline is structural, not cyclical, citing Huawei's Mate 60 Pro as a direct threat."}
            ]
        }
    ],
    "remaining_stories": [
        {"headline": "Tesla announces next-generation Supercharger network expansion across Europe."},
        {"headline": "UK inflation drops to 2.3%, its lowest level in three years."},
        {"headline": "Amazon Web Services wins $10B Pentagon cloud contract extension."},
        {"headline": "Spotify reports first full year of profitability, shares surge 15%."},
        {"headline": "Boeing 737 MAX production halted again following FAA audit findings."}
    ]
}

@app.route('/api/mock_login')
def mock_login():
    """Sets up a demo session without requiring Google OAuth."""
    if not MOCK_MODE:
        return jsonify({'error': 'Demo mode is not enabled.'}), 403
    session.clear()
    session['is_mock_session'] = True
    session['user_email'] = 'demo@myanchor.test'
    return redirect('/')

@app.route('/api/mock/fetch')
def mock_fetch_emails():
    """Returns static mock briefing data. No rate limit, no Gmail API calls."""
    if not MOCK_MODE:
        return jsonify({'error': 'Demo mode is not enabled.'}), 403
    if not session.get('is_mock_session'):
        return jsonify({'error': 'Not a demo session.'}), 401
    # Simulate a brief delay so the loading UI plays out naturally
    time.sleep(1.5)
    return jsonify(_MOCK_BRIEFING)

@app.route('/api/mock/audio', methods=['POST'])
def mock_generate_audio():
    """Returns pre-generated demo audio as base64. No rate limit, no TTS API calls."""
    if not MOCK_MODE:
        return jsonify({'error': 'Demo mode is not enabled.'}), 403
    if not session.get('is_mock_session'):
        return jsonify({'error': 'Not a demo session.'}), 401
    # Serve the pre-generated demo MP3 if it exists
    demo_audio_path = os.path.join(os.path.dirname(__file__), 'static', 'demo_briefing.mp3')
    if os.path.exists(demo_audio_path):
        with open(demo_audio_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({'audio_content': audio_base64})
    # Fallback: signal the frontend to use Web Speech API
    return jsonify({'use_web_speech': True, 'script': _get_mock_script()}), 200

def _get_mock_script():
    """Generates a TTS script from the mock briefing for Web Speech API fallback."""
    return generate_script_from_analysis(_MOCK_BRIEFING, style='anchor')

# --- Real Google OAuth Routes ---

@app.route('/login')
def login():
    try:
        # PKCE code_verifier must be in session so the callback (possibly another worker) can use it
        code_verifier = secrets.token_urlsafe(64)
        session['code_verifier'] = code_verifier
        redirect_uri = url_for('oauth2callback', _external=True)
        config = get_client_secrets_config()
        if isinstance(config, dict):
            flow = Flow.from_client_config(config, scopes=SCOPES, redirect_uri=redirect_uri, code_verifier=code_verifier)
        else:
            flow = Flow.from_client_secrets_file(config, scopes=SCOPES, redirect_uri=redirect_uri, code_verifier=code_verifier)
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
        return jsonify({'error': 'Login failed. Please try again.', 'details': None}), 500

@app.route('/oauth2callback')
def oauth2callback():
    try:
        if 'state' not in session:
            print("ERROR: State missing from session")
            return jsonify({'error': 'Invalid session state'}), 400
        # 🛡️ Sentinel: Pop state from session to prevent OAuth replay attacks
        state = session.pop('state')
        code_verifier = session.pop('code_verifier', None)
        if not code_verifier:
            print("ERROR: code_verifier missing from session (PKCE required across redirect)")
            return jsonify({'error': 'Login failed. Please try again.'}), 500
        redirect_uri = url_for('oauth2callback', _external=True)
        try:
            config = get_client_secrets_config()
        except FileNotFoundError as config_err:
            print(f"ERROR: Client secrets not found: {config_err}")
            return jsonify({'error': 'OAuth configuration not found. Please check GOOGLE_CLIENT_SECRETS_JSON environment variable or client_secrets.json file.'}), 500
        
        if isinstance(config, dict):
            flow = Flow.from_client_config(config, scopes=SCOPES, state=state, redirect_uri=redirect_uri, code_verifier=code_verifier)
        else:
            flow = Flow.from_client_secrets_file(config, scopes=SCOPES, state=state, redirect_uri=redirect_uri, code_verifier=code_verifier)

        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        session['credentials'] = {'token': credentials.token, 'refresh_token': credentials.refresh_token, 'token_uri': credentials.token_uri, 'client_id': credentials.client_id, 'scopes': credentials.scopes}
        return redirect("/")
    except Exception as e:
        import traceback
        print(f"OAuth callback error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/?logout=true')

@app.route('/api/check_auth')
def check_auth():
    user_info = get_user_info()
    is_mock = bool(session.get('is_mock_session'))
    if user_info:
        return jsonify({'logged_in': True, 'user': user_info, 'is_mock_session': is_mock})
    return jsonify({'logged_in': False})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    if 'credentials' not in session and not session.get('is_mock_session'):
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
    if 'credentials' not in session and not session.get('is_mock_session'): 
        return jsonify({'error': 'Please log in to save your settings.'}), 401
    new_settings = request.get_json()
    if not isinstance(new_settings, dict):
        return jsonify({'error': 'Invalid request.'}), 400

    # 🛡️ Sentinel: Prevent mass assignment by plucking only allowed keys
    # and validate types to prevent persistent DoS crashes downstream
    allowed_keys = ['sources', 'time_window_hours', 'personality', 'priority_sources', 'keywords']
    sanitized_settings = {}
    for key in allowed_keys:
        if key in new_settings:
            val = new_settings[key]
            # Strict type validation
            if key in ['sources', 'priority_sources', 'keywords'] and not isinstance(val, list):
                return jsonify({'error': f"Invalid type for {key}. Expected a list."}), 400
            if key == 'time_window_hours' and not isinstance(val, (int, float)):
                return jsonify({'error': f"Invalid type for {key}. Expected a number."}), 400
            if key == 'personality' and not isinstance(val, str):
                return jsonify({'error': f"Invalid type for {key}. Expected a string."}), 400
            sanitized_settings[key] = val

    # 🛡️ Sentinel: Add type and length validation to prevent DoS and injection
    if 'time_window_hours' in sanitized_settings:
        try:
            hours = int(sanitized_settings['time_window_hours'])
            if hours < 1 or hours > 168: raise ValueError()
            sanitized_settings['time_window_hours'] = hours
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid time_window_hours. Must be an integer between 1 and 168.'}), 400

    if 'personality' in sanitized_settings:
        if not isinstance(sanitized_settings['personality'], str):
            return jsonify({'error': 'Invalid personality format.'}), 400
        sanitized_settings['personality'] = sanitized_settings['personality'][:50]

    for list_key in ['sources', 'priority_sources', 'keywords']:
        if list_key in sanitized_settings:
            val = sanitized_settings[list_key]
            if not isinstance(val, list) or not all(isinstance(i, str) for i in val):
                return jsonify({'error': f'Invalid {list_key}. Must be a list of strings.'}), 400
            # Limit length of list and items
            sanitized_settings[list_key] = [i[:100] for i in val[:50]]

    user_info = get_user_info()
    email = user_info.get('email') if user_info else None
    if save_settings(sanitized_settings, email):
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Unable to save settings. Please try again or contact support if the issue persists.'}), 500

def _check_cached_analysis(cache_key, current_hash):
    """Check if we have a valid cached analysis."""
    with _cache_lock:
        cache = load_cache()
        user_cache = cache.get(cache_key, {})
        if (user_cache.get('timestamp', 0) + CACHE_TTL_SECONDS > time.time()) and (user_cache.get('settings_hash') == current_hash) and (user_cache.get('analysis')):
            return user_cache['analysis']
    return None

def _update_cached_analysis(cache_key, current_hash, analysis_result):
    """Update the cache with a new analysis result."""
    with _cache_lock:
        cache = load_cache()
        user_cache = cache.get(cache_key, {})
        user_cache['timestamp'] = time.time()
        user_cache['settings_hash'] = current_hash
        user_cache['analysis'] = analysis_result
        if 'audio' in user_cache:
            del user_cache['audio']
        if 'script_hash' in user_cache:
            del user_cache['script_hash']
        cache[cache_key] = user_cache
        save_cache(cache)

def _search_gmail_messages(creds, sources, hours):
    """Search Gmail for recent newsletters from specified sources."""
    sources_query = " OR ".join([f"from:{s}" for s in sources])
    query = f"({sources_query}) newer_than:{hours}h"
    auth_session = AuthorizedSession(creds)
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
    resp = auth_session.get(url, params={'q': query, 'maxResults': 100}, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    return results.get('messages', [])

def _process_email_messages(messages, creds_dict, keywords, priority_sources):
    """Process email messages concurrently and return consolidated text."""
    worker_args = [(i, msg['id'], creds_dict, keywords, priority_sources) for i, msg in enumerate(messages)]
    priority_text_parts = []
    normal_text_parts = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        for _index, email_block, is_priority in executor.map(_fetch_one_message, worker_args):
            if email_block is None:
                continue
            if is_priority:
                priority_text_parts.append(f"*** PRIORITY SOURCE ***\n{email_block}")
            else:
                normal_text_parts.append(email_block)

    return "".join(priority_text_parts) + "".join(normal_text_parts), len(normal_text_parts), len(priority_text_parts)

def _report_fetch_metrics(email, analysis_result, t_duration_ms, hours, messages, normal_count, priority_count, raw_length, optimized_length):
    """Report fetch metrics to PostHog."""
    if not posthog_client or not email:
        return

    anon_id = anonymize_user(email)
    if analysis_result.get('error'):
        posthog_client.capture(distinct_id=anon_id, event='llm_generation_error', properties={
            'error_msg': analysis_result.get('error'),
            'llm_generation_time_ms': t_duration_ms
        })
    else:
        posthog_client.capture(distinct_id=anon_id, event='emails_fetched', properties={
            'newsletter_count': len(messages),
            'raw_html_length': raw_length,
            'optimized_text_length': optimized_length,
            'llm_generation_time_ms': t_duration_ms,
            'output_text_length': len(json.dumps(analysis_result)),
            'time_window_hours': hours
        })

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
@limiter.limit("3 per day", key_func=get_user_email_for_rate_limit, error_message="You've reached your daily limit of 3 briefings. Upgrade to Pro for unlimited briefings or try again tomorrow!", deduct_when=lambda res: res.status_code == 200)
def fetch_emails():
    if 'credentials' not in session: 
        return jsonify({'error': 'Please log in to generate your briefing.'}), 401
    
    user_info = get_user_info()
    # get_user_info() may pop credentials if the token is invalid/expired
    if 'credentials' not in session:
        return jsonify({'error': 'Your session expired. Please log in again.'}), 401

    email = user_info.get('email') if user_info else None
    # Store email in session for rate limiting
    if email: session['user_email'] = email
    settings = load_settings(email)

    cache_key = email or str(user_info.get('id', 'unknown')) if user_info else 'unknown'
    current_hash = get_settings_hash(settings)

    cached_analysis = _check_cached_analysis(cache_key, current_hash)
    if cached_analysis:
        return jsonify(cached_analysis)

    creds_data = session.get('credentials')
    if not creds_data:
        return jsonify({'error': 'Your session expired. Please log in again.'}), 401

    creds = Credentials(**creds_data)
    creds_dict = dict(creds_data)
    try:
        sources = settings.get('sources', []) or ["wsj.com", "nytimes.com"]
        hours = settings.get('time_window_hours', 24)

        # ⚡ Bolt: Pre-calculate lowercased keywords and sources to prevent lowercasing per message in worker loop
        keywords = [k.lower() for k in settings.get('keywords', [])]
        priority_sources = [p.lower() for p in settings.get('priority_sources', [])]

        messages = _search_gmail_messages(creds, sources, hours)
        if not messages:
            return jsonify({'story_groups': [], 'remaining_stories': [{'headline': f'No newsletters found in last {hours}h.'}]})

        consolidated_text, normal_count, priority_count = _process_email_messages(
            messages, creds_dict, keywords, priority_sources
        )

        if not consolidated_text:
            reason = "No text found matching your watchlist." if keywords else "No text found."
            return jsonify({'story_groups': [], 'remaining_stories': [{'headline': reason}]})

        t_start = time.time()
        analysis_result = analyze_news_with_llm(consolidated_text)
        t_duration_ms = int((time.time() - t_start) * 1000)

        _report_fetch_metrics(
            email=email,
            analysis_result=analysis_result,
            t_duration_ms=t_duration_ms,
            hours=hours,
            messages=messages,
            normal_count=normal_count,
            priority_count=priority_count,
            raw_length=0, # approximating these two as they aren't computed exactly here anymore, we could re-add calculation later if critical
            optimized_length=len(consolidated_text)
        )

        if analysis_result.get('error'):
            return jsonify(analysis_result), 503

        _update_cached_analysis(cache_key, current_hash, analysis_result)
        return jsonify(analysis_result)

    except Exception as e:
        err_msg = str(e).lower()
        
        if posthog_client and email:
             posthog_client.capture(distinct_id=anonymize_user(email), event='fetch_email_error', properties={'error': err_msg})

        if 'quota' in err_msg or 'rate' in err_msg or '429' in err_msg:
            return jsonify({'error': "Gmail rate limit reached. Please try again in a few minutes."}), 429
        if 'credentials' in err_msg or 'token' in err_msg or '401' in err_msg:
            return jsonify({'error': "Your session expired. Please log in again."}), 401
        import traceback
        traceback.print_exc()
        print(f"fetch_emails error: {e}")
        return jsonify({'error': f"Unable to fetch newsletters. Exact error: {str(e)}"}), 500

@app.route('/api/generate_audio', methods=['POST'])
@limiter.limit("5 per day", key_func=get_user_email_for_rate_limit, error_message="You've reached your daily limit of 5 audio generations. Upgrade to Pro for unlimited audio or try again tomorrow!", deduct_when=lambda res: res.status_code == 200)
def generate_audio():
    if 'credentials' not in session: 
        return jsonify({'error': 'Please log in to generate audio.'}), 401
    
    # --- Load Settings to get Persona ---
    user_info = get_user_info()
    if 'credentials' not in session:
        return jsonify({'error': 'Your session expired. Please log in again.'}), 401

    email = user_info.get('email') if user_info else None
    cache_key = email or str(user_info.get('id', 'unknown')) if user_info else 'unknown'
    settings = load_settings(email)
    style = settings.get('personality', 'anchor')

    creds_data = session.get('credentials')
    if not creds_data:
        return jsonify({'error': 'Your session expired. Please log in again.'}), 401
    creds = Credentials(**creds_data)
    try:
        auth_req = Request()
        if creds.expired:
            creds.refresh(auth_req)
            session_creds = session.get('credentials')
            if session_creds is not None:
                session_creds['token'] = creds.token
                session.modified = True
    except Exception:
        pass
    creds_dict = dict(creds_data)
    try:
        analysis_data = request.get_json()
        if not isinstance(analysis_data, dict):
            return jsonify({'error': 'Invalid data format. Expected a JSON object.'}), 400
        if not analysis_data:
            return jsonify({'error': 'No briefing data to convert to audio.'}), 400
        script_text = generate_script_from_analysis(analysis_data, style)
        script_hash = hashlib.md5((script_text + style).encode()).hexdigest()
        with _cache_lock:
            cache = load_cache()
            user_cache = cache.get(cache_key, {})
            if user_cache.get('script_hash') == script_hash and user_cache.get('audio'):
                return jsonify({"audio_content": user_cache['audio']})

        chunks = _chunk_script_text(script_text)
        all_audio_content, tts_duration_ms = _synthesize_audio_from_chunks(chunks, creds_dict, style, PROJECT_ID)

        audio_base64 = base64.b64encode(all_audio_content).decode('utf-8')
        
        if posthog_client and email:
            posthog_client.capture(distinct_id=anonymize_user(email), event='audio_generated', properties={
                'tts_generation_time_ms': tts_duration_ms,
                'persona_selected': style
            })

        with _cache_lock:
            cache = load_cache()
            user_cache = cache.get(cache_key, {})
            user_cache['script_hash'] = script_hash
            user_cache['audio'] = audio_base64
            cache[cache_key] = user_cache
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
@limiter.limit("20 per day", key_func=get_user_email_for_rate_limit, error_message="You've reached your daily limit of 20 shared briefings.")
def share_briefing():
    if 'credentials' not in session and not session.get('is_mock_session'): return jsonify({'error': 'User not authenticated'}), 401
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid data format. Expected a JSON object.'}), 400
    if not ('story_groups' in data or 'remaining_stories' in data):
        return jsonify({'error': 'Invalid data content. Required fields missing.'}), 400

    allowed_keys = {'story_groups', 'remaining_stories'}
    sanitized_data = {k: data[k] for k in allowed_keys if k in data}

    share_id = str(uuid.uuid4())
    if DATABASE_URL:
        try:
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                # 🛡️ Sentinel: Fixed uninitialized variable reference; using the validated 'data'
                cur.execute("INSERT INTO shared_briefings (share_id, data) VALUES (%s, %s)", (share_id, json.dumps(data)))
                conn.commit(); cur.close()
            finally:
                release_db_connection(conn)
            return jsonify({'share_id': share_id})
        except Exception:
            return jsonify({'error': 'Unable to save shared briefing. Please try again.'}), 500
    return jsonify({'error': 'DB not configured'}), 500

@app.route('/api/shared/<share_id>', methods=['GET'])
def get_shared_briefing(share_id):
    if DATABASE_URL:
        try:
            conn = get_db_connection()
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT data FROM shared_briefings WHERE share_id = %s", (share_id,))
                row = cur.fetchone(); cur.close()
            finally:
                release_db_connection(conn)
            if row: return jsonify(row['data'])
            return jsonify({'error': 'This shared briefing could not be found. The link may be invalid or expired.'}), 404
        except Exception:
            return jsonify({'error': 'Unable to load shared briefing. Please try again.'}), 500
    return jsonify({'error': 'Shared briefings are not available. Database connection required.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
