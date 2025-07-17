import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
from contextlib import contextmanager

class TaskDB:
    """SQLite数据库管理器，用于持久化任务数据"""
    
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
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT,
                    parent_task_id TEXT,
                    context TEXT,
                    sequence_order INTEGER DEFAULT 0,
                    task_type TEXT DEFAULT 'single',
                    FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
                )
            ''')
            
            # 创建索引以提高查询性能
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_status 
                ON tasks(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_project 
                ON tasks(project_path)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_created 
                ON tasks(created_at DESC)
            ''')
            
            # Add missing columns if they don't exist
            cursor.execute("PRAGMA table_info(tasks)")
            columns = {row[1] for row in cursor.fetchall()}
            
            if 'started_at' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN started_at TIMESTAMP')
            
            if 'execution_time' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN execution_time REAL')
                
            if 'exit_code' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN exit_code INTEGER')
                
            if 'files_changed' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN files_changed TEXT')
                
            if 'error' not in columns:
                cursor.execute('ALTER TABLE tasks ADD COLUMN error TEXT')
            
            conn.commit()
    
    def save_task(self, task: 'Task'):
        """保存或更新任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 准备元数据
            metadata = json.dumps({
                'files_changed': getattr(task, 'files_changed', []),
                'execution_time': getattr(task, 'execution_time', None),
                'exit_code': getattr(task, 'exit_code', None),
                'error': getattr(task, 'error', None),
                'started_at': getattr(task, 'started_at', None)
            })
            
            # 检查表结构是否包含新字段
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'parent_task_id' in columns:
                # 使用包含新字段的插入语句
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks 
                    (id, prompt, project_path, status, output, error_message, 
                     created_at, updated_at, completed_at, metadata,
                     parent_task_id, context, sequence_order, task_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.id,
                    task.prompt,
                    task.project_path,
                    task.status,
                    task.output,
                    task.error_message,
                    task.created_at,
                    datetime.now(),
                    task.completed_at,
                    metadata,
                    getattr(task, 'parent_task_id', None),
                    getattr(task, 'context', None),
                    getattr(task, 'sequence_order', 0),
                    getattr(task, 'task_type', 'single')
                ))
            else:
                # 使用旧的插入语句（向后兼容）
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks 
                    (id, prompt, project_path, status, output, error_message, 
                     created_at, updated_at, completed_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.id,
                    task.prompt,
                    task.project_path,
                    task.status,
                    task.output,
                    task.error_message,
                    task.created_at,
                    datetime.now(),
                    task.completed_at,
                    metadata
                ))
            
            conn.commit()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取单个任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
    
    def get_all_tasks(self, project_path: Optional[str] = None, 
                      status: Optional[str] = None, 
                      limit: int = 100) -> List[Dict]:
        """获取任务列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM tasks WHERE 1=1'
            params = []
            
            if project_path:
                query += ' AND project_path = ?'
                params.append(project_path)
            
            if status:
                query += ' AND status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def delete_old_tasks(self, days: int = 30):
        """删除旧任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM tasks 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            conn.commit()
            return cursor.rowcount
    
    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典"""
        task_dict = dict(row)
        
        # 解析元数据
        if task_dict.get('metadata'):
            metadata = json.loads(task_dict['metadata'])
            task_dict.update(metadata)
            del task_dict['metadata']
        
        return task_dict


class TaskManager:
    """任务管理器，提供内存缓存和持久化功能"""
    
    def __init__(self, db_path: str = "tasks.db", cache_size: int = 1000):
        self.db = TaskDB(db_path)
        self.cache = {}  # 内存缓存
        self.cache_size = cache_size
        self._load_recent_tasks()
    
    def _load_recent_tasks(self):
        """加载最近的任务到缓存"""
        recent_tasks = self.db.get_all_tasks(limit=self.cache_size)
        for task_data in recent_tasks:
            task = Task(
                id=task_data['id'],
                prompt=task_data['prompt'],
                project_path=task_data['project_path']
            )
            task.status = task_data['status']
            task.output = task_data.get('output', '')
            task.error_message = task_data.get('error_message')
            task.created_at = task_data['created_at']
            task.completed_at = task_data.get('completed_at')
            task.files_changed = task_data.get('files_changed', [])
            task.execution_time = task_data.get('execution_time')
            
            self.cache[task.id] = task
    
    def add_task(self, task: 'Task'):
        """添加任务到管理器"""
        self.cache[task.id] = task
        self.db.save_task(task)
        
        # 维护缓存大小
        if len(self.cache) > self.cache_size:
            # 移除最旧的任务
            oldest_id = min(self.cache.keys(), 
                          key=lambda k: self.cache[k].created_at)
            del self.cache[oldest_id]
    
    def update_task(self, task: 'Task'):
        """更新任务"""
        if task.id in self.cache:
            self.cache[task.id] = task
        self.db.save_task(task)
    
    def get_task(self, task_id: str) -> Optional['Task']:
        """获取任务"""
        # 先检查缓存
        if task_id in self.cache:
            return self.cache[task_id]
        
        # 从数据库加载
        task_data = self.db.get_task(task_id)
        if task_data:
            # 确保必需的字段存在
            task_id = task_data.get('id')
            prompt = task_data.get('prompt')
            project_path = task_data.get('project_path')
            
            if not all([task_id, prompt, project_path]):
                import logging
                logging.error(f"Task {task_id} missing required fields: id={task_id}, prompt={bool(prompt)}, project_path={bool(project_path)}")
                return None
                
            task = Task(
                id=task_id,
                prompt=prompt,
                project_path=project_path
            )
            # 恢复其他属性
            task.status = task_data.get('status', 'pending')
            task.output = task_data.get('output', '')
            task.error_message = task_data.get('error_message')
            task.created_at = task_data.get('created_at')
            task.completed_at = task_data.get('completed_at')
            task.files_changed = task_data.get('files_changed', [])
            task.execution_time = task_data.get('execution_time')
            task.exit_code = task_data.get('exit_code')
            task.error = task_data.get('error')
            
            # 恢复父子任务相关属性
            task.parent_task_id = task_data.get('parent_task_id')
            task.context = task_data.get('context')
            task.sequence_order = task_data.get('sequence_order', 0)
            task.task_type = task_data.get('task_type', 'single')
            
            # 添加到缓存
            self.cache[task.id] = task
            return task
        
        return None
    
    def get_all_tasks(self, project_path: Optional[str] = None,
                      status: Optional[str] = None) -> List['Task']:
        """获取所有任务"""
        # 对于小查询，从缓存返回
        if not project_path and not status and len(self.cache) < 100:
            return list(self.cache.values())
        
        # 否则从数据库查询
        task_data_list = self.db.get_all_tasks(project_path, status)
        tasks = []
        
        for task_data in task_data_list:
            if task_data['id'] in self.cache:
                tasks.append(self.cache[task_data['id']])
            else:
                task = Task(
                    id=task_data['id'],
                    prompt=task_data['prompt'],
                    project_path=task_data['project_path']
                )
                task.status = task_data['status']
                task.output = task_data.get('output', '')
                task.error_message = task_data.get('error_message')
                task.created_at = task_data['created_at']
                task.started_at = task_data.get('started_at')
                task.completed_at = task_data.get('completed_at')
                
                # Handle files_changed which might be JSON string
                files_changed = task_data.get('files_changed', [])
                if isinstance(files_changed, str):
                    try:
                        task.files_changed = json.loads(files_changed) if files_changed else []
                    except:
                        task.files_changed = []
                else:
                    task.files_changed = files_changed or []
                    
                task.execution_time = task_data.get('execution_time')
                task.exit_code = task_data.get('exit_code')
                task.error = task_data.get('error')
                tasks.append(task)
        
        return tasks
    
    def cleanup_old_tasks(self, days: int = 30):
        """清理旧任务"""
        deleted_count = self.db.delete_old_tasks(days)
        
        # 从缓存中移除已删除的任务
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        to_remove = []
        for task_id, task in self.cache.items():
            if isinstance(task.created_at, str):
                created_timestamp = datetime.fromisoformat(task.created_at).timestamp()
            else:
                created_timestamp = task.created_at
            
            if created_timestamp < cutoff_date:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.cache[task_id]
        
        return deleted_count


# 更新原有的Task类
class Task:
    def __init__(self, id, prompt, project_path, parent_task_id=None):
        self.id = id
        self.prompt = prompt
        self.project_path = project_path
        self.status = 'pending'
        self.output = ''
        self.error_message = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.files_changed = []
        self.execution_time = None
        self.process = None
        self.exit_code = None
        self.error = None
        self.completion_callback = None
        # 父子任务支持
        self.parent_task_id = parent_task_id
        self.context = None
        self.sequence_order = 0
        self.task_type = 'single'  # 'single', 'parent', 'child'
        self.children = []  # 子任务列表
        
    def to_dict(self):
        def format_datetime(dt):
            """Format datetime object or string"""
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            return dt  # Already a string
            
        return {
            'id': self.id,
            'prompt': self.prompt,
            'project_path': self.project_path,
            'status': self.status,
            'output': self.output,
            'error_message': self.error_message,
            'created_at': format_datetime(self.created_at),
            'completed_at': format_datetime(self.completed_at),
            'started_at': format_datetime(getattr(self, 'started_at', None)),
            'files_changed': self.files_changed,
            'execution_time': self.execution_time,
            'exit_code': getattr(self, 'exit_code', None),
            'error': getattr(self, 'error', None),
            # 父子任务相关
            'parent_task_id': self.parent_task_id,
            'context': self.context,
            'sequence_order': self.sequence_order,
            'task_type': self.task_type,
            'children': [child.to_dict() for child in self.children] if hasattr(self, 'children') else []
        }