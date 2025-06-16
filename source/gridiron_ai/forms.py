# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# '/register' form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
    ])

    email = StringField("Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Please enter a valid email.")
    ])

    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
        # 'password' refers to variable password above
    ])

    submit = SubmitField("Register")

# '/login' form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(message="Username is required, please enter a username."),
        Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
    ])

    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    submit = SubmitField("Login")

    remember = BooleanField("Remember Me")