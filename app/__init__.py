from flask import Flask, session
from flask_session import Session
from config import Config
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize session
    Session(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Add main routes
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        from app.utils.db import db_manager
        db_status = db_manager.test_connection()
        return {
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }
    
    return app
