#!/usr/bin/env python3
"""
测试 Flask 应用是否能够正常启动
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing Flask app import...")
    from app import app
    print("✓ Flask app imported successfully")
    
    print("\nChecking routes...")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    
    print("\n✓ All imports successful!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)