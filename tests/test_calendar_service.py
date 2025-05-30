import pytest
from unittest.mock import patch, MagicMock
# Keep existing create_calendar_event import for the old test, will be adapted
from app.calendar_service import create_calendar_event, build_user_calendar_service
from google.oauth2.credentials import Credentials as UserCredentials # Alias for new tests
import unittest # For the new test class
from flask import Flask
from datetime import datetime, timedelta

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config["GOOGLE_CALENDAR_ID"] = "primary"
    app.config["TIMEZONE"] = "UTC"
    with app.app_context():
        yield

@patch("app.calendar_service.build_user_calendar_service") # MODIFIED: patch target
def test_create_calendar_event_success(mock_build_user_service, app_context): # MODIFIED: mock name
    mock_service = MagicMock()
    mock_events = mock_service.events.return_value
    mock_insert = mock_events.insert.return_value
    mock_insert.execute.return_value = {
        "htmlLink": "https://calendar.google.com/calendar/event?eid=mock123"
    }

    mock_build_user_service.return_value = mock_service # MODIFIED: mock name

    test_date_info = {'day': '11', 'month': '4', 'year': '2025', 'time': '14:00', 'day_of_week': 'Friday', 'event_description': 'Meeting with Team'}
    mock_user_creds = MagicMock(spec=UserCredentials) # MODIFIED: Add mock creds
    
    link = create_calendar_event(test_date_info, mock_user_creds) # MODIFIED: Pass mock creds

    assert link == "https://calendar.google.com/calendar/event?eid=mock123"

    expected_start = datetime(2025, 4, 11, 14, 0).isoformat()
    expected_end = (datetime(2025, 4, 11, 14, 0) + timedelta(hours=1)).isoformat()

    mock_events.insert.assert_called_once()
    args, kwargs = mock_events.insert.call_args
    body = kwargs["body"]

    assert body["start"]["dateTime"] == expected_start
    assert body["end"]["dateTime"] == expected_end
    assert body["summary"] == "Event from Flora Image"


# New tests for user auth related calendar service functions
class TestCalendarServiceWithUserAuth(unittest.TestCase):

    @patch('app.calendar_service.build') # Patch 'build' where it's defined/imported in calendar_service.py
    def test_build_user_calendar_service(self, mock_build):
        mock_creds = MagicMock(spec=UserCredentials)
        service = build_user_calendar_service(mock_creds)
        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
        self.assertIsNotNone(service)

    @patch('app.calendar_service.build_user_calendar_service')
    def test_create_calendar_event_uses_user_creds_and_primary_calendar(self, mock_build_user_service_func):
        # This is the mock for the build_user_calendar_service *function*
        # It should return a mock service object
        mock_service_instance = MagicMock()

        # Mock the chain of calls: service.events().insert().execute()
        mock_events_method = MagicMock()
        mock_insert_method = MagicMock()
        mock_execute_method = MagicMock()

        mock_service_instance.events.return_value = mock_events_method
        mock_events_method.insert.return_value = mock_insert_method
        mock_insert_method.execute.return_value = mock_execute_method

        # Set the return value for the .get("htmlLink") call
        mock_execute_method.get.return_value = 'http://event_link'

        # Make the build_user_calendar_service function return our top-level service mock
        mock_build_user_service_func.return_value = mock_service_instance

        mock_user_creds = MagicMock(spec=UserCredentials)
        date_info = {"year": "2024", "month": "01", "day": "15", "time": "10:00"}

        # Setup Flask app context if your config is accessed via current_app
        # For this specific test, if TIMEZONE is the only thing from current_app.config,
        # we can mock current_app or ensure the test runs within a context.
        # Assuming create_calendar_event uses current_app.config['TIMEZONE']
        app = Flask(__name__)
        app.config["TIMEZONE"] = "UTC" # Minimal config for the test
        with app.app_context():
            event_link = create_calendar_event(date_info, mock_user_creds)

        mock_build_user_service_func.assert_called_once_with(mock_user_creds)

        # Check that insert was called with calendarId='primary'
        # The call is service.events().insert(calendarId='primary', body=event)
        mock_events_method.insert.assert_called_once()
        args, kwargs = mock_events_method.insert.call_args
        self.assertEqual(kwargs.get('calendarId'), 'primary')
        self.assertEqual(event_link, 'http://event_link')

# If you want to run unittest tests from this file via `python tests/test_calendar_service.py`
if __name__ == '__main__':
    unittest.main()
