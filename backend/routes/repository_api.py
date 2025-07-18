"""
GitHub 风格的仓库管理 API
"""
from flask import Blueprint, jsonify, request, session
from models.repository import RepositoryManager, Repository, Branch, Issue
from services.claude_executor import get_executor
from utils.decorators import login_required
import logging

logger = logging.getLogger(__name__)

repo_bp = Blueprint('repository', __name__)
repo_manager = RepositoryManager()


@repo_bp.route('/repos', methods=['GET'])
@login_required
def list_repositories():
    """列出用户的仓库"""
    try:
        user_id = session.get('user_id')
        repos = repo_manager.list_repositories(user_id)
        
        # 添加统计信息
        repo_list = []
        for repo in repos:
            repo_dict = repo.to_dict()
            
            # 获取分支数和议题数
            with repo_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # 分支数
                cursor.execute('SELECT COUNT(*) as count FROM branches WHERE repository_id = ?', (repo.id,))
                repo_dict['branch_count'] = cursor.fetchone()['count']
                
                # 议题数
                cursor.execute('SELECT COUNT(*) as count FROM issues WHERE repository_id = ?', (repo.id,))
                repo_dict['issue_count'] = cursor.fetchone()['count']
                
                # 开放议题数
                cursor.execute('SELECT COUNT(*) as count FROM issues WHERE repository_id = ? AND status = "open"', (repo.id,))
                repo_dict['open_issue_count'] = cursor.fetchone()['count']
                
            repo_list.append(repo_dict)
            
        return jsonify({'repositories': repo_list}), 200
        
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos', methods=['POST'])
@login_required
def create_repository():
    """创建仓库"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        organization = data.get('organization', 'personal')
        is_private = data.get('is_private', False)
        github_url = data.get('github_url')
        
        if not name:
            return jsonify({'error': 'Repository name is required'}), 400
            
        user_id = session.get('user_id')
        
        # 创建仓库
        repo = repo_manager.create_repository(
            name=name,
            owner_id=user_id,
            organization=organization,
            description=description,
            is_private=is_private,
            github_url=github_url
        )
        
        return jsonify({
            'message': 'Repository created successfully',
            'repository': repo.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>', methods=['GET'])
@login_required
def get_repository(repo_id):
    """获取仓库详情"""
    try:
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        repo_dict = repo.to_dict()
        
        # 获取分支列表
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM branches 
                WHERE repository_id = ? 
                ORDER BY created_at DESC
            ''', (repo_id,))
            
            branches = []
            for row in cursor.fetchall():
                branch = {
                    'id': row['id'],
                    'name': row['name'],
                    'status': row['status'],
                    'description': row['description'],
                    'created_at': row['created_at']
                }
                branches.append(branch)
                
            repo_dict['branches'] = branches
            
        return jsonify(repo_dict), 200
        
    except Exception as e:
        logger.error(f"Error getting repository: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/branches', methods=['POST'])
@login_required
def create_branch(repo_id):
    """创建分支（任务）"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        base_branch = data.get('base_branch', 'main')
        
        if not name:
            return jsonify({'error': 'Branch name is required'}), 400
            
        user_id = session.get('user_id')
        
        # 创建分支
        branch = repo_manager.create_branch(
            repository_id=repo_id,
            name=name,
            created_by=user_id,
            base_branch=base_branch,
            description=description
        )
        
        return jsonify({
            'message': 'Branch created successfully',
            'branch': branch.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating branch: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/branches/<branch_id>/execute', methods=['POST'])
@login_required
def execute_branch(branch_id):
    """执行分支任务（AI 生成代码）"""
    try:
        # 获取分支信息
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.*, r.local_path 
                FROM branches b
                JOIN repositories r ON b.repository_id = r.id
                WHERE b.id = ?
            ''', (branch_id,))
            
            branch_row = cursor.fetchone()
            if not branch_row:
                return jsonify({'error': 'Branch not found'}), 404
                
        # 切换到分支
        repo_path = branch_row['local_path']
        branch_name = branch_row['name']
        
        import subprocess
        try:
            subprocess.run(['git', 'checkout', branch_name], cwd=repo_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to checkout branch: {e}")
            
        # 执行任务
        executor = get_executor()
        task_id = executor.execute(
            prompt=branch_row['description'],
            project_path=repo_path,
            user_id=session.get('user_id')
        )
        
        # 更新分支状态
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE branches 
                SET status = 'in_progress', updated_at = datetime('now')
                WHERE id = ?
            ''', (branch_id,))
            conn.commit()
            
        return jsonify({
            'message': 'Task execution started',
            'task_id': task_id,
            'branch_id': branch_id
        }), 202
        
    except Exception as e:
        logger.error(f"Error executing branch: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/issues', methods=['POST'])
@login_required
def create_issue(repo_id):
    """创建议题（子任务）"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        branch_id = data.get('branch_id')
        priority = data.get('priority', 'medium')
        
        if not title:
            return jsonify({'error': 'Issue title is required'}), 400
            
        user_id = session.get('user_id')
        
        # 创建议题
        issue = repo_manager.create_issue(
            repository_id=repo_id,
            title=title,
            created_by=user_id,
            description=description,
            branch_id=branch_id,
            priority=priority
        )
        
        return jsonify({
            'message': 'Issue created successfully',
            'issue': issue.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating issue: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/issues', methods=['GET'])
@login_required
def list_issues(repo_id):
    """列出仓库的议题"""
    try:
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.*, u.email as created_by_email
                FROM issues i
                LEFT JOIN users u ON i.created_by = u.id
                WHERE i.repository_id = ?
                ORDER BY i.created_at DESC
            ''', (repo_id,))
            
            issues = []
            for row in cursor.fetchall():
                issue = {
                    'id': row['id'],
                    'number': row['number'],
                    'title': row['title'],
                    'description': row['description'],
                    'status': row['status'],
                    'priority': row['priority'],
                    'created_by': row['created_by'],
                    'created_by_email': row['created_by_email'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                
                # 获取标签
                cursor.execute('SELECT label, color FROM issue_labels WHERE issue_id = ?', (row['id'],))
                issue['labels'] = [{'label': r['label'], 'color': r['color']} for r in cursor.fetchall()]
                
                issues.append(issue)
                
        return jsonify({'issues': issues}), 200
        
    except Exception as e:
        logger.error(f"Error listing issues: {str(e)}")
        return jsonify({'error': str(e)}), 500