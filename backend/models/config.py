"""
系统配置管理
"""
import json
import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化配置表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            ''')
            conn.commit()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value, type FROM system_config WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if not row:
                return default
            
            value, value_type = row
            
            # 根据类型转换值
            try:
                if value_type == 'boolean':
                    return value.lower() == 'true'
                elif value_type == 'integer':
                    return int(value)
                elif value_type == 'float':
                    return float(value)
                elif value_type == 'json':
                    return json.loads(value)
                else:
                    return value
            except Exception as e:
                logger.error(f"Error parsing config value for {key}: {e}")
                return default
    
    def set_config(self, key: str, value: Any, description: str = None, 
                   category: str = 'general', user_id: str = None) -> bool:
        """设置配置值"""
        try:
            # 确定值的类型
            if isinstance(value, bool):
                value_type = 'boolean'
                value_str = 'true' if value else 'false'
            elif isinstance(value, int):
                value_type = 'integer'
                value_str = str(value)
            elif isinstance(value, float):
                value_type = 'float'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                value_type = 'json'
                value_str = json.dumps(value)
            else:
                value_type = 'string'
                value_str = str(value)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO system_config 
                    (key, value, type, description, category, updated_at, updated_by)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
                ''', (key, value_str, value_type, description, category, user_id))
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    def get_all_configs(self, category: str = None) -> Dict[str, Dict[str, Any]]:
        """获取所有配置"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute('''
                    SELECT * FROM system_config 
                    WHERE category = ? 
                    ORDER BY category, key
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT * FROM system_config 
                    ORDER BY category, key
                ''')
            
            configs = {}
            for row in cursor.fetchall():
                key = row['key']
                configs[key] = {
                    'value': self.get_config(key),  # 使用 get_config 进行类型转换
                    'type': row['type'],
                    'description': row['description'],
                    'category': row['category'],
                    'updated_at': row['updated_at'],
                    'updated_by': row['updated_by']
                }
            
            return configs
    
    def get_configs_by_category(self) -> Dict[str, Dict[str, Any]]:
        """按分类获取配置"""
        configs = self.get_all_configs()
        categorized = {}
        
        for key, config in configs.items():
            category = config['category']
            if category not in categorized:
                categorized[category] = {}
            categorized[category][key] = config
        
        return categorized
    
    def delete_config(self, key: str) -> bool:
        """删除配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM system_config WHERE key = ?', (key,))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting config {key}: {e}")
            return False
    
    def initialize_default_configs(self):
        """初始化默认配置"""
        default_configs = [
            # GitHub 集成配置
            ('github.access_token', '', 'string', 'GitHub 个人访问令牌', 'github'),
            ('github.webhook_secret', '', 'string', 'GitHub Webhook 密钥', 'github'),
            ('github.default_branch', 'main', 'string', '默认分支名称', 'github'),
            ('github.auto_sync', False, 'boolean', '自动同步仓库', 'github'),
            ('github.sync_interval', 3600, 'integer', '同步间隔（秒）', 'github'),
            
            # 任务执行配置
            ('task.default_timeout', 600, 'integer', '任务默认超时时间（秒）', 'task'),
            ('task.max_retries', 3, 'integer', '任务最大重试次数', 'task'),
            ('task.auto_save', True, 'boolean', '自动保存任务结果', 'task'),
            ('task.log_level', 'INFO', 'string', '任务日志级别', 'task'),
            
            # UI 配置
            ('ui.auto_refresh', False, 'boolean', '启用自动刷新', 'ui'),
            ('ui.refresh_interval', 5, 'integer', '刷新间隔（秒）', 'ui'),
            ('ui.theme', 'light', 'string', '界面主题', 'ui'),
            ('ui.language', 'zh-CN', 'string', '界面语言', 'ui'),
            
            # 系统配置
            ('system.debug_mode', False, 'boolean', '调试模式', 'system'),
            ('system.max_upload_size', 10485760, 'integer', '最大上传文件大小（字节）', 'system'),
            ('system.session_timeout', 86400, 'integer', '会话超时时间（秒）', 'system'),
            ('system.enable_metrics', True, 'boolean', '启用指标收集', 'system'),
            
            # Claude 配置
            ('claude.api_key', '', 'string', 'Claude API 密钥', 'claude'),
            ('claude.model', 'claude-3-opus-20240229', 'string', 'Claude 模型', 'claude'),
            ('claude.max_tokens', 4096, 'integer', '最大令牌数', 'claude'),
            ('claude.temperature', 0.7, 'float', '温度参数', 'claude'),
        ]
        
        for key, value, value_type, description, category in default_configs:
            # 只有当配置不存在时才设置默认值
            if self.get_config(key) is None:
                self.set_config(key, value, description, category, 'system')
        
        logger.info("Default configurations initialized")