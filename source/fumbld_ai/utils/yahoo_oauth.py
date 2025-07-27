# yahoo_oauth
from datetime import datetime, timedelta, timezone
from flask import Blueprint, redirect, url_for, current_app, session,request, jsonify
# from rauth import OAuth2Service
from requests_oauthlib import OAuth2Session
from types import SimpleNamespace
import binascii, requests, os
from .extensions import db, limiter
from flask_login import login_required, current_user
from .helper import TokenEncryptor
from flask_limiter.errors import RateLimitExceeded
import base64, logging
import os

# Allow insecure transport on development machine
if os.getenv('APP_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Yahoo Blueprint to handle Flask routes
yahoo_bp = Blueprint('yahoo', __name__, template_folder='templates')

logger = logging.getLogger("fumbld_logger")

def update_token_in_db(user, token):
    """
    Saves the new token dictionary to the database for a given user.

    Args:
        user: Database user object
        token: Yahoo token to refresh
    """
    # Cryptography
    crypt = TokenEncryptor(current_app.config.get("ENCRYPT_KEY").encode())

    # Update database fields
    user.yahoo_token.access_token = base64.b64encode(crypt.encrypt(token['access_token'].encode())).decode()
    user.yahoo_token.refresh_token = base64.b64encode(crypt.encrypt(token['refresh_token'].encode())).decode()
    user.yahoo_token.token_type = token['token_type']
    
    # Calculate the new expiry time from the 'expires_in' field
    # datetime.utcnow()
    user.yahoo_token.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token['expires_in'])
    
    try:
        # Commit the changes to the database
        db.session.commit()
        logger.info(f"User ID: {current_user.id} | Username: {current_user.username}: Successfully saved new Yahoo! token to the database")
    except Exception as e:
        db.session.rollback()
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: Failed to save new Yahoo! yoken to the database: {e}")

@login_required
def yahoo_api_connect():
    """
    Connects user to the Yahoo! Sports API

    Returns: OAuth Handler
    """
    # Retrieve Yahoo Credentials
    consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
    consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')

    # Retrieve Secret Key
    app_key = current_app.config.get("ENCRYPT_KEY").encode()
    
    def token_updater(token):
        logger.info(f"User ID: {current_user.id} | Username: {current_user.username}: Running token_updater callback.")
        update_token_in_db(current_user, token)
        logger.info(f"User ID: {current_user.id} | Username: {current_user.username}: Finished token_updater callback.")
    
    # Calculate token expiration
    expires_in = (current_user.yahoo_token.token_expiry - datetime.now(timezone.utc)).total_seconds()

    try:
        # Cryptography
        crypt = TokenEncryptor(app_key)

        # Base64-decode before decrypting
        encrypted_access_token = base64.b64decode(current_user.yahoo_token.access_token)
        encrypted_refresh_token = base64.b64decode(current_user.yahoo_token.refresh_token)

        access_token = crypt.decrypt(encrypted_access_token).decode()
        refresh_token = crypt.decrypt(encrypted_refresh_token).decode()
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: Unable to read access tokens from the database: {e}")
        return None
    
    try:  
        token_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': current_user.yahoo_token.token_type,
            'expires_in': expires_in
        }
    except Exception as e:
        logger.error(f"User ID: {current_user.id} | Username: {current_user.username}: An error occured building token payload: {e}")        

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
    try:
        with limiter.limit("1 per hour"):
            #  ..models import User, YahooToken

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
                # yahoo_service = OAuth2Service(
                #     name='yahoo',
                #     client_id=consumer_key,
                #     client_secret=consumer_secret,
                #     access_token_url='https://api.login.yahoo.com/oauth2/get_token',
                #     authorize_url='https://api.login.yahoo.com/oauth2/request_auth'
                # )

                # Generate a random token
                # generated_state = binascii.hexlify(os.urandom(16)).decode()
                oauth = OAuth2Session(
                    client_id=consumer_key,
                    redirect_uri=callback_url
                )

                # Generate authorization URL
                authorization_url, state = oauth.authorization_url(
                    'https://api.login.yahoo.com/oauth2/request_auth'
                )

                # session['yahoo_oauth_state'] = generated_state
                # Store state for CSRF protection
                session['yahoo_oauth_state'] = state
                
                # Build OAuth URL 
                # auth_url = yahoo_service.get_authorize_url(
                #     state=generated_state,
                #     redirect_uri=callback_url,
                #     response_type='code'
                # )
            except Exception as e:
                print(f"Yahoo Authorize Error: {e}")
            return redirect(authorization_url)
    except RateLimitExceeded:
        return jsonify({"error": "Please allow one hour in between Yahoo! authorization requests."})


@yahoo_bp.route('/yahoo/callback')
@login_required
def yahoo_callback():
    """Handles the callback from Yahoo after authorization"""
    from ..models import YahooToken

    # Get Yahoo API Keys
    consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
    consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')
    callback_url = url_for('yahoo.yahoo_callback', _external=True, _scheme='https')

    # Get Secret Key
    app_key = current_app.config.get("ENCRYPT_KEY").encode()

    # The two 'if' checks are not really needed due to the 'login_required' decorator
    # Fetch user_id by session
    # user_id = session.get('user_id')
    if not current_user.is_authenticated:
        # ----> Print for now, adding logger later <----
        print("User is not logged in.")
        return redirect(url_for('main.handle_login'))
    
    # added
    authorization_response = request.url

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
        # payload = {
        #     'code': code,
        #     'redirect_uri': callback_url,
        #     'grant_type': 'authorization_code'
        # }

        # # Exchange the authorization code for an access token from Yahoo
        # auth = (consumer_key, consumer_secret)
        # response = requests.post(token_url, data=payload, auth=auth)
        # response.raise_for_status()
        # token_payload = response.json()
        oauth = OAuth2Session(
            client_id=consumer_key,
            redirect_uri=callback_url,
            state=original_state
        )

        # Exchange authorization code for token
        token = oauth.fetch_token(
            'https://api.login.yahoo.com/oauth2/get_token',
            authorization_response=authorization_response,
            client_secret=consumer_secret
        )

        # ----> Print for now, adding logger later <----
        print("Token Received! SUCCESS!")

    except Exception as e:
        print(f"Error getting token from Yahoo for user: {e}")
        return redirect(url_for('main.dashboard'))
    
    # Access the users related YahooToken model
    token_entry = current_user.yahoo_token
    if not token_entry:
        token_entry = YahooToken(user_id=current_user.id)
        current_user.yahoo_token = token_entry

    # Cryptography
    crypt = TokenEncryptor(app_key)
    access_token = base64.b64encode(crypt.encrypt(token['access_token'].encode())).decode()
    refresh_token = base64.b64encode(crypt.encrypt(token['refresh_token'].encode())).decode()

    # Update users database with Yahoo's token
    token_entry.access_token = access_token
    token_entry.refresh_token = refresh_token
    token_entry.token_type = token.get('token_type', 'Bearer')
    expires_in = token.get('expires_in', 3600)
    token_entry.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    try:
        db.session.commit()
        # ----> Print for now, adding logger later <----
        print("Success Yahoo connect!")
    except Exception as e:
        # ----> Print for now, adding logger later <----
        print(f"Failed to save Yahoo token to database: {e}")
        db.session.rollback()

    from ..yahoo_fantasy import yahoo_refresh
    yahoo_refresh()

    return redirect(url_for('main.dashboard'))