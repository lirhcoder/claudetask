#!/usr/bin/env python3
"""
测试 API 端点的脚本
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_health():
    """测试健康检查端点"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_execute():
    """测试执行端点"""
    # 测试数据
    test_cases = [
        # 缺少数据
        {
            "data": {},
            "expected_error": "No data provided"
        },
        # 缺少 prompt
        {
            "data": {"project_path": "/tmp/test"},
            "expected_error": "Prompt is required"
        },
        # 缺少 project_path
        {
            "data": {"prompt": "test prompt"},
            "expected_error": "Project path is required"
        },
        # 无效的项目路径
        {
            "data": {"prompt": "test prompt", "project_path": "/nonexistent/path"},
            "expected_error": "Project path does not exist"
        },
        # 相对路径
        {
            "data": {"prompt": "test prompt", "project_path": "./relative/path"},
            "expected_error": "Project path must be absolute"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test['data']}")
        try:
            response = requests.post(
                f"{BASE_URL}/execute",
                json=test["data"],
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 400:
                error_msg = response.json().get('error', '')
                if test['expected_error'] in error_msg:
                    print("✓ Expected error received")
                else:
                    print(f"✗ Unexpected error: {error_msg}")
        except Exception as e:
            print(f"Request failed: {e}")

def main():
    print("Testing Claude Code Web API...")
    print("=" * 50)
    
    if not test_health():
        print("\nError: API server is not running!")
        print("Please start the backend server first:")
        print("  cd backend")
        print("  python app_no_socketio.py")
        sys.exit(1)
    
    print("\nTesting /api/execute endpoint...")
    print("-" * 50)
    test_execute()

if __name__ == "__main__":
    main()