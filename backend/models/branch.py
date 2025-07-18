"""
分支模型 - 管理仓库分支（任务）
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class BranchManager:
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建分支表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                id TEXT PRIMARY KEY,
                repository_id TEXT NOT NULL,
                task_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                base_branch TEXT DEFAULT 'main',
                created_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (repository_id) REFERENCES repositories(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_branch(self, repository_id: str, name: str, description: str = '', 
                     created_by: str = None) -> Dict:
        """创建新分支"""
        branch_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO branches (id, repository_id, name, description, status, 
                                created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (branch_id, repository_id, name, description, 'draft', 
              created_by, now, now))
        
        conn.commit()
        conn.close()
        
        return {
            'id': branch_id,
            'repository_id': repository_id,
            'name': name,
            'description': description,
            'status': 'draft',
            'created_at': now,
            'updated_at': now
        }
    
    def update_branch_status(self, branch_id: str, status: str):
        """更新分支状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE branches 
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), branch_id))
        
        conn.commit()
        conn.close()
    
    def list_branches(self, repository_id: str) -> List[Dict]:
        """列出仓库的所有分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, status, base_branch, 
                   created_by, created_at, updated_at
            FROM branches
            WHERE repository_id = ?
            ORDER BY created_at DESC
        ''', (repository_id,))
        
        branches = []
        for row in cursor.fetchall():
            branches.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'status': row[3],
                'base_branch': row[4],
                'created_by': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            })
        
        conn.close()
        return branches
    
    def _count_table_rows(self, table_name: str) -> int:
        """统计表中的行数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
        except:
            count = 0
        
        conn.close()
        return count