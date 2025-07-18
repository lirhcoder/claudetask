"""
统一 API - 合并任务和分支功能，提供简化的接口
"""
from flask import Blueprint, request, jsonify, session
import logging
from functools import wraps
from datetime import datetime
import subprocess
import os
import json
from pathlib import Path

from ..models.project import ProjectManager
from ..models.task import TaskManager  
from ..models.repository import RepositoryManager
from ..models.branch import BranchManager
from ..executors.factory import ExecutorFactory
from ..models.config import ConfigManager
from ..models.agent_metrics import AgentMetricsManager

unified_bp = Blueprint('unified', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

class UnifiedWorkflow:
    """统一的工作流管理"""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.branch_manager = BranchManager()
        self.executor_factory = ExecutorFactory()
        self.config_manager = ConfigManager()
        self.metrics_manager = AgentMetricsManager()
        
    def create_and_execute(self, repo_id, task_data, user_id):
        """一键创建分支并执行任务"""
        try:
            # 1. 创建分支
            branch_name = self._generate_branch_name(task_data['title'])
            branch = self.branch_manager.create_branch(
                repository_id=repo_id,
                name=branch_name,
                description=task_data.get('description', ''),
                created_by=user_id
            )
            
            if not branch:
                return None, "Failed to create branch"
            
            # 2. 自动创建执行配置
            execution_config = {
                'prompt': task_data.get('prompt', task_data['title']),
                'files': task_data.get('files', []),
                'executor_type': task_data.get('executor_type', 'claude'),
                'auto_commit': task_data.get('auto_commit', True),
                'auto_pr': task_data.get('auto_pr', False)
            }
            
            # 3. 切换到分支
            repo = self.repo_manager.get_repository(repo_id)
            repo_path = self._get_repo_path(repo)
            
            # 创建并切换到新分支
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         cwd=repo_path, capture_output=True)
            
            # 4. 执行任务
            executor = self.executor_factory.create(
                execution_config['executor_type'],
                str(repo_path)
            )
            
            # 更新分支状态为执行中
            self.branch_manager.update_branch_status(branch['id'], 'in_progress')
            
            # 记录执行开始时间
            import time
            start_time = time.time()
            
            # 执行
            result = executor.execute(
                prompt=execution_config['prompt'],
                files=execution_config['files']
            )
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 5. 处理执行结果
            if result.get('status') == 'success':
                # 自动提交更改
                if execution_config['auto_commit'] and result.get('files_changed'):
                    commit_msg = f"Complete task: {task_data['title']}\n\n{result.get('summary', '')}"
                    subprocess.run(['git', 'add', '.'], cwd=repo_path)
                    subprocess.run(['git', 'commit', '-m', commit_msg], cwd=repo_path)
                
                # 更新分支状态
                self.branch_manager.update_branch_status(
                    branch['id'], 
                    'ready_for_review' if execution_config['auto_pr'] else 'completed'
                )
                
                # 自动创建 PR
                if execution_config['auto_pr']:
                    pr_result = self._create_pull_request(repo, branch, task_data)
                    result['pull_request'] = pr_result
                
                # 更新Agent指标
                self.metrics_manager.update_task_metrics(user_id, execution_time)
                
            else:
                self.branch_manager.update_branch_status(branch['id'], 'failed')
            
            result['branch'] = branch
            return result, None
            
        except Exception as e:
            logging.error(f"Error in create_and_execute: {str(e)}")
            return None, str(e)
    
    def _generate_branch_name(self, title):
        """生成分支名称"""
        import re
        # 清理标题，生成合法的分支名
        clean_title = re.sub(r'[^a-zA-Z0-9\-_]', '-', title.lower())
        clean_title = re.sub(r'-+', '-', clean_title)[:30].strip('-')
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        return f"task/{timestamp}-{clean_title}"
    
    def _get_repo_path(self, repo):
        """获取仓库路径"""
        if repo.get('github_url'):
            return Path('repos') / repo['id']
        else:
            return Path('projects') / repo['project_id']
    
    def _create_pull_request(self, repo, branch, task_data):
        """创建 Pull Request"""
        try:
            # 如果是 GitHub 仓库，使用 GitHub API
            if repo.get('github_url'):
                # TODO: 实现 GitHub PR 创建
                pass
            else:
                # 本地仓库，创建 PR 记录
                pr_data = {
                    'repository_id': repo['id'],
                    'branch_id': branch['id'],
                    'title': f"Complete: {task_data['title']}",
                    'description': task_data.get('description', ''),
                    'status': 'open',
                    'created_at': datetime.now().isoformat()
                }
                # TODO: 保存 PR 记录
                return pr_data
        except Exception as e:
            logging.error(f"Error creating PR: {str(e)}")
            return None

# 实例化统一工作流
workflow = UnifiedWorkflow()

@unified_bp.route('/api/v2/repos/<repo_id>/quick-task', methods=['POST'])
@login_required
def quick_task(repo_id):
    """快速创建并执行任务"""
    data = request.json
    user_id = session.get('user_id')
    
    # 验证必需字段
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # 执行统一工作流
    result, error = workflow.create_and_execute(repo_id, data, user_id)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'success': True,
        'branch': result['branch'],
        'execution': {
            'status': result.get('status'),
            'summary': result.get('summary'),
            'files_changed': result.get('files_changed', [])
        },
        'pull_request': result.get('pull_request')
    })

@unified_bp.route('/api/v2/repos/<repo_id>/branches', methods=['GET'])
@login_required
def list_branches_unified(repo_id):
    """列出所有分支（包括任务信息）"""
    branches = workflow.branch_manager.list_branches(repo_id)
    
    # 增强分支信息
    enhanced_branches = []
    for branch in branches:
        enhanced = {
            **branch,
            'type': 'task' if branch['name'].startswith('task/') else 'feature',
            'can_merge': branch['status'] in ['ready_for_review', 'completed'],
            'execution_status': branch.get('status', 'draft')
        }
        enhanced_branches.append(enhanced)
    
    return jsonify({
        'branches': enhanced_branches,
        'total': len(enhanced_branches)
    })

@unified_bp.route('/api/v2/settings/simplify', methods=['POST'])
@login_required
def simplify_settings():
    """简化设置 - 只保留必要的配置"""
    essential_configs = [
        'github.token',
        'github.webhook_secret',
        'claude.api_key',
        'execution.timeout',
        'execution.auto_commit',
        'ui.theme',
        'ui.language'
    ]
    
    # 获取所有配置
    all_configs = workflow.config_manager.get_all_configs()
    
    # 过滤出必要的配置
    simplified = {}
    for key in essential_configs:
        if key in all_configs:
            simplified[key] = all_configs[key]
    
    return jsonify({
        'configs': simplified,
        'removed': len(all_configs) - len(simplified)
    })

@unified_bp.route('/api/v2/migrate/status', methods=['GET'])
@login_required
def migration_status():
    """检查迁移状态"""
    try:
        # 检查是否存在迁移配置
        migration_config_path = Path('migration_config.json')
        if migration_config_path.exists():
            with open(migration_config_path, 'r') as f:
                config = json.load(f)
                return jsonify({
                    'migrated': True,
                    'migration_date': config.get('migration_date'),
                    'api_mapping': config.get('api_mapping')
                })
        
        # 检查新旧表的数据量
        stats = {
            'projects': workflow.repo_manager._count_table_rows('projects'),
            'repositories': workflow.repo_manager._count_table_rows('repositories'),
            'tasks': workflow.branch_manager._count_table_rows('tasks'),
            'branches': workflow.branch_manager._count_table_rows('branches')
        }
        
        return jsonify({
            'migrated': False,
            'stats': stats,
            'ready_to_migrate': stats['projects'] > 0 or stats['tasks'] > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@unified_bp.route('/api/v2/dashboard', methods=['GET'])
@login_required
def unified_dashboard():
    """统一仪表板 - 简化的首页数据"""
    user_id = session.get('user_id')
    
    # 获取用户的活跃仓库
    repos = workflow.repo_manager.list_repositories()
    active_repos = sorted(repos, key=lambda x: x.get('updated_at', ''), reverse=True)[:5]
    
    # 获取最近的任务（分支）
    recent_tasks = []
    for repo in active_repos[:3]:
        branches = workflow.branch_manager.list_branches(repo['id'])
        for branch in branches[:2]:
            if branch['name'].startswith('task/'):
                recent_tasks.append({
                    'id': branch['id'],
                    'title': branch['name'].replace('task/', '').split('-', 1)[-1],
                    'repository': repo['name'],
                    'status': branch['status'],
                    'created_at': branch['created_at']
                })
    
    # 统计信息
    stats = {
        'total_repos': len(repos),
        'active_tasks': sum(1 for t in recent_tasks if t['status'] == 'in_progress'),
        'completed_today': sum(1 for t in recent_tasks 
                              if t['status'] == 'completed' 
                              and t['created_at'].startswith(datetime.now().strftime('%Y-%m-%d')))
    }
    
    return jsonify({
        'repositories': active_repos,
        'recent_tasks': recent_tasks,
        'stats': stats,
        'quick_actions': [
            {'id': 'create_task', 'label': '创建任务', 'icon': 'plus'},
            {'id': 'view_repos', 'label': '查看仓库', 'icon': 'folder'},
            {'id': 'settings', 'label': '设置', 'icon': 'setting'}
        ]
    })

# 注册蓝图时会自动加载
def init_app(app):
    """初始化统一 API"""
    app.register_blueprint(unified_bp)
    
    # 添加兼容性支持
    if Path('migration_config.json').exists():
        from ..compatibility import init_compatibility
        init_compatibility(app)