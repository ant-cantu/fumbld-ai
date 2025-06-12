import os
from flask import Flask
from gridiron_ai.utils import db
from dotenv import load_dotenv # Development Stage ONLY
from gridiron_ai.routes import main_bp
from gridiron_ai.utils import yahoo_bp

def init_app():
    # Load environment variables
    load_dotenv() # <- Development Stage ONLY

    # Configure application
    app = Flask(__name__)

    # DB File Location
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "gridiron.db")

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