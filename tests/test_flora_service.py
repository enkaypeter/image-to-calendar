import pytest
from unittest.mock import patch, MagicMock
from app.flora_service import extract_event_from_image
from flask import Flask

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config["FLORA_API_URL"] = "https://fake-flora.com"
    app.config["FLORA_API_KEY"] = "flr-sk-fakeapikey"
    with app.app_context():
        yield

@patch("app.flora_service.requests.post")
def test_extract_event_from_image_success(mock_post, app_context):
    mock_response_data = {
        "status": True,
        "message": "Extraction completed successfully",
        "data": {
            "id": "mock-id-123",
            "output": {
                "day": "11",
                "time": "2 PM",
                "day_of_week": "Friday",
                "year": "2025",
                "month": 4,
                "event_description": "Mock Meeting"
            },
            "totalTokens": 899
        }
    }

    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    image_url = "https://mock-image-url.com/test.jpg"
    result = extract_event_from_image(image_url)

    assert result == {
        "day": "11",
        "month": 4,
        "year": "2025",
        "day_of_week": "Friday",
        "time": "14:00",
        "event_description": "Mock Meeting"
    }
