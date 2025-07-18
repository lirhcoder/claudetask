"""
认证相关的路由
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps
import re
from models.user import UserManager, User, SystemConfig

auth_bp = Blueprint('auth', __name__)
user_manager = UserManager()

def login_required(f):
    """需要登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """需要管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user = user_manager.get_user_by_id(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    username = data.get('username', '').strip()
    
    # 验证邮箱格式
    if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'error': '请输入有效的邮箱地址'}), 400
        
    # 验证密码
    if not password or len(password) < 6:
        return jsonify({'error': '密码至少需要6个字符'}), 400
        
    # 验证邮箱域名
    if not user_manager.validate_email_domain(email):
        config = user_manager.get_system_config()
        return jsonify({
            'error': f'只允许使用 @{config.allowed_email_domain.lstrip("@")} 邮箱注册'
        }), 400
        
    # 创建用户
    user = user_manager.create_user(email, password, username)
    if not user:
        return jsonify({'error': '该邮箱已被注册'}), 400
        
    # 自动登录
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['is_admin'] = user.is_admin
    user_manager.update_last_login(user.id)
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': '请输入邮箱和密码'}), 400
        
    # 获取用户
    user = user_manager.get_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'error': '邮箱或密码错误'}), 401
        
    # 设置会话
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['is_admin'] = user.is_admin
    user_manager.update_last_login(user.id)
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'message': '已登出'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    user = user_manager.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/config', methods=['GET'])
def get_config():
    """获取系统配置（公开接口，用于显示注册要求）"""
    config = user_manager.get_system_config()
    return jsonify({
        'allowed_email_domain': config.allowed_email_domain,
        'require_email_verification': config.require_email_verification
    }), 200

@auth_bp.route('/admin/config', methods=['GET'])
@admin_required
def get_admin_config():
    """获取完整系统配置（管理员）"""
    config = user_manager.get_system_config()
    return jsonify(config.to_dict()), 200

@auth_bp.route('/admin/config', methods=['PUT'])
@admin_required
def update_admin_config():
    """更新系统配置（管理员）"""
    data = request.get_json()
    config = user_manager.get_system_config()
    
    if 'allowed_email_domain' in data:
        domain = data['allowed_email_domain'].strip()
        if domain and not domain.startswith('@'):
            domain = '@' + domain
        config.allowed_email_domain = domain
        
    if 'require_email_verification' in data:
        config.require_email_verification = bool(data['require_email_verification'])
        
    if 'super_admin_email' in data:
        config.super_admin_email = data['super_admin_email']
        
    user_manager.update_system_config(config)
    
    return jsonify({
        'message': '配置已更新',
        'config': config.to_dict()
    }), 200

@auth_bp.route('/admin/users', methods=['GET'])
@admin_required
def list_users():
    """获取所有用户列表（管理员）"""
    users = user_manager.list_users()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@auth_bp.route('/admin/users/<user_id>/make-admin', methods=['POST'])
@admin_required
def make_admin(user_id):
    """设置用户为管理员（管理员）"""
    user = user_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 使用新的方法更新管理员状态
    user_manager.make_user_admin(user_id)
    user.is_admin = True
    
    return jsonify({
        'message': '已设置为管理员',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/admin/users/register', methods=['POST'])
@admin_required
def admin_register_user():
    """管理员直接注册新用户"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    claude_token = data.get('claude_token', '').strip()
    is_admin = data.get('is_admin', False)
    
    # 验证邮箱格式
    if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'error': '请输入有效的邮箱地址'}), 400
    
    # 生成默认密码：邮箱前缀 + 123456
    default_password = email.split('@')[0] + '123456'
    
    # 创建用户
    user = user_manager.create_user(
        email=email, 
        password=default_password, 
        username=username,
        claude_token=claude_token if claude_token else None,
        is_admin=is_admin
    )
    
    if not user:
        return jsonify({'error': '该邮箱已被注册'}), 400
    
    return jsonify({
        'message': '用户创建成功',
        'user': user.to_dict(),
        'default_password': default_password
    }), 201

@auth_bp.route('/admin/users/<user_id>/claude-token', methods=['PUT'])
@admin_required
def update_user_claude_token(user_id):
    """更新用户的Claude token（管理员）"""
    data = request.get_json()
    claude_token = data.get('claude_token', '').strip()
    
    user = user_manager.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 更新token
    user_manager.update_claude_token(user_id, claude_token)
    user.claude_token = claude_token
    
    return jsonify({
        'message': 'Claude token已更新',
        'user': user.to_dict()
    }), 200