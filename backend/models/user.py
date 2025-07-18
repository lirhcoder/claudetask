"""
用户模型 - 管理用户认证和权限
"""
from datetime import datetime
import json
from pathlib import Path
import sqlite3
import bcrypt
from typing import Optional, List, Dict
import logging

class User:
    def __init__(self, id: Optional[str] = None, email: str = "", username: str = "", 
                 password_hash: str = "", is_admin: bool = False, 
                 created_at: Optional[datetime] = None, last_login: Optional[datetime] = None,
                 claude_token: Optional[str] = None):
        self.id = id
        self.email = email
        self.username = username or email.split('@')[0]
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
        self.claude_token = claude_token
        
    def set_password(self, password: str):
        """设置密码（加密存储）"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        
    def to_dict(self):
        """转换为字典（不包含密码）"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'claude_token': self.claude_token
        }


class SystemConfig:
    """系统配置模型"""
    def __init__(self):
        self.id = 'system_config'
        self.allowed_email_domain = None  # 允许的企业邮箱域名，如 @company.com
        self.require_email_verification = True
        self.super_admin_email = None  # 超级管理员邮箱
        
    def to_dict(self):
        return {
            'id': self.id,
            'allowed_email_domain': self.allowed_email_domain,
            'require_email_verification': self.require_email_verification,
            'super_admin_email': self.super_admin_email
        }


class UserManager:
    """用户管理器"""
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用绝对路径，确保总是使用同一个数据库文件
            from pathlib import Path
            self.db_path = str(Path(__file__).parent.parent / "tasks.db")
        else:
            self.db_path = db_path
        self._init_db()
        self._init_super_admin()
        
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL,
                last_login TEXT,
                claude_token TEXT
            )
        ''')
        
        # 添加claude_token列（如果不存在）
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'claude_token' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN claude_token TEXT')
        
        # 创建系统配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id TEXT PRIMARY KEY,
                allowed_email_domain TEXT,
                require_email_verification BOOLEAN DEFAULT 1,
                super_admin_email TEXT
            )
        ''')
        
        # 创建任务用户关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_users (
                task_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                PRIMARY KEY (task_id, user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_super_admin(self):
        """初始化超级管理员账户"""
        # 检查是否已有超级管理员
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE is_admin = 1 LIMIT 1')
        if cursor.fetchone():
            conn.close()
            return
            
        # 创建默认超级管理员
        import uuid
        admin = User(
            id=str(uuid.uuid4()),
            email='admin@claudetask.local',
            username='admin',
            is_admin=True
        )
        admin.set_password('admin123')  # 默认密码，首次登录应提示修改
        
        cursor.execute('''
            INSERT INTO users (id, email, username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (admin.id, admin.email, admin.username, admin.password_hash, 
              1, admin.created_at.isoformat()))
              
        conn.commit()
        conn.close()
        
    def create_user(self, email: str, password: str, username: Optional[str] = None, 
                   claude_token: Optional[str] = None, is_admin: bool = False) -> Optional[User]:
        """创建新用户"""
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username or email.split('@')[0],
            claude_token=claude_token,
            is_admin=is_admin
        )
        user.set_password(password)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, email, username, password_hash, is_admin, created_at, claude_token)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user.id, user.email, user.username, user.password_hash, 
                  1 if is_admin else 0, user.created_at.isoformat(), claude_token))
            conn.commit()
            conn.close()
            return user
        except sqlite3.IntegrityError:
            return None  # 用户已存在
            
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, username, password_hash, is_admin, created_at, last_login, claude_token
            FROM users WHERE email = ?
        ''', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                email=row[1],
                username=row[2],
                password_hash=row[3],
                is_admin=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                claude_token=row[7] if len(row) > 7 else None
            )
        return None
        
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """通过ID获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, username, password_hash, is_admin, created_at, last_login, claude_token
            FROM users WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                email=row[1],
                username=row[2],
                password_hash=row[3],
                is_admin=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                claude_token=row[7] if len(row) > 7 else None
            )
        return None
        
    def update_last_login(self, user_id: str):
        """更新最后登录时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        
    def list_users(self) -> List[User]:
        """列出所有用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, username, password_hash, is_admin, created_at, last_login, claude_token
            FROM users ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                id=row[0],
                email=row[1],
                username=row[2],
                password_hash=row[3],
                is_admin=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_login=datetime.fromisoformat(row[6]) if row[6] else None,
                claude_token=row[7] if len(row) > 7 else None
            ))
        return users
        
    def get_system_config(self) -> SystemConfig:
        """获取系统配置（兼容新旧两种表结构）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_config'")
            if not cursor.fetchone():
                conn.close()
                return SystemConfig()  # 返回默认配置
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(system_config)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 新的配置系统（key-value 格式）
            if 'key' in columns and 'value' in columns:
                cursor.execute('''
                    SELECT key, value FROM system_config 
                    WHERE key IN ('auth.allowed_email_domain', 
                                  'auth.require_email_verification', 
                                  'auth.super_admin_email')
                ''')
                
                config_dict = {row[0]: row[1] for row in cursor.fetchall()}
                config = SystemConfig()
                config.allowed_email_domain = config_dict.get('auth.allowed_email_domain', '@sparticle.com')
                config.require_email_verification = config_dict.get('auth.require_email_verification', 'false').lower() == 'true'
                config.super_admin_email = config_dict.get('auth.super_admin_email', 'admin@sparticle.com')
                conn.close()
                return config
                
            # 旧的配置系统
            elif 'allowed_email_domain' in columns:
                cursor.execute('''
                    SELECT allowed_email_domain, require_email_verification, super_admin_email
                    FROM system_config WHERE id = 'system_config'
                ''')
                row = cursor.fetchone()
                conn.close()
                
                config = SystemConfig()
                if row:
                    config.allowed_email_domain = row[0]
                    config.require_email_verification = bool(row[1])
                    config.super_admin_email = row[2]
                return config
                
        except Exception as e:
            logging.error(f"Error getting system config: {e}")
            conn.close()
            
        return SystemConfig()  # 返回默认配置
        
    def update_system_config(self, config: SystemConfig):
        """更新系统配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 先尝试更新
        cursor.execute('''
            UPDATE system_config 
            SET allowed_email_domain = ?, require_email_verification = ?, super_admin_email = ?
            WHERE id = 'system_config'
        ''', (config.allowed_email_domain, int(config.require_email_verification), config.super_admin_email))
        
        # 如果没有更新到任何行，则插入
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO system_config (id, allowed_email_domain, require_email_verification, super_admin_email)
                VALUES ('system_config', ?, ?, ?)
            ''', (config.allowed_email_domain, int(config.require_email_verification), config.super_admin_email))
            
        conn.commit()
        conn.close()
        
    def delete_user(self, user_id: str) -> bool:
        """删除用户（仅管理员可用）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查用户是否存在
            cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            if not cursor.fetchone():
                return False
            
            # 删除用户
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            import logging
            logging.error(f"Error deleting user {user_id}: {str(e)}")
            return False
        finally:
            conn.close()
    
    def validate_email_domain(self, email: str) -> bool:
        """验证邮箱域名是否符合要求"""
        config = self.get_system_config()
        if not config.allowed_email_domain:
            return True  # 未设置域名限制
            
        domain = email.split('@')[1] if '@' in email else ''
        return domain == config.allowed_email_domain.lstrip('@')
    
    def update_claude_token(self, user_id: str, token: str):
        """更新用户的Claude token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET claude_token = ? WHERE id = ?
        ''', (token, user_id))
        conn.commit()
        conn.close()
    
    def make_user_admin(self, user_id: str):
        """将用户设为管理员"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_admin = 1 WHERE id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def get_or_create_user_from_email_hint(self, email_hint: str, user_id: Optional[str] = None) -> Optional[User]:
        """根据邮箱提示获取或创建用户"""
        # 如果是完整邮箱，直接查找
        if '@' in email_hint:
            user = self.get_user_by_email(email_hint)
            if user:
                return user
            
            # 创建新用户
            import uuid
            new_user_id = user_id or str(uuid.uuid4())
            return self.create_user(
                email=email_hint,
                password=email_hint.split('@')[0] + '123456',  # 默认密码
                username=email_hint.split('@')[0]
            )
        
        # 如果只是用户名部分，尝试匹配
        users = self.list_users()
        for user in users:
            if user.email.startswith(email_hint + '@'):
                return user
        
        # 无法匹配，返回None
        return None