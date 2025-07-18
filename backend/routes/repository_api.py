"""
GitHub 风格的仓库管理 API
"""
from flask import Blueprint, jsonify, request, session
from models.repository import RepositoryManager, Repository, Branch, Issue
from services.claude_executor import get_executor
from services.github_integration import GitHubIntegration
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


@repo_bp.route('/repos/import', methods=['POST'])
@login_required
def import_repository():
    """从 GitHub 导入仓库"""
    try:
        data = request.get_json()
        github_url = data.get('github_url')
        
        if not github_url:
            return jsonify({'error': 'GitHub URL is required'}), 400
            
        # 初始化 GitHub 集成
        github = GitHubIntegration()
        
        # 导入仓库信息
        repo_info = github.import_repository(github_url)
        
        # 创建本地仓库记录
        user_id = session.get('user_id')
        repo = repo_manager.create_repository(
            name=repo_info['name'],
            owner_id=user_id,
            description=repo_info['description'],
            is_private=repo_info['is_private'],
            github_url=repo_info['github_url']
        )
        
        # 克隆仓库到本地
        import os
        local_path = os.path.join('repositories', str(user_id), repo_info['name'])
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        if github.clone_repository(github_url, local_path):
            # 更新仓库本地路径
            with repo_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE repositories 
                    SET local_path = ?, updated_at = datetime('now')
                    WHERE id = ?
                ''', (local_path, repo.id))
                conn.commit()
        
        return jsonify({
            'message': 'Repository imported successfully',
            'repository': repo.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error importing repository: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/sync', methods=['POST'])
@login_required
def sync_repository(repo_id):
    """同步仓库与 GitHub"""
    try:
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        if not repo.github_url:
            return jsonify({'error': 'Repository is not linked to GitHub'}), 400
            
        # 解析 GitHub URL
        parts = repo.github_url.rstrip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        
        # 初始化 GitHub 集成
        github = GitHubIntegration()
        
        # 同步统计信息
        stats = github.sync_repository_stats(owner, repo_name)
        
        # 同步分支
        branches = github.list_branches(owner, repo_name)
        
        # 同步议题
        issues = github.list_issues(owner, repo_name)
        
        # 更新本地数据
        # TODO: 更新数据库中的分支和议题信息
        
        return jsonify({
            'message': 'Repository synced successfully',
            'stats': stats,
            'branches_count': len(branches),
            'issues_count': len(issues)
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing repository: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/commit', methods=['POST'])
@login_required
def commit_changes(repo_id):
    """提交代码更改"""
    try:
        data = request.get_json()
        message = data.get('message')
        branch = data.get('branch', 'main')
        
        if not message:
            return jsonify({'error': 'Commit message is required'}), 400
            
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        if not repo.local_path:
            return jsonify({'error': 'Repository has no local path'}), 400
            
        import subprocess
        
        # 切换到指定分支
        subprocess.run(['git', 'checkout', branch], 
                      cwd=repo.local_path, check=True, capture_output=True)
        
        # 添加所有更改
        subprocess.run(['git', 'add', '.'], 
                      cwd=repo.local_path, check=True, capture_output=True)
        
        # 提交更改
        user_email = session.get('user_email', 'claude.task@sparticle.com')
        subprocess.run(['git', 'commit', '-m', message, '--author', f'ClaudeTask <{user_email}>'], 
                      cwd=repo.local_path, check=True, capture_output=True)
        
        # 记录提交到数据库
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commits (repository_id, branch_name, message, author_id, sha)
                VALUES (?, ?, ?, ?, ?)
            ''', (repo_id, branch, message, session.get('user_id'), 'pending'))
            conn.commit()
        
        return jsonify({
            'message': 'Changes committed successfully',
            'commit_message': message,
            'branch': branch
        }), 201
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return jsonify({'error': f'Git error: {e.stderr.decode() if e.stderr else str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error committing changes: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/push', methods=['POST'])
@login_required
def push_to_remote(repo_id):
    """推送到远程仓库"""
    try:
        data = request.get_json()
        branch = data.get('branch', 'main')
        
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        if not repo.local_path:
            return jsonify({'error': 'Repository has no local path'}), 400
            
        if not repo.github_url:
            return jsonify({'error': 'Repository is not linked to GitHub'}), 400
            
        # 初始化 GitHub 集成
        github = GitHubIntegration()
        
        # 推送更改
        success = github.push_changes(repo.local_path, branch)
        
        if success:
            return jsonify({
                'message': 'Changes pushed successfully',
                'branch': branch
            }), 200
        else:
            return jsonify({'error': 'Failed to push changes'}), 500
            
    except Exception as e:
        logger.error(f"Error pushing to remote: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/pull', methods=['POST'])
@login_required
def pull_from_remote(repo_id):
    """从远程仓库拉取更新"""
    try:
        data = request.get_json()
        branch = data.get('branch', 'main')
        
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        if not repo.local_path:
            return jsonify({'error': 'Repository has no local path'}), 400
            
        if not repo.github_url:
            return jsonify({'error': 'Repository is not linked to GitHub'}), 400
            
        import subprocess
        
        # 切换到指定分支
        subprocess.run(['git', 'checkout', branch], 
                      cwd=repo.local_path, check=True, capture_output=True)
        
        # 拉取更新
        result = subprocess.run(['git', 'pull', 'origin', branch], 
                               cwd=repo.local_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'message': 'Updates pulled successfully',
                'branch': branch,
                'output': result.stdout
            }), 200
        else:
            return jsonify({
                'error': 'Failed to pull updates',
                'output': result.stderr
            }), 500
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return jsonify({'error': f'Git error: {e.stderr.decode() if e.stderr else str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error pulling from remote: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/branches/<branch_id>/pr', methods=['POST'])
@login_required
def create_pull_request(branch_id):
    """创建 Pull Request"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        base_branch = data.get('base_branch', 'main')
        
        if not title:
            return jsonify({'error': 'Pull request title is required'}), 400
            
        # 获取分支信息
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.*, r.github_url, r.local_path
                FROM branches b
                JOIN repositories r ON b.repository_id = r.id
                WHERE b.id = ?
            ''', (branch_id,))
            
            branch_row = cursor.fetchone()
            if not branch_row:
                return jsonify({'error': 'Branch not found'}), 404
                
        if not branch_row['github_url']:
            return jsonify({'error': 'Repository is not linked to GitHub'}), 400
            
        # 解析 GitHub URL
        parts = branch_row['github_url'].rstrip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        
        # 初始化 GitHub 集成
        github = GitHubIntegration()
        
        # 创建 Pull Request
        pr = github.create_pull_request(
            owner=owner,
            repo=repo_name,
            title=title,
            head=branch_row['name'],
            base=base_branch,
            body=description
        )
        
        if pr:
            # 记录到数据库
            with repo_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pull_requests 
                    (repository_id, branch_id, title, description, github_pr_number, 
                     github_pr_url, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    branch_row['repository_id'], branch_id, title, description,
                    pr['number'], pr['html_url'], 'open', session.get('user_id')
                ))
                conn.commit()
                
            return jsonify({
                'message': 'Pull request created successfully',
                'pr_number': pr['number'],
                'pr_url': pr['html_url'],
                'title': title
            }), 201
        else:
            return jsonify({'error': 'Failed to create pull request'}), 500
            
    except Exception as e:
        logger.error(f"Error creating pull request: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/webhook', methods=['POST'])
@login_required
def create_webhook(repo_id):
    """为仓库创建 GitHub Webhook"""
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url')
        
        if not webhook_url:
            # 使用默认的 webhook URL
            base_url = request.host_url.rstrip('/')
            webhook_url = f"{base_url}/api/webhooks/github"
        
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        if not repo.github_url:
            return jsonify({'error': 'Repository is not linked to GitHub'}), 400
            
        # 解析 GitHub URL
        parts = repo.github_url.rstrip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        
        # 初始化 GitHub 集成
        github = GitHubIntegration()
        
        # 获取 webhook 密钥
        import os
        webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
        
        # 创建 webhook
        webhook = github.create_webhook(
            owner=owner,
            repo=repo_name,
            webhook_url=webhook_url,
            secret=webhook_secret
        )
        
        if webhook:
            # 更新数据库
            with repo_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE repositories 
                    SET webhook_id = ?, webhook_url = ?, webhook_active = 1, 
                        updated_at = datetime('now')
                    WHERE id = ?
                ''', (webhook['id'], webhook_url, repo_id))
                conn.commit()
                
            return jsonify({
                'message': 'Webhook created successfully',
                'webhook_id': webhook['id'],
                'webhook_url': webhook_url,
                'events': webhook.get('events', [])
            }), 201
        else:
            return jsonify({'error': 'Failed to create webhook'}), 500
            
    except Exception as e:
        logger.error(f"Error creating webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500


@repo_bp.route('/repos/<repo_id>/webhook', methods=['DELETE'])
@login_required
def delete_webhook(repo_id):
    """删除仓库的 GitHub Webhook"""
    try:
        repo = repo_manager.get_repository(repo_id)
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        # 获取 webhook ID
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT webhook_id FROM repositories WHERE id = ?', (repo_id,))
            row = cursor.fetchone()
            
            if not row or not row['webhook_id']:
                return jsonify({'error': 'No webhook configured'}), 404
                
            webhook_id = row['webhook_id']
            
        # 解析 GitHub URL
        parts = repo.github_url.rstrip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        
        # 删除 webhook
        github = GitHubIntegration()
        success = github.delete_webhook(owner, repo_name, int(webhook_id))
        
        if success:
            # 更新数据库
            with repo_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE repositories 
                    SET webhook_id = NULL, webhook_url = NULL, webhook_active = 0,
                        updated_at = datetime('now')
                    WHERE id = ?
                ''', (repo_id,))
                conn.commit()
                
            return jsonify({'message': 'Webhook deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete webhook'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500