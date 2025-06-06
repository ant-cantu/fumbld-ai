# In your yahoo_utils.py or models.py file

from datetime import datetime, timedelta
from extensions import db  # Adjust this to import your database instance

def update_token_in_db(user, token):
    """
    Saves the new token dictionary to the database for a given user.
    This is the callback function used by requests-oauthlib.
    """
    print("--- Running token_updater callback to save new token ---")
    
    # Update all the critical fields
    user.yahoo_token.access_token = token['access_token']
    user.yahoo_token.refresh_token = token['refresh_token']  # <-- THE CRITICAL LINE
    user.yahoo_token.token_type = token['token_type']
    
    # Calculate the new expiry time from the 'expires_in' field
    user.yahoo_token.token_expiry = datetime.utcnow() + timedelta(seconds=token['expires_in'])
    
    try:
        # Commit the changes to the database
        db.session.commit()
        print("--- Successfully saved new token to the database. ---")
    except Exception as e:
        db.session.rollback()
        print(f"--- FAILED to save new token to the database: {e} ---")