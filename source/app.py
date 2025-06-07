import os, pytz
from extensions import db
from flask import Flask, render_template, flash, redirect, session, url_for, current_app, request
from models import User, YahooToken #, Roster
import account_manager as account
from datetime import datetime, timedelta
import roster
from dotenv import load_dotenv # Development Stage ONLY
#from yahoo_oauth import OAuth2
from rauth import OAuth2Service
import binascii
import requests
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2
from account_manager import yahoo_utils 
from decorators import login_required
from requests_oauthlib import OAuth2Session
from types import SimpleNamespace
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

def init_app():
    # Load environment variables
    load_dotenv() # <- Development Stage ONLY

    # Configure application
    app = Flask(__name__)

    # DB File Location
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "gridiron.db")

    # Disable Modification Warnings
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    # Super Duper Secret Key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Yahoo OAuth Credentials
    app.config['YAHOO_CONSUMER_KEY'] = os.environ.get('YAHOO_CONSUMER_KEY')
    app.config['YAHOO_CONSUMER_SECRET'] = os.environ.get('YAHOO_CONSUMER_SECRET')

    if not app.config['YAHOO_CONSUMER_KEY'] or \
       not app.config['YAHOO_CONSUMER_SECRET']:
        print("[CRITICAL]: Yahoo OAuth credentials are not fully configured in .env.")
        print("[CRITICAL] Terminating Application")
        return 

    # Initialize SQLAlchemy
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Defining Root Page
    @app.route('/')
    def home():
        message = f"Welcome to Gridiron AI"
        return render_template("index.html", message=message)

    # def get_yahoo_fantasy_roster():
        consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
        consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')

        oauth = OAuth2(consumer_key, consumer_secret)
        print("Roster OAuth2 Called Successfully")
        # Check if token is valid. If not, user needs to re-authorize.
        if not oauth.token_is_valid():
            print("Token is not valid. Please re-authorize.")
            return {"error": "Invalid Token"}
        
        # Pass the authenticated 'oauth' object to the Game class
        gm = yfa.Game(oauth, 'nfl')

        # Fetch the teams
        roster_data = []
        # print(gm.league_ids(year=2024))
        league = gm.to_league('449.l.142565')
        team = league.to_team(league.team_key())
        roster = team.roster()
        for player in roster:
            if "name" in player:
                roster_data.append(player["name"])
                print(player["name"])

    
        return roster_data
    
   # def get_roster():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('handle_login'))
        
        user = User.query.filter_by(id=user_id).first()
        if not user or not user.yahoo_token or not user.yahoo_token.access_token:
            # If no token, redirect to authorization flow
            return redirect(url_for('yahoo_authorize'))
        
        # Retrieve yahoo credentials
        consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
        consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')

        # Get the token details from your database
        token_data = {
            'access_token': user.yahoo_token.access_token,
            'refresh_token': user.yahoo_token.refresh_token,
            'token_type': user.yahoo_token.token_type,
            'expires_in': (user.yahoo_token.token_expiry - datetime.utcnow()).total_seconds()
        }

        oauth = OAuth2(
            consumer_key, 
            consumer_secret, 
            token=token_data, 
            token_updater=yahoo_utils.update_token_in_db
        )

        if not oauth.token_is_valid():
            print("Token is expired, attempting to refresh...")
            oauth.refresh_access_token()

        try:
            # Pass the authenticated 'oauth' object to the Game class
            gm = yfa.Game(oauth, 'nfl')

            # Fetch the teams
            roster_data = []
            # print(gm.league_ids(year=2024))
            league = gm.to_league('449.l.142565')
            team = league.to_team(league.team_key())
            roster = team.roster()
            for player in roster:
                if "name" in player:
                    roster_data.append(player["name"])
                    print(player["name"])

        
            return roster_data
        except Exception as e:
            print(f"An error occured with the Yahoo Fantasy API: {e}")
        
    def get_roster():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('handle_login'))
    
        # Retrieve Yahoo Credentials
        consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
        consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')

        user = User.query.filter_by(id=user_id).first()
        print(f"Roster Pull From User: {user.username}") # Debug

        def token_updater(token):
            # This is the callback function we've discussed
            print("--- Running token_updater callback ---")
            yahoo_utils.update_token_in_db(user, token)
            print("--- Finished token_updater callback ---")

        # Calculate token expiration
        expires_in = (user.yahoo_token.token_expiry - datetime.utcnow()).total_seconds()

        token_data = {
            'access_token': user.yahoo_token.access_token,
            'refresh_token': user.yahoo_token.refresh_token,
            'token_type': user.yahoo_token.token_type,
            'expires_in': expires_in
        }

        # The token endpoint for Yahoo Fantasy Sports
        token_url = 'https://api.login.yahoo.com/oauth2/get_token'

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

        try:
            # Pass the authenticated OAuth2Session object to the yahoo_fantasy_api Game class
            gm = yfa.Game(auth_handler, 'nfl')
            print(gm.game_id())
            roster_data = []
            # Example: Fetching data for a specific league
            # You would likely have the league_id stored or passed in for a multi-user app
            leagues = gm.league_ids()
            print(leagues)
            league = gm.to_league(leagues[0])
            team = league.to_team(league.team_key())
            roster = team.roster()

            for player in roster:
                if "name" in player:
                    roster_data.append(player["name"])
                    print(player["name"])

            return roster_data

        except InvalidGrantError:
            # Step 4: If the automatic refresh fails, handle it gracefully
            # This means the refresh token is bad, and the user must re-authenticate.
            print(f"Refresh token for user {user.id} is invalid. Forcing re-authentication.")
        except Exception as e:
            print(f"An error occurred with the Yahoo Fantasy API: {e}")
            # You might want to handle specific OAuth errors here,
            # like redirecting to re-authorize if the refresh token is invalid.
            return None, 500 # Or render an error template

    # User Dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():
        # If user is not logged in, redirect to login page
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            return redirect(url_for('handle_login'))

        # Get the logged in user by user ID
        query_user = User.query.filter_by(id=session['user_id']).first()

        # Get date for last login
        if not query_user.last_login:
            last_login = query_user.now_login.strftime("%m-%d-%y %I:%M:%S")
        elif query_user.last_login:
            last_login = query_user.last_login.strftime("%m-%d-%y %I:%M:%S")
            
            # ** Need to figure out where to store the last login, so we can display it before its updated to the current time **
            utc_now = datetime.now(pytz.utc)
            pacific_tmz = pytz.timezone("America/Los_Angeles")
            pacific_now = utc_now.astimezone(pacific_tmz)
            query_user.last_login = pacific_now

        # Yahoo Sports
        team_roster = []
        if not query_user or not query_user.yahoo_token or not query_user.yahoo_token.access_token:
            team_roster.append("You are not authenticated with Yahoo.")
        else:
            team_roster = get_roster()

        return render_template("dashboard.html",
                               username=query_user.username,
                               last_login=last_login,
                               roster=team_roster)
    
    
        
    
    # User roster (TESTING)
    @app.route('/roster')
    def handle_roster():
        return roster.roster()
        
    # User Registration
    @app.route('/register', methods=['GET', 'POST'])
    def handle_reg():
        return account.account_register()
            
    # User Login
    @app.route('/login', methods=['GET', 'POST'])
    def handle_login():
        return account.account_login()

    # User Logout
    @app.route('/logout')
    def handle_logout():
        # Remove user from session & redirect to login page
        session.pop('user_id', None)
        flash("You have been logged out." "info")
        return redirect(url_for('handle_login'))
    
    @app.route('/yahoo/authorize')
    @login_required
    def yahoo_authorize():
        """Redirects the user to Yahoo for authentication."""
        consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
        consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')
        # callback_url = current_app.config.get('YAHOO_CALLBACK_URL')
        callback_url = url_for('yahoo_callback', _external=True, _scheme='https')

        print(f"yahoo_authorize() CALLBACK: {callback_url}")

        if not all([consumer_key, consumer_secret, callback_url]):
            print("Yahoo API credentials are not properly configured.")
            return redirect(url_for('dashboard'))
        
        print("Passed the yahoo config check")
        
        try:
            yahoo_service = OAuth2Service(
                name='yahoo',
                client_id=consumer_key,
                client_secret=consumer_secret,
                access_token_url='https://api.login.yahoo.com/oauth2/get_token',
                authorize_url='https://api.login.yahoo.com/oauth2/request_auth'
            )

            generated_state = binascii.hexlify(os.urandom(16)).decode()
            session['yahoo_oauth_state'] = generated_state
            
            auth_url = yahoo_service.get_authorize_url(
                state=generated_state,
                redirect_uri=callback_url,
                response_type='code'
            )
        except Exception as e:
            print(f"Yahoo Authorize Error: {e}")

        print(f"Generated Yahoo Auth URL: {auth_url}")
    
        return redirect(auth_url)
    
    @app.route('/yahoo/callback')
    @login_required
    def yahoo_callback():
        """Handles the callback from Yahoo after authorization"""
        print("Entering Yahoo Callback")

        consumer_key = current_app.config.get('YAHOO_CONSUMER_KEY')
        consumer_secret = current_app.config.get('YAHOO_CONSUMER_SECRET')
        # callback_url = current_app.config.get('YAHOO_CALLBACK_URL')
        callback_url = url_for('yahoo_callback', _external=True, _scheme='https')

        print(f"yahoo_callback() CALLBACK: {callback_url}")

        user_id = session.get('user_id')
        if not user_id:
            print("User is not logged in.")
            return redirect(url_for('handle_login'))
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            print("User was not found. Please log in again.")
            session.pop('user_id', None)
            return redirect(url_for('handle_login'))
        
        code = request.args.get('code')
        returned_state = request.args.get('state')
        original_state = session.pop('yahoo_oauth_state', None)

        if not code:
            print("No auth code provided by Yahoo.")
            return "Missing auth code.", 400

        if not returned_state or returned_state != original_state:
            print("Invalid state parameter. CSRF attempt suspected.")
            return "Missing state parameter.", 403

        # Recreate the service object to get the access token
        # yahoo_service = OAuth2Service(
        #    name='yahoo',
        #    client_id=consumer_key,
        #    client_secret=consumer_secret,
        #    access_token_url='https://api.login.yahoo.com/oauth2/get_token',
        #    authorize_url='https://api.login.yahoo.com/oauth2/request_auth'
        # )

        try:
            token_url = 'https://api.login.yahoo.com/oauth2/get_token'

            payload = {
                'code': code,
                'redirect_uri': callback_url,
                'grant_type': 'authorization_code'
            }

            auth = (consumer_key, consumer_secret)
            response = requests.post(token_url, data=payload, auth=auth)
            response.raise_for_status()
            token_payload = response.json()

            print("Token Received! SUCCESS!")

        except Exception as e:
            print("Error getting token from Yahoo for user.")
            print(f"AN EXCEPTION OCCURRED: {e}")
            return redirect(url_for('dashboard'))
        
        token_entry = user.yahoo_token # Access the related YahooToken model
        if not token_entry:
            token_entry = YahooToken(user_id=user.id)
            user.yahoo_token = token_entry

        token_entry.access_token = token_payload.get('access_token')
        token_entry.refresh_token = token_payload.get('refresh_token')
        token_entry.token_type = token_payload.get('token_type')
        expires_in = token_payload.get('expires_in', 3600)
        token_entry.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

        try:
            db.session.commit()
            print("Success Yahoo connect!")
        except Exception as e:
            db.session.rollback()
            print("ERRRRRROOOOOORRRRRRRR")
        
        return redirect(url_for('dashboard'))
        

    return app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)