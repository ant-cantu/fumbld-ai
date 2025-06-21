# models.py
from .utils import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    # Username column, string 30 characters, must be unique, must not be empty
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_login = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    now_login = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    # Relationship with Roster
    roster = db.relationship('Roster', backref='team', lazy=True, cascade="all, delete-orphan")

    # Relationship to the YahooToken table
    # 'uselist=False' makes this a one-to-one relationship from the User side
    # 'back_populates' connects it to the 'user' attribute in YahooToken
    yahoo_token = db.relationship("YahooToken", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        """
        Take plain text and generate password hash
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """
        Compare the plain-text password with
        the stored has.

        Returns True if matched, otherwise False
        """
        return check_password_hash(self.password_hash, password)
    
    def __init__(self, username, email):
        self.username = username
        self.email = email

    # String representation for debugging
    def __repr__(self):
        return f"<user {self.username}>"

# Probably get rid of this
class Roster(db.Model):
    __tablename__ = "roster"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)
    # Store roster information in this table
    sleeper_id = db.Column(db.String(30), unique=True, nullable=False)
    league_id = db.Column(db.String(30), unique=True, nullable=True)
    season = db.Column(db.DateTime, nullable=False) 
    
    # Foreign key defintion
    # (Integer ID, users.id refers to 'id' in users table, must not be empty)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 

    def __init__(self, sleeper_id, league_id, season, user_id):
        self.sleeper_id = sleeper_id
        self.league_id = league_id
        self.season = season
        self.user_id = user_id

# Save Yahoo! credentials
class YahooToken(db.Model):
    __tablename__ = 'yahoo_tokens'

    # Primary key for this table
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key to link to the User table
    # 'users.id' refers to the 'id' column in the 'users' table
    # unique=True enforces the one-to-one
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Yahoo OAuth fields
    access_token = db.Column(db.String(1024), nullable=True)
    refresh_token = db.Column(db.String(1024), nullable=True)
    token_type = db.Column(db.String(50), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # Relationship back to the User table
    # 'back_populates' connects it to the 'yahoo_token' attribute in User
    user = db.relationship("User", back_populates="yahoo_token")

    def __repr__(self):
        return f'<YahooToken for User ID: {self.user_id}>'