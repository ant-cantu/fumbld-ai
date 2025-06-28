from flask import render_template, Blueprint, flash, redirect, url_for, request, abort, jsonify
import pytz, datetime
from .yahoo_fantasy import yahoo_get_roster, yahoo_get_opp_roster, yahoo_get_league, yahoo_refresh
from .utils import db, is_safe_url
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required


main_bp = Blueprint('main', __name__, template_folder='templates')

# Defining Root Page
@main_bp.route('/')
def home():
    return render_template("index.html")

# User Dashboard
@main_bp.route("/dashboard")
@login_required
def dashboard():
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

    return render_template("dashboard.html",
                            username=current_user.username,
                            last_login=last_login)#,
                            #user_team=team_starters,
                            #opp_team=opp_starters)
    
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
        userName = form.username.data
        userEmail = form.email.data
        password = form.password.data

        # Check for existing user
        # SQL Equivalent: SELECT * FROM user WHERE username = '<username>' LIMIT 1;
        existing_user = User.query.filter_by(username=userName).first()
        if existing_user:
            flash("The username already exists, please choose another.", "error")
            return render_template("registration.html", form=form)
        
        # Check if existing email
        exisiting_email = User.query.filter_by(email=userEmail).first()
        if exisiting_email:
            flash("This email is already registered!", "error")
            return render_template("registration.html", form=form)

        # Pass user name, email and hash from forms and store into DB
        new_user = User(username=userName, email=userEmail)
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

@main_bp.route('/fetch/yahoo/roster', methods=['GET'])
@login_required
def get_roster():
    if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
        abort(403)

    # /fetch/yahoo/roster?league_id=423.l.1215322
    league_id = request.args.get('league-id', '')

    return jsonify(yahoo_get_roster(league_id)), 201

@main_bp.route('/fetch/yahoo/leagues', methods=['GET'])
@login_required
def get_leagues():
    if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
        abort(403)

    return jsonify(yahoo_get_league()), 201

@main_bp.route('/fetch/yahoo/refresh', methods=['GET'])
@login_required
def refresh_roster():
    if not current_user or not current_user.yahoo_token or not current_user.yahoo_token.access_token:
        abort(403)

    # Delete all yahoo related entries in the database and refresh
    yahoo_refresh()

    return jsonify({"status": "success", "message": f"Roster refreshed for user id: {current_user.id}"})

@main_bp.errorhandler(403)
def forbidden_error(error):
    return render_template("/errors/403.html"), 403