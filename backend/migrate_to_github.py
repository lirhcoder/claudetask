#!/usr/bin/env python3
"""
数据迁移脚本：将旧的项目/任务系统迁移到 GitHub 风格的仓库/分支系统
"""
import os
import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubMigration:
    def __init__(self, db_path='tasks.db', projects_dir='projects', repos_dir='repos'):
        self.db_path = db_path
        self.projects_dir = Path(projects_dir)
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(exist_ok=True)
        
    def migrate_all(self):
        """执行完整迁移"""
        logging.info("Starting migration to GitHub style system...")
        
        # 1. Backup database
        self.backup_database()
        
        # 2. Migrate projects to repositories
        self.migrate_projects_to_repos()
        
        # 3. Migrate tasks to branches
        self.migrate_tasks_to_branches()
        
        # 4. Update API compatibility
        self.update_api_compatibility()
        
        logging.info("Migration completed!")
        
    def backup_database(self):
        """备份数据库"""
        backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.db_path, backup_path)
        logging.info(f"Database backed up to: {backup_path}")
        
    def migrate_projects_to_repos(self):
        """将项目迁移到仓库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有项目
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()
        
        for project in projects:
            project_id, name, description, created_at, updated_at = project[:5]
            
            logging.info(f"Migrating project: {name}")
            
            # Check if repository already exists
            cursor.execute('SELECT id FROM repositories WHERE project_id = ?', (project_id,))
            if cursor.fetchone():
                logging.info(f"Project {name} already has repository, skipping")
                continue
            
            # 创建对应的仓库记录
            repo_data = {
                'id': project_id,  # 使用相同 ID 便于关联
                'project_id': project_id,
                'name': name,
                'description': description or f"Migrated from project: {name}",
                'github_url': '',  # 本地仓库
                'is_private': True,
                'default_branch': 'main',
                'created_at': created_at,
                'updated_at': updated_at
            }
            
            cursor.execute('''
                INSERT INTO repositories (id, project_id, name, description, github_url, 
                                        is_private, default_branch, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (repo_data['id'], repo_data['project_id'], repo_data['name'], 
                  repo_data['description'], repo_data['github_url'], 
                  1 if repo_data['is_private'] else 0, repo_data['default_branch'],
                  repo_data['created_at'], repo_data['updated_at']))
            
            # 迁移项目文件到仓库目录
            project_path = self.projects_dir / project_id
            repo_path = self.repos_dir / project_id
            
            if project_path.exists() and not repo_path.exists():
                shutil.copytree(project_path, repo_path)
                
                # 初始化为 Git 仓库
                if not (repo_path / '.git').exists():
                    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
                    subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
                    subprocess.run(['git', 'commit', '-m', 'Initial migration from project'], 
                                 cwd=repo_path, capture_output=True)
                
                logging.info(f"Project files migrated to: {repo_path}")
        
        conn.commit()
        conn.close()
        
    def migrate_tasks_to_branches(self):
        """将任务迁移到分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有任务
        cursor.execute('''
            SELECT t.*, p.id as project_id 
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.parent_id IS NULL
        ''')
        tasks = cursor.fetchall()
        
        for task_row in tasks:
            task_id = task_row[0]
            title = task_row[1]
            description = task_row[2]
            status = task_row[3]
            project_id = task_row[-1]
            
            if not project_id:
                logging.warning(f"Task {title} has no associated project, skipping")
                continue
            
            logging.info(f"Migrating task: {title}")
            
            # Check if branch already exists
            cursor.execute('SELECT id FROM branches WHERE task_id = ?', (task_id,))
            if cursor.fetchone():
                logging.info(f"Task {title} already has branch, skipping")
                continue
            
            # 创建对应的分支记录
            branch_name = f"task/{task_id[:8]}-{self._sanitize_branch_name(title)}"
            
            # 映射任务状态到分支状态
            branch_status = {
                'pending': 'draft',
                'in_progress': 'in_progress',
                'completed': 'merged',
                'failed': 'closed'
            }.get(status, 'draft')
            
            cursor.execute('''
                INSERT INTO branches (id, repository_id, task_id, name, description, 
                                    status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            ''', (task_id, project_id, task_id, branch_name, description, branch_status))
            
            # 获取子任务并创建为 issues
            cursor.execute('SELECT * FROM tasks WHERE parent_id = ?', (task_id,))
            subtasks = cursor.fetchall()
            
            for i, subtask in enumerate(subtasks, 1):
                subtask_title = subtask[1]
                subtask_desc = subtask[2]
                subtask_status = subtask[3]
                
                issue_state = 'open' if subtask_status in ['pending', 'in_progress'] else 'closed'
                
                cursor.execute('''
                    INSERT INTO issues (repository_id, number, title, body, state, 
                                      created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ''', (project_id, i, subtask_title, subtask_desc, issue_state))
        
        conn.commit()
        conn.close()
        
    def _sanitize_branch_name(self, name):
        """清理分支名称"""
        # 移除特殊字符，保留字母数字和连字符
        import re
        name = re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower())
        name = re.sub(r'-+', '-', name)  # 合并多个连字符
        return name[:30].strip('-')  # 限制长度
        
    def update_api_compatibility(self):
        """创建 API 兼容层配置"""
        compatibility_config = {
            'api_mapping': {
                '/api/projects': '/api/repos',
                '/api/tasks': '/api/branches',
                '/api/projects/{id}/tasks': '/api/repos/{id}/branches',
                '/api/tasks/{id}/execute': '/api/branches/{id}/execute'
            },
            'status_mapping': {
                'tasks': {
                    'pending': 'draft',
                    'in_progress': 'in_progress',
                    'completed': 'merged',
                    'failed': 'closed'
                }
            },
            'migration_date': datetime.now().isoformat()
        }
        
        config_path = Path('migration_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(compatibility_config, f, indent=2, ensure_ascii=False)
        
        logging.info(f"API compatibility config saved to: {config_path}")
        
        # 创建兼容性中间件
        self.create_compatibility_middleware()
        
    def create_compatibility_middleware(self):
        """创建兼容性中间件"""
        middleware_code = '''"""
API 兼容性中间件 - 将旧 API 请求转发到新 API
"""
from flask import request, jsonify, redirect
import json

class CompatibilityMiddleware:
    def __init__(self, app):
        self.app = app
        self.load_mapping()
        
    def load_mapping(self):
        """加载 API 映射配置"""
        with open('migration_config.json', 'r') as f:
            config = json.load(f)
            self.api_mapping = config['api_mapping']
            self.status_mapping = config['status_mapping']
    
    def __call__(self, environ, start_response):
        """处理请求"""
        path = environ.get('PATH_INFO', '')
        
        # 检查是否需要重定向
        for old_path, new_path in self.api_mapping.items():
            if path.startswith(old_path.split('{')[0]):
                # 构建新路径
                new_path_actual = path.replace(old_path.split('{')[0], new_path.split('{')[0])
                environ['PATH_INFO'] = new_path_actual
                
                # 添加标记表示这是兼容性请求
                environ['HTTP_X_COMPATIBILITY_MODE'] = '1'
                
                break
        
        return self.app(environ, start_response)

def init_compatibility(app):
    """初始化兼容性支持"""
    from functools import wraps
    
    # 添加响应转换装饰器
    def transform_response(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # 如果是兼容模式，转换响应
            if request.headers.get('X-Compatibility-Mode'):
                if isinstance(response, tuple):
                    data, status = response[0], response[1]
                else:
                    data = response
                    status = 200
                
                # 转换数据格式
                if isinstance(data, dict):
                    # 转换字段名
                    if 'branches' in data:
                        data['tasks'] = data.pop('branches')
                    if 'repository' in data:
                        data['project'] = data.pop('repository')
                    
                    # 转换状态
                    if 'status' in data and data['status'] in ['draft', 'in_progress', 'merged', 'closed']:
                        status_map = {
                            'draft': 'pending',
                            'in_progress': 'in_progress', 
                            'merged': 'completed',
                            'closed': 'failed'
                        }
                        data['status'] = status_map.get(data['status'], data['status'])
                
                return jsonify(data), status
            
            return response
        
        return decorated_function
    
    # 应用到所有路由
    for endpoint, func in app.view_functions.items():
        app.view_functions[endpoint] = transform_response(func)
    
    return app
'''
        
        with open('backend/compatibility.py', 'w', encoding='utf-8') as f:
            f.write(middleware_code)
        
        logging.info("Compatibility middleware created")


def main():
    """执行迁移"""
    # 设置控制台编码为 UTF-8
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    migration = GitHubMigration()
    
    print("=== GitHub Style System Migration Tool ===")
    print("\nThis script will:")
    print("1. Backup existing database")
    print("2. Migrate projects to repository system")
    print("3. Migrate tasks to branch system")
    print("4. Create API compatibility layer")
    print("\nOld APIs will continue to work and automatically forward to new APIs")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() == 'y':
        migration.migrate_all()
        print("\n✅ Migration completed!")
        print("\nNext steps:")
        print("1. Restart backend service")
        print("2. Test both old and new APIs")
        print("3. Gradually update frontend to use new APIs")
    else:
        print("Migration cancelled")


if __name__ == '__main__':
    main()