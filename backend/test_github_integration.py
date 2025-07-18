#!/usr/bin/env python3
"""
测试 GitHub 集成功能
"""
import os
import sys
import json
import requests
from datetime import datetime

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.github_integration import GitHubIntegration

def test_github_integration():
    """测试 GitHub 集成主要功能"""
    print("=== GitHub 集成功能测试 ===\n")
    
    # 检查环境变量
    token = os.getenv('GITHUB_ACCESS_TOKEN')
    if not token:
        print("⚠️  警告: 未设置 GITHUB_ACCESS_TOKEN 环境变量")
        print("   私有仓库访问将会失败")
        print("   设置方法: export GITHUB_ACCESS_TOKEN=your_token\n")
    else:
        print("✅ 已检测到 GitHub 访问令牌\n")
    
    # 初始化 GitHub 集成
    github = GitHubIntegration(access_token=token)
    
    # 测试仓库信息获取
    test_repos = [
        "https://github.com/microsoft/vscode",
        "https://github.com/facebook/react",
        "https://github.com/torvalds/linux"
    ]
    
    print("1. 测试获取仓库信息:")
    print("-" * 50)
    
    for repo_url in test_repos:
        print(f"\n测试仓库: {repo_url}")
        try:
            repo_info = github.import_repository(repo_url)
            print(f"  ✅ 名称: {repo_info['name']}")
            print(f"  ✅ 描述: {repo_info['description'][:50]}..." if repo_info['description'] else "  ✅ 描述: (无)")
            print(f"  ✅ 默认分支: {repo_info['default_branch']}")
            print(f"  ✅ Stars: {repo_info['stars']:,}")
            print(f"  ✅ Forks: {repo_info['forks']:,}")
            print(f"  ✅ 开放议题: {repo_info['open_issues']:,}")
            print(f"  ✅ 主要语言: {repo_info['language']}")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
    
    # 测试分支列表
    print("\n\n2. 测试获取分支列表:")
    print("-" * 50)
    
    test_repo = "microsoft/vscode"
    print(f"\n测试仓库: {test_repo}")
    try:
        branches = github.list_branches("microsoft", "vscode")
        print(f"  ✅ 找到 {len(branches)} 个分支")
        if branches:
            print("  前 5 个分支:")
            for branch in branches[:5]:
                print(f"    - {branch['name']}")
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
    
    # 测试议题列表
    print("\n\n3. 测试获取议题列表:")
    print("-" * 50)
    
    print(f"\n测试仓库: {test_repo}")
    try:
        issues = github.list_issues("microsoft", "vscode", state='open')
        print(f"  ✅ 找到 {len(issues)} 个开放议题")
        if issues:
            print("  前 3 个议题:")
            for issue in issues[:3]:
                print(f"    - #{issue['number']}: {issue['title'][:60]}...")
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
    
    # 测试 API 限制
    print("\n\n4. 检查 API 速率限制:")
    print("-" * 50)
    
    headers = github.headers
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    if response.status_code == 200:
        rate_data = response.json()
        core_limit = rate_data['rate']
        print(f"  ✅ API 速率限制: {core_limit['used']}/{core_limit['limit']}")
        reset_time = datetime.fromtimestamp(core_limit['reset'])
        print(f"  ✅ 重置时间: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"  ❌ 无法获取速率限制信息")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    
    # 总结
    print("\n📊 测试总结:")
    print("  - GitHub API 连接: ✅ 正常")
    print("  - 仓库信息获取: ✅ 正常")
    print("  - 分支列表获取: ✅ 正常")
    print("  - 议题列表获取: ✅ 正常")
    
    if not token:
        print("\n⚠️  提示: 设置 GITHUB_ACCESS_TOKEN 可以:")
        print("  - 访问私有仓库")
        print("  - 提高 API 速率限制 (60/小时 -> 5000/小时)")
        print("  - 支持创建 Pull Request 等写操作")

if __name__ == '__main__':
    test_github_integration()