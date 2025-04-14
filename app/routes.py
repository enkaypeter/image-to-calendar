from flask import Blueprint, request, jsonify
from .flora_service import extract_event_from_image
from .calendar_service import create_calendar_event

calendar_bp = Blueprint("calendar_bp", __name__)

@calendar_bp.route("/add-to-calendar", methods=["POST"])
def add_to_calendar():
    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "image_url is required"}), 400

    try:
        date_info = extract_event_from_image(image_url)
        print("Extracted date info:", date_info)
        
        event_link = create_calendar_event(date_info)
        return jsonify({"status": "success", "event_link": event_link})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
