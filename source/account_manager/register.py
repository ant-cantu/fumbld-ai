# account_manager.py
from flask import render_template, flash, redirect, url_for
from forms import RegistrationForm
from models import User
from extensions import db

# User Registration
def account_register():
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

        try:
            # Add new_user to session query
            db.session.add(new_user)
            # Save the changes to the database
            db.session.commit()
            flash("Account successfully created! You can now log in!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            # Rollback changes made to database incase of error
            db.session.rollback()
            flash("There was an internal error with creating the account.", "error")
            return render_template("registration.html", form=form)
    return render_template("registration.html", form=form)