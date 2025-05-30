import os

class Config:
    FLORA_API_URL = os.getenv("FLORA_API_BASE_URL")
    FLORA_API_KEY = os.getenv("FLORA_API_KEY")
    OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
    FLORA_SCHEMA_ID = {
        "EVENT_EXTRACTION_SCHEMA": os.getenv("FLORA_DATE_TIME_EXTRACTION_SCHEMA_ID"),
    }
    TIMEZONE = os.getenv("TIMEZONE", "UTC+1")
    PORT = os.getenv("PORT", 3040)
    GOOGLE_CALENDAR_SCOPES = [
        "https://www.googleapis.com/auth/calendar"
    ]
