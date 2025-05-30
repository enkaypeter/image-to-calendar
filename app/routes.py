from flask import Blueprint, request, jsonify, url_for, redirect, session, current_app, render_template
from google_auth_oauthlib.flow import Flow
import os
import google.oauth2.credentials
from .flora_service import extract_event_from_image
from .calendar_service import create_calendar_event

calendar_bp = Blueprint("calendar_bp", __name__)

@calendar_bp.route("/authorize")
def authorize():
    # Create a Flow instance to manage the OAuth 2.0 Authorization Grant Flow
    flow = Flow.from_client_secrets_file(
        current_app.config['OAUTH_CLIENT_SECRET'], # This should be the path to the client_secret.json file
        scopes=current_app.config['GOOGLE_CALENDAR_SCOPES'],
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True)
    )

    # The URI that Google will redirect the user to after the user completes the
    # authorization flow. It must match one of the authorized redirect URIs
    # configured for the OAuth 2.0 client in the Google API Console.
    authorization_url, state = flow.authorization_url(
        # Recommended: Enable offline access to get a refresh token
        access_type='offline',
        # Recommended: Incremental authorization
        include_granted_scopes='true'
    )

    # Store the state in the session so that the callback can verify the
    # authorization server response.
    session['state'] = state

    return redirect(authorization_url)

@calendar_bp.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = session['state']

    flow = Flow.from_client_secrets_file(
        current_app.config['OAUTH_CLIENT_SECRET'], # This should be the path to the client_secret.json file
        scopes=current_app.config['GOOGLE_CALENDAR_SCOPES'],
        state=state,
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True)
    )

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return render_template('oauth_success.html')


@calendar_bp.route("/add-to-calendar", methods=["POST"])
def add_to_calendar():
    # Check if user is authenticated
    if 'credentials' not in session:
        return redirect(url_for('calendar_bp.authorize'))

    # TODO: Retrieve user credentials from session and pass to create_calendar_event
    # Example:
    # user_creds_dict = session['credentials']
    # from google.oauth2.credentials import Credentials
    # user_creds = Credentials(**user_creds_dict)
    # date_info = extract_event_from_image(image_url) # Needs image_url from request
    # event_link = create_calendar_event(date_info, user_creds)


    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "image_url is required"}), 400

    try:
        # This part needs to be adjusted to use user_creds
        # For now, let's assume the old logic for non-OAuth flow or a placeholder
        # until the next step where this route is fully updated.
        # The original POST request to /add-to-calendar might not have image_url
        # if it's redirected from oauth2callback. This needs careful handling.

        if not image_url: # image_url might not be in JSON body if redirected
            # If redirected from OAuth, we might not have the image_url in the session or request body.
            # This indicates a potential UX flow issue to be addressed.
            # For now, returning an error or redirecting to an input page might be options.
            # Or, the add_to_calendar route should perhaps be a GET route after OAuth,
            # and expect image_url (or some identifier) to be passed differently (e.g. session).
            # For this subtask, I will keep the existing logic but it's flagged for review.
             return jsonify({"error": "image_url is required after OAuth flow or session is missing data."}), 400


        date_info = extract_event_from_image(image_url)
        print("Extracted date info:", date_info)
        
        # Retrieve credentials from session
        user_creds_dict = session['credentials']
        user_creds = google.oauth2.credentials.Credentials(**user_creds_dict)

        event_link = create_calendar_event(date_info, user_creds)
        return jsonify({"status": "success", "event_link": event_link})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
