from flask import Flask
from dotenv import load_dotenv
from .config import Config
import os

load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the instance folder exists for Flask if you use instance-relative config
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Set a default secret key if not set, required for session
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)
    
    # It's generally better to import and register blueprints outside app_context
    # unless strictly necessary for some specific initialization within the context.
    from .routes import calendar_bp # Import blueprint
    app.register_blueprint(calendar_bp) # Register without prefix based on test expectations

    # If you have other blueprints or extensions, initialize them here
    
    return app
