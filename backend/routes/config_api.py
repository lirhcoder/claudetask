"""
系统配置 API
"""
from flask import Blueprint, request, jsonify, session
from models.config import ConfigManager
from utils.decorators import login_required, admin_required
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__)
config_manager = ConfigManager()

# 初始化默认配置
config_manager.initialize_default_configs()


@config_bp.route('/configs', methods=['GET'])
@login_required
def get_configs():
    """获取所有配置（隐藏敏感信息）"""
    try:
        # 获取分类参数
        category = request.args.get('category')
        
        if category:
            configs = config_manager.get_all_configs(category)
        else:
            configs = config_manager.get_configs_by_category()
        
        # 隐藏敏感配置的值
        sensitive_keys = [
            'github.access_token', 
            'github.webhook_secret',
            'claude.api_key',
            'system.secret_key'
        ]
        
        def mask_sensitive_value(key, config):
            """隐藏敏感值"""
            if key in sensitive_keys and config['value']:
                # 保留前4个字符，其余用星号替换
                value = str(config['value'])
                if len(value) > 4:
                    config['value'] = value[:4] + '*' * (len(value) - 4)
                else:
                    config['value'] = '*' * len(value)
            return config
        
        # 处理返回的配置
        if category:
            # 单一分类的配置
            masked_configs = {}
            for key, config in configs.items():
                masked_configs[key] = mask_sensitive_value(key, config.copy())
            return jsonify(masked_configs), 200
        else:
            # 按分类组织的配置
            masked_configs = {}
            for cat, cat_configs in configs.items():
                masked_configs[cat] = {}
                for key, config in cat_configs.items():
                    masked_configs[cat][key] = mask_sensitive_value(key, config.copy())
            return jsonify(masked_configs), 200
            
    except Exception as e:
        logger.error(f"Error getting configs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs/<key>', methods=['GET'])
@login_required
def get_config(key):
    """获取单个配置"""
    try:
        value = config_manager.get_config(key)
        if value is None:
            return jsonify({'error': 'Config not found'}), 404
        
        # 隐藏敏感信息
        sensitive_keys = ['github.access_token', 'github.webhook_secret', 'claude.api_key']
        if key in sensitive_keys and value:
            value = str(value)[:4] + '*' * (len(str(value)) - 4)
        
        return jsonify({'key': key, 'value': value}), 200
        
    except Exception as e:
        logger.error(f"Error getting config {key}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs', methods=['PUT'])
@login_required
def update_configs():
    """批量更新配置"""
    try:
        data = request.get_json()
        configs = data.get('configs', {})
        user_id = session.get('user_id')
        
        # 记录哪些配置需要重启服务
        restart_required = False
        restart_configs = [
            'system.debug_mode',
            'system.session_timeout',
            'claude.api_key',
            'claude.model'
        ]
        
        results = {}
        for key, value in configs.items():
            # 检查是否需要管理员权限
            if key.startswith('system.') and not session.get('is_admin'):
                results[key] = {'success': False, 'error': 'Admin privileges required'}
                continue
            
            # 更新配置
            success = config_manager.set_config(
                key=key,
                value=value,
                user_id=user_id
            )
            
            results[key] = {'success': success}
            
            if success and key in restart_configs:
                restart_required = True
        
        response = {
            'results': results,
            'restart_required': restart_required
        }
        
        if restart_required:
            response['message'] = '某些配置更改需要重启服务才能生效'
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error updating configs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs/<key>', methods=['PUT'])
@login_required
def update_config(key):
    """更新单个配置"""
    try:
        data = request.get_json()
        value = data.get('value')
        description = data.get('description')
        category = data.get('category', 'general')
        user_id = session.get('user_id')
        
        # 检查是否需要管理员权限
        if key.startswith('system.') and not session.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        success = config_manager.set_config(
            key=key,
            value=value,
            description=description,
            category=category,
            user_id=user_id
        )
        
        if success:
            return jsonify({'message': 'Config updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update config'}), 500
            
    except Exception as e:
        logger.error(f"Error updating config {key}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs/<key>', methods=['DELETE'])
@admin_required
def delete_config(key):
    """删除配置（仅管理员）"""
    try:
        # 防止删除核心配置
        protected_keys = [
            'system.debug_mode',
            'system.session_timeout',
            'ui.language'
        ]
        
        if key in protected_keys:
            return jsonify({'error': 'Cannot delete protected config'}), 403
        
        success = config_manager.delete_config(key)
        
        if success:
            return jsonify({'message': 'Config deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete config'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting config {key}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs/reset', methods=['POST'])
@admin_required
def reset_configs():
    """重置为默认配置（仅管理员）"""
    try:
        # 重新初始化默认配置
        config_manager.initialize_default_configs()
        
        return jsonify({'message': 'Configs reset to defaults'}), 200
        
    except Exception as e:
        logger.error(f"Error resetting configs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/configs/export', methods=['GET'])
@admin_required
def export_configs():
    """导出配置（仅管理员）"""
    try:
        configs = config_manager.get_all_configs()
        
        # 移除敏感信息
        sensitive_keys = ['github.access_token', 'github.webhook_secret', 'claude.api_key']
        for key in sensitive_keys:
            if key in configs:
                configs[key]['value'] = '<REDACTED>'
        
        return jsonify({
            'configs': configs,
            'exported_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error exporting configs: {str(e)}")
        return jsonify({'error': str(e)}), 500