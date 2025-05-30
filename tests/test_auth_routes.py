import unittest
from unittest.mock import patch, MagicMock
from flask import session, url_for, Flask
from app import create_app # Assuming you have a create_app factory
from app.config import Config

# A minimal config for testing
class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False # Often disabled in testing
    SECRET_KEY = 'test_secret_key' # Needed for session
    # Mock OAuth specific configs - these would ideally be paths to mock client_secret files
    # or structured dicts if using from_client_config
    OAUTH_CLIENT_ID = 'test_client_id'
    OAUTH_CLIENT_SECRET = 'test_client_secret_path.json' # Path to a dummy file or mock
    OAUTH_REDIRECT_URI = 'http://localhost/oauth2callback'
    GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']


class AuthRoutesTests(unittest.TestCase):

    def setUp(self):
        # Create a dummy client_secret.json for Flow.from_client_secrets_file to work
        # In a real scenario, you might mock the Flow object more directly
        with open('test_client_secret_path.json', 'w') as f:
            f.write('{"web": {"client_id": "test_client_id", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "client_secret": "supersecret"}}')

        self.app = create_app(TestConfig) # Use your app factory with test config
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        import os
        # Safely remove the file, check if it exists first
        if os.path.exists('test_client_secret_path.json'):
            os.remove('test_client_secret_path.json') # Clean up dummy file
        self.app_context.pop()

    @patch('google_auth_oauthlib.flow.Flow.authorization_url')
    def test_authorize_redirects_and_sets_state(self, mock_auth_url):
        mock_auth_url.return_value = ('https://mocked_google_auth_url.com', 'mock_state')

        response = self.client.get(url_for('calendar_bp.authorize'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'https://mocked_google_auth_url.com')
        mock_auth_url.assert_called_once()
        with self.client.session_transaction() as sess:
            self.assertIn('state', sess)
            self.assertEqual(sess['state'], 'mock_state')

    @patch('google_auth_oauthlib.flow.Flow.fetch_token')
    @patch('google_auth_oauthlib.flow.Flow.from_client_secrets_file') # Mock from_client_secrets_file
    def test_oauth2callback_success(self, mock_from_client_secrets_file, mock_fetch_token):
        # Mock the flow object that from_client_secrets_file would return
        mock_flow_instance = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.token = 'mock_token'
        mock_credentials.refresh_token = 'mock_refresh_token'
        mock_credentials.token_uri = 'mock_token_uri'
        mock_credentials.client_id = 'mock_client_id'
        mock_credentials.client_secret = 'mock_client_secret'
        mock_credentials.scopes = ['https://www.googleapis.com/auth/calendar']
        mock_flow_instance.credentials = mock_credentials
        mock_from_client_secrets_file.return_value = mock_flow_instance

        with self.client.session_transaction() as sess:
            sess['state'] = 'mock_state_value'

        # The URL here needs to match what fetch_token expects (including state)
        # The 'request.url' in routes.py will be this full URL.
        response = self.client.get(url_for('calendar_bp.oauth2callback', state='mock_state_value', code='mock_auth_code'))

        self.assertEqual(response.status_code, 200) # Now renders a template
        self.assertIn(b'Authorization Successful', response.data)
        mock_fetch_token.assert_called_once()
        # Verify that fetch_token was called with the correct authorization_response
        mock_flow_instance.fetch_token.assert_called_once_with(authorization_response=url_for('calendar_bp.oauth2callback', state='mock_state_value', code='mock_auth_code', _external=False))

        with self.client.session_transaction() as sess:
            self.assertIn('credentials', sess)
            self.assertEqual(sess['credentials']['token'], 'mock_token')

    def test_add_to_calendar_unauthenticated(self):
        response = self.client.post(url_for('calendar_bp.add_to_calendar'), json={'image_url': 'http://example.com/image.jpg'})
        self.assertEqual(response.status_code, 302)
        # Check if the redirect location ends with the authorize URL.
        # url_for('calendar_bp.authorize', _external=False) might produce a relative path
        # while response.location might be absolute. Testing endswith is safer.
        self.assertTrue(response.location.endswith(url_for('calendar_bp.authorize')))


    @patch('app.routes.extract_event_from_image') # Patch extract_event_from_image
    @patch('app.routes.create_calendar_event') # Patch create_calendar_event where it's used in routes.py
    def test_add_to_calendar_authenticated(self, mock_create_event, mock_extract_event):
        mock_extract_event.return_value = {"year": "2024", "month": "01", "day": "15", "time": "10:00"} # Mock extraction
        mock_create_event.return_value = 'http://mock_event_link'

        with self.client.session_transaction() as sess:
            sess['credentials'] = {
                'token': 'test_token', 'refresh_token': 'test_refresh',
                'token_uri': 'uri', 'client_id': 'id', 'client_secret': 'secret',
                'scopes': ['scope1']
            }
            # session might also store user_id or other identifiers, add if necessary
            # sess['user_id'] = 'test_user'

        response = self.client.post(url_for('calendar_bp.add_to_calendar'), json={'image_url': 'http://example.com/image.jpg'})

        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertIn('event_link', json_response)
        self.assertEqual(json_response['event_link'], 'http://mock_event_link')

        mock_extract_event.assert_called_once_with('http://example.com/image.jpg')
        # Check that create_calendar_event was called with credentials from session
        # This requires inspecting the arguments passed to mock_create_event
        args, kwargs = mock_create_event.call_args
        self.assertEqual(args[0], mock_extract_event.return_value) # date_info
        self.assertTrue(hasattr(args[1], 'token')) # Check if it's a Credentials-like object
        self.assertEqual(args[1].token, 'test_token')


if __name__ == '__main__':
    unittest.main()
