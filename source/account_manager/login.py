# login.py
from flask import render_template, flash, redirect
from forms import LoginForm
from models import User
from extensions import db

def account_login():
    form = LoginForm()

    if form.validate_on_submit():
        userName = form.username.data
        raw_password = form.password.data

        query_user = User.query.filter_by(username=userName).first()

        if not query_user:
            flash("Username was not found!", "error")
            return render_template("login.html", form=form)
        
        if query_user.check_password(raw_password):
            flash("Successfully logged in!", "success")
            print("[DEBUG LOG] Login was successful.")
            return redirect("login.html")
        else:
            flash("You entered the wrong password!", "error")
            print("[DEBUG LOG] Login attempt failed.")
            return render_template("login.html", form=form)
        
    return render_template("login.html", form=form)