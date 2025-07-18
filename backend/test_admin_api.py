"""
测试管理员API端点
"""
import requests
import json

base_url = "http://localhost:5000"

# 测试健康检查
print("1. 测试健康检查...")
try:
    response = requests.get(f"{base_url}/api/health")
    print(f"   状态: {response.status_code}")
    print(f"   响应: {response.json()}")
except Exception as e:
    print(f"   错误: {e}")

# 登录管理员账号
print("\n2. 登录管理员账号...")
login_data = {
    "email": "admin@claudetask.local",
    "password": "admin123"
}
try:
    session = requests.Session()
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"   状态: {response.status_code}")
    if response.status_code == 200:
        print(f"   用户: {response.json()['user']['email']}")
        print(f"   是否管理员: {response.json()['user']['is_admin']}")
    else:
        print(f"   错误: {response.text}")
except Exception as e:
    print(f"   错误: {e}")

# 测试管理员任务列表
print("\n3. 获取所有用户的任务...")
try:
    response = session.get(f"{base_url}/api/admin/tasks")
    print(f"   状态: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()['tasks']
        print(f"   任务数量: {len(tasks)}")
        if tasks:
            print("   示例任务:")
            for task in tasks[:3]:
                print(f"     - ID: {task['id'][:8]}")
                print(f"       用户: {task.get('user_email', 'N/A')}")
                print(f"       提示词: {task['prompt'][:50]}...")
    else:
        print(f"   错误: {response.text}")
except Exception as e:
    print(f"   错误: {e}")

# 测试管理员项目列表
print("\n4. 获取所有用户的项目...")
try:
    response = session.get(f"{base_url}/api/admin/projects")
    print(f"   状态: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()['projects']
        print(f"   项目数量: {len(projects)}")
        if projects:
            print("   项目列表:")
            for project in projects:
                print(f"     - 名称: {project['name']}")
                print(f"       用户: {project.get('user_email', 'N/A')}")
                print(f"       路径: {project['path']}")
    else:
        print(f"   错误: {response.text}")
except Exception as e:
    print(f"   错误: {e}")

print("\n测试完成！")