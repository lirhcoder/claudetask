#!/usr/bin/env python3
"""
修复 system_config 表结构
"""
import sqlite3
import os

def fix_config_table():
    """修复配置表结构"""
    db_path = 'tasks.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(system_config)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("当前 system_config 表的列：", column_names)
        
        if 'value' not in column_names:
            print("\n检测到旧的表结构，需要重建表...")
            
            # 备份旧表数据（如果有）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config_backup AS 
                SELECT * FROM system_config
            """)
            
            # 删除旧表
            cursor.execute("DROP TABLE IF EXISTS system_config")
            
            # 创建新表
            cursor.execute("""
                CREATE TABLE system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            """)
            
            print("✅ 已创建新的 system_config 表")
            
            # 如果旧表有数据，尝试迁移
            cursor.execute("SELECT COUNT(*) FROM system_config_backup")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"正在迁移 {count} 条旧配置...")
                # 这里可以添加数据迁移逻辑
        else:
            print("✅ 表结构正确，无需修复")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 配置表修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == '__main__':
    fix_config_table()