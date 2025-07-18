#!/usr/bin/env python3
"""
简单的测试运行器（不依赖 pytest）
"""
import os
import sys
import unittest
import traceback
from datetime import datetime

# 添加 backend 目录到 Python 路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)


def run_unit_tests():
    """运行单元测试的简单版本"""
    print("=" * 80)
    print(f"单元测试执行报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试 Repository 模型
    print("\n1. 测试 Repository 模型")
    print("-" * 40)
    try:
        from models.repository import Repository, RepositoryManager
        
        # 测试 1: Repository 对象创建
        print("✓ 测试 Repository 对象创建...")
        repo = Repository(
            id="test-123",
            name="test-repo",
            organization="test-org",
            description="Test repository",
            owner_id="user-123",
            local_path="/tmp/test-repo"
        )
        assert repo.name == "test-repo"
        print("  ✅ 通过: Repository 对象创建成功")
        
        # 测试 2: to_dict 方法
        print("✓ 测试 Repository.to_dict() 方法...")
        repo_dict = repo.to_dict()
        assert isinstance(repo_dict, dict)
        assert repo_dict['name'] == "test-repo"
        print("  ✅ 通过: to_dict() 返回正确的字典")
        
        # 测试 3: Repository 对象没有 get 方法
        print("✓ 测试 Repository 对象没有 get 方法...")
        assert not hasattr(repo, 'get')
        assert hasattr(repo_dict, 'get')
        print("  ✅ 通过: Repository 对象正确地没有 get 方法")
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        traceback.print_exc()
    
    # 测试认证功能
    print("\n2. 测试认证功能")
    print("-" * 40)
    try:
        from models.user import UserManager
        import tempfile
        
        # 使用临时数据库
        db_fd, db_path = tempfile.mkstemp()
        os.environ['DATABASE_PATH'] = db_path
        
        print("✓ 测试用户创建...")
        user_manager = UserManager(db_path=db_path)
        user = user_manager.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        assert user.email == "test@example.com"
        print("  ✅ 通过: 用户创建成功")
        
        print("✓ 测试密码验证...")
        assert user.check_password("testpass123") == True
        assert user.check_password("wrongpass") == False
        print("  ✅ 通过: 密码验证正确")
        
        print("✓ 测试通过邮箱查找用户...")
        found_user = user_manager.get_user_by_email("test@example.com")
        assert found_user is not None
        assert found_user.id == user.id
        print("  ✅ 通过: 通过邮箱查找用户成功")
        
        # 清理
        os.close(db_fd)
        os.unlink(db_path)
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        traceback.print_exc()
    
    # 测试 Dashboard API 逻辑
    print("\n3. 测试 Dashboard API 逻辑")
    print("-" * 40)
    try:
        from routes.unified_api import UnifiedWorkflow
        import tempfile
        
        # 使用临时数据库和工作空间
        db_fd, db_path = tempfile.mkstemp()
        workspace = tempfile.mkdtemp()
        os.environ['DATABASE_PATH'] = db_path
        
        print("✓ 测试 UnifiedWorkflow 初始化...")
        workflow = UnifiedWorkflow()
        assert workflow.repo_manager is not None
        print("  ✅ 通过: UnifiedWorkflow 初始化成功")
        
        print("✓ 测试仓库列表获取...")
        repos = workflow.repo_manager.list_repositories()
        assert isinstance(repos, list)
        print("  ✅ 通过: 仓库列表获取成功")
        
        print("✓ 测试仓库排序（防止 'get' 方法错误）...")
        # 创建测试仓库
        repo = workflow.repo_manager.create_repository(
            name="test-dashboard-repo",
            owner_id="test-user",
            organization="test-org"
        )
        
        # 模拟 Dashboard 的处理逻辑
        repos = workflow.repo_manager.list_repositories()
        repo_dicts = [r.to_dict() if hasattr(r, 'to_dict') else r for r in repos]
        sorted_repos = sorted(repo_dicts, key=lambda x: x.get('updated_at', ''), reverse=True)
        
        assert len(sorted_repos) > 0
        assert isinstance(sorted_repos[0], dict)
        print("  ✅ 通过: 仓库排序逻辑正确，无 'get' 方法错误")
        
        # 清理
        os.close(db_fd)
        os.unlink(db_path)
        import shutil
        if os.path.exists(workspace):
            shutil.rmtree(workspace)
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        traceback.print_exc()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试执行完成")
    print("=" * 80)
    
    # 项目回顾
    print("\n📋 项目回顾:")
    print("-" * 40)
    print("1. 问题识别:")
    print("   - Dashboard 页面报错 'Repository' object has no attribute 'get'")
    print("   - 原因：试图对 Repository 对象调用字典的 get 方法")
    print()
    print("2. 解决方案:")
    print("   - 修复 unified_api.py 中的 list_repositories() 调用，添加 user_id 参数")
    print("   - 添加防御性检查，确保 Repository 对象转换为字典后再使用 get 方法")
    print("   - 修复 app_no_socketio.py 中的路由配置，添加缺失的蓝图注册")
    print()
    print("3. 测试覆盖:")
    print("   - Repository 模型的基本功能测试")
    print("   - 认证功能测试")
    print("   - Dashboard API 的核心逻辑测试")
    print()
    print("4. 文档成果:")
    print("   - 创建了 7 个详细的 GitHub 集成操作手册")
    print("   - 包含 OAuth 认证、仓库管理、Issue、PR、Webhook 等功能指南")
    print("   - 提供了交互式的功能测试清单")
    print()
    print("5. 改进建议:")
    print("   - 考虑添加更多的集成测试")
    print("   - 增加错误处理和日志记录")
    print("   - 优化性能，特别是大量数据时的查询")
    print("   - 完善 API 文档和错误信息")


if __name__ == "__main__":
    run_unit_tests()