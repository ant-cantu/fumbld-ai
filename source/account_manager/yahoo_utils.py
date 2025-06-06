from extensions import db # Assuming 'db' is your SQLAlchemy instance
from models import User, YahooToken # Import your User and YahooToken models
from datetime import datetime, timedelta
from flask import session

def update_token_in_db(token_dict):
    """
    Callback function to update the user's token in the database.
    """
    # You need a way to identify the current user within this callback.
    # One common way is to use a request context if this is Flask-specific,
    # or pass the user_id when setting up the oauth object.
    # For this example, we'll assume you can get the user_id from the session.
    user_id = session.get('user_id')
    if not user_id:
        print("Error: Could not find user_id in session to update token.")
        return

    user_token = YahooToken.query.filter_by(user_id=user_id).first()
    if user_token:
        user_token.access_token = token_dict.get('access_token')
        user_token.refresh_token = token_dict.get('refresh_token')
        user_token.token_type = token_dict.get('token_type')
        expires_in = token_dict.get('expires_in', 3600)
        user_token.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        
        try:
            db.session.commit()
            print("Successfully updated token in the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating token in DB: {e}")