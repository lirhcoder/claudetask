#!/usr/bin/env python3
"""
启动后端服务的简单脚本
"""
import subprocess
import sys
import os

print("Starting ClaudeTask Backend...")

# 检查是否在 Windows 上运行
if os.name == 'nt' or 'microsoft' in os.uname().release.lower():
    print("Detected Windows/WSL environment")
    
    # 尝试使用 Windows 的 Python
    try:
        # 首先尝试运行 pip install
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      capture_output=True, text=True)
    except:
        print("Warning: Could not install dependencies. They may already be installed.")
    
    # 启动 Flask 应用
    print("Starting Flask app...")
    subprocess.run([sys.executable, "app.py"])
else:
    # Linux/Mac
    subprocess.run(["python3", "app.py"])