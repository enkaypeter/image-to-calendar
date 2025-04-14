from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from flask import current_app

def build_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        current_app.config["SERVICE_ACCOUNT_FILE"],
        scopes=current_app.config["GOOGLE_CALENDAR_SCOPES"]
    )
    return build("calendar", "v3", credentials=credentials)

def create_calendar_event(date_info: dict):
    calendar_id = current_app.config["GOOGLE_CALENDAR_ID"]
    timezone = current_app.config["TIMEZONE"]

    year = int(date_info["year"])
    month = int(date_info["month"])
    day = int(date_info["day"])
    hour, minute = map(int, date_info["time"].split(":"))

    # print(f"Creating event for {year}-{month}-{day} {hour}:{minute} in timezone {timezone}...")
    start_dt = datetime(year, month, day, hour, minute)
    end_dt = start_dt + timedelta(hours=1)

    event = {
        "summary": "Event from Flora Image",
        "description": "Automatically created event from photo.",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone}
    }

    service = build_calendar_service()
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    
    print("Event created:", created_event)
    return created_event.get("htmlLink")
