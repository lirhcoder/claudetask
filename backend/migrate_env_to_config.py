#!/usr/bin/env python3
"""
将环境变量迁移到配置系统
"""
import os
import sys
from models.config import ConfigManager

def migrate_env_to_config():
    """迁移环境变量到配置管理系统"""
    config_manager = ConfigManager()
    
    print("=== 环境变量迁移工具 ===\n")
    
    # 定义要迁移的环境变量映射
    env_mappings = [
        ('GITHUB_ACCESS_TOKEN', 'github.access_token'),
        ('GITHUB_WEBHOOK_SECRET', 'github.webhook_secret'),
        ('CLAUDE_API_KEY', 'claude.api_key'),
        ('CLAUDE_MODEL', 'claude.model'),
        ('DEBUG', 'system.debug_mode'),
        ('SESSION_TIMEOUT', 'system.session_timeout'),
    ]
    
    migrated_count = 0
    
    for env_var, config_key in env_mappings:
        env_value = os.getenv(env_var)
        
        if env_value:
            # 获取当前配置值
            current_value = config_manager.get_config(config_key)
            
            # 如果配置为空或是默认值，则更新
            if not current_value or current_value == '':
                # 处理布尔值
                if config_key == 'system.debug_mode':
                    env_value = env_value.lower() in ['true', '1', 'yes', 'on']
                elif config_key == 'system.session_timeout':
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        continue
                
                success = config_manager.set_config(
                    key=config_key,
                    value=env_value,
                    user_id='migration'
                )
                
                if success:
                    print(f"✅ 已迁移 {env_var} -> {config_key}")
                    migrated_count += 1
                else:
                    print(f"❌ 迁移失败 {env_var} -> {config_key}")
            else:
                print(f"⏭️  跳过 {config_key}（已有值）")
        else:
            print(f"⚠️  未找到环境变量 {env_var}")
    
    print(f"\n✅ 迁移完成！共迁移 {migrated_count} 个配置项")
    
    # 显示当前配置
    print("\n当前配置值：")
    print("-" * 50)
    
    configs = config_manager.get_configs_by_category()
    for category, category_configs in configs.items():
        print(f"\n[{category}]")
        for key, config in category_configs.items():
            value = config['value']
            # 隐藏敏感信息
            if any(s in key for s in ['token', 'secret', 'key', 'password']):
                if value and len(str(value)) > 4:
                    value = str(value)[:4] + '*' * (len(str(value)) - 4)
            print(f"  {key} = {value}")
    
    print("\n💡 提示：")
    print("  - 配置已保存到数据库")
    print("  - 可以通过设置页面修改配置")
    print("  - 某些配置修改后需要重启服务")

if __name__ == '__main__':
    migrate_env_to_config()