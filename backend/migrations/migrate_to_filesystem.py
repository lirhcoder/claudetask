"""
将现有任务迁移到文件系统结构的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from pathlib import Path
from models.task_filesystem import TaskFileSystem
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_existing_tasks():
    """迁移现有任务到文件系统结构"""
    db_path = Path(__file__).parent.parent / "tasks.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    task_fs = TaskFileSystem(str(db_path))
    
    try:
        # 1. 首先执行数据库结构更新（跳过，因为已经手动执行过）
        logger.info("跳过数据库结构更新（已完成）...")
        
        # 2. 获取所有现有项目
        logger.info("获取现有项目...")
        cursor.execute("""
            SELECT DISTINCT project_path 
            FROM tasks 
            WHERE project_path IS NOT NULL
        """)
        
        projects = {}
        for row in cursor.fetchall():
            project_path = row['project_path']
            # 提取项目名称
            project_name = project_path.rstrip('/').split('/')[-1]
            if project_name and project_name not in projects:
                projects[project_name] = project_path
        
        logger.info(f"找到 {len(projects)} 个项目")
        
        # 3. 为每个项目创建根文件夹
        for project_name, original_path in projects.items():
            logger.info(f"处理项目: {project_name}")
            
            # 创建项目根文件夹
            project_task = task_fs.create_task_folder(
                parent_path="/",
                name=project_name,
                description=f"项目: {project_name}\n原始路径: {original_path}"
            )
            
            # 获取该项目的所有任务
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE project_path = ?
                ORDER BY created_at
            """, (original_path,))
            
            tasks = cursor.fetchall()
            logger.info(f"  找到 {len(tasks)} 个任务")
            
            # 处理任务层级关系
            task_mapping = {}  # old_id -> new_task_path
            
            for task in tasks:
                task_id = task['id']
                parent_task_id = task['parent_task_id']
                prompt = task['prompt']
                
                # 生成任务名称（从prompt提取前30个字符）
                task_name = prompt[:30].replace('/', '-').replace('\\', '-').strip()
                if not task_name:
                    task_name = f"task_{task_id[:8]}"
                
                # 确定父路径
                if parent_task_id and parent_task_id in task_mapping:
                    parent_path = task_mapping[parent_task_id]
                else:
                    parent_path = f"/{project_name}"
                
                # 创建任务文件夹
                new_task = task_fs.create_task_folder(
                    parent_path=parent_path,
                    name=task_name,
                    prompt=prompt,
                    description=""
                )
                
                # 更新任务属性
                cursor.execute("""
                    UPDATE tasks 
                    SET task_path = ?, 
                        task_name = ?,
                        depth = ?,
                        is_folder = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    new_task.path,
                    new_task.name,
                    new_task.depth,
                    1 if task['task_type'] == 'parent' else 0,
                    datetime.now().isoformat(),
                    task_id
                ))
                
                task_mapping[task_id] = new_task.path
                logger.info(f"    迁移任务: {task_name} -> {new_task.path}")
        
        # 4. 提交更改
        conn.commit()
        logger.info("迁移完成！")
        
        # 5. 显示迁移统计
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_path IS NOT NULL")
        migrated_count = cursor.fetchone()[0]
        logger.info(f"\n迁移统计:")
        logger.info(f"  - 已迁移任务数: {migrated_count}")
        logger.info(f"  - 项目数: {len(projects)}")
        
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_migration():
    """验证迁移结果"""
    db_path = Path(__file__).parent.parent / "tasks.db"
    task_fs = TaskFileSystem(str(db_path))
    
    logger.info("\n验证迁移结果...")
    
    # 获取任务树
    tree = task_fs.get_task_tree("/", max_depth=3)
    
    def print_tree(node, indent=0):
        """打印任务树"""
        prefix = "  " * indent
        if indent == 0:
            print(f"{prefix}{node['name']}")
        else:
            print(f"{prefix}├── {node['name']}")
        
        if 'children' in node:
            for child in node['children']:
                print_tree(child, indent + 1)
    
    print("\n任务树结构:")
    print_tree(tree)

if __name__ == '__main__':
    try:
        migrate_existing_tasks()
        verify_migration()
    except Exception as e:
        logger.error(f"迁移过程出错: {str(e)}")
        exit(1)