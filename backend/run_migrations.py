#!/usr/bin/env python3
"""
运行数据库迁移脚本
"""
import os
import sys
from pathlib import Path

# 添加项目目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

def run_migrations():
    """运行所有迁移脚本"""
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        print("❌ 迁移目录不存在")
        return False
    
    # 获取所有迁移文件
    migration_files = sorted(migrations_dir.glob('*.py'))
    
    if not migration_files:
        print("ℹ️ 没有找到迁移文件")
        return True
    
    print(f"📋 找到 {len(migration_files)} 个迁移文件")
    
    for migration_file in migration_files:
        if migration_file.name.startswith('__'):
            continue
            
        print(f"\n▶️ 运行迁移: {migration_file.name}")
        
        try:
            # 动态导入并执行迁移
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                migration_file.stem, 
                migration_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 执行升级函数
            if hasattr(module, 'upgrade'):
                module.upgrade()
                print(f"✅ 迁移成功: {migration_file.name}")
            else:
                print(f"⚠️ 迁移文件缺少 upgrade() 函数: {migration_file.name}")
                
        except Exception as e:
            print(f"❌ 迁移失败: {migration_file.name}")
            print(f"   错误: {str(e)}")
            return False
    
    print("\n✅ 所有迁移执行完成")
    return True

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)