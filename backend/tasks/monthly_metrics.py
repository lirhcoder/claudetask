"""
月度Agent指标计算任务
"""
import schedule
import time
from datetime import datetime
from models.agent_metrics import AgentMetricsManager

def calculate_monthly_metrics():
    """计算所有用户的月度Agent指标"""
    print(f"[{datetime.now()}] 开始计算月度Agent指标...")
    
    try:
        metrics_manager = AgentMetricsManager()
        metrics_manager.calculate_monthly_metrics()
        print(f"[{datetime.now()}] 月度Agent指标计算完成")
    except Exception as e:
        print(f"[{datetime.now()}] 月度Agent指标计算失败: {str(e)}")

def run_scheduler():
    """运行定时任务调度器"""
    # 每天凌晨1点运行
    schedule.every().day.at("01:00").do(calculate_monthly_metrics)
    
    # 立即运行一次
    calculate_monthly_metrics()
    
    print("月度指标计算调度器已启动...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    run_scheduler()