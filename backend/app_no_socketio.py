"""
Simple Flask app without Socket.IO for basic functionality
"""
import os
from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize CORS only
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from routes.api import api_bp
    from routes.unified_api import unified_bp
    from routes.auth import auth_bp
    from routes.repository_api import repo_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(unified_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(repo_bp, url_prefix='/api')
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

app = create_app()

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running Flask without Socket.IO - Real-time features disabled")
    print("Tasks will still execute, but without real-time output streaming")
    print(f"Claude path: {app.config.get('CLAUDE_CODE_PATH', 'claude')}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)