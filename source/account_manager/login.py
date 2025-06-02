# login.py
from flask import render_template, flash, redirect, session, url_for
from forms import LoginForm
from models import User
from extensions import db

def account_login():
    form = LoginForm()

    # Check if user is logged in already
    if 'user_id' in session:
        print("[DEBUG LOG] User is logged in already.")
        flash("You are already logged in.", "info")
        return redirect(url_for('index'))

    if form.validate_on_submit():
        userName = form.username.data
        raw_password = form.password.data

        query_user = User.query.filter_by(username=userName).first()

        if not query_user:
            flash("Username was not found!", "error")
            return render_template("login.html", form=form)
        
        if query_user.check_password(raw_password):
            flash("Successfully logged in!", "success")
            print(f"[DEBUG LOG] Login was successful. User ID: {query_user.id}")
            
            # Add login session to browser
            session['user_id'] = query_user.id
            return redirect(url_for('index'))
        else:
            flash("You entered the wrong password!", "error")
            print("[DEBUG LOG] Login attempt failed.")
            return render_template("login.html", form=form)
        
    return render_template("login.html", form=form)