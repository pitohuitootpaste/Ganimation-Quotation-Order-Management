import os

GMAIL_SENDER_EMAIL = "kjellmolas.neust@gmail.com"
RESPONSE_SERVICE_URL = os.getenv("RESPONSE_SERVICE_URL", "").rstrip("/")
RESPONSE_API_KEY = os.getenv("RESPONSE_API_KEY", "")
