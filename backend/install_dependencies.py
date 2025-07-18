#!/usr/bin/env python3
"""
安装必要的 Python 依赖
"""
import subprocess
import sys

def install_dependencies():
    """安装依赖包"""
    print("=== 安装 Python 依赖 ===\n")
    
    # 必须的包列表
    packages = [
        'Flask==3.0.0',
        'Flask-CORS==4.0.0',
        'Flask-SocketIO==5.3.5',
        'python-socketio==5.10.0',
        'python-dotenv==1.0.0',
        'bcrypt==4.0.1',
        'requests',  # 用于 GitHub 集成
    ]
    
    print("正在安装以下包：")
    for pkg in packages:
        print(f"  - {pkg}")
    print()
    
    # 尝试不同的安装方法
    install_methods = [
        [sys.executable, '-m', 'pip', 'install'],
        ['pip3', 'install'],
        ['pip', 'install'],
    ]
    
    installed = False
    for method in install_methods:
        try:
            print(f"尝试使用: {' '.join(method)}")
            for package in packages:
                cmd = method + [package]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ 成功安装 {package}")
                else:
                    print(f"❌ 安装失败 {package}: {result.stderr}")
            installed = True
            break
        except Exception as e:
            print(f"❌ 方法失败: {e}")
            continue
    
    if not installed:
        print("\n❌ 无法自动安装依赖包")
        print("\n请手动运行以下命令之一：")
        print("  python3 -m pip install -r requirements.txt")
        print("  pip3 install -r requirements.txt")
        print("  pip install -r requirements.txt")
        print("\n或者在 Windows 上使用：")
        print("  py -m pip install -r requirements.txt")
        return False
    
    print("\n✅ 依赖安装完成！")
    return True

def test_imports():
    """测试导入"""
    print("\n=== 测试导入 ===")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask 导入失败")
        return False
    
    try:
        import flask_cors
        print("✅ Flask-CORS")
    except ImportError:
        print("❌ Flask-CORS 导入失败")
        return False
    
    try:
        import flask_socketio
        print("✅ Flask-SocketIO")
    except ImportError:
        print("❌ Flask-SocketIO 导入失败")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt")
    except ImportError:
        print("❌ bcrypt 导入失败")
        return False
    
    return True

if __name__ == '__main__':
    # 安装依赖
    success = install_dependencies()
    
    if success:
        # 测试导入
        if test_imports():
            print("\n✅ 所有依赖已就绪！")
            print("\n现在可以运行：")
            print("  python3 app.py")
        else:
            print("\n⚠️  部分模块导入失败，请检查安装")
    else:
        print("\n⚠️  请按照上述说明手动安装依赖")