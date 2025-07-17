"""
添加父子任务支持的数据库迁移脚本
"""
import sqlite3
from datetime import datetime

def upgrade(db_path='tasks.db'):
    """升级数据库以支持父子任务"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 添加新字段到 tasks 表
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN parent_task_id TEXT
        """)
        
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN context TEXT
        """)
        
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN sequence_order INTEGER DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'single'
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX idx_parent_task_id ON tasks(parent_task_id)
        """)
        
        conn.commit()
        print("✅ 数据库升级成功：添加了父子任务支持")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ 字段已存在，跳过迁移")
        else:
            print(f"❌ 迁移失败：{e}")
            raise
    finally:
        conn.close()

def downgrade(db_path='tasks.db'):
    """回滚迁移"""
    # 注意：SQLite 不支持 DROP COLUMN，需要重建表
    print("⚠️ SQLite 不支持直接删除列，需要手动处理")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()