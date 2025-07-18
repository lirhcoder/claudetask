#!/usr/bin/env python3
"""
诊断 Flask 应用问题
"""
import os
import sys
import subprocess

print("=== ClaudeTask 后端诊断 ===\n")

# 1. 检查 Python 版本
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}\n")

# 2. 检查当前目录
print(f"当前目录: {os.getcwd()}")
print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}\n")

# 3. 检查虚拟环境
venv_paths = ['venv', '../venv', 'env', '.venv']
venv_found = False

print("检查虚拟环境:")
for venv_path in venv_paths:
    if os.path.exists(venv_path):
        print(f"  ✅ 找到: {os.path.abspath(venv_path)}")
        venv_found = True
        
        # 检查激活脚本
        if os.name == 'nt':  # Windows
            activate = os.path.join(venv_path, 'Scripts', 'activate.bat')
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Linux/Mac
            activate = os.path.join(venv_path, 'bin', 'activate')
            python_exe = os.path.join(venv_path, 'bin', 'python')
        
        if os.path.exists(python_exe):
            print(f"  ✅ Python 可执行文件: {python_exe}")
            
            # 检查虚拟环境中的 Flask
            try:
                result = subprocess.run([python_exe, '-c', 'import flask; print(flask.__version__)'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ Flask 版本 (在虚拟环境中): {result.stdout.strip()}")
                else:
                    print(f"  ❌ Flask 未在虚拟环境中安装")
            except Exception as e:
                print(f"  ❌ 无法检查 Flask: {e}")
        break

if not venv_found:
    print("  ❌ 未找到虚拟环境")

# 4. 检查依赖
print("\n检查依赖:")
try:
    import flask
    print(f"  ✅ Flask {flask.__version__} (全局)")
except ImportError:
    print("  ❌ Flask 未安装 (全局)")

try:
    import flask_cors
    print("  ✅ Flask-CORS (全局)")
except ImportError:
    print("  ❌ Flask-CORS 未安装 (全局)")

try:
    import bcrypt
    print("  ✅ bcrypt (全局)")
except ImportError:
    print("  ❌ bcrypt 未安装 (全局)")

# 5. 检查数据库
print("\n检查数据库:")
if os.path.exists('tasks.db'):
    print(f"  ✅ tasks.db 存在 (大小: {os.path.getsize('tasks.db')} 字节)")
else:
    print("  ❌ tasks.db 不存在")

# 6. 提供解决方案
print("\n=== 解决方案 ===")

if venv_found:
    print("\n在 Windows 上:")
    print("  1. 激活虚拟环境: venv\\Scripts\\activate")
    print("  2. 安装依赖: pip install -r requirements.txt")
    print("  3. 运行应用: python run.py")
    print("\n在 Linux/Mac 上:")
    print("  1. 激活虚拟环境: source venv/bin/activate")
    print("  2. 安装依赖: pip install -r requirements.txt")
    print("  3. 运行应用: python run.py")
else:
    print("\n创建虚拟环境:")
    print("  1. python -m venv venv")
    print("  2. 激活虚拟环境 (见上方)")
    print("  3. pip install -r requirements.txt")
    print("  4. python run.py")

print("\n或者直接运行启动脚本:")
print("  Windows: start_backend.bat")
print("  Linux/Mac: bash start_backend.sh")