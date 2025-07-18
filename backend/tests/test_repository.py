"""
Repository 模型和管理器的单元测试
"""
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from models.repository import Repository, RepositoryManager


class TestRepositoryModel:
    """测试 Repository 模型"""
    
    def test_repository_creation(self):
        """测试创建 Repository 对象"""
        repo = Repository(
            id="test-123",
            name="test-repo",
            organization="test-org",
            description="Test repository",
            owner_id="user-123",
            local_path="/tmp/test-repo"
        )
        
        assert repo.id == "test-123"
        assert repo.name == "test-repo"
        assert repo.organization == "test-org"
        assert repo.description == "Test repository"
        assert repo.owner_id == "user-123"
        assert repo.local_path == "/tmp/test-repo"
        assert repo.is_private == False  # 默认值
        assert repo.default_branch == "main"  # 默认值
    
    def test_repository_to_dict(self):
        """测试 Repository 对象转换为字典"""
        repo = Repository(
            id="test-123",
            name="test-repo",
            organization="test-org",
            description="Test repository",
            owner_id="user-123",
            local_path="/tmp/test-repo",
            github_url="https://github.com/test-org/test-repo",
            created_at=datetime(2025, 1, 1, 10, 0, 0),
            updated_at=datetime(2025, 1, 1, 11, 0, 0)
        )
        
        repo_dict = repo.to_dict()
        
        assert isinstance(repo_dict, dict)
        assert repo_dict['id'] == "test-123"
        assert repo_dict['name'] == "test-repo"
        assert repo_dict['organization'] == "test-org"
        assert repo_dict['description'] == "Test repository"
        assert repo_dict['owner_id'] == "user-123"
        assert repo_dict['local_path'] == "/tmp/test-repo"
        assert repo_dict['github_url'] == "https://github.com/test-org/test-repo"
        assert repo_dict['created_at'] == "2025-01-01T10:00:00"
        assert repo_dict['updated_at'] == "2025-01-01T11:00:00"
    
    def test_repository_to_dict_without_dates(self):
        """测试没有日期的 Repository 对象转换"""
        repo = Repository(
            id="test-123",
            name="test-repo",
            organization="test-org",
            description="Test repository",
            owner_id="user-123",
            local_path="/tmp/test-repo"
        )
        
        repo_dict = repo.to_dict()
        
        assert repo_dict['created_at'] is None
        assert repo_dict['updated_at'] is None
    
    def test_repository_has_no_get_method(self):
        """测试 Repository 对象没有 get 方法（这是我们修复的 bug）"""
        repo = Repository(
            id="test-123",
            name="test-repo",
            organization="test-org",
            description="Test repository",
            owner_id="user-123",
            local_path="/tmp/test-repo"
        )
        
        # Repository 对象不应该有 get 方法
        assert not hasattr(repo, 'get')
        
        # 但转换为字典后应该有 get 方法
        repo_dict = repo.to_dict()
        assert hasattr(repo_dict, 'get')
        assert repo_dict.get('name') == "test-repo"
        assert repo_dict.get('nonexistent', 'default') == 'default'


class TestRepositoryManager:
    """测试 RepositoryManager"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        db_fd, db_path = tempfile.mkstemp()
        yield db_path
        os.close(db_fd)
        os.unlink(db_path)
    
    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间"""
        workspace = tempfile.mkdtemp()
        yield workspace
        import shutil
        if os.path.exists(workspace):
            shutil.rmtree(workspace)
    
    @pytest.fixture
    def repo_manager(self, temp_db, temp_workspace):
        """创建 RepositoryManager 实例"""
        return RepositoryManager(db_path=temp_db, workspace_path=temp_workspace)
    
    def test_create_repository(self, repo_manager):
        """测试创建仓库"""
        repo = repo_manager.create_repository(
            name="test-repo",
            owner_id="user-123",
            organization="test-org",
            description="Test repository"
        )
        
        assert repo is not None
        assert repo.name == "test-repo"
        assert repo.owner_id == "user-123"
        assert repo.organization == "test-org"
        assert repo.description == "Test repository"
        assert os.path.exists(repo.local_path)
        
        # 检查 Git 仓库是否初始化
        git_dir = os.path.join(repo.local_path, '.git')
        assert os.path.exists(git_dir)
    
    def test_list_repositories(self, repo_manager):
        """测试列出仓库"""
        # 创建几个仓库
        repo1 = repo_manager.create_repository(
            name="repo1",
            owner_id="user-123",
            organization="org1"
        )
        repo2 = repo_manager.create_repository(
            name="repo2",
            owner_id="user-123",
            organization="org2"
        )
        repo3 = repo_manager.create_repository(
            name="repo3",
            owner_id="user-456",
            organization="org3"
        )
        
        # 列出所有仓库
        all_repos = repo_manager.list_repositories()
        assert len(all_repos) == 3
        
        # 列出特定用户的仓库
        user_repos = repo_manager.list_repositories(user_id="user-123")
        assert len(user_repos) == 2
        assert all(repo.owner_id == "user-123" for repo in user_repos)
        
        # 确保返回的是 Repository 对象
        for repo in user_repos:
            assert isinstance(repo, Repository)
            assert hasattr(repo, 'to_dict')
            assert not hasattr(repo, 'get')
    
    def test_get_repository(self, repo_manager):
        """测试获取单个仓库"""
        created_repo = repo_manager.create_repository(
            name="test-repo",
            owner_id="user-123",
            organization="test-org"
        )
        
        # 通过 ID 获取
        repo = repo_manager.get_repository(created_repo.id)
        assert repo is not None
        assert repo.id == created_repo.id
        assert repo.name == "test-repo"
        
        # 获取不存在的仓库
        repo = repo_manager.get_repository("nonexistent-id")
        assert repo is None
    
    def test_repository_with_github_url(self, repo_manager):
        """测试带 GitHub URL 的仓库"""
        repo = repo_manager.create_repository(
            name="github-repo",
            owner_id="user-123",
            organization="my-org",
            github_url="https://github.com/my-org/github-repo"
        )
        
        assert repo.github_url == "https://github.com/my-org/github-repo"
        
        # 检查字典转换
        repo_dict = repo.to_dict()
        assert repo_dict['github_url'] == "https://github.com/my-org/github-repo"
    
    def test_repository_sorting(self, repo_manager):
        """测试仓库排序（这是 Dashboard 中使用的功能）"""
        import time
        
        # 创建几个仓库，间隔一些时间
        repo1 = repo_manager.create_repository(
            name="repo1",
            owner_id="user-123",
            organization="org1"
        )
        time.sleep(0.1)
        
        repo2 = repo_manager.create_repository(
            name="repo2",
            owner_id="user-123",
            organization="org2"
        )
        time.sleep(0.1)
        
        repo3 = repo_manager.create_repository(
            name="repo3",
            owner_id="user-123",
            organization="org3"
        )
        
        # 获取所有仓库
        repos = repo_manager.list_repositories(user_id="user-123")
        
        # 转换为字典（模拟 Dashboard 的做法）
        repo_dicts = [repo.to_dict() if hasattr(repo, 'to_dict') else repo for repo in repos]
        
        # 按更新时间排序（最新的在前）
        sorted_repos = sorted(repo_dicts, key=lambda x: x.get('updated_at', ''), reverse=True)
        
        # 验证排序结果
        assert len(sorted_repos) == 3
        # 最后创建的应该在最前面
        assert sorted_repos[0]['name'] == 'repo3'
        assert sorted_repos[1]['name'] == 'repo2'
        assert sorted_repos[2]['name'] == 'repo1'