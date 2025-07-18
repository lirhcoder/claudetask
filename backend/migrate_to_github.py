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
        logging.info("开始迁移到 GitHub 风格系统...")
        
        # 1. 备份数据库
        self.backup_database()
        
        # 2. 迁移项目到仓库
        self.migrate_projects_to_repos()
        
        # 3. 迁移任务到分支
        self.migrate_tasks_to_branches()
        
        # 4. 更新 API 兼容性
        self.update_api_compatibility()
        
        logging.info("迁移完成！")
        
    def backup_database(self):
        """备份数据库"""
        backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(self.db_path, backup_path)
        logging.info(f"数据库已备份到: {backup_path}")
        
    def migrate_projects_to_repos(self):
        """将项目迁移到仓库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有项目
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()
        
        for project in projects:
            project_id, name, description, created_at, updated_at = project[:5]
            
            logging.info(f"迁移项目: {name}")
            
            # 检查是否已存在对应的仓库
            cursor.execute('SELECT id FROM repositories WHERE project_id = ?', (project_id,))
            if cursor.fetchone():
                logging.info(f"项目 {name} 已有对应仓库，跳过")
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
                
                logging.info(f"项目文件已迁移到: {repo_path}")
        
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
                logging.warning(f"任务 {title} 没有关联项目，跳过")
                continue
            
            logging.info(f"迁移任务: {title}")
            
            # 检查是否已存在对应的分支
            cursor.execute('SELECT id FROM branches WHERE task_id = ?', (task_id,))
            if cursor.fetchone():
                logging.info(f"任务 {title} 已有对应分支，跳过")
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
        
        logging.info(f"API 兼容性配置已保存到: {config_path}")
        
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
        
        logging.info("兼容性中间件已创建")


def main():
    """执行迁移"""
    migration = GitHubMigration()
    
    print("=== GitHub 风格系统迁移工具 ===")
    print("\n此脚本将：")
    print("1. 备份现有数据库")
    print("2. 将项目迁移到仓库系统")
    print("3. 将任务迁移到分支系统")
    print("4. 创建 API 兼容层")
    print("\n迁移后旧的 API 仍可使用，会自动转发到新 API")
    
    response = input("\n是否继续？(y/n): ")
    if response.lower() == 'y':
        migration.migrate_all()
        print("\n✅ 迁移完成！")
        print("\n下一步：")
        print("1. 重启后端服务")
        print("2. 测试新旧 API 是否正常工作")
        print("3. 逐步更新前端使用新 API")
    else:
        print("已取消迁移")


if __name__ == '__main__':
    main()