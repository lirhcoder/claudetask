#!/usr/bin/env python3
"""
测试 GitHub Webhook 功能
"""
import json
import hmac
import hashlib
import requests
from datetime import datetime

def create_github_signature(payload: str, secret: str) -> str:
    """创建 GitHub webhook 签名"""
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def test_webhook(base_url: str = "http://localhost:5000", secret: str = None):
    """测试 webhook 端点"""
    webhook_url = f"{base_url}/api/webhooks/github"
    
    print("=== GitHub Webhook 测试 ===\n")
    
    # 1. 测试 ping 事件
    print("1. 测试 Ping 事件:")
    print("-" * 50)
    
    ping_payload = {
        "zen": "Design for failure.",
        "hook_id": 12345,
        "hook": {
            "type": "Repository",
            "id": 12345,
            "events": ["push", "pull_request"]
        },
        "repository": {
            "full_name": "test-user/test-repo",
            "html_url": "https://github.com/test-user/test-repo"
        }
    }
    
    headers = {
        "X-GitHub-Event": "ping",
        "Content-Type": "application/json"
    }
    
    if secret:
        payload_str = json.dumps(ping_payload, separators=(',', ':'))
        headers["X-Hub-Signature-256"] = create_github_signature(payload_str, secret)
    
    try:
        response = requests.post(
            f"{webhook_url}/test", 
            json=ping_payload, 
            headers=headers
        )
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    # 2. 测试 push 事件
    print("\n\n2. 测试 Push 事件:")
    print("-" * 50)
    
    push_payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "test-user/test-repo",
            "html_url": "https://github.com/test-user/test-repo"
        },
        "pusher": {
            "name": "test-user",
            "email": "test@example.com"
        },
        "commits": [
            {
                "id": "abc123",
                "message": "Test commit",
                "timestamp": datetime.now().isoformat(),
                "author": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "added": ["new-file.txt"],
                "modified": ["README.md"],
                "removed": []
            }
        ]
    }
    
    headers["X-GitHub-Event"] = "push"
    
    if secret:
        payload_str = json.dumps(push_payload, separators=(',', ':'))
        headers["X-Hub-Signature-256"] = create_github_signature(payload_str, secret)
    
    try:
        response = requests.post(webhook_url, json=push_payload, headers=headers)
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    # 3. 测试 pull_request 事件
    print("\n\n3. 测试 Pull Request 事件:")
    print("-" * 50)
    
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "title": "Add new feature",
            "state": "open",
            "merged": False,
            "user": {
                "login": "test-user"
            },
            "base": {
                "ref": "main"
            },
            "head": {
                "ref": "feature-branch"
            }
        },
        "repository": {
            "full_name": "test-user/test-repo",
            "html_url": "https://github.com/test-user/test-repo"
        }
    }
    
    headers["X-GitHub-Event"] = "pull_request"
    
    if secret:
        payload_str = json.dumps(pr_payload, separators=(',', ':'))
        headers["X-Hub-Signature-256"] = create_github_signature(payload_str, secret)
    
    try:
        response = requests.post(webhook_url, json=pr_payload, headers=headers)
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    # 4. 查看 webhook 事件历史
    print("\n\n4. 查看 Webhook 事件历史:")
    print("-" * 50)
    
    try:
        response = requests.get(f"{webhook_url}/events?limit=5")
        if response.status_code == 200:
            events = response.json().get('events', [])
            print(f"  找到 {len(events)} 个事件")
            for event in events:
                print(f"  - {event['event_type']} at {event['processed_at']}")
        else:
            print(f"  ❌ 无法获取事件历史: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    
    print("\n📝 说明:")
    print("  - 确保后端服务正在运行")
    print("  - 如果设置了 GITHUB_WEBHOOK_SECRET，需要传入相同的密钥")
    print("  - 生产环境中，webhook URL 必须是公网可访问的 HTTPS 地址")

if __name__ == "__main__":
    import sys
    import os
    
    # 从环境变量获取密钥
    secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    
    # 从命令行参数获取 URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    test_webhook(base_url, secret)