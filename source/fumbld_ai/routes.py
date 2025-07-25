from flask import render_template, Blueprint, flash, redirect, url_for, request, abort, jsonify, current_app
import pytz, datetime
from .yahoo_fantasy import yahoo_get_roster, yahoo_get_league, yahoo_refresh
from .sleeper import get_sleeper_leagues, get_sleeper_roster, get_sleeper_userid
from .utils import db, is_safe_url, gpt_call, gemini_call, limiter
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, SleeperForm
from flask_login import current_user, login_user, logout_user, login_required
from .models import YahooToken, SleeperLeague, RegCodes
from flask_limiter.errors import RateLimitExceeded
import requests


main_bp = Blueprint('main', __name__, template_folder='templates')

# Google reCaptcha
def verify_recaptcha():
    recaptcha_response = request.form.get('g-recaptcha-response')
    secret_key = current_app.config.get('GOOGLE_CAPTCHA_KEY')

    payload = {
        'secret': secret_key,
        'response': recaptcha_response
    }

    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = response.json()

    if result.get('success'):
        return True
    else:
        return True # False (remove comment for production)

# Defining Root Page
@main_bp.route('/')
def home():
    return render_template("index.html")

# User Dashboard
@main_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    from .models import User
    # Get date for last login
    if not current_user.last_login:
        last_login = current_user.now_login.strftime("%m-%d-%y %I:%M:%S")
    elif current_user.last_login:
        last_login = current_user.last_login.strftime("%m-%d-%y %I:%M:%S")
        
        # ** Need to figure out where to store the last login, so we can display it before its updated to the current time **
        utc_now = datetime.datetime.now(pytz.utc)
        pacific_tmz = pytz.timezone("America/Los_Angeles")
        pacific_now = utc_now.astimezone(pacific_tmz)
        current_user.last_login = pacific_now
    
    # Password reset form
    pass_reset_form = ChangePasswordForm()

    # Sleeper username form
    sleeper_user_form = SleeperForm()

    # Is user authenticated with Yahoo?
    yahoo_query = YahooToken.query.filter_by(user_id=current_user.id).first()
    if yahoo_query:
        yahoo_auth = True
    else:
        yahoo_auth = False

    # Is user set up with Sleeper?
    sleeper_query = SleeperLeague.query.filter_by(user_id=current_user.id).first()
    if sleeper_query:
        sleeper_username = sleeper_query.sleeper_username
        sleeper_auth = True
    else:
        sleeper_username = ""
        sleeper_auth = False

    if current_user.role == "admin":
        admin_user = True
    else:
        admin_user = False

    return render_template("dashboard.html",
                            username=current_user.username,
                            last_login=last_login,
                            pass_reset=pass_reset_form,
                            yahoo=yahoo_auth,
                            sleeper_form=sleeper_user_form,
                            sleeper=sleeper_auth,
                            sleeper_username=sleeper_username,
                            admin=admin_user)
    
# User Registration
@main_bp.route('/register', methods=['GET', 'POST'])
def account_register():
    from .models import User

    if current_user.is_authenticated:
       return redirect(url_for('main.dashboard'))

    # Create an object of RegistrationForm
    form = RegistrationForm()

    # If everything passes validation on forms
    if form.validate_on_submit():
        if verify_recaptcha():
            username = form.username.data
            user_email = form.email.data
            password = form.password.data
            terms = form.terms.data

            # Check for existing user
            # SQL Equivalent: SELECT * FROM user WHERE username = '<username>' LIMIT 1;
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print("No REG CODE")
                flash("The username already exists, please choose another.", "error")
                return render_template("registration.html", form=form)
            
            # Check if existing email
            exisiting_email = User.query.filter_by(email=user_email).first()
            if exisiting_email:
                flash("This email is already registered!", "error")
                return render_template("registration.html", form=form)
            
            # Beta Test Only
            reg_code = form.reg_code.data
            query_reg_codes = RegCodes.query.filter_by(reg_code=reg_code).first()
            if not query_reg_codes:
                flash("Invalid registration code.", "error")
                return render_template("registration.html", form=form)
            else:
                query_reg_codes.used = True
                query_reg_codes.used_by = username
                role = "beta"

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash("There was an error processing the registration code.", "error")
                    return render_template("registration.html", form=form)

            # Pass user name, email and hash from forms and store into DB
            new_user = User(username=username, email=user_email, role=role, accepted_terms=terms)
            new_user.set_password(password)

            utc_now = datetime.datetime.now(pytz.utc)
            pacific_tmz = pytz.timezone("America/Los_Angeles")
            pacific_now = utc_now.astimezone(pacific_tmz)
            new_user.last_login = pacific_now
            new_user.date_registered = pacific_now
            new_user.now_login = pacific_now

            try:
                # Add new_user to session query
                db.session.add(new_user)
                # Save the changes to the database
                db.session.commit()

                # add new user to session and login
                login_user(new_user)
                next_page = request.args.get('next')
                if next_page and not is_safe_url(next_page):
                    return abort(400)

                print(f"New account created successfully for: {current_user.username} with ID: {current_user.id}")
                return redirect(next_page or url_for('main.dashboard'))
            except Exception as e:
                # Rollback changes made to database incase of error
                db.session.rollback()
                flash("There was an internal error with creating the account.", "error")
                return render_template("registration.html", form=form)
        else:
            print("Google reCaptcha was not verified!")
    return render_template("registration.html", form=form)
        
# User Login
@main_bp.route('/login', methods=['GET', 'POST'])
def account_login():
    from .models import User

    form = LoginForm()

    # User is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # Check if forms have valid information
    if form.validate_on_submit():
        if verify_recaptcha():
            userName = form.username.data
            raw_password = form.password.data

            # Find the user in the database
            query_user = User.query.filter_by(username=userName).first()

            # If user was not found
            if not query_user:
                #form.username.validators[0].message = "Invalid login"
                return render_template("login.html", form=form)
            
            # Check if the password matches
            if query_user.check_password(raw_password):
                print(f"[DEBUG LOG] Login was successful. User ID: {query_user.id}")
                
                # Add login session to browser
                #session['user_id'] = query_user.id
                login_user(query_user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page and not is_safe_url(next_page):
                    return abort(400)

                # ** Need to figure out where to store the last login, so we can display it before its updated to the current time **
                # update 'last login' date to now in database
                utc_now = datetime.datetime.now(pytz.utc)
                pacific_tmz = pytz.timezone("America/Los_Angeles")
                pacific_now = utc_now.astimezone(pacific_tmz)
                query_user.now_login = pacific_now

                try:
                    db.session.commit()
                    print(f"[DEBUG LOG] Successfully updated database for '{query_user.username}' time logged in: {query_user.last_login}")
                except Exception as e:
                    db.session.rollback()
                    print(f"[DEBUG LOG] There was an internal error: {e}")
                finally:
                    return redirect(next_page or url_for('main.dashboard'))
            else:
                flash("You entered the wrong password!", "error")
                print("[DEBUG LOG] Login attempt failed.")
                return render_template("login.html", form=form)
        else:
            print("reCaptcha was not verified!")
        
    return render_template("login.html", form=form)

# User Logout
@main_bp.route('/logout')
@login_required
def handle_logout():
    # Remove user from session & redirect to login page
    logout_user()
    return redirect(url_for('main.account_login'))

# ------------------------------------------------------------------------
# Fumbld AI API
@main_bp.route('/api/<provider>/leagues/<league_id>/recommendations', methods=['GET'])
@login_required
def get_ai_rec(provider, league_id):
    try:
        with limiter.limit("1 per 2 minutes"):
            if provider == "yahoo":
                current_roster = yahoo_get_roster(league_id)
            elif provider == "sleeper":
                sleeper_query = SleeperLeague.query.filter_by(user_id=current_user.id).first()
                current_roster = get_sleeper_roster(league_id, sleeper_query.sleeper_username)
            
            # Separate the URL from the player dictionary
            parsed_roster = []
            parsed_url = []
            for roster in current_roster:
                parsed_roster.append({
                    'n': roster['name'],
                    'p': roster['position']
                })

                parsed_url.append({
                    'name': roster['name'],
                    'url': roster['url']
                })
            
            ai_response = gemini_call(parsed_roster)
            import json
            import re

            # Extrct the JSON block between --- markers in gpt response
            # --- three dashes in string
            # \s* match any whitespace
            # (\[.*?\]) match and capture a json style list inside of [ ]
            json_match = re.search(r"---\s*(\[.*?\])\s*---", ai_response, re.DOTALL)
            if json_match:
                # return the captured group
                json_part = json_match.group(1)
                # parse the json string into a dictionary
                players = json.loads(json_part)
            else:
                return jsonify({'error': 'There was an error making an AI call.'})
            
            # Extract the reason text in gpt response
            # start search starting with reason:
            # \s* optional whitespace after reason
            # (.*) capture group that grabs everything after the optional whitespace
            reason_match = re.search(r"Reason:\s*(.*)", ai_response, re.DOTALL)
            if reason_match:
                reason = reason_match.group(1).strip()
            else:
                return jsonify({'error': 'There was an error making an AI call.'})
            
            # Add URL back into AI response
            for player in players:
                for urls in parsed_url:
                    if player['name'] == urls['name']:
                        player['url'] = urls['url']

            response = {
                'players': players,
                'reason': reason
            }
            
            return jsonify(response), 201
    except RateLimitExceeded:
        return jsonify({"error": "Please allow two minutes in between Fumbld AI calls."})

@main_bp.route('/api/<provider>/leagues/<league_id>/roster', methods=['GET'])
@login_required
def get_roster(provider, league_id):
    if provider == "yahoo":
        if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
            abort(403)

        return jsonify(yahoo_get_roster(league_id)), 201
    elif provider == "sleeper":
        # Query database for sleeper data
        sleeper_query = SleeperLeague.query.filter_by(
            user_id=current_user.id,
            sleeper_league_id=league_id
        ).first()

        return jsonify(get_sleeper_roster(league_id, sleeper_query.sleeper_username)), 201



@main_bp.route('/api/<provider>/leagues', methods=['GET'])
@login_required
def get_leagues(provider):
    if provider == "yahoo":
        if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
            abort(403)

        return jsonify(yahoo_get_league()), 201
    elif provider == "sleeper":
        sleeper_query = SleeperLeague.query.filter_by(user_id=current_user.id).first()
    
        return jsonify(get_sleeper_leagues(sleeper_query.sleeper_user_id))
        
@main_bp.route('/api/<provider>/leagues/refresh', methods=['POST'])
@login_required
def refresh_roster(provider):
    try:
        with limiter.limit("1 per minute"):
            if provider == "yahoo":
                if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
                    abort(403)
                    # Log a warning here, user should not be able to access this without being authenticated with yahoo.
                    return jsonify({"error": "There was an error refreshing your Yahoo! data. Try reauthenticating yourself with Yahoo!"}), 403

                try:
                    # Delete all yahoo related entries in the database and refresh
                    yahoo_refresh()
                    return jsonify({"success": "Yahoo! Sports refresh has comepleted. Thanks for waiting! 🏈🏆"}), 200
                except:
                    # Log error here <---------------
                    return jsonify({"error": "There was an error refreshing your Yahoo! data. Please submit an error report."}), 500
    except RateLimitExceeded:
        return jsonify({"error": "Please give one minute in between Yahoo refresh."})

@main_bp.errorhandler(403)
def forbidden_error(error):
    return render_template("/errors/403.html"), 403

# ------------------------------------------------------------
# Sleeper Integration
from .sleeper import setup_sleeper
@main_bp.route('/api/users/me/sleeper/setup', methods=['POST'])
@login_required
def set_sleeper_username():
    sleeper_username_form = SleeperForm()
    # query_sleeper = SleeperLeague.query.filter_by(user_id=current_user.id).first()

    if sleeper_username_form.validate_on_submit():
        # Check if sleeper data exist and handle it
        username = sleeper_username_form.sleeper_username.data
        setup_sleeper(username)
        return jsonify({'success': f'Sleeper data successfully saved from sleeper acount: {username}'})
    else:
        return jsonify({'error': 'Please enter your sleeper username'})

# ------------------------------------------------------------
# Backend Function Calls

# User Change Password
@main_bp.route('/api/users/me/password', methods=['POST'])
@login_required
def change_password():
    from .models import User

    pass_reset_form = ChangePasswordForm()
    if pass_reset_form.validate_on_submit():
        curr_password = pass_reset_form.current_password.data
        new_password = pass_reset_form.new_password.data

        query_user = User.query.filter_by(id=current_user.id).first()
        if query_user.check_password(curr_password):
            # Password was correct, continue
            query_user.set_password(new_password)
            try:
                db.session.commit()
                return jsonify({"success": "Your password has been changed."}), 200
            except:
                return jsonify({"error": "There was an error writing to the database."}), 500
        else:
            return jsonify({"error": "Current password entered was not correct."}), 403
    else:
        return jsonify({"error": "Password in confirmation form does not patch new password."}), 400
    
@main_bp.route('/api/admin/generate-reg-code', methods=['POST'])
@login_required
def generate_reg_code():
    print("called")
    if current_user.role != "admin":
        return jsonify({"error": "You are not authorized to access this function."}), 403
    
    import string, random

    characters = string.ascii_uppercase + string.digits # A-Z and 0-9

    # Generate a random code
    reg_code = ''.join(random.choice(characters) for _ in range(6))

    # Make sure the code generated does not exist in the DB already
    while RegCodes.query.filter_by(reg_code=reg_code).first():
        reg_code = ''.join(random.choice(characters) for _ in range(6))
    
    # Create new registration code
    new_reg_code = RegCodes(reg_code=reg_code, used=False, created_by=current_user.username)

    try:
        db.session.add(new_reg_code)
        db.session.commit()
        return jsonify({
            "success": f"Registration code '{reg_code}' has been generated successfully.",
            "reg_code": reg_code
        }), 201
    except Exception as e:
        return jsonify({"error": "There was an error saving the registration code to the database."}), 500
    
