"""
GitHub 集成服务
"""
import os
import re
import json
import subprocess
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests

from models.config import ConfigManager

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """GitHub 集成类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.token = self._get_github_token()
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        } if self.token else {}
        self.api_base = 'https://api.github.com'
    
    def _get_github_token(self) -> Optional[str]:
        """获取 GitHub Token"""
        # 优先从配置管理器获取
        token = self.config_manager.get_config('github.token')
        if token:
            return token
            
        # 其次从环境变量获取
        return os.environ.get('GITHUB_TOKEN')
    
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """解析 GitHub URL
        
        支持格式：
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git
        - owner/repo
        """
        # 移除 .git 后缀
        url = url.rstrip('.git')
        
        # 处理 SSH 格式
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/')
        
        # 处理简短格式 owner/repo
        if '/' in url and not url.startswith('http'):
            parts = url.split('/')
            if len(parts) == 2:
                return {
                    'owner': parts[0],
                    'repo': parts[1],
                    'full_name': url
                }
        
        # 解析 HTTPS URL
        if url.startswith('https://github.com/'):
            path = url.replace('https://github.com/', '')
            parts = path.split('/')
            if len(parts) >= 2:
                return {
                    'owner': parts[0],
                    'repo': parts[1],
                    'full_name': f"{parts[0]}/{parts[1]}"
                }
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def import_repository(self, github_url: str) -> Dict:
        """从 GitHub 导入仓库信息"""
        try:
            # 解析 URL
            repo_info = self.parse_github_url(github_url)
            
            # 如果没有 token，返回基本信息
            if not self.token:
                return {
                    'name': repo_info['repo'],
                    'organization': repo_info['owner'],
                    'description': '',
                    'is_private': False,
                    'github_url': f"https://github.com/{repo_info['full_name']}",
                    'default_branch': 'main'
                }
            
            # 调用 GitHub API 获取详细信息
            api_url = f"{self.api_base}/repos/{repo_info['full_name']}"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"Repository not found: {repo_info['full_name']}")
            elif response.status_code == 401:
                raise ValueError("GitHub token is invalid or expired")
            elif response.status_code \!= 200:
                raise ValueError(f"GitHub API error: {response.status_code}")
            
            data = response.json()
            
            return {
                'name': data['name'],
                'organization': data['owner']['login'],
                'description': data.get('description', ''),
                'is_private': data.get('private', False),
                'github_url': data['html_url'],
                'default_branch': data.get('default_branch', 'main'),
                'language': data.get('language'),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error importing repository: {str(e)}")
            raise
    
    def clone_repository(self, github_url: str, local_path: str) -> bool:
        """克隆仓库到本地"""
        try:
            # 确保父目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 如果目录已存在，先删除
            if os.path.exists(local_path):
                import shutil
                shutil.rmtree(local_path)
            
            # 构建克隆命令
            clone_url = github_url
            if self.token and github_url.startswith('https://'):
                # 添加 token 到 URL 中进行认证
                clone_url = github_url.replace('https://', f'https://{self.token}@')
            
            # 执行克隆
            cmd = ['git', 'clone', clone_url, local_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode \!= 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return False
            
            logger.info(f"Successfully cloned repository to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            return False
    
    def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """列出仓库的所有分支"""
        if not self.token:
            return []
            
        try:
            api_url = f"{self.api_base}/repos/{owner}/{repo}/branches"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list branches: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing branches: {str(e)}")
            return []
    
    def list_issues(self, owner: str, repo: str, state: str = 'open') -> List[Dict]:
        """列出仓库的 Issues"""
        if not self.token:
            return []
            
        try:
            api_url = f"{self.api_base}/repos/{owner}/{repo}/issues"
            params = {'state': state}
            response = requests.get(api_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list issues: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing issues: {str(e)}")
            return []
    
    def create_webhook(self, owner: str, repo: str, webhook_url: str, secret: str) -> Optional[Dict]:
        """创建 Webhook"""
        if not self.token:
            logger.warning("No GitHub token available for creating webhook")
            return None
            
        try:
            api_url = f"{self.api_base}/repos/{owner}/{repo}/hooks"
            
            config = {
                'url': webhook_url,
                'content_type': 'json',
                'secret': secret
            }
            
            data = {
                'name': 'web',
                'active': True,
                'events': ['push', 'pull_request', 'issues', 'issue_comment'],
                'config': config
            }
            
            response = requests.post(api_url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                logger.info(f"Webhook created successfully for {owner}/{repo}")
                return response.json()
            else:
                logger.error(f"Failed to create webhook: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating webhook: {str(e)}")
            return None
    
    def sync_repository(self, local_path: str) -> bool:
        """同步本地仓库与远程仓库"""
        try:
            # 拉取最新代码
            cmd = ['git', 'pull', 'origin']
            result = subprocess.run(cmd, cwd=local_path, capture_output=True, text=True)
            
            if result.returncode \!= 0:
                logger.error(f"Git pull failed: {result.stderr}")
                return False
            
            logger.info(f"Successfully synced repository at {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing repository: {str(e)}")
            return False
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str, 
                          head: str, base: str = 'main') -> Optional[Dict]:
        """创建 Pull Request"""
        if not self.token:
            logger.warning("No GitHub token available for creating PR")
            return None
            
        try:
            api_url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
            
            data = {
                'title': title,
                'body': body,
                'head': head,
                'base': base
            }
            
            response = requests.post(api_url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                logger.info(f"Pull request created successfully")
                return response.json()
            else:
                logger.error(f"Failed to create PR: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            return None
EOF < /dev/null
