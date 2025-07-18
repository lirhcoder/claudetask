import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config import config

socketio = SocketIO()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 设置会话密钥
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    # 只在启用时初始化 Socket.IO
    if app.config.get('SOCKETIO_ENABLED', True):
        socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'], 
                          async_mode=app.config['SOCKETIO_ASYNC_MODE'],
                          logger=False, engineio_logger=False)  # 减少日志输出
    
    # Register blueprints
    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.task_filesystem_api import task_fs_bp
    from routes.websocket import register_socketio_handlers
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(task_fs_bp, url_prefix='/api/taskfs')
    register_socketio_handlers(socketio)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)