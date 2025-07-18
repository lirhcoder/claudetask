#!/usr/bin/env python3
"""
应用 GitHub 架构数据库迁移
"""
import sqlite3
import os
import sys

def apply_github_architecture():
    """执行 GitHub 架构迁移"""
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tasks.db')
    
    # 获取迁移文件路径
    migration_dir = os.path.dirname(__file__)
    github_sql = os.path.join(migration_dir, 'github_architecture.sql')
    
    if not os.path.exists(github_sql):
        print(f"Error: Migration file not found: {github_sql}")
        return False
    
    print(f"Applying GitHub architecture migration to {db_path}...")
    
    # 读取 SQL 文件
    with open(github_sql, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # 连接数据库并执行脚本
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_script)
        
        # 添加额外的列
        cursor = conn.cursor()
        
        # 检查并添加 webhook 相关列
        cursor.execute("PRAGMA table_info(repositories)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'webhook_id' not in columns:
            cursor.execute('ALTER TABLE repositories ADD COLUMN webhook_id TEXT')
            print("Added webhook_id column")
            
        if 'webhook_url' not in columns:
            cursor.execute('ALTER TABLE repositories ADD COLUMN webhook_url TEXT')
            print("Added webhook_url column")
            
        if 'webhook_active' not in columns:
            cursor.execute('ALTER TABLE repositories ADD COLUMN webhook_active BOOLEAN DEFAULT 0')
            print("Added webhook_active column")
        
        # 修复 commits 表
        cursor.execute("PRAGMA table_info(commits)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'repository_id' not in columns:
            cursor.execute('ALTER TABLE commits ADD COLUMN repository_id TEXT')
            print("Added repository_id column to commits")
            
        if 'branch_name' not in columns:
            cursor.execute('ALTER TABLE commits ADD COLUMN branch_name TEXT')
            print("Added branch_name column to commits")
            
        if 'sha' not in columns:
            cursor.execute('ALTER TABLE commits ADD COLUMN sha TEXT')
            print("Added sha column to commits")
        
        conn.commit()
        print("GitHub architecture migration completed successfully!")
        
        # 验证表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print("\nDatabase tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"Error applying migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = apply_github_architecture()
    sys.exit(0 if success else 1)