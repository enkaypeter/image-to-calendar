import os

class Config:
    FLORA_API_URL = os.getenv("FLORA_API_BASE_URL")
    FLORA_API_KEY = os.getenv("FLORA_API_KEY")
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
