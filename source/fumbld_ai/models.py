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
    role = db.Column(db.String(5), default="user", unique=False, nullable=False)
    accepted_terms = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship with Yahoo roster
    yahoo_leagues = db.relationship('YahooLeague', back_populates='user', lazy=True, cascade="all, delete-orphan")

    # Relationship with Sleeper roster
    sleeper_leagues = db.relationship('SleeperLeague', back_populates='user', lazy=True, cascade="all, delete-orphan")

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
    
    def __init__(self, username, email, role, accepted_terms):
        self.username = username
        self.email = email
        self.role = role
        self.accepted_terms = accepted_terms

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
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_type = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationship back to the User table
    # 'back_populates' connects it to the 'yahoo_token' attribute in User
    user = db.relationship("User", back_populates="yahoo_token")

    def __repr__(self):
        return f'<YahooToken for User ID: {self.user_id}>'
    
# Table for Yahoo! Sports data
class YahooLeague(db.Model):
    __tablename__ = "yahoo_league"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    # Store roster information in this table
    yahoo_league_id = db.Column(db.String(20), unique=False, nullable=False)
    yahoo_league_name = db.Column(db.String(45), unique=False, nullable=False)
    yahoo_roster = db.Column(JSON)
    
    # Foreign key defintion
    # (Integer ID, users.id refers to 'id' in users table, must not be empty)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 

    user = db.relationship("User", back_populates="yahoo_leagues")

    def __init__(self, yahoo_league_id, yahoo_league_name, yahoo_roster, user=None):
        self.yahoo_league_id = yahoo_league_id
        self.yahoo_league_name = yahoo_league_name
        self.yahoo_roster = yahoo_roster
        self.user = user

    def __repr__(self):
        return f"{self.yahoo_roster}"
    
class SleeperLeague(db.Model):
    __tablename__ = "sleeper_league"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    # Store roster information in this table
    sleeper_username = db.Column(db.String(35), unique=False, nullable=False)
    sleeper_user_id = db.Column(db.String(50), unique=False, nullable=False)
    sleeper_league_id = db.Column(db.String(20), unique=False, nullable=False)
    sleeper_league_name = db.Column(db.String(45), unique=False, nullable=False)
    sleeper_roster = db.Column(JSON)
    
    # Foreign key defintion
    # (Integer ID, users.id refers to 'id' in users table, must not be empty)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 

    user = db.relationship("User", back_populates="sleeper_leagues")

    def __init__(self, sleeper_username, sleeper_user_id, sleeper_league_id, sleeper_league_name, sleeper_roster, user=None):
        self.sleeper_username = sleeper_username
        self.sleeper_user_id = sleeper_user_id
        self.sleeper_league_id = sleeper_league_id
        self.sleeper_league_name = sleeper_league_name
        self.sleeper_roster = sleeper_roster
        self.user = user

    def __repr__(self):
        return f"{self.sleeper_roster}"
    
class RegCodes(db.Model):
    __tablename__ = "registration_codes"

    # ID Column (Primary Key)
    id = db.Column(db.Integer, primary_key=True)

    reg_code = db.Column(db.String(6), unique=True, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_by = db.Column(db.String(30), unique=True, nullable=True)
    created_by = db.Column(db.String(30), unique=False, nullable=False)

    def __init__(self, reg_code, used, created_by):
        self.reg_code = reg_code
        self.used = used
        self.created_by = created_by

    def __repr__(self):
        return f"<RegCode {self.reg_code} - Used: {self.used}>"