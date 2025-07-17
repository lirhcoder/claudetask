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
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tasks'
        """)
        if not cursor.fetchone():
            print("⚠️ tasks 表不存在，跳过迁移")
            print("   请先运行应用程序以创建基础表结构")
            return
            
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加新字段到 tasks 表
        if 'parent_task_id' not in columns:
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN parent_task_id TEXT
            """)
            print("✅ 添加字段: parent_task_id")
        
        if 'context' not in columns:
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN context TEXT
            """)
            print("✅ 添加字段: context")
        
        if 'sequence_order' not in columns:
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN sequence_order INTEGER DEFAULT 0
            """)
            print("✅ 添加字段: sequence_order")
        
        if 'task_type' not in columns:
            cursor.execute("""
                ALTER TABLE tasks ADD COLUMN task_type TEXT DEFAULT 'single'
            """)
            print("✅ 添加字段: task_type")
        
        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_parent_task_id ON tasks(parent_task_id)
        """)
        
        conn.commit()
        print("✅ 数据库升级成功：添加了父子任务支持")
        
    except sqlite3.OperationalError as e:
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