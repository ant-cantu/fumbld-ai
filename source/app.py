import os
from werkzeug.security import check_password_hash, generate_password_hash
import account_manager.login
from extensions import db
from flask import Flask, render_template, flash, redirect
from models import User #, Roster
import account_manager as account

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

    # Defining root page
    @app.route("/")
    def index():
        message = "Database Initialized"
        return render_template("index.html", message=message)

    # User Registration
    @app.route('/register', methods=['GET', 'POST'])
    def handle_reg():
        return account.account_register()
            
    # User Login
    @app.route('/login', methods=['GET', 'POST'])
    def handle_login():
        return account.account_login()

    # User Logout
    return app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)