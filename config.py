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
        print("\n[!] Geçerli bir GOOGLE_API_KEY bulunamadı.")
        print("    Ücretsiz anahtar almak için: https://aistudio.google.com/app/apikey")
        api_key = input("Google Gemini API Key'inizi girin (AIzaSy...): ").strip().strip('"').strip("'")
        if not api_key:
            print("Hata: AI PDF Analyzer'ı çalıştırmak için API Key gereklidir.")
            sys.exit(1)
        os.environ["GOOGLE_API_KEY"] = api_key
    return api_key

