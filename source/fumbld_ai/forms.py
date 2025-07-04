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
        DataRequired(message="Username is required."),
        Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
    ])

    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    submit = SubmitField("Login")

    remember = BooleanField("Remember Me")

# '/change-password' form
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[
        DataRequired(message="Current password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    new_password = PasswordField("New Password", validators=[
        DataRequired(message="New password is required."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])

    confirm_new_password = PasswordField("Confirm New Password", validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo('new_password', message="Passwords must match")
    ])

    submit = SubmitField("Change Password")