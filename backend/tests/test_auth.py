"""
认证相关功能的单元测试
"""
import pytest
import json
from models.user import UserManager


class TestAuthentication:
    """测试认证功能"""
    
    def test_login_success(self, client):
        """测试成功登录"""
        # 先创建测试用户
        user_manager = UserManager()
        user_manager.create_user(
            email="login@example.com",
            username="loginuser",
            password="password123"
        )
        
        # 尝试登录
        response = client.post('/login', json={
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == '登录成功'
        assert 'user' in data
        assert data['user']['email'] == 'login@example.com'
        
        # 检查是否设置了 session cookie
        assert 'Set-Cookie' in response.headers
        assert 'session=' in response.headers['Set-Cookie']
    
    def test_login_invalid_email(self, client):
        """测试无效邮箱登录"""
        response = client.post('/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert '邮箱或密码错误' in data['error']
    
    def test_login_invalid_password(self, client):
        """测试错误密码登录"""
        # 先创建测试用户
        user_manager = UserManager()
        user_manager.create_user(
            email="wrongpass@example.com",
            username="wrongpassuser",
            password="correctpassword"
        )
        
        response = client.post('/login', json={
            'email': 'wrongpass@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert '邮箱或密码错误' in data['error']
    
    def test_login_missing_fields(self, client):
        """测试缺少字段的登录请求"""
        # 缺少邮箱
        response = client.post('/login', json={
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert '请输入邮箱和密码' in data['error']
        
        # 缺少密码
        response = client.post('/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert '请输入邮箱和密码' in data['error']
    
    def test_login_empty_fields(self, client):
        """测试空字段的登录请求"""
        response = client.post('/login', json={
            'email': '',
            'password': ''
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert '请输入邮箱和密码' in data['error']
    
    def test_logout(self, client, auth_headers):
        """测试登出功能"""
        response = client.post('/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == '已退出登录'
    
    def test_protected_route_without_auth(self, client):
        """测试未认证访问受保护路由"""
        # 尝试访问需要认证的 API
        response = client.get('/api/v2/dashboard')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Authentication required'
    
    def test_protected_route_with_auth(self, client, auth_headers):
        """测试已认证访问受保护路由"""
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        
        assert response.status_code == 200
        # 不应该返回认证错误
        data = json.loads(response.data)
        assert 'error' not in data or data.get('error') != 'Authentication required'
    
    def test_session_persistence(self, client):
        """测试 session 持久性"""
        # 创建并登录用户
        user_manager = UserManager()
        user_manager.create_user(
            email="session@example.com",
            username="sessionuser",
            password="password123"
        )
        
        # 登录
        response = client.post('/login', json={
            'email': 'session@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        
        # 使用同一个客户端访问受保护的路由
        # Flask 测试客户端会自动保持 cookies
        response = client.get('/api/v2/dashboard')
        assert response.status_code == 200
        
        # 登出
        response = client.post('/logout')
        assert response.status_code == 200
        
        # 登出后应该无法访问受保护的路由
        response = client.get('/api/v2/dashboard')
        assert response.status_code == 401
    
    def test_case_insensitive_email(self, client):
        """测试邮箱大小写不敏感"""
        user_manager = UserManager()
        user_manager.create_user(
            email="CaseSensitive@Example.COM",
            username="caseuser",
            password="password123"
        )
        
        # 使用不同大小写的邮箱登录
        response = client.post('/login', json={
            'email': 'casesensitive@example.com',  # 全小写
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # 存储的邮箱应该是小写的
        assert data['user']['email'] == 'casesensitive@example.com'


class TestUserManagement:
    """测试用户管理功能"""
    
    def test_create_user(self):
        """测试创建用户"""
        user_manager = UserManager()
        user = user_manager.create_user(
            email="newuser@example.com",
            username="newuser",
            password="password123"
        )
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.id is not None
        
        # 密码应该被加密
        assert user.password_hash != "password123"
        assert user.check_password("password123") == True
        assert user.check_password("wrongpassword") == False
    
    def test_duplicate_email(self):
        """测试重复邮箱"""
        user_manager = UserManager()
        
        # 创建第一个用户
        user1 = user_manager.create_user(
            email="duplicate@example.com",
            username="user1",
            password="password123"
        )
        assert user1 is not None
        
        # 尝试创建相同邮箱的用户
        with pytest.raises(Exception) as exc_info:
            user_manager.create_user(
                email="duplicate@example.com",
                username="user2",
                password="password456"
            )
        
        assert "already exists" in str(exc_info.value)
    
    def test_get_user_by_email(self):
        """测试通过邮箱获取用户"""
        user_manager = UserManager()
        
        # 创建用户
        created_user = user_manager.create_user(
            email="findme@example.com",
            username="findmeuser",
            password="password123"
        )
        
        # 通过邮箱查找
        found_user = user_manager.get_user_by_email("findme@example.com")
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "findme@example.com"
        
        # 查找不存在的用户
        not_found = user_manager.get_user_by_email("notexist@example.com")
        assert not_found is None