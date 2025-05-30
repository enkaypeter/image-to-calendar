from googleapiclient.discovery import build
from datetime import datetime, timedelta
from flask import current_app
from google.oauth2.credentials import Credentials # Add this import

# ... other imports ...

def build_user_calendar_service(user_creds: Credentials): # Changed type hint
    return build("calendar", "v3", credentials=user_creds)

def create_calendar_event(date_info: dict, user_creds: Credentials):
    calendar_id = "primary"
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

    service = build_user_calendar_service(user_creds)
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    
    print("Event created:", created_event)
    return created_event.get("htmlLink")
