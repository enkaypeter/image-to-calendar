import pytest
from unittest.mock import patch, MagicMock
from app.calendar_service import create_calendar_event
from flask import Flask
from datetime import datetime, timedelta

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config["GOOGLE_CALENDAR_ID"] = "primary"
    app.config["TIMEZONE"] = "UTC"
    with app.app_context():
        yield

@patch("app.calendar_service.build_calendar_service")
def test_create_calendar_event_success(mock_build_service, app_context):
    mock_service = MagicMock()
    mock_events = mock_service.events.return_value
    mock_insert = mock_events.insert.return_value
    mock_insert.execute.return_value = {
        "htmlLink": "https://calendar.google.com/calendar/event?eid=mock123"
    }

    mock_build_service.return_value = mock_service

    test_date_info = {'day': '11', 'month': '4', 'year': '2025', 'time': '14:00', 'day_of_week': 'Friday', 'event_description': 'Meeting with Team'}
    
    link = create_calendar_event(test_date_info)

    assert link == "https://calendar.google.com/calendar/event?eid=mock123"

    expected_start = datetime(2025, 4, 11, 14, 0).isoformat()
    expected_end = (datetime(2025, 4, 11, 14, 0) + timedelta(hours=1)).isoformat()

    mock_events.insert.assert_called_once()
    args, kwargs = mock_events.insert.call_args
    body = kwargs["body"]

    assert body["start"]["dateTime"] == expected_start
    assert body["end"]["dateTime"] == expected_end
    assert body["summary"] == "Event from Flora Image"
