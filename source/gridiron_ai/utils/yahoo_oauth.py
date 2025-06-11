# yahoo_oauth
from datetime import datetime, timedelta, timezone
from flask import Blueprint, redirect, url_for, current_app, session,request
from rauth import OAuth2Service
from requests_oauthlib import OAuth2Session
from types import SimpleNamespace
import binascii, requests, os
from .extensions import db 
from .decorators import login_required

# Yahoo Blueprint to handle Flask routes
yahoo_bp = Blueprint('yahoo', __name__, template_folder='templates')

def update_token_in_db(user, token):
    """
    Saves the new token dictionary to the database for a given user.

    Args:
        user: Database user object
        token: Yahoo token to refresh
    """
    # Update database fields
    user.yahoo_token.access_token = token['access_token']
    user.yahoo_token.refresh_token = token['refresh_token'] 
    user.yahoo_token.token_type = token['token_type']
    
    # Calculate the new expiry time from the 'expires_in' field
    # datetime.utcnow()
    user.yahoo_token.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token['expires_in'])
    
    try:
        # Commit the changes to the database
        db.session.commit()
        # ----> Print for now, adding logger later <----
        print("--- Successfully saved new token to the database. ---")
    except Exception as e:
        db.session.rollback()
        # ----> Print for now, adding logger later <----
        print(f"--- FAILED to save new token to the database: {e} ---")

def yahoo_api_connect():
    """
    Connects user to the Yahoo! Sports API

    Returns: OAuth Handler
    """
    from ..models import User

    # Get user_id from session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('handle_login'))

    # Retrieve Yahoo Credentials
    consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
    consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')

    # Fetch the current user from the database using their user_id
    user = User.query.filter_by(id=user_id).first()
    
    def token_updater(token):
        # ----> Print for now, adding logger later <----
        print("--- Running token_updater callback ---")
        update_token_in_db(user, token)
        # ----> Print for now, adding logger later <----
        print("--- Finished token_updater callback ---")

    # Calculate token expiration
    expires_in = (user.yahoo_token.token_expiry - datetime.utcnow()).total_seconds()

    # Prepare the token dictionary for OAuth2Session
    token_data = {
        'access_token': user.yahoo_token.access_token,
        'refresh_token': user.yahoo_token.refresh_token,
        'token_type': user.yahoo_token.token_type,
        'expires_in': expires_in
    }

    # The token endpoint for Yahoo Fantasy Sports
    token_url = 'https://api.login.yahoo.com/oauth2/get_token'

    # Create an OAuth2Session with automatic token refresh and update callback
    oauth = OAuth2Session(
        client_id=consumer_key,
        token=token_data,
        auto_refresh_url=token_url,
        auto_refresh_kwargs={
            'client_id': consumer_key,
            'client_secret': consumer_secret,
        },
        token_updater=token_updater
    )

    auth_handler = SimpleNamespace()
    auth_handler.session = oauth
    return auth_handler

# ----------------------------------------------------------------------
# Flask routes which handle Yahoo! authorization
@yahoo_bp.route('/yahoo/authorize')
@login_required
def yahoo_authorize():
    """Redirects the user to Yahoo for authentication."""
    from ..models import User, YahooToken

    # Get Yahoo API Keys
    consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
    consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')
    callback_url = url_for('yahoo.yahoo_callback', _external=True, _scheme='https')

    # Make sure API keys are configured correct.
    if not all([consumer_key, consumer_secret, callback_url]):
        print("Yahoo API credentials are not properly configured.")
        return redirect(url_for('main.dashboard'))
    
    try:
        # Create an OAuth2Service object to handle Yahoo API connection
        yahoo_service = OAuth2Service(
            name='yahoo',
            client_id=consumer_key,
            client_secret=consumer_secret,
            access_token_url='https://api.login.yahoo.com/oauth2/get_token',
            authorize_url='https://api.login.yahoo.com/oauth2/request_auth'
        )

        # Generate a random token
        generated_state = binascii.hexlify(os.urandom(16)).decode()
        session['yahoo_oauth_state'] = generated_state
        
        # Build OAuth URL 
        auth_url = yahoo_service.get_authorize_url(
            state=generated_state,
            redirect_uri=callback_url,
            response_type='code'
        )
    except Exception as e:
        print(f"Yahoo Authorize Error: {e}")
    return redirect(auth_url)

@yahoo_bp.route('/yahoo/callback')
@login_required
def yahoo_callback():
    """Handles the callback from Yahoo after authorization"""
    from ..models import User, YahooToken

    # Get Yahoo API Keys
    consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
    consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')
    callback_url = url_for('yahoo.yahoo_callback', _external=True, _scheme='https')

    # The two 'if' checks are not really needed due to the 'login_required' decorator
    # Fetch user_id by session
    user_id = session.get('user_id')
    if not user_id:
        # ----> Print for now, adding logger later <----
        print("User is not logged in.")
        return redirect(url_for('main.handle_login'))
    
    # Fetch the current user from the database using their user_id
    user = User.query.filter_by(id=user_id).first()
    if not user:
        # ----> Print for now, adding logger later <----
        print("User was not found. Please log in again.")
        session.pop('user_id', None)
        return redirect(url_for('main.handle_login'))
    
    # Get 'code' arg from url
    code = request.args.get('code')

    # Get 'state' arg from url
    returned_state = request.args.get('state')

    # Get original 'state' from session
    original_state = session.pop('yahoo_oauth_state', None)

    # Check if auth code was provided by Yahoo
    if not code:
        print("No auth code provided by Yahoo.")
        return "Missing auth code.", 400

    # CSRF check
    if not returned_state or returned_state != original_state:
        # ----> Print for now, adding logger later <----
        print("Invalid state parameter. CSRF attempt suspected.")
        return "Missing state parameter.", 403

    try:
        token_url = 'https://api.login.yahoo.com/oauth2/get_token'


        # Prepare the payload for exchanging the authorization code for tokens
        payload = {
            'code': code,
            'redirect_uri': callback_url,
            'grant_type': 'authorization_code'
        }

        # Exchange the authorization code for an access token from Yahoo
        auth = (consumer_key, consumer_secret)
        response = requests.post(token_url, data=payload, auth=auth)
        response.raise_for_status()
        token_payload = response.json()

        # ----> Print for now, adding logger later <----
        print("Token Received! SUCCESS!")

    except Exception as e:
        print(f"Error getting token from Yahoo for user: {e}")
        return redirect(url_for('main.dashboard'))
    
    # Access the users related YahooToken model
    token_entry = user.yahoo_token
    if not token_entry:
        token_entry = YahooToken(user_id=user.id)
        user.yahoo_token = token_entry

    # Update users database with Yahoo's token
    token_entry.access_token = token_payload.get('access_token')
    token_entry.refresh_token = token_payload.get('refresh_token')
    token_entry.token_type = token_payload.get('token_type')
    expires_in = token_payload.get('expires_in', 3600)
    token_entry.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

    try:
        db.session.commit()
        # ----> Print for now, adding logger later <----
        print("Success Yahoo connect!")
    except Exception as e:
        # ----> Print for now, adding logger later <----
        print(f"Failed to save Yahoo token to database: {e}")
        db.session.rollback()
    return redirect(url_for('main.dashboard'))