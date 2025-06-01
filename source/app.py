import os
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from flask import Flask, render_template, flash, redirect
from models import User #, Roster
from forms import RegistrationForm

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
    @app.route("/register", methods=["GET", "POST"])
    def register():
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
            
            exisiting_email = User.query.filter_by(email=userEmail).first()
            if exisiting_email:
                flash("This email is already registered!", "error")
                return render_template("registration.html", form=form)

            # Pass user name, email and hash from forms and store into DB
            new_user = User(username=userName, email=userEmail)
            new_user.set_password(password)

            try:
                # Add new_user to session query
                db.session.add(new_user)
                # Save the changes to the database
                db.session.commit()
                flash("Account successfully created! You can now log in!", "success")
                return redirect("index.html")
            except Exception as e:
                # Rollback changes made to database incase of error
                db.session.rollback()
                flash("There was an internal error with creating the account.", "error")
                return render_template("registration.html", form=form)
        return render_template("registration.html", form=form)

            
    # User Login


    # User Logout
    return app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)