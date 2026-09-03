import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

if not FIREBASE_WEB_API_KEY:
    raise RuntimeError(
        "FIREBASE_WEB_API_KEY is not set. Add it to your .env file. "
        "Find it in Firebase Console > Project Settings > General > Web API Key."
    )

if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
    raise RuntimeError(
        "GMAIL_ADDRESS / GMAIL_APP_PASSWORD is not set. Add both to your .env file. "
        "Generate an App Password at https://myaccount.google.com/apppasswords"
    )

OTP_EXPIRY_MINUTES = 3
OTP_MAX_ATTEMPTS = 5