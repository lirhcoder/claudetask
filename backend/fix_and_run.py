#!/usr/bin/env python3
"""
修复并运行 Flask 应用（无需虚拟环境）
"""
import subprocess
import sys
import os

print("=== ClaudeTask 快速启动 ===\n")

# 必需的包
required_packages = [
    'flask',
    'flask-cors',
    'flask-socketio',
    'python-socketio',
    'python-dotenv',
    'bcrypt',
    'requests'
]

print("检查并安装必需的包...")

# 尝试导入，如果失败则安装
for package in required_packages:
    try:
        if package == 'flask-cors':
            __import__('flask_cors')
        elif package == 'flask-socketio':
            __import__('flask_socketio')
        elif package == 'python-socketio':
            __import__('socketio')
        elif package == 'python-dotenv':
            __import__('dotenv')
        else:
            __import__(package)
        print(f"✅ {package} 已安装")
    except ImportError:
        print(f"❌ {package} 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 安装失败")
            print("\n请手动安装:")
            print(f"  {sys.executable} -m pip install {package}")

# 检查数据库
if not os.path.exists('tasks.db'):
    print("\n创建管理员账号...")
    subprocess.run([sys.executable, 'create_admin.py'])

print("\n=== 启动 Flask 应用 ===")
print("默认登录账号:")
print("  邮箱: admin@claudetask.local")
print("  密码: admin123")
print("\n访问地址: http://localhost:5000")
print("按 Ctrl+C 停止服务\n")

# 启动应用
try:
    subprocess.run([sys.executable, 'run.py'])
except KeyboardInterrupt:
    print("\n服务已停止")