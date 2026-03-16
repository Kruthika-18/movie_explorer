"""
app/__init__.py - Application Factory
----------------------------------------
This file creates and configures the Flask app.
Using the "Application Factory" pattern is a best practice
because it makes testing easier and avoids circular imports.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Initialize extensions (not yet bound to any app)
db = SQLAlchemy()
login_manager = LoginManager()

# Tell Flask-Login which route handles login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """
    Application factory function.
    Creates and returns a configured Flask app.
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Bind extensions to this app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register Blueprints (groups of related routes)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.media import media_bp
    from app.routes.user import user_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(media_bp, url_prefix='/media')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
