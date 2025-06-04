import os, pytz
from extensions import db
from flask import Flask, render_template, flash, redirect, session, url_for
from models import User #, Roster
import account_manager as account
from datetime import datetime

def init_app():
    # Configure application
    app = Flask(__name__)

    # DB File Location
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "gridiron.db")

    # Disable Modification Warnings
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    # Super Duper Secret Key
    app.config['SECRET_KEY'] = "fuh849r438ur4df8jwefi348r8234u2342394fjewfienfsjnvufghsh4839"

    # Initialize SQLAlchemy
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Defining Root Page
    @app.route('/')
    def home():
        message = f"Welcome to Gridiron AI"
        return render_template("index.html", message=message)

    # User Dashboard
    @app.route("/dashboard")
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
            
            utc_now = datetime.now(pytz.utc)
            pacific_tmz = pytz.timezone("America/Los_Angeles")
            pacific_now = utc_now.astimezone(pacific_tmz)
            query_user.last_login = pacific_now

        return render_template("dashboard.html",
                               username=query_user.username,
                               last_login=last_login)
        
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
    return app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)