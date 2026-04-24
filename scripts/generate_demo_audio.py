"""
scripts/generate_demo_audio.py
--------------------------------
One-time script to generate the demo briefing MP3 for MOCK_MODE.
This hits the Google Cloud Text-to-Speech API exactly ONCE and saves
the result to static/demo_briefing.mp3.

Run from the project root:
    python scripts/generate_demo_audio.py

Prerequisites:
  - pip install google-cloud-texttospeech python-dotenv
  - GOOGLE_CLOUD_PROJECT and valid credentials in your .env (same as prod)
  - client_secrets.json must exist OR GOOGLE_CLIENT_SECRETS_JSON must be set.

After running, the file is cached permanently. Re-run only if you update
the mock briefing data in main.py.
"""
import os
import sys
import json
import base64
import random

# Fix UnicodeEncodeError for emojis on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Allow running from project root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from google.cloud import texttospeech
from google.oauth2 import service_account

# --- Inline the mock data so this script is self-contained ---
MOCK_BRIEFING = {
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
            "group_summary": "OpenAI unveiled GPT-5, its most powerful model to date, featuring native real-time reasoning and a dramatically expanded context window of one million tokens. Enterprise pricing starts at $60 per million output tokens.",
            "stories": [
                {"headline": "GPT-5 Arrives with Landmark Reasoning", "source": "techcrunch.com", "angle": "Details the model's new chain-of-thought transparency features."},
                {"headline": "AI Arms Race Intensifies with GPT-5 Drop", "source": "theguardian.com", "angle": "Raises ethical concerns about the accelerating pace of deployment."}
            ]
        },
        {
            "group_headline": "Apple Reports Record Services Revenue, iPhone Sales Disappoint",
            "group_summary": "Apple's Q2 earnings beat on services, with the segment reaching $26 billion in revenue driven by App Store and Apple TV Plus growth. However, iPhone unit sales fell 8% year-over-year amid competition in China from Huawei.",
            "stories": [
                {"headline": "Apple Services Hit Record High", "source": "wsj.com", "angle": "Notes that services now represent 28% of total revenue."},
                {"headline": "iPhone Slump Clouds Apple's Quarter", "source": "axios.com", "angle": "Highlights that the China market decline is structural, not cyclical."}
            ]
        }
    ],
    "remaining_stories": [
        {"headline": "Tesla announces next-generation Supercharger network expansion across Europe."},
        {"headline": "UK inflation drops to 2.3%, its lowest level in three years."},
        {"headline": "Amazon Web Services wins $10 billion Pentagon cloud contract extension."},
        {"headline": "Spotify reports first full year of profitability, shares surge 15%."},
        {"headline": "Boeing 737 MAX production halted again following FAA audit findings."}
    ]
}

PERSONAS = {
    "anchor": {
        "voice_name": "en-US-Journey-D",
        "gender": texttospeech.SsmlVoiceGender.MALE,
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "intro": ["Good morning. Here is your daily briefing.", "This is My Anchor. Let's look at the news."],
        "transition": ["Next up...", "Moving on...", "In other news...", "Turning to..."],
        "outro": "That concludes your briefing. Have a good day."
    }
}

def generate_script(analysis_json, style="anchor"):
    persona = PERSONAS.get(style, PERSONAS["anchor"])
    script_parts = [f"{random.choice(persona['intro'])} "]
    story_groups = analysis_json.get('story_groups', [])
    for i, group in enumerate(story_groups):
        script_parts.append(f"{group.get('group_headline', '')}. {group.get('group_summary', '')}. ")
        stories = group.get('stories', [])
        if len(stories) > 1:
            script_parts.append("Perspectives: ")
            for story in stories:
                source = story.get('source', 'One source').split('<')[0].strip().replace('.com', '')
                script_parts.append(f"The {source} {story.get('angle', '')}. ")
        if i < len(story_groups) - 1:
            script_parts.append(f" {random.choice(persona['transition'])} ")
    remaining = analysis_json.get('remaining_stories', [])
    if remaining:
        script_parts.append("Briefly: ")
        for story in remaining:
            script_parts.append(f"{story.get('headline', '')}. ")
    script_parts.append(f" {persona['outro']}")
    return "".join(script_parts)

def main():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "demo_briefing.mp3")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("📝 Generating demo script...")
    script = generate_script(MOCK_BRIEFING, style="anchor")
    print(f"   Script length: {len(script)} characters")
    print(f"\n   Preview:\n   {script[:200]}...\n")

    print("🎙️  Calling Google Cloud Text-to-Speech API...")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    from google.api_core import client_options as co
    
    if api_key:
        # Use API Key authentication
        client_opts = co.ClientOptions(api_key=api_key)
    elif project_id:
        # Fallback to Application Default Credentials with quota project
        client_opts = co.ClientOptions(quota_project_id=project_id)
    else:
        client_opts = None

    tts_client = texttospeech.TextToSpeechClient(client_options=client_opts, transport="rest")

    # Split into chunks to avoid the 5000 byte limit
    import re
    sentences = re.split(r'(?<=[.!?])\s+', script)
    chunks, current, byte_limit = [], [], 4800
    for s in sentences:
        if sum(len(p.encode()) for p in current) + len(s.encode()) < byte_limit:
            current.append(s)
        else:
            if current: chunks.append(" ".join(current))
            current = [s]
    if current: chunks.append(" ".join(current))

    print(f"   Processing {len(chunks)} chunk(s)...")
    audio_parts = []
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}/{len(chunks)}...")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Journey-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        response = tts_client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=chunk),
            voice=voice,
            audio_config=audio_config
        )
        audio_parts.append(response.audio_content)

    combined_audio = b"".join(audio_parts)
    with open(output_path, "wb") as f:
        f.write(combined_audio)

    size_kb = len(combined_audio) / 1024
    print(f"\n✅ Demo audio saved to: {output_path}")
    print(f"   File size: {size_kb:.1f} KB")
    print(f"\n🚀 You can now run the app with MOCK_MODE=true and the audio will be served from this file.")

if __name__ == "__main__":
    main()
