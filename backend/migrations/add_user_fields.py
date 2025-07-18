"""
添加用户字段到项目和任务表的迁移脚本
"""
import sqlite3
import os
from pathlib import Path

def migrate():
    """执行迁移"""
    db_path = Path(__file__).parent.parent / "tasks.db"
    
    if not db_path.exists():
        print("数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 添加 user_id 字段到 tasks 表
        print("正在为 tasks 表添加 user_id 字段...")
        cursor.execute('''
            ALTER TABLE tasks ADD COLUMN user_id TEXT
        ''')
        print("✓ tasks.user_id 字段添加成功")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("- tasks.user_id 字段已存在，跳过")
        else:
            raise
    
    try:
        # 创建 projects 表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        print("✓ projects 表已就绪")
    except Exception as e:
        print(f"创建 projects 表时出错: {e}")
    
    # 获取第一个管理员用户的 ID
    cursor.execute('''
        SELECT id FROM users WHERE is_admin = 1 LIMIT 1
    ''')
    admin_user = cursor.fetchone()
    
    if admin_user:
        admin_id = admin_user[0]
        print(f"找到管理员用户: {admin_id}")
        
        # 将所有没有 user_id 的任务分配给管理员
        cursor.execute('''
            UPDATE tasks 
            SET user_id = ? 
            WHERE user_id IS NULL
        ''', (admin_id,))
        updated_tasks = cursor.rowcount
        print(f"✓ 已将 {updated_tasks} 个任务分配给管理员")
        
        # 将所有没有 user_id 的项目分配给管理员
        cursor.execute('''
            UPDATE projects 
            SET user_id = ? 
            WHERE user_id IS NULL
        ''', (admin_id,))
        updated_projects = cursor.rowcount
        print(f"✓ 已将 {updated_projects} 个项目分配给管理员")
    else:
        print("⚠ 未找到管理员用户")
    
    # 创建索引以提高查询性能
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)
        ''')
        print("✓ 索引创建成功")
    except Exception as e:
        print(f"创建索引时出错: {e}")
    
    conn.commit()
    conn.close()
    print("\n迁移完成！")

if __name__ == "__main__":
    migrate()