#!/usr/bin/env python3
"""
运行配置表迁移
"""
import sqlite3
import os

def run_migration():
    """执行数据库迁移"""
    db_path = 'tasks.db'
    migration_file = 'migrations/add_config_table.sql'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return False
    
    if not os.path.exists(migration_file):
        print(f"迁移文件 {migration_file} 不存在")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取迁移脚本
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # 执行迁移
        cursor.executescript(migration_sql)
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("✅ 配置表迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

if __name__ == '__main__':
    run_migration()