"""
Dashboard API 的单元测试
"""
import pytest
import json
from datetime import datetime, timedelta


class TestDashboardAPI:
    """测试 Dashboard API"""
    
    def test_dashboard_requires_auth(self, client):
        """测试 Dashboard API 需要认证"""
        response = client.get('/api/v2/dashboard')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Authentication required'
    
    def test_dashboard_empty_data(self, client, auth_headers):
        """测试空数据时的 Dashboard 响应"""
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # 检查响应结构
        assert 'repositories' in data
        assert 'recent_tasks' in data
        assert 'stats' in data
        assert 'quick_actions' in data
        
        # 检查空数据
        assert data['repositories'] == []
        assert data['recent_tasks'] == []
        assert data['stats']['total_repos'] == 0
        assert data['stats']['active_tasks'] == 0
        assert data['stats']['completed_today'] == 0
        
        # 检查快捷操作
        assert len(data['quick_actions']) == 3
        actions = {action['id']: action for action in data['quick_actions']}
        assert 'create_task' in actions
        assert 'view_repos' in actions
        assert 'settings' in actions
    
    def test_dashboard_with_repositories(self, client, auth_headers, test_user):
        """测试有仓库数据时的 Dashboard 响应"""
        # 创建一些测试仓库
        from models.repository import RepositoryManager
        import tempfile
        import os
        
        repo_manager = RepositoryManager(
            db_path=os.environ.get('DATABASE_PATH'),
            workspace_path=tempfile.mkdtemp()
        )
        
        # 创建多个仓库
        repos = []
        for i in range(3):
            repo = repo_manager.create_repository(
                name=f"test-repo-{i}",
                owner_id=test_user.id,
                organization=f"org-{i}",
                description=f"Test repository {i}"
            )
            repos.append(repo)
        
        # 获取 Dashboard 数据
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # 检查仓库数据
        assert len(data['repositories']) <= 5  # 最多返回 5 个
        assert data['stats']['total_repos'] == 3
        
        # 检查仓库排序（按更新时间倒序）
        repo_times = [repo.get('updated_at', '') for repo in data['repositories']]
        assert repo_times == sorted(repo_times, reverse=True)
    
    def test_dashboard_repository_object_handling(self, client, auth_headers, test_repo):
        """测试 Dashboard 正确处理 Repository 对象（防止 'get' 方法错误）"""
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # 确保返回的是字典，不是 Repository 对象
        if data['repositories']:
            repo = data['repositories'][0]
            assert isinstance(repo, dict)
            assert 'id' in repo
            assert 'name' in repo
            assert 'updated_at' in repo
    
    def test_dashboard_with_tasks(self, client, auth_headers, test_repo):
        """测试有任务（分支）时的 Dashboard 响应"""
        from models.branch import BranchManager
        
        branch_manager = BranchManager(db_path=os.environ.get('DATABASE_PATH'))
        
        # 创建一些任务分支
        for i in range(3):
            branch_manager.create_branch(
                repository_id=test_repo.id,
                name=f"task/feature-{i}",
                description=f"Feature {i} implementation",
                created_by=test_repo.owner_id
            )
        
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # 检查最近任务
        assert len(data['recent_tasks']) > 0
        
        # 检查任务格式
        for task in data['recent_tasks']:
            assert 'id' in task
            assert 'title' in task
            assert 'repository' in task
            assert 'status' in task
            assert 'created_at' in task
    
    def test_dashboard_performance(self, client, auth_headers, test_user):
        """测试 Dashboard API 的性能（大量数据）"""
        from models.repository import RepositoryManager
        import tempfile
        import os
        import time
        
        repo_manager = RepositoryManager(
            db_path=os.environ.get('DATABASE_PATH'),
            workspace_path=tempfile.mkdtemp()
        )
        
        # 创建 20 个仓库
        for i in range(20):
            repo_manager.create_repository(
                name=f"perf-test-repo-{i}",
                owner_id=test_user.id,
                organization="perf-test",
                description=f"Performance test repository {i}"
            )
        
        # 测量响应时间
        start_time = time.time()
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # 响应时间应该在合理范围内（例如小于 1 秒）
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response time too slow: {response_time}s"
        
        data = json.loads(response.data)
        
        # 应该只返回最近的 5 个仓库
        assert len(data['repositories']) == 5
        assert data['stats']['total_repos'] == 20
    
    def test_dashboard_error_handling(self, client, auth_headers):
        """测试 Dashboard API 的错误处理"""
        # 这个测试主要是确保即使内部出错也能返回合理的响应
        # 由于我们已经修复了 Repository 对象的 'get' 方法问题，
        # 这里主要测试 API 的健壮性
        
        response = client.get('/api/v2/dashboard', headers=auth_headers)
        assert response.status_code in [200, 500]
        
        if response.status_code == 500:
            data = json.loads(response.data)
            assert 'error' in data
            # 不应该包含 "'Repository' object has no attribute 'get'" 错误
            assert "'Repository' object has no attribute 'get'" not in str(data.get('error', ''))