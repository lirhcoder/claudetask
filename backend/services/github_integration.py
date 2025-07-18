"""
GitHub API 集成服务
"""
import os
import json
import logging
from typing import Dict, List, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """GitHub API 集成"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv('GITHUB_ACCESS_TOKEN')
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.access_token:
            self.headers['Authorization'] = f'token {self.access_token}'
    
    def import_repository(self, github_url: str) -> Dict:
        """从 GitHub 导入仓库信息"""
        # 解析 GitHub URL
        # https://github.com/owner/repo -> owner, repo
        parts = github_url.rstrip('/').split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL")
        
        owner = parts[-2]
        repo_name = parts[-1].replace('.git', '')
        
        # 获取仓库信息
        repo_info = self.get_repository_info(owner, repo_name)
        
        return {
            'name': repo_info['name'],
            'description': repo_info['description'] or '',
            'is_private': repo_info['private'],
            'default_branch': repo_info['default_branch'],
            'github_url': repo_info['html_url'],
            'stars': repo_info['stargazers_count'],
            'forks': repo_info['forks_count'],
            'open_issues': repo_info['open_issues_count'],
            'language': repo_info['language'],
            'created_at': repo_info['created_at'],
            'updated_at': repo_info['updated_at']
        }
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """获取仓库信息"""
        url = f"{self.api_base}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            raise ValueError(f"Repository {owner}/{repo} not found")
        elif response.status_code == 401:
            raise ValueError("GitHub authentication failed")
        elif response.status_code != 200:
            raise ValueError(f"GitHub API error: {response.status_code}")
        
        return response.json()
    
    def list_branches(self, owner: str, repo: str) -> List[Dict]:
        """列出仓库的所有分支"""
        url = f"{self.api_base}/repos/{owner}/{repo}/branches"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to list branches: {response.status_code}")
            return []
    
    def create_branch(self, owner: str, repo: str, branch_name: str, 
                     base_branch: str = 'main') -> bool:
        """创建新分支"""
        # 首先获取基础分支的 SHA
        base_ref = self.get_branch_ref(owner, repo, base_branch)
        if not base_ref:
            return False
        
        # 创建新分支
        url = f"{self.api_base}/repos/{owner}/{repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': base_ref['object']['sha']
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.status_code == 201
    
    def get_branch_ref(self, owner: str, repo: str, branch: str) -> Optional[Dict]:
        """获取分支引用"""
        url = f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{branch}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get branch ref: {response.status_code}")
            return None
    
    def list_issues(self, owner: str, repo: str, state: str = 'open') -> List[Dict]:
        """列出议题"""
        url = f"{self.api_base}/repos/{owner}/{repo}/issues"
        params = {'state': state}
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to list issues: {response.status_code}")
            return []
    
    def create_issue(self, owner: str, repo: str, title: str, 
                    body: str = '', labels: List[str] = None) -> Optional[Dict]:
        """创建议题"""
        url = f"{self.api_base}/repos/{owner}/{repo}/issues"
        data = {
            'title': title,
            'body': body,
        }
        if labels:
            data['labels'] = labels
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            logger.error(f"Failed to create issue: {response.status_code}")
            return None
    
    def create_pull_request(self, owner: str, repo: str, title: str,
                          head: str, base: str = 'main', body: str = '') -> Optional[Dict]:
        """创建 Pull Request"""
        url = f"{self.api_base}/repos/{owner}/{repo}/pulls"
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body,
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            logger.error(f"Failed to create pull request: {response.status_code}")
            return None
    
    def sync_repository_stats(self, owner: str, repo: str) -> Dict:
        """同步仓库统计信息"""
        repo_info = self.get_repository_info(owner, repo)
        
        # 获取最新的提交
        commits_url = f"{self.api_base}/repos/{owner}/{repo}/commits"
        commits_response = requests.get(commits_url, params={'per_page': 1}, 
                                       headers=self.headers)
        
        latest_commit = None
        if commits_response.status_code == 200:
            commits = commits_response.json()
            if commits:
                latest_commit = commits[0]
        
        return {
            'stars': repo_info['stargazers_count'],
            'forks': repo_info['forks_count'],
            'open_issues': repo_info['open_issues_count'],
            'watchers': repo_info['watchers_count'],
            'size': repo_info['size'],
            'latest_commit': latest_commit,
            'updated_at': repo_info['updated_at'],
            'pushed_at': repo_info['pushed_at']
        }
    
    def clone_repository(self, github_url: str, local_path: str) -> bool:
        """克隆仓库到本地"""
        import subprocess
        
        try:
            # 如果提供了 token，使用认证的 URL
            if self.access_token and github_url.startswith('https://'):
                # 插入 token 到 URL 中
                auth_url = github_url.replace('https://', f'https://{self.access_token}@')
                subprocess.run(['git', 'clone', auth_url, local_path], 
                             check=True, capture_output=True)
            else:
                subprocess.run(['git', 'clone', github_url, local_path], 
                             check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repository: {e}")
            return False
    
    def push_changes(self, local_path: str, branch: str = 'main', 
                    message: str = 'Update from ClaudeTask') -> bool:
        """推送本地更改到 GitHub"""
        import subprocess
        
        try:
            # 添加所有更改
            subprocess.run(['git', 'add', '.'], cwd=local_path, check=True)
            
            # 提交更改
            subprocess.run(['git', 'commit', '-m', message], 
                         cwd=local_path, check=True)
            
            # 推送到远程
            subprocess.run(['git', 'push', 'origin', branch], 
                         cwd=local_path, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push changes: {e}")
            return False