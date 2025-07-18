#!/usr/bin/env python3
"""
执行 GitHub 架构迁移脚本
"""
import sqlite3
import sys
import os
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """执行迁移"""
    db_path = Path(__file__).parent.parent / "tasks.db"
    migration_sql = Path(__file__).parent / "github_architecture.sql"
    
    print(f"Migrating database: {db_path}")
    print(f"Using migration script: {migration_sql}")
    
    # 读取迁移脚本
    with open(migration_sql, 'r', encoding='utf-8') as f:
        migration_script = f.read()
    
    # 执行迁移
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 执行整个脚本
        cursor.executescript(migration_script)
        conn.commit()
        print("Migration completed successfully!")
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\nCreated tables:")
        for table in ['repositories', 'branches', 'issues', 'commits', 'pull_requests']:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (missing)")
                
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
        
    return True

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)