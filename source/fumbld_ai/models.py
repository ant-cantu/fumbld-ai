# models.py
from .utils import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_login import UserMixin
from sqlalchemy import JSON

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
    yahoo_rosters = db.relationship('YahooRoster', back_populates='user', lazy=True, cascade="all, delete-orphan")

    # Relationship with UserLeagues
    user_leagues = db.relationship('UserLeagues', back_populates='user', lazy=True, cascade="all, delete-orphan")

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
    
class UserLeagues(db.Model):
    __tablename__ = "user_league"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    league_type = db.Column(db.String(10), unique=False, nullable=False)
    league_id = db.Column(db.String(25), unique=True, nullable=False)
    league_name = db.Column(db.String(45), unique=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="user_leagues")

    def __init__(self, league_type, league_id, league_name, user=None):
        self.league_type = league_type
        self.league_id = league_id
        self.league_name = league_name
        self.user = user
    
# Probably get rid of this
class YahooRoster(db.Model):
    __tablename__ = "yahoo_roster"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    # Store roster information in this table
    yahoo_league_id = db.Column(db.String(20), unique=True, nullable=False)
    yahoo_roster = db.Column(JSON)
    
    # Foreign key defintion
    # (Integer ID, users.id refers to 'id' in users table, must not be empty)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 

    user = db.relationship("User", back_populates="yahoo_rosters")

    def __init__(self, yahoo_league_id, yahoo_roster, user=None):
        self.yahoo_league_id = yahoo_league_id
        self.yahoo_roster = yahoo_roster
        self.user = user

    def __repr__(self):
        return f"{self.yahoo_roster}"