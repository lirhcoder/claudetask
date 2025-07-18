"""
Agent负荷指标模型 - 管理员工生产力指标
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from contextlib import contextmanager
import json

class AgentMetrics:
    """Agent负荷指标模型"""
    def __init__(self, user_id: str, month: str, 
                 total_hours: float = 0.0, 
                 total_tasks: int = 0,
                 cumulative_hours: float = 0.0,
                 rank: int = 0):
        self.user_id = user_id
        self.month = month  # 格式: YYYY-MM
        self.total_hours = total_hours
        self.total_tasks = total_tasks
        self.cumulative_hours = cumulative_hours  # 累积总时长
        self.agent_load = 0.0  # Agent负荷百分比
        self.rank = rank  # 公司内排名
        
    def calculate_agent_load(self):
        """计算Agent负荷（百分比）
        一个满负荷Agent = 7x24x30 = 5040小时/月
        """
        FULL_AGENT_HOURS = 7 * 24 * 30  # 5040小时
        self.agent_load = (self.total_hours / FULL_AGENT_HOURS) * 100
        return self.agent_load
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'month': self.month,
            'total_hours': round(self.total_hours, 2),
            'total_tasks': self.total_tasks,
            'cumulative_hours': round(self.cumulative_hours, 2),
            'agent_load': round(self.calculate_agent_load(), 2),
            'rank': self.rank
        }


class AgentMetricsDB:
    """Agent指标数据库管理器"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建月度指标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    user_id TEXT NOT NULL,
                    month TEXT NOT NULL,
                    total_hours REAL DEFAULT 0,
                    total_tasks INTEGER DEFAULT 0,
                    cumulative_hours REAL DEFAULT 0,
                    agent_load REAL DEFAULT 0,
                    rank INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, month)
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_month 
                ON agent_metrics(month)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_rank 
                ON agent_metrics(month, rank)
            ''')
            
            conn.commit()
    
    def update_user_metrics(self, user_id: str, month: str, hours: float, tasks: int):
        """更新用户的月度指标"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取当前数据
            cursor.execute('''
                SELECT total_hours, total_tasks, cumulative_hours 
                FROM agent_metrics 
                WHERE user_id = ? AND month = ?
            ''', (user_id, month))
            
            row = cursor.fetchone()
            if row:
                # 更新现有记录
                new_hours = row['total_hours'] + hours
                new_tasks = row['total_tasks'] + tasks
                
                cursor.execute('''
                    UPDATE agent_metrics 
                    SET total_hours = ?, total_tasks = ?, updated_at = ?
                    WHERE user_id = ? AND month = ?
                ''', (new_hours, new_tasks, datetime.now().isoformat(), user_id, month))
            else:
                # 获取累积时长
                cursor.execute('''
                    SELECT SUM(total_hours) as cumulative 
                    FROM agent_metrics 
                    WHERE user_id = ?
                ''', (user_id,))
                
                cumulative_row = cursor.fetchone()
                cumulative_hours = (cumulative_row['cumulative'] or 0) + hours
                
                # 创建新记录
                cursor.execute('''
                    INSERT INTO agent_metrics 
                    (user_id, month, total_hours, total_tasks, cumulative_hours, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, month, hours, tasks, cumulative_hours, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_monthly_rankings(self, month: str) -> List[Dict]:
        """获取月度排名"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取所有用户的月度数据并计算排名
            cursor.execute('''
                SELECT user_id, total_hours, total_tasks, cumulative_hours,
                       RANK() OVER (ORDER BY total_hours DESC) as rank
                FROM agent_metrics
                WHERE month = ?
                ORDER BY total_hours DESC
            ''', (month,))
            
            rankings = []
            for row in cursor.fetchall():
                metrics = AgentMetrics(
                    user_id=row['user_id'],
                    month=month,
                    total_hours=row['total_hours'],
                    total_tasks=row['total_tasks'],
                    cumulative_hours=row['cumulative_hours'],
                    rank=row['rank']
                )
                rankings.append(metrics.to_dict())
            
            return rankings
    
    def get_user_metrics(self, user_id: str, month: str) -> Optional[Dict]:
        """获取用户的月度指标"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM agent_metrics
                WHERE user_id = ? AND month = ?
            ''', (user_id, month))
            
            row = cursor.fetchone()
            if row:
                metrics = AgentMetrics(
                    user_id=row['user_id'],
                    month=row['month'],
                    total_hours=row['total_hours'],
                    total_tasks=row['total_tasks'],
                    cumulative_hours=row['cumulative_hours'],
                    rank=0  # 需要单独计算
                )
                
                # 计算排名
                cursor.execute('''
                    SELECT COUNT(*) + 1 as rank
                    FROM agent_metrics
                    WHERE month = ? AND total_hours > ?
                ''', (month, row['total_hours']))
                
                rank_row = cursor.fetchone()
                metrics.rank = rank_row['rank']
                
                return metrics.to_dict()
            
            return None
    
    def get_all_time_rankings(self) -> List[Dict]:
        """获取累积总排名"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, 
                       SUM(total_hours) as total_hours,
                       SUM(total_tasks) as total_tasks,
                       MAX(cumulative_hours) as cumulative_hours
                FROM agent_metrics
                GROUP BY user_id
                ORDER BY total_hours DESC
            ''')
            
            rankings = []
            rank = 1
            for row in cursor.fetchall():
                rankings.append({
                    'user_id': row['user_id'],
                    'total_hours': round(row['total_hours'], 2),
                    'total_tasks': row['total_tasks'],
                    'cumulative_hours': round(row['cumulative_hours'], 2),
                    'rank': rank
                })
                rank += 1
            
            return rankings


class AgentMetricsManager:
    """Agent指标管理器"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db = AgentMetricsDB(db_path)
    
    def update_task_metrics(self, user_id: str, execution_time: float):
        """当任务完成时更新指标"""
        if not user_id or not execution_time:
            return
        
        # 获取当前月份
        current_month = datetime.now().strftime('%Y-%m')
        
        # 将秒转换为小时
        hours = execution_time / 3600
        
        # 更新数据库
        self.db.update_user_metrics(user_id, current_month, hours, 1)
    
    def get_dashboard_metrics(self, user_id: str) -> Dict:
        """获取仪表板显示的指标"""
        current_month = datetime.now().strftime('%Y-%m')
        
        # 获取用户当月指标
        user_metrics = self.db.get_user_metrics(user_id, current_month)
        
        if not user_metrics:
            # 如果没有数据，返回默认值
            user_metrics = {
                'user_id': user_id,
                'month': current_month,
                'total_hours': 0.0,
                'total_tasks': 0,
                'cumulative_hours': 0.0,
                'agent_load': 0.0,
                'rank': 0
            }
        
        # 获取公司排名（前10）
        monthly_rankings = self.db.get_monthly_rankings(current_month)[:10]
        
        return {
            'user_metrics': user_metrics,
            'monthly_rankings': monthly_rankings,
            'full_agent_hours': 7 * 24 * 30  # 5040小时
        }
    
    def calculate_monthly_metrics(self):
        """计算所有用户的月度指标（定时任务调用）"""
        from models.task import TaskManager
        from models.user import UserManager
        
        task_manager = TaskManager()
        user_manager = UserManager()
        
        current_month = datetime.now().strftime('%Y-%m')
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        # 获取所有用户
        users = user_manager.list_users()
        
        for user in users:
            # 获取用户本月完成的任务
            tasks = task_manager.get_all_tasks()
            
            total_hours = 0.0
            total_tasks = 0
            
            for task in tasks:
                # 检查任务是否属于该用户且在本月完成
                if (hasattr(task, 'user_id') and task.user_id == user.id and 
                    task.status == 'completed' and task.completed_at):
                    
                    # 检查完成时间是否在本月
                    if isinstance(task.completed_at, str):
                        completed_time = datetime.fromisoformat(task.completed_at)
                    else:
                        completed_time = task.completed_at
                    
                    if completed_time >= month_start:
                        # 累加执行时间
                        if task.execution_time:
                            total_hours += task.execution_time / 3600
                            total_tasks += 1
            
            # 更新数据库
            if total_tasks > 0:
                self.db.update_user_metrics(user.id, current_month, total_hours, total_tasks)