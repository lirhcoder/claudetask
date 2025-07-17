import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    CLAUDE_CODE_PATH = os.environ.get('CLAUDE_CODE_PATH', 'claude')
    MAX_CONCURRENT_TASKS = int(os.environ.get('MAX_CONCURRENT_TASKS', '5'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.txt', '.md', '.html', '.css'}
    
    # Socket.IO settings
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_ENABLED = os.environ.get('SOCKETIO_ENABLED', 'true').lower() == 'true'
    
    # Security settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Project workspace
    PROJECTS_DIR = Path(os.environ.get('PROJECTS_DIR', './projects'))
    PROJECTS_DIR.mkdir(exist_ok=True)
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}