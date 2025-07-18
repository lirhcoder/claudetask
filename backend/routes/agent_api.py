"""
Agent 员工指数 API
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
import logging

from ..models.agent_metrics import AgentMetricsManager, AgentMetricsDB
from ..models.user import UserManager

agent_bp = Blueprint('agent', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 初始化管理器
metrics_manager = AgentMetricsManager()
metrics_db = AgentMetricsDB()
user_manager = UserManager()

@agent_bp.route('/api/agent/metrics', methods=['GET'])
@login_required
def get_my_metrics():
    """获取当前用户的 Agent 指标"""
    user_id = session.get('user_id')
    
    try:
        # 获取仪表板指标
        dashboard_data = metrics_manager.get_dashboard_metrics(user_id)
        
        # 添加用户信息
        user = user_manager.get_user_by_id(user_id)
        if user:
            dashboard_data['user_info'] = {
                'email': user.email,
                'username': user.username
            }
        
        return jsonify(dashboard_data)
    except Exception as e:
        logging.error(f"Error getting agent metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/api/agent/rankings', methods=['GET'])
@login_required
def get_rankings():
    """获取排行榜"""
    period = request.args.get('period', 'monthly')  # monthly or cumulative
    limit = int(request.args.get('limit', 10))
    
    try:
        if period == 'monthly':
            current_month = datetime.now().strftime('%Y-%m')
            rankings = metrics_db.get_monthly_rankings(current_month)[:limit]
        else:  # cumulative
            rankings = metrics_db.get_all_time_rankings()[:limit]
        
        # 添加用户信息
        for ranking in rankings:
            user = user_manager.get_user_by_id(ranking['user_id'])
            if user:
                ranking['email'] = user.email
                ranking['username'] = user.username
                
                # 计算员工指数
                if period == 'monthly':
                    # 月度指数 = 月度时间 / (30天 * 24小时)
                    monthly_hours = 30 * 24  # 720小时
                    ranking['employee_index'] = round(ranking['total_hours'] / monthly_hours, 4)
                else:
                    # 累计指数需要知道用户注册了多少天
                    days_since_creation = (datetime.now() - user.created_at).days + 1
                    total_hours = days_since_creation * 24
                    ranking['employee_index'] = round(ranking['total_hours'] / total_hours, 4)
        
        return jsonify({
            'period': period,
            'rankings': rankings
        })
    except Exception as e:
        logging.error(f"Error getting rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/api/agent/history/<user_id>', methods=['GET'])
@login_required
def get_user_history(user_id):
    """获取用户历史数据（管理员或用户本人可查看）"""
    current_user_id = session.get('user_id')
    current_user = user_manager.get_user_by_id(current_user_id)
    
    # 权限检查：管理员或用户本人
    if not current_user.is_admin and current_user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    months = int(request.args.get('months', 6))
    
    try:
        history = []
        current_date = datetime.now()
        
        for i in range(months):
            # 计算月份
            year = current_date.year
            month = current_date.month - i
            if month <= 0:
                year -= 1
                month += 12
            
            month_str = f"{year}-{month:02d}"
            
            # 获取该月数据
            metrics = metrics_db.get_user_metrics(user_id, month_str)
            if metrics:
                history.append({
                    'month': month_str,
                    'total_hours': metrics['total_hours'],
                    'total_tasks': metrics['total_tasks'],
                    'agent_load': metrics['agent_load'],
                    'rank': metrics['rank']
                })
            else:
                history.append({
                    'month': month_str,
                    'total_hours': 0,
                    'total_tasks': 0,
                    'agent_load': 0,
                    'rank': 0
                })
        
        return jsonify({
            'user_id': user_id,
            'history': history
        })
    except Exception as e:
        logging.error(f"Error getting user history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/api/agent/company-stats', methods=['GET'])
@login_required
def get_company_stats():
    """获取公司整体统计"""
    current_user = user_manager.get_user_by_id(session.get('user_id'))
    
    # 仅管理员可查看
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_month = datetime.now().strftime('%Y-%m')
        
        # 获取所有用户的月度数据
        monthly_data = metrics_db.get_monthly_rankings(current_month)
        cumulative_data = metrics_db.get_all_time_rankings()
        
        # 计算统计数据
        monthly_stats = {
            'total_users': len(monthly_data),
            'total_hours': sum(d['total_hours'] for d in monthly_data),
            'total_tasks': sum(d['total_tasks'] for d in monthly_data),
            'average_hours': round(sum(d['total_hours'] for d in monthly_data) / len(monthly_data), 2) if monthly_data else 0,
            'average_load': round(sum(d['agent_load'] for d in monthly_data) / len(monthly_data), 2) if monthly_data else 0
        }
        
        cumulative_stats = {
            'total_users': len(cumulative_data),
            'total_hours': sum(d['total_hours'] for d in cumulative_data),
            'total_tasks': sum(d['total_tasks'] for d in cumulative_data),
            'average_hours': round(sum(d['total_hours'] for d in cumulative_data) / len(cumulative_data), 2) if cumulative_data else 0
        }
        
        return jsonify({
            'monthly_stats': monthly_stats,
            'cumulative_stats': cumulative_stats,
            'month': current_month
        })
    except Exception as e:
        logging.error(f"Error getting company stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/api/agent/update-metrics', methods=['POST'])
@login_required
def update_metrics():
    """手动更新指标（仅管理员）"""
    current_user = user_manager.get_user_by_id(session.get('user_id'))
    
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # 触发指标计算
        metrics_manager.calculate_monthly_metrics()
        
        return jsonify({
            'success': True,
            'message': 'Metrics updated successfully'
        })
    except Exception as e:
        logging.error(f"Error updating metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500