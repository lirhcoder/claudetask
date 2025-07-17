import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # 根据环境加载不同的配置文件
    env_files = ['.env', '.env.local']
    
    # WSL 环境特殊配置
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                env_files.insert(0, '.env.wsl')
    except:
        pass
    
    # 加载第一个存在的配置文件
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded configuration from {env_file}")
            break
    else:
        load_dotenv()  # 默认加载 .env
        
except ImportError:
    pass  # dotenv not installed, use system environment variables

# 自动检测 Claude 路径
try:
    from utils.claude_detector import detect_claude_path
    detected_claude_path = detect_claude_path()
except:
    detected_claude_path = None

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # 优先使用环境变量，其次使用自动检测，最后使用默认值
    CLAUDE_CODE_PATH = os.environ.get('CLAUDE_CODE_PATH') or detected_claude_path or 'claude'
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