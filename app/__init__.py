from flask import Flask
from dotenv import load_dotenv
from .config import Config

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        from .routes import calendar_bp
        app.register_blueprint(calendar_bp)
    
    return app
