"""
测试配置和固件
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app_no_socketio import create_app
from models.user import UserManager
from models.repository import RepositoryManager
from models.config import ConfigManager


@pytest.fixture
def app():
    """创建测试应用"""
    # 使用临时数据库
    db_fd, db_path = tempfile.mkstemp()
    
    # 创建测试配置
    test_config = {
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    }
    
    # 设置环境变量
    os.environ['DATABASE_PATH'] = db_path
    
    app = create_app()
    app.config.update(test_config)
    
    # 初始化数据库
    with app.app_context():
        # 这里可以添加数据库初始化代码
        pass
    
    yield app
    
    # 清理
    os.close(db_fd)
    os.unlink(db_path)
    if os.path.exists(test_config['UPLOAD_FOLDER']):
        import shutil
        shutil.rmtree(test_config['UPLOAD_FOLDER'])


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试运行器"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """创建认证头"""
    # 先创建测试用户
    user_manager = UserManager(db_path=os.environ.get('DATABASE_PATH'))
    test_user = user_manager.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123"
    )
    
    # 登录获取 session
    response = client.post('/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    # 返回带有 cookie 的 headers
    return {'Cookie': response.headers.get('Set-Cookie')}


@pytest.fixture
def test_user():
    """创建测试用户"""
    user_manager = UserManager(db_path=os.environ.get('DATABASE_PATH'))
    return user_manager.create_user(
        email="fixture@example.com",
        username="fixtureuser",
        password="fixturepass123"
    )


@pytest.fixture
def test_repo(test_user):
    """创建测试仓库"""
    repo_manager = RepositoryManager(
        db_path=os.environ.get('DATABASE_PATH'),
        workspace_path=tempfile.mkdtemp()
    )
    return repo_manager.create_repository(
        name="test-repo",
        owner_id=test_user.id,
        organization="test-org",
        description="Test repository"
    )