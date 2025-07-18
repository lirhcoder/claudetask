"""
GitHub Webhook API 路由
"""
import os
import json
import logging
from flask import Blueprint, request, jsonify
from services.github_webhook import GitHubWebhookHandler
from models.repository import RepositoryManager

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

# 初始化 webhook 处理器
webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
webhook_handler = GitHubWebhookHandler(webhook_secret)
repo_manager = RepositoryManager()


@webhook_bp.route('/github', methods=['POST'])
def github_webhook():
    """接收 GitHub Webhook 事件"""
    # 获取事件类型
    event_type = request.headers.get('X-GitHub-Event')
    if not event_type:
        return jsonify({'error': 'Missing X-GitHub-Event header'}), 400
    
    # 获取签名
    signature = request.headers.get('X-Hub-Signature-256')
    
    # 获取请求体
    try:
        payload = request.get_json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {str(e)}")
        return jsonify({'error': 'Invalid JSON payload'}), 400
    
    # 处理 webhook
    result = webhook_handler.process_webhook(event_type, payload, signature)
    
    # 根据事件类型执行相应的操作
    if result['status'] == 'processed':
        process_webhook_result(event_type, payload, result)
    
    # GitHub 期望收到 2xx 响应
    return jsonify(result), 200 if result['status'] in ['processed', 'ignored'] else 400


def process_webhook_result(event_type: str, payload: dict, result: dict):
    """处理 webhook 结果，更新本地数据"""
    try:
        repository = payload.get('repository', {})
        repo_full_name = repository.get('full_name', '')
        
        if not repo_full_name:
            return
        
        # 查找对应的本地仓库
        github_url = repository.get('html_url', '')
        
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, local_path FROM repositories 
                WHERE github_url = ? OR github_url = ?
            ''', (github_url, github_url + '.git'))
            
            repo_row = cursor.fetchone()
            if not repo_row:
                logger.info(f"No local repository found for {github_url}")
                return
            
            repo_id = repo_row['id']
            
            # 根据事件类型更新数据
            if event_type == 'push':
                # 更新最后推送时间
                cursor.execute('''
                    UPDATE repositories 
                    SET updated_at = datetime('now')
                    WHERE id = ?
                ''', (repo_id,))
                
                # 记录推送事件
                cursor.execute('''
                    INSERT INTO webhook_events 
                    (repository_id, event_type, payload, processed_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (repo_id, event_type, json.dumps(result['result'])))
                
            elif event_type == 'pull_request':
                pr_data = result['result']
                if pr_data['action'] in ['opened', 'closed', 'reopened']:
                    # 更新 PR 状态
                    cursor.execute('''
                        UPDATE pull_requests 
                        SET status = ?, updated_at = datetime('now')
                        WHERE repository_id = ? AND github_pr_number = ?
                    ''', (pr_data['pr_state'], repo_id, pr_data['pr_number']))
                    
            elif event_type == 'issues':
                issue_data = result['result']
                # TODO: 更新议题状态
                logger.info(f"Issue {issue_data['action']}: #{issue_data['issue_number']}")
                
            elif event_type == 'create' and result['result']['ref_type'] == 'branch':
                # 新分支创建
                branch_name = result['result']['ref_name']
                logger.info(f"New branch created: {branch_name}")
                # TODO: 同步新分支到本地
                
            conn.commit()
            
    except Exception as e:
        logger.error(f"Error processing webhook result: {str(e)}")


@webhook_bp.route('/github/test', methods=['POST'])
def test_github_webhook():
    """测试 Webhook 配置"""
    # GitHub 发送 ping 事件来测试 webhook
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'ping':
        payload = request.get_json()
        return jsonify({
            'message': 'pong',
            'zen': payload.get('zen', 'Design for failure.'),
            'hook_id': payload.get('hook_id'),
            'repository': payload.get('repository', {}).get('full_name')
        }), 200
    
    return jsonify({'message': 'Webhook test endpoint'}), 200


@webhook_bp.route('/github/events', methods=['GET'])
def list_webhook_events():
    """列出最近的 webhook 事件"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        with repo_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT we.*, r.name as repo_name
                FROM webhook_events we
                LEFT JOIN repositories r ON we.repository_id = r.id
                ORDER BY we.processed_at DESC
                LIMIT ?
            ''', (limit,))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row['id'],
                    'repository': row['repo_name'],
                    'event_type': row['event_type'],
                    'payload': json.loads(row['payload']) if row['payload'] else None,
                    'processed_at': row['processed_at']
                })
            
        return jsonify({'events': events}), 200
        
    except Exception as e:
        logger.error(f"Error listing webhook events: {str(e)}")
        return jsonify({'error': str(e)}), 500