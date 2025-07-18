"""
GitHub Webhook 处理服务
"""
import os
import hmac
import hashlib
import json
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubWebhookHandler:
    """处理 GitHub Webhook 事件"""
    
    def __init__(self, webhook_secret: Optional[str] = None):
        # 优先使用传入的密钥，其次从配置系统，最后从环境变量
        if not webhook_secret:
            try:
                from models.config import ConfigManager
                config_manager = ConfigManager()
                webhook_secret = config_manager.get_config('github.webhook_secret')
            except:
                pass
        
        self.webhook_secret = webhook_secret or os.getenv('GITHUB_WEBHOOK_SECRET')
        self.event_handlers = {
            'push': self.handle_push,
            'pull_request': self.handle_pull_request,
            'issues': self.handle_issues,
            'issue_comment': self.handle_issue_comment,
            'create': self.handle_create,
            'delete': self.handle_delete,
            'repository': self.handle_repository,
            'release': self.handle_release,
            'star': self.handle_star,
            'fork': self.handle_fork
        }
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """验证 GitHub Webhook 签名"""
        if not self.webhook_secret:
            return True  # 如果没有设置密钥，跳过验证
            
        expected_signature = 'sha256=' + hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self, event_type: str, payload: Dict, 
                       signature: Optional[str] = None) -> Dict:
        """处理 Webhook 事件"""
        # 验证签名
        if signature and not self.verify_signature(
            json.dumps(payload, separators=(',', ':')).encode('utf-8'), 
            signature
        ):
            logger.warning(f"Invalid webhook signature for event: {event_type}")
            return {'error': 'Invalid signature', 'status': 'rejected'}
        
        # 记录事件
        logger.info(f"Processing GitHub webhook event: {event_type}")
        
        # 调用对应的处理器
        handler = self.event_handlers.get(event_type)
        if handler:
            try:
                result = handler(payload)
                return {
                    'status': 'processed',
                    'event': event_type,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Error processing webhook event {event_type}: {str(e)}")
                return {
                    'status': 'error',
                    'event': event_type,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        else:
            logger.info(f"No handler for event type: {event_type}")
            return {
                'status': 'ignored',
                'event': event_type,
                'message': 'Event type not handled',
                'timestamp': datetime.now().isoformat()
            }
    
    def handle_push(self, payload: Dict) -> Dict:
        """处理推送事件"""
        repository = payload.get('repository', {})
        pusher = payload.get('pusher', {})
        commits = payload.get('commits', [])
        ref = payload.get('ref', '')
        
        branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else None
        
        result = {
            'repository': repository.get('full_name'),
            'branch': branch,
            'pusher': pusher.get('name'),
            'commits_count': len(commits),
            'commits': []
        }
        
        # 处理每个提交
        for commit in commits:
            result['commits'].append({
                'id': commit.get('id'),
                'message': commit.get('message'),
                'author': commit.get('author', {}).get('name'),
                'timestamp': commit.get('timestamp'),
                'added': len(commit.get('added', [])),
                'modified': len(commit.get('modified', [])),
                'removed': len(commit.get('removed', []))
            })
        
        logger.info(f"Push event: {result['commits_count']} commits to {result['repository']}/{branch}")
        
        # TODO: 触发仓库同步
        return result
    
    def handle_pull_request(self, payload: Dict) -> Dict:
        """处理 Pull Request 事件"""
        action = payload.get('action')
        pr = payload.get('pull_request', {})
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'pr_number': pr.get('number'),
            'pr_title': pr.get('title'),
            'pr_state': pr.get('state'),
            'pr_merged': pr.get('merged'),
            'user': pr.get('user', {}).get('login'),
            'base_branch': pr.get('base', {}).get('ref'),
            'head_branch': pr.get('head', {}).get('ref')
        }
        
        logger.info(f"PR event: {action} PR #{result['pr_number']} in {result['repository']}")
        
        # TODO: 更新本地 PR 状态
        return result
    
    def handle_issues(self, payload: Dict) -> Dict:
        """处理议题事件"""
        action = payload.get('action')
        issue = payload.get('issue', {})
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'issue_number': issue.get('number'),
            'issue_title': issue.get('title'),
            'issue_state': issue.get('state'),
            'user': issue.get('user', {}).get('login'),
            'labels': [label.get('name') for label in issue.get('labels', [])]
        }
        
        logger.info(f"Issue event: {action} issue #{result['issue_number']} in {result['repository']}")
        
        # TODO: 同步议题状态
        return result
    
    def handle_issue_comment(self, payload: Dict) -> Dict:
        """处理议题评论事件"""
        action = payload.get('action')
        issue = payload.get('issue', {})
        comment = payload.get('comment', {})
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'issue_number': issue.get('number'),
            'comment_id': comment.get('id'),
            'comment_body': comment.get('body', '')[:100] + '...',
            'user': comment.get('user', {}).get('login')
        }
        
        logger.info(f"Comment event: {action} on issue #{result['issue_number']}")
        return result
    
    def handle_create(self, payload: Dict) -> Dict:
        """处理创建事件（分支、标签）"""
        ref_type = payload.get('ref_type')
        ref = payload.get('ref')
        repository = payload.get('repository', {})
        
        result = {
            'ref_type': ref_type,
            'ref_name': ref,
            'repository': repository.get('full_name'),
            'pusher': payload.get('sender', {}).get('login')
        }
        
        logger.info(f"Create event: {ref_type} '{ref}' in {result['repository']}")
        
        # TODO: 如果是分支创建，同步到本地
        return result
    
    def handle_delete(self, payload: Dict) -> Dict:
        """处理删除事件（分支、标签）"""
        ref_type = payload.get('ref_type')
        ref = payload.get('ref')
        repository = payload.get('repository', {})
        
        result = {
            'ref_type': ref_type,
            'ref_name': ref,
            'repository': repository.get('full_name'),
            'pusher': payload.get('sender', {}).get('login')
        }
        
        logger.info(f"Delete event: {ref_type} '{ref}' in {result['repository']}")
        
        # TODO: 如果是分支删除，更新本地状态
        return result
    
    def handle_repository(self, payload: Dict) -> Dict:
        """处理仓库事件"""
        action = payload.get('action')
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'private': repository.get('private'),
            'description': repository.get('description')
        }
        
        logger.info(f"Repository event: {action} {result['repository']}")
        return result
    
    def handle_release(self, payload: Dict) -> Dict:
        """处理发布事件"""
        action = payload.get('action')
        release = payload.get('release', {})
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'tag_name': release.get('tag_name'),
            'release_name': release.get('name'),
            'prerelease': release.get('prerelease'),
            'author': release.get('author', {}).get('login')
        }
        
        logger.info(f"Release event: {action} {result['tag_name']} in {result['repository']}")
        return result
    
    def handle_star(self, payload: Dict) -> Dict:
        """处理 Star 事件"""
        action = payload.get('action')
        repository = payload.get('repository', {})
        
        result = {
            'action': action,
            'repository': repository.get('full_name'),
            'stars_count': repository.get('stargazers_count'),
            'user': payload.get('sender', {}).get('login')
        }
        
        logger.info(f"Star event: {action} by {result['user']} on {result['repository']}")
        return result
    
    def handle_fork(self, payload: Dict) -> Dict:
        """处理 Fork 事件"""
        forkee = payload.get('forkee', {})
        repository = payload.get('repository', {})
        
        result = {
            'repository': repository.get('full_name'),
            'fork_name': forkee.get('full_name'),
            'fork_owner': forkee.get('owner', {}).get('login'),
            'forks_count': repository.get('forks_count')
        }
        
        logger.info(f"Fork event: {result['fork_owner']} forked {result['repository']}")
        return result