import requests
from flask import current_app
from dateutil import parser as date_parser


def extract_event_from_image(image_url: str):
    try:
        extraction_url = f"{current_app.config["FLORA_API_URL"]}/extractions"

        headers = {
            "Authorization": f"Bearer {current_app.config['FLORA_API_KEY']}"
        }

        
        payload = {
            "schema_id": current_app.config['FLORA_SCHEMA_ID']['EVENT_EXTRACTION_SCHEMA'],
            "type": "image",
            "model": "gpt-4o",
            "source": image_url
        }

        response = requests.post(extraction_url, json=payload, headers=headers, timeout=10)

        response.raise_for_status()
        data = response.json()

        if not data.get("status") or "output" not in data.get("data", {}):
            raise ValueError("Invalid response structure from Flora API.")

        output = data["data"]["output"]

        # Parse and validate fields
        day = output.get("day")
        year = output.get("year")
        day_of_week = output.get("day_of_week")
        month = output.get("month", "")
        time_str = output.get("time", "").strip()
        event_description = output.get("event_description", "Event from Flora Image")

        if not all([day, year, month, day_of_week, time_str]):
            raise ValueError("Missing one or more required fields in Flora output.")

        # Convert time to 24-hour format
        dt_obj = date_parser.parse(time_str)
        time_24h = dt_obj.strftime("%H:%M")

        return {
            "day": day,
            "day_of_week": day_of_week,
            "month": month,
            "year": year,
            "time": time_24h,
            "event_description": event_description
        }

    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"Flora API returned an HTTP error: {http_err.response.status_code} - {http_err.response.text}") from http_err

    except requests.exceptions.RequestException as req_err:
        raise RuntimeError(f"Error connecting to Flora API: {str(req_err)}") from req_err

    except ValueError as val_err:
        raise RuntimeError(f"Invalid response from Flora API: {str(val_err)}") from val_err

    except Exception as e:
        raise RuntimeError(f"Unexpected error while extracting from image: {str(e)}") from e
