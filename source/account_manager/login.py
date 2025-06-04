# login.py
from flask import render_template, flash, redirect, session, url_for
from forms import LoginForm
from models import User
from extensions import db
from datetime import datetime, timezone
import pytz

def account_login():
    form = LoginForm()

    # Check if user is logged in already
    if 'user_id' in session:
        print("[DEBUG LOG] User is logged in already.")
        flash("You are already logged in.", "info")
        return redirect(url_for('dashboard'))

    # Check if forms have valid information
    if form.validate_on_submit():
        userName = form.username.data
        raw_password = form.password.data

        # Find the user in the database
        query_user = User.query.filter_by(username=userName).first()

        # If user was not found
        if not query_user:
            flash("Username was not found!", "error")
            return render_template("login.html", form=form)
        
        # Check if the password matches
        if query_user.check_password(raw_password):
            flash("Successfully logged in!", "success")
            print(f"[DEBUG LOG] Login was successful. User ID: {query_user.id}")
            
            # Add login session to browser
            session['user_id'] = query_user.id

            # ** Need to figure out where to store the last login, so we can display it before its updated to the current time **
            # update 'last login' date to now in database
            utc_now = datetime.now(pytz.utc)
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
                return redirect(url_for('dashboard'))
        else:
            flash("You entered the wrong password!", "error")
            print("[DEBUG LOG] Login attempt failed.")
            return render_template("login.html", form=form)
        
    return render_template("login.html", form=form)