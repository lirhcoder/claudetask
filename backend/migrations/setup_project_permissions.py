"""
迁移脚本：为现有项目设置权限
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.project_permission import ProjectPermissionManager

def main():
    """执行迁移"""
    print("开始迁移项目权限...")
    
    try:
        # 创建权限管理器
        permission_manager = ProjectPermissionManager()
        
        # 执行迁移
        migrated_count = permission_manager.migrate_existing_projects()
        
        print(f"迁移完成！共迁移了 {migrated_count} 个项目的权限记录。")
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())