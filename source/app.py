import os
from flask import Flask
from fumbld_ai.utils import db, TokenEncryptor
from dotenv import load_dotenv # Development Stage ONLY
from fumbld_ai.routes import main_bp
from fumbld_ai.utils import yahoo_bp
from fumbld_ai.models import User
from flask_login import LoginManager

def init_app():
    # Load environment variables
    load_dotenv() # <- Development Stage ONLY

    # Configure application
    app = Flask(__name__)

    # DB File Location
    # THIS IS FOR DEV ONLY, PRODUCTION WILL BE MOVED TO A MORE SECURE DATABASE
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "fumbld.db")

    # Disable Modification Warnings
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    # Super Duper Secret Key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Yahoo OAuth Credentials
    app.config['YAHOO_CONSUMER_KEY'] = os.environ.get('YAHOO_CONSUMER_KEY')
    app.config['YAHOO_CONSUMER_SECRET'] = os.environ.get('YAHOO_CONSUMER_SECRET')

    if not app.config['YAHOO_CONSUMER_KEY'] or \
       not app.config['YAHOO_CONSUMER_SECRET']:
        print("[CRITICAL]: Yahoo OAuth credentials are not fully configured in .env.")
        print("[CRITICAL] Terminating Application")
        return 
    
    # OpenAI Key
    app.config['OPENAI_KEY'] = os.environ.get('OPENAI_KEY')

    if not app.config['OPENAI_KEY']:
        print("[CRITICAL] OpenAI Key not configured correctly.")
        print('[CRITICAL] Terminating Application')
        return
    
    # TLogin Manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "main.account_login"
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        # return User.query.get(int(user_id))
    
    # # Generate Key
    # from cryptography.fernet import Fernet
    # key = Fernet.generate_key()
    # print(key)

    # Initialize SQLAlchemy
    db.init_app(app)
    with app.app_context():
        db.create_all()    
        
    app.register_blueprint(main_bp)
    app.register_blueprint(yahoo_bp)

    return app

app = init_app()

if __name__ == "__main__":
    app.run(debug=True)