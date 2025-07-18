"""
GitHub 风格的仓库管理模型
"""
import json
import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import uuid
import logging

logger = logging.getLogger(__name__)


class Repository:
    """仓库模型"""
    def __init__(self, id: str, name: str, organization: str = 'personal',
                 description: str = '', readme: str = '', is_private: bool = False,
                 default_branch: str = 'main', github_url: Optional[str] = None,
                 local_path: str = '', owner_id: str = '', created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.organization = organization
        self.description = description
        self.readme = readme
        self.is_private = is_private
        self.default_branch = default_branch
        self.github_url = github_url
        self.local_path = local_path
        self.owner_id = owner_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'description': self.description,
            'readme': self.readme,
            'is_private': self.is_private,
            'default_branch': self.default_branch,
            'github_url': self.github_url,
            'local_path': self.local_path,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Branch:
    """分支模型（任务）"""
    def __init__(self, id: str, name: str, repository_id: str,
                 base_branch: str = 'main', description: str = '',
                 status: str = 'draft', created_by: str = '',
                 assigned_to: Optional[str] = None, pull_request_id: Optional[str] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.repository_id = repository_id
        self.base_branch = base_branch
        self.description = description
        self.status = status  # draft, in_progress, review, merged, closed
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.pull_request_id = pull_request_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'repository_id': self.repository_id,
            'base_branch': self.base_branch,
            'description': self.description,
            'status': self.status,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'pull_request_id': self.pull_request_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Issue:
    """议题模型（子任务）"""
    def __init__(self, id: str, number: int, title: str, repository_id: str,
                 description: str = '', branch_id: Optional[str] = None,
                 status: str = 'open', priority: str = 'medium',
                 created_by: str = '', assigned_to: Optional[str] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None,
                 closed_at: Optional[datetime] = None):
        self.id = id
        self.number = number
        self.title = title
        self.repository_id = repository_id
        self.description = description
        self.branch_id = branch_id
        self.status = status  # open, in_progress, resolved, closed
        self.priority = priority  # low, medium, high, critical
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.closed_at = closed_at
        
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'repository_id': self.repository_id,
            'description': self.description,
            'branch_id': self.branch_id,
            'status': self.status,
            'priority': self.priority,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }


class RepositoryManager:
    """仓库管理器"""
    def __init__(self, db_path: str = "tasks.db", workspace_path: str = "workspace"):
        self.db_path = db_path
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
        
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
            
    def create_repository(self, name: str, owner_id: str, organization: str = 'personal',
                         description: str = '', is_private: bool = False,
                         github_url: Optional[str] = None) -> Repository:
        """创建仓库"""
        repo_id = str(uuid.uuid4())
        
        # 创建本地目录
        org_path = self.workspace_path / organization
        org_path.mkdir(exist_ok=True)
        repo_path = org_path / name
        repo_path.mkdir(exist_ok=True)
        
        # 初始化 Git 仓库
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True)
            
            # 创建 README
            readme_content = f"# {name}\n\n{description}\n"
            (repo_path / 'README.md').write_text(readme_content, encoding='utf-8')
            
            # 初始提交
            subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize git repository: {e}")
            
        # 保存到数据库
        repo = Repository(
            id=repo_id,
            name=name,
            organization=organization,
            description=description,
            readme=readme_content,
            is_private=is_private,
            github_url=github_url,
            local_path=str(repo_path),
            owner_id=owner_id
        )
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO repositories (
                    id, name, organization, description, readme, is_private,
                    default_branch, github_url, local_path, owner_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                repo.id, repo.name, repo.organization, repo.description, repo.readme,
                repo.is_private, repo.default_branch, repo.github_url, repo.local_path,
                repo.owner_id, repo.created_at.isoformat(), repo.updated_at.isoformat()
            ))
            conn.commit()
            
        return repo
        
    def get_repository(self, repo_id: str) -> Optional[Repository]:
        """获取仓库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM repositories WHERE id = ?', (repo_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_repository(row)
            return None
            
    def list_repositories(self, user_id: Optional[str] = None) -> List[Repository]:
        """列出仓库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                # 获取用户拥有的和协作的仓库
                cursor.execute('''
                    SELECT DISTINCT r.* FROM repositories r
                    LEFT JOIN repository_collaborators rc ON r.id = rc.repository_id
                    WHERE r.owner_id = ? OR rc.user_id = ?
                    ORDER BY r.updated_at DESC
                ''', (user_id, user_id))
            else:
                cursor.execute('SELECT * FROM repositories ORDER BY updated_at DESC')
                
            return [self._row_to_repository(row) for row in cursor.fetchall()]
            
    def create_branch(self, repository_id: str, name: str, created_by: str,
                     base_branch: str = 'main', description: str = '') -> Branch:
        """创建分支（任务）"""
        branch_id = str(uuid.uuid4())
        
        # 获取仓库
        repo = self.get_repository(repository_id)
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")
            
        # 在 Git 中创建分支
        try:
            repo_path = Path(repo.local_path)
            subprocess.run(['git', 'checkout', base_branch], cwd=repo_path, check=True)
            subprocess.run(['git', 'checkout', '-b', name], cwd=repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create git branch: {e}")
            
        # 保存到数据库
        branch = Branch(
            id=branch_id,
            name=name,
            repository_id=repository_id,
            base_branch=base_branch,
            description=description,
            created_by=created_by
        )
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO branches (
                    id, name, repository_id, base_branch, description,
                    status, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                branch.id, branch.name, branch.repository_id, branch.base_branch,
                branch.description, branch.status, branch.created_by,
                branch.created_at.isoformat(), branch.updated_at.isoformat()
            ))
            conn.commit()
            
        return branch
        
    def create_issue(self, repository_id: str, title: str, created_by: str,
                    description: str = '', branch_id: Optional[str] = None,
                    priority: str = 'medium') -> Issue:
        """创建议题（子任务）"""
        issue_id = str(uuid.uuid4())
        
        # 获取下一个议题编号
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(MAX(number), 0) + 1 as next_number
                FROM issues WHERE repository_id = ?
            ''', (repository_id,))
            number = cursor.fetchone()['next_number']
            
            # 创建议题
            issue = Issue(
                id=issue_id,
                number=number,
                title=title,
                repository_id=repository_id,
                description=description,
                branch_id=branch_id,
                priority=priority,
                created_by=created_by
            )
            
            cursor.execute('''
                INSERT INTO issues (
                    id, number, title, description, repository_id, branch_id,
                    status, priority, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                issue.id, issue.number, issue.title, issue.description,
                issue.repository_id, issue.branch_id, issue.status, issue.priority,
                issue.created_by, issue.created_at.isoformat(), issue.updated_at.isoformat()
            ))
            conn.commit()
            
        return issue
        
    def _row_to_repository(self, row) -> Repository:
        """将数据库行转换为 Repository 对象"""
        return Repository(
            id=row['id'],
            name=row['name'],
            organization=row['organization'],
            description=row['description'] or '',
            readme=row['readme'] or '',
            is_private=bool(row['is_private']),
            default_branch=row['default_branch'],
            github_url=row['github_url'],
            local_path=row['local_path'],
            owner_id=row['owner_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )