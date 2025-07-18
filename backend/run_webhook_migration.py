#!/usr/bin/env python3
"""
运行 webhook 迁移脚本
"""
import sqlite3
import os

def run_migration():
    """执行数据库迁移"""
    db_path = 'tasks.db'
    migration_file = 'migrations/add_webhook_events.sql'
    
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
        
        # 分割 SQL 语句并执行
        statements = migration_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ 执行成功: {statement[:50]}...")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"⚠️  列已存在，跳过: {statement[:50]}...")
                    else:
                        print(f"❌ 执行失败: {statement[:50]}...")
                        print(f"   错误: {e}")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("\n✅ Webhook 迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

if __name__ == '__main__':
    run_migration()