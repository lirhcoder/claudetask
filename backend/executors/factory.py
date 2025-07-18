"""
执行器工厂 - 创建不同类型的任务执行器
"""

class BaseExecutor:
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
    
    def execute(self, prompt: str, files: list = None):
        """执行任务"""
        return {
            'status': 'success',
            'summary': f'Task executed: {prompt}',
            'files_changed': files or []
        }

class ClaudeExecutor(BaseExecutor):
    """Claude AI 执行器"""
    pass

class LocalExecutor(BaseExecutor):
    """本地执行器"""
    pass

class ExecutorFactory:
    """执行器工厂"""
    
    @staticmethod
    def create(executor_type: str, working_dir: str) -> BaseExecutor:
        """创建执行器实例"""
        executors = {
            'claude': ClaudeExecutor,
            'local': LocalExecutor
        }
        
        executor_class = executors.get(executor_type, BaseExecutor)
        return executor_class(working_dir)