"""
同步文件系统中的项目到数据库
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.project import ProjectManager
from models.user import UserManager
from config import Config

def sync_projects():
    """同步所有项目到数据库"""
    project_manager = ProjectManager()
    user_manager = UserManager()
    
    # 获取管理员用户
    admin_user = None
    for user in user_manager.list_users():
        if user.is_admin:
            admin_user = user
            break
    
    if not admin_user:
        print("未找到管理员用户")
        return
    
    print(f"找到管理员用户: {admin_user.email}")
    
    # 同步项目
    projects_dir = Config.PROJECTS_DIR
    if projects_dir.exists():
        count = 0
        for item in projects_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 检查项目是否已存在
                existing = project_manager.get_project_by_name(item.name)
                if not existing:
                    # 创建项目记录
                    project = project_manager.create_project(
                        name=item.name,
                        path=str(item),
                        user_id=admin_user.id
                    )
                    print(f"✓ 创建项目: {item.name}")
                    count += 1
                else:
                    print(f"- 项目已存在: {item.name}")
        
        print(f"\n同步完成！共创建 {count} 个项目记录")
    else:
        print("项目目录不存在")

if __name__ == "__main__":
    sync_projects()