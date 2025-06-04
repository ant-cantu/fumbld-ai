# models.py
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(db.Model):
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