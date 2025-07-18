"""
文件系统化的任务管理模型
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sqlite3
from contextlib import contextmanager

class TaskNode:
    """任务节点 - 类似文件系统中的文件/文件夹"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 path: str,
                 parent_id: Optional[str] = None,
                 is_folder: bool = True,
                 depth: int = 0):
        self.id = id
        self.name = name
        self.path = path  # 完整路径，如: /project1/feature1/task1
        self.parent_id = parent_id
        self.is_folder = is_folder
        self.depth = depth
        
        # 任务属性
        self.prompt = ""  # 任务提示词
        self.description = ""  # 详细描述（README）
        self.status = "pending"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 子节点和资源
        self.children: List['TaskNode'] = []
        self.documents: List[Dict] = []  # 文档列表
        self.resources: List[Dict] = []  # 资源文件列表
        
        # 执行相关
        self.output = None
        self.error_message = None
        self.completed_at = None
        self.execution_time = None
        
    def get_breadcrumb(self) -> List[Tuple[str, str]]:
        """获取面包屑导航路径"""
        parts = self.path.strip('/').split('/')
        breadcrumb = []
        current_path = ""
        
        for part in parts:
            current_path += f"/{part}"
            breadcrumb.append((part, current_path))
            
        return breadcrumb
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'parent_id': self.parent_id,
            'is_folder': self.is_folder,
            'depth': self.depth,
            'prompt': self.prompt,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'output': self.output,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'child_count': len(self.children),
            'document_count': len(self.documents),
            'resource_count': len(self.resources)
        }


class TaskFileSystem:
    """任务文件系统管理器"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库（执行迁移脚本）"""
        # 这里应该执行 filesystem_structure.sql
        pass
    
    def create_task_folder(self, parent_path: str, name: str, prompt: str = "", description: str = "") -> TaskNode:
        """创建任务文件夹"""
        import uuid
        
        # 生成路径
        if parent_path == "/":
            full_path = f"/{name}"
            depth = 1
            parent_id = None
        else:
            full_path = f"{parent_path.rstrip('/')}/{name}"
            depth = len(full_path.strip('/').split('/'))
            # 获取父任务ID
            parent_task = self.get_task_by_path(parent_path)
            parent_id = parent_task.id if parent_task else None
        
        # 创建任务节点
        task = TaskNode(
            id=str(uuid.uuid4()),
            name=name,
            path=full_path,
            parent_id=parent_id,
            is_folder=True,
            depth=depth
        )
        task.prompt = prompt
        task.description = description
        
        # 保存到数据库
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (
                    id, task_name, task_path, parent_task_id, is_folder, depth,
                    prompt, description, status, created_at, updated_at, project_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id, task.name, task.path, task.parent_id, task.is_folder,
                task.depth, task.prompt, task.description, task.status,
                task.created_at.isoformat(), task.updated_at.isoformat(),
                task.path  # 使用task_path作为project_path
            ))
            conn.commit()
        
        return task
    
    def get_task_by_path(self, path: str) -> Optional[TaskNode]:
        """根据路径获取任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE task_path = ?', (path,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_task_node(row)
            return None
    
    def list_directory(self, path: str = "/") -> List[TaskNode]:
        """列出目录内容（子任务）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if path == "/":
                # 列出根目录
                cursor.execute('SELECT * FROM tasks WHERE depth = 1 ORDER BY task_name')
            else:
                # 获取父任务
                parent = self.get_task_by_path(path)
                if parent:
                    cursor.execute(
                        'SELECT * FROM tasks WHERE parent_task_id = ? ORDER BY task_name',
                        (parent.id,)
                    )
                else:
                    return []
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append(self._row_to_task_node(row))
            
            return tasks
    
    def get_task_tree(self, root_path: str = "/", max_depth: int = -1) -> Dict:
        """获取任务树结构"""
        def build_tree(path: str, current_depth: int = 0) -> List[Dict]:
            if max_depth >= 0 and current_depth >= max_depth:
                return []
            
            children = []
            for task in self.list_directory(path):
                task_dict = task.to_dict()
                if task.is_folder:
                    task_dict['children'] = build_tree(task.path, current_depth + 1)
                children.append(task_dict)
            
            return children
        
        if root_path == "/":
            return {
                'name': 'Workspace',
                'path': '/',
                'children': build_tree("/")
            }
        else:
            root_task = self.get_task_by_path(root_path)
            if root_task:
                root_dict = root_task.to_dict()
                root_dict['children'] = build_tree(root_path)
                return root_dict
            return None
    
    def move_task(self, source_path: str, dest_parent_path: str, new_name: Optional[str] = None) -> bool:
        """移动任务（类似 mv 命令）"""
        source_task = self.get_task_by_path(source_path)
        if not source_task:
            return False
        
        # 构建新路径
        name = new_name or source_task.name
        if dest_parent_path == "/":
            new_path = f"/{name}"
            new_depth = 1
            new_parent_id = None
        else:
            dest_parent = self.get_task_by_path(dest_parent_path)
            if not dest_parent:
                return False
            new_path = f"{dest_parent_path.rstrip('/')}/{name}"
            new_depth = dest_parent.depth + 1
            new_parent_id = dest_parent.id
        
        # 更新数据库
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 更新任务本身
            cursor.execute('''
                UPDATE tasks SET 
                    task_path = ?, 
                    task_name = ?,
                    parent_task_id = ?,
                    depth = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (new_path, name, new_parent_id, new_depth, datetime.now().isoformat(), source_task.id))
            
            # 如果是文件夹，需要递归更新所有子任务的路径
            if source_task.is_folder:
                self._update_children_paths(cursor, source_task.path, new_path)
            
            conn.commit()
        
        return True
    
    def _update_children_paths(self, cursor, old_parent_path: str, new_parent_path: str):
        """递归更新子任务路径"""
        cursor.execute(
            "SELECT id, task_path, depth FROM tasks WHERE task_path LIKE ?",
            (f"{old_parent_path}/%",)
        )
        
        for row in cursor.fetchall():
            old_path = row['task_path']
            new_path = old_path.replace(old_parent_path, new_parent_path, 1)
            new_depth = len(new_path.strip('/').split('/'))
            
            cursor.execute(
                "UPDATE tasks SET task_path = ?, depth = ?, updated_at = ? WHERE id = ?",
                (new_path, new_depth, datetime.now().isoformat(), row['id'])
            )
    
    def delete_task(self, path: str, recursive: bool = False) -> bool:
        """删除任务（类似 rm 命令）"""
        task = self.get_task_by_path(path)
        if not task:
            return False
        
        # 检查是否有子任务
        children = self.list_directory(path)
        if children and not recursive:
            raise ValueError("Directory not empty. Use recursive=True to delete.")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if recursive and task.is_folder:
                # 递归删除所有子任务
                cursor.execute(
                    "DELETE FROM tasks WHERE task_path LIKE ? OR id = ?",
                    (f"{path}/%", task.id)
                )
            else:
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task.id,))
            
            conn.commit()
        
        return True
    
    def _row_to_task_node(self, row) -> TaskNode:
        """将数据库行转换为TaskNode对象"""
        task = TaskNode(
            id=row['id'],
            name=row['task_name'] or row['prompt'][:30],  # 如果没有名称，使用prompt前30字符
            path=row['task_path'] or f"/{row['id']}",
            parent_id=row['parent_task_id'],
            is_folder=bool(row['is_folder']) if 'is_folder' in row.keys() else True,
            depth=row['depth'] if 'depth' in row.keys() else 0
        )
        
        # 设置其他属性
        task.prompt = row['prompt']
        task.description = row['description'] if 'description' in row.keys() else ""
        task.status = row['status']
        task.output = row['output']
        task.error_message = row['error_message']
        
        # 时间戳
        if row['created_at']:
            task.created_at = datetime.fromisoformat(row['created_at'])
        if row['updated_at']:
            task.updated_at = datetime.fromisoformat(row['updated_at'])
        if row['completed_at']:
            task.completed_at = datetime.fromisoformat(row['completed_at'])
        
        return task