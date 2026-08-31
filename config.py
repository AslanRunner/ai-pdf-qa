import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project directory
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)


PLACEHOLDER_KEYS = {
    "your_gemini_api_key_here",
    "your_api_key_here",
    "your_google_api_key_here",
    "replace_with_your_api_key",
}


def get_api_key() -> str:
    """Retrieve Google Gemini API Key from environment or prompt the user."""
    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key or api_key in PLACEHOLDER_KEYS:
        print("\n[!] A valid GOOGLE_API_KEY was not found.")
        print("    To obtain a free API key: https://aistudio.google.com/app/apikey")
        api_key = input("Enter your Google Gemini API Key (AIzaSy...): ").strip().strip('"').strip("'")
        if not api_key:
            print("Error: A Google Gemini API Key is required to run Folio PDF Intelligence.")
            sys.exit(1)
        os.environ["GOOGLE_API_KEY"] = api_key
    return api_key

