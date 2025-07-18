"""
项目模型 - 管理项目数据和用户关联
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import contextmanager

class Project:
    def __init__(self, id: str, name: str, path: str, user_id: Optional[str] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.path = path
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }


class ProjectDB:
    """SQLite数据库管理器，用于持久化项目数据"""
    
    def __init__(self, db_path: str = "tasks.db"):
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    user_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_projects_user_id 
                ON projects(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_projects_name 
                ON projects(name)
            ''')
            
            conn.commit()
    
    def save_project(self, project: Project):
        """保存或更新项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO projects 
                (id, name, path, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                project.id,
                project.name,
                project.path,
                project.user_id,
                project.created_at.isoformat() if isinstance(project.created_at, datetime) else project.created_at,
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取单个项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """通过名称获取项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE name = ?', (name,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_projects(self, user_id: Optional[str] = None) -> List[Dict]:
        """获取项目列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT * FROM projects 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM projects 
                    ORDER BY created_at DESC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_project(self, project_id: str):
        """删除项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            return cursor.rowcount


class ProjectManager:
    """项目管理器，提供项目的增删改查功能"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db = ProjectDB(db_path)
    
    def create_project(self, name: str, path: str, user_id: Optional[str] = None) -> Project:
        """创建新项目"""
        import uuid
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            path=path,
            user_id=user_id
        )
        self.db.save_project(project)
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目"""
        data = self.db.get_project(project_id)
        if data:
            return Project(
                id=data['id'],
                name=data['name'],
                path=data['path'],
                user_id=data.get('user_id'),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            )
        return None
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """通过名称获取项目"""
        data = self.db.get_project_by_name(name)
        if data:
            return Project(
                id=data['id'],
                name=data['name'],
                path=data['path'],
                user_id=data.get('user_id'),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            )
        return None
    
    def list_projects(self, user_id: Optional[str] = None) -> List[Dict]:
        """列出项目"""
        projects_data = self.db.get_all_projects(user_id)
        return projects_data
    
    def update_project(self, project: Project):
        """更新项目"""
        self.db.save_project(project)
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        return self.db.delete_project(project_id) > 0
    
    def sync_from_filesystem(self, projects_dir: Path, user_id: Optional[str] = None):
        """从文件系统同步项目到数据库"""
        if not projects_dir.exists():
            return
        
        # 获取数据库中的所有项目
        db_projects = {p['name']: p for p in self.list_projects()}
        
        # 扫描文件系统中的项目
        for item in projects_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name not in db_projects:
                    # 新项目，添加到数据库
                    self.create_project(
                        name=item.name,
                        path=str(item),
                        user_id=user_id
                    )