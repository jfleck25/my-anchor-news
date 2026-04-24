# My Anchor - Daily Briefing

My Anchor is a personalized AI-powered daily news briefing application. It securely connects to your Gmail account to scan newsletters and email subscriptions, analyzes the content using Google's Gemini LLM based on your preferred topics and sources, and generates a cohesive, podcast-style audio briefing using Google Cloud Text-to-Speech.

## Features

- **Email Integration**: Authenticate with Google to fetch newsletters and news emails.
- **AI Analysis**: Uses Google's Gemini LLM to summarize and analyze your emails, highlighting top stories, source perspectives, and in-brief items.
- **Trust-First Design**: A modern `slate/amber` UI emphasizing intelligence over noise, featuring a split-pane layout to compare differing source perspectives side-by-side.
- **Audio Generation**: Converts the text briefing into an engaging audio podcast using Google Cloud Text-to-Speech. Single-story groups are now fully supported in audio generation.
- **Personalized Configuration**: Customize your anchor personality (e.g., Professional, Conversational, Humorous), prioritize specific sources, and set up watchlists for topics.
- **Sharing**: Generate shareable links to your daily briefings.
- **Dark Mode**: Toggleable dark mode interface for comfortable reading.
- **PDF Export**: Download your briefing as a PDF document.
- **Synthetic Audio Testing**: Use `scripts/generate_demo_audio.py` to create sample audio for UI development without hitting live API endpoints.

## Prerequisites

- Python 3.9+
- PostgreSQL (optional, for persistent sharing/caching)
- Google Cloud Platform Account with the following APIs enabled:
  - Gmail API
  - Google Generative AI API (Gemini)
  - Google Cloud Text-to-Speech API
- Google OAuth 2.0 Client Credentials

## Environment Variables

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
```

Key variables to configure:
- `FLASK_SECRET_KEY`: A secure random string for session management.
- `GOOGLE_API_KEY`: Your Gemini API key.
- `GOOGLE_CLOUD_PROJECT`: Your GCP Project ID.
- `GOOGLE_CLIENT_SECRETS_JSON`: Your OAuth 2.0 client secrets in JSON format.
- `DATABASE_URL`: (Optional) PostgreSQL connection string.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jfleck25/my-anchor-news.git
   cd my-anchor-news
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python3 main.py
   ```
   Or use gunicorn for production:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 main:app
   ```

## Development

The application uses Flask for the backend and React (via CDN) with Tailwind CSS for the frontend. Tests are located in the `tests/` directory and `test_*.py` files in the root.

Run tests using pytest:
```bash
python3 -m pytest
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[ISC](https://choosealicense.com/licenses/isc/)
