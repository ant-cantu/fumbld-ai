import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from fumbld_ai.utils import db, limiter, crsf
from fumbld_ai.routes import main_bp
from fumbld_ai.utils import yahoo_bp
from fumbld_ai.models import User
from flask_login import LoginManager

def init_app():
    # Load environment variables
    # load_dotenv() # <- Development Stage ONLY

    # Configure application
    app = Flask(__name__)

    # App Environment
    app.config['APP_ENV'] = os.getenv("APP_ENV", "production")

    # Initialize Logging --------------
    if app.config['APP_ENV'] == "development":
        log_dir = 'logs'
    else:
        log_dir = '/app/logs'
    
    # Create the logs directory
    os.makedirs(log_dir, exist_ok=True)

    # File path for log file
    log_file = os.path.join(log_dir, 'fumbld.log')

    # Setup Logger
    logger = logging.getLogger("fumbld_logger")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Logging Format
    log_format = logging.Formatter("[%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s()]: %(message)s")

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024, 
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)

    # End Logger Set Up -----------------

    # PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    # Disable Modification Warnings
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

    # Super Duper Secret Key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # Encrypt Key
    app.config['ENCRYPT_KEY'] = os.environ.get('ENCRYPT_KEY')

    # Yahoo OAuth Credentials
    if app.config['APP_ENV'] == "development":
        app.config['YAHOO_CONSUMER_KEY'] = os.environ.get('DEV_YAHOO_CONSUMER_KEY')
        app.config['YAHOO_CONSUMER_SECRET'] = os.environ.get('DEV_YAHOO_CONSUMER_SECRET')
    else:
        app.config['YAHOO_CONSUMER_KEY'] = os.environ.get('YAHOO_CONSUMER_KEY')
        app.config['YAHOO_CONSUMER_SECRET'] = os.environ.get('YAHOO_CONSUMER_SECRET')

    if not app.config['YAHOO_CONSUMER_KEY'] or \
       not app.config['YAHOO_CONSUMER_SECRET']:
        logger.critical("Yahoo OAuth credentials are not fully configured in .env.")
        logger.critical("Terminating Application")
        return 
    
    # OpenAI Key
    app.config['OPENAI_KEY'] = os.environ.get('OPENAI_KEY')

    if not app.config['OPENAI_KEY']:
        logger.critical("OpenAI Key not configured correctly.")
        logger.critical("Terminating Application")
        return
    
    # Gemini Key
    app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')
    
    # Google reCaptcha Key
    app.config['GOOGLE_CAPTCHA_KEY'] = os.environ.get('GOOGLE_CAPTCHA_KEY')
    
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
    
    # Initialize Flask-Limiter
    if app.config['APP_ENV'] == "development":
        app.config['RATELIMIT_STORAGE_URI'] = 'memory://'
        logger.debug('Using memory storage for rate limiting (development)')
    else:
        app.config['RATELIMIT_STORAGE_URI'] = 'redis://redis:6379/0'
        logger.debug('Using Redis for rate limiting (production)')

    limiter.init_app(app)

    # Initialize CSRF Protection
    crsf.init_app(app)

    # Initialize SQLAlchemy
    db.init_app(app)
    with app.app_context():
        db.create_all()    
        
    app.register_blueprint(main_bp)
    app.register_blueprint(yahoo_bp)

    return app

app = init_app()

# if __name__ == "__main__":
#    app.run(host="0.0.0.0", port="5000", debug=True)