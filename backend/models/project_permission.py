"""
项目权限模型 - 管理用户对项目的访问权限
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
from pathlib import Path

class ProjectPermission:
    """项目权限类型"""
    OWNER = 'owner'      # 所有者 - 所有权限
    ADMIN = 'admin'      # 管理员 - 除删除外的所有权限
    VIEWER = 'viewer'    # 查看者 - 只读权限
    
    @staticmethod
    def can_delete(role: str) -> bool:
        """是否可以删除项目"""
        return role == ProjectPermission.OWNER
    
    @staticmethod
    def can_edit(role: str) -> bool:
        """是否可以编辑项目"""
        return role in [ProjectPermission.OWNER, ProjectPermission.ADMIN]
    
    @staticmethod
    def can_view(role: str) -> bool:
        """是否可以查看项目"""
        return role in [ProjectPermission.OWNER, ProjectPermission.ADMIN, ProjectPermission.VIEWER]


class ProjectPermissionDB:
    """项目权限数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            from pathlib import Path
            self.db_path = str(Path(__file__).parent.parent.absolute() / "tasks.db")
        else:
            self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建项目权限表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'viewer')),
                    granted_by TEXT,
                    granted_at TEXT NOT NULL,
                    UNIQUE(project_id, user_id),
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (granted_by) REFERENCES users(id)
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_permissions_user 
                ON project_permissions(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_permissions_project 
                ON project_permissions(project_id)
            ''')
            
            conn.commit()
    
    def grant_permission(self, project_id: str, user_id: str, role: str, granted_by: str):
        """授予用户项目权限"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO project_permissions 
                (project_id, user_id, role, granted_by, granted_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, user_id, role, granted_by, datetime.now().isoformat()))
            conn.commit()
    
    def revoke_permission(self, project_id: str, user_id: str):
        """撤销用户项目权限"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM project_permissions 
                WHERE project_id = ? AND user_id = ?
            ''', (project_id, user_id))
            conn.commit()
    
    def get_user_role(self, project_id: str, user_id: str) -> Optional[str]:
        """获取用户在项目中的角色"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 首先检查权限表
            cursor.execute('''
                SELECT role FROM project_permissions 
                WHERE project_id = ? AND user_id = ?
            ''', (project_id, user_id))
            
            result = cursor.fetchone()
            if result:
                return result['role']
            
            # 如果权限表中没有，检查是否是项目所有者
            cursor.execute('''
                SELECT user_id FROM projects 
                WHERE id = ? AND user_id = ?
            ''', (project_id, user_id))
            
            if cursor.fetchone():
                return ProjectPermission.OWNER
            
            return None
    
    def get_project_users(self, project_id: str) -> List[Dict]:
        """获取项目的所有用户及其权限"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取所有者
            cursor.execute('''
                SELECT p.user_id, u.email, 'owner' as role, p.created_at as granted_at
                FROM projects p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = ?
            ''', (project_id,))
            
            users = [dict(row) for row in cursor.fetchall()]
            
            # 获取其他权限
            cursor.execute('''
                SELECT pp.user_id, u.email, pp.role, pp.granted_at, 
                       gu.email as granted_by_email
                FROM project_permissions pp
                JOIN users u ON pp.user_id = u.id
                LEFT JOIN users gu ON pp.granted_by = gu.id
                WHERE pp.project_id = ?
            ''', (project_id,))
            
            for row in cursor.fetchall():
                users.append(dict(row))
            
            return users
    
    def get_user_projects(self, user_id: str, role_filter: Optional[str] = None) -> List[Dict]:
        """获取用户的所有项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            queries = []
            params = []
            
            # 获取用户创建的项目（所有者）
            if not role_filter or role_filter == ProjectPermission.OWNER:
                queries.append('''
                    SELECT p.*, 'owner' as role
                    FROM projects p
                    WHERE p.user_id = ?
                ''')
                params.append(user_id)
            
            # 获取用户有权限的项目
            if not role_filter:
                queries.append('''
                    SELECT p.*, pp.role
                    FROM projects p
                    JOIN project_permissions pp ON p.id = pp.project_id
                    WHERE pp.user_id = ?
                ''')
                params.append(user_id)
            elif role_filter in [ProjectPermission.ADMIN, ProjectPermission.VIEWER]:
                queries.append('''
                    SELECT p.*, pp.role
                    FROM projects p
                    JOIN project_permissions pp ON p.id = pp.project_id
                    WHERE pp.user_id = ? AND pp.role = ?
                ''')
                params.extend([user_id, role_filter])
            
            # 合并查询
            if queries:
                query = ' UNION '.join(queries) + ' ORDER BY created_at DESC'
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
            
            return []


class ProjectPermissionManager:
    """项目权限管理器"""
    
    def __init__(self, db_path: str = None):
        self.db = ProjectPermissionDB(db_path)
    
    def check_permission(self, project_id: str, user_id: str, action: str) -> bool:
        """检查用户是否有执行特定操作的权限"""
        role = self.db.get_user_role(project_id, user_id)
        
        if not role:
            return False
        
        if action == 'delete':
            return ProjectPermission.can_delete(role)
        elif action in ['edit', 'write', 'update']:
            return ProjectPermission.can_edit(role)
        elif action in ['view', 'read']:
            return ProjectPermission.can_view(role)
        
        return False
    
    def grant_permission(self, project_id: str, user_id: str, role: str, granted_by: str):
        """授予权限"""
        if role not in [ProjectPermission.OWNER, ProjectPermission.ADMIN, ProjectPermission.VIEWER]:
            raise ValueError(f"Invalid role: {role}")
        
        # 不能授予 owner 权限（owner 只能通过创建项目获得）
        if role == ProjectPermission.OWNER:
            raise ValueError("Cannot grant owner permission")
        
        self.db.grant_permission(project_id, user_id, role, granted_by)
    
    def get_user_projects_by_filter(self, user_id: str, filter_type: str = 'all') -> List[Dict]:
        """根据过滤条件获取用户项目
        
        filter_type:
        - 'all': 所有我能访问的项目
        - 'owned': 我创建的项目
        - 'participated': 我参与的项目（非所有者）
        """
        if filter_type == 'owned':
            return self.db.get_user_projects(user_id, ProjectPermission.OWNER)
        elif filter_type == 'participated':
            # 获取所有项目，然后过滤掉自己创建的
            all_projects = self.db.get_user_projects(user_id)
            return [p for p in all_projects if p['role'] != ProjectPermission.OWNER]
        else:
            return self.db.get_user_projects(user_id)
    
    def migrate_existing_projects(self):
        """迁移现有项目，为所有者创建权限记录"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取所有项目
            cursor.execute('''
                SELECT id, user_id, created_at 
                FROM projects 
                WHERE user_id IS NOT NULL
            ''')
            
            projects = cursor.fetchall()
            migrated = 0
            
            for project in projects:
                # 检查是否已有 owner 权限记录
                cursor.execute('''
                    SELECT 1 FROM project_permissions 
                    WHERE project_id = ? AND user_id = ? AND role = 'owner'
                ''', (project['id'], project['user_id']))
                
                if not cursor.fetchone():
                    # 创建 owner 权限记录
                    cursor.execute('''
                        INSERT INTO project_permissions 
                        (project_id, user_id, role, granted_by, granted_at)
                        VALUES (?, ?, 'owner', ?, ?)
                    ''', (project['id'], project['user_id'], project['user_id'], 
                          project['created_at'] or datetime.now().isoformat()))
                    migrated += 1
            
            conn.commit()
            return migrated