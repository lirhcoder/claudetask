import os
import subprocess
import threading
import queue
import json
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable
from pathlib import Path
from models.task import Task, TaskManager

class ClaudeExecutor:
    """Service for executing Claude Code commands and managing tasks."""
    
    def __init__(self, claude_path: str = None, max_concurrent: int = 5, db_path: str = "tasks.db"):
        self.claude_path = claude_path or os.environ.get('CLAUDE_CODE_PATH', 'claude')
        self.max_concurrent = max_concurrent
        self.task_manager = TaskManager(db_path=db_path)
        self.active_tasks: Dict[str, 'Task'] = {}
        self.task_queue = queue.Queue()
        self.output_callbacks: Dict[str, Callable] = {}
        
        # Start worker threads
        self.workers = []
        for _ in range(max_concurrent):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def execute(self, prompt: str, project_path: str, 
                output_callback: Optional[Callable] = None,
                completion_callback: Optional[Callable] = None) -> str:
        """Execute Claude Code with given prompt and project path."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            prompt=prompt,
            project_path=project_path
        )
        
        self.active_tasks[task_id] = task
        self.task_manager.add_task(task)
        
        if output_callback:
            self.output_callbacks[task_id] = output_callback
        
        if completion_callback:
            task.completion_callback = completion_callback
            
        self.task_queue.put(task)
        return task_id
    
    def _worker(self):
        """Worker thread for processing tasks."""
        while True:
            task = self.task_queue.get()
            if task is None:
                break
                
            self._run_task(task)
            self.task_queue.task_done()
    
    def _run_task(self, task: 'Task'):
        """Run a single task."""
        task.status = 'running'
        task.started_at = datetime.utcnow()
        self.task_manager.update_task(task)
        
        try:
            # Build command
            cmd = [self.claude_path, '--project-dir', task.project_path]
            
            # Create process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=task.project_path
            )
            
            task.process = process
            
            # Send prompt to stdin
            process.stdin.write(task.prompt + '\n')
            process.stdin.flush()
            process.stdin.close()
            
            # Read output line by line
            output_lines = []
            output_callback = self.output_callbacks.get(task.id)
            
            for line in process.stdout:
                output_lines.append(line)
                if output_callback:
                    output_callback(task.id, line.rstrip('\n'))
            
            # Wait for process to complete
            process.wait()
            
            task.output = ''.join(output_lines)
            task.exit_code = process.returncode
            task.status = 'completed' if process.returncode == 0 else 'failed'
            
            # 计算执行时间
            if task.started_at:
                task.execution_time = (datetime.utcnow() - task.started_at).total_seconds()
            
            # 保存最终状态
            self.task_manager.update_task(task)
            
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.error_message = str(e)
            self.task_manager.update_task(task)
            if task.id in self.output_callbacks:
                self.output_callbacks[task.id](task.id, f"Error: {str(e)}")
        
        finally:
            task.completed_at = datetime.utcnow()
            self.task_manager.update_task(task)
            if task.completion_callback:
                task.completion_callback(task)
            
            # Cleanup
            self.output_callbacks.pop(task.id, None)
            # 从活动任务中移除（但保留在数据库中）
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self.active_tasks.get(task_id)
        if not task:
            return False
            
        if task.status == 'running' and task.process:
            try:
                task.process.terminate()
                task.status = 'cancelled'
                task.completed_at = datetime.utcnow()
                self.task_manager.update_task(task)
                return True
            except:
                pass
                
        return False
    
    def get_task(self, task_id: str) -> Optional['Task']:
        """Get task by ID."""
        # 先从活动任务中查找
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        # 再从持久化存储中查找
        return self.task_manager.get_task(task_id)
    
    def get_all_tasks(self) -> list:
        """Get all tasks."""
        # 返回所有任务（包括历史任务）
        return self.task_manager.get_all_tasks()
    
    def cleanup(self):
        """Cleanup resources."""
        # Stop worker threads
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Cancel all running tasks
        for task in self.active_tasks.values():
            if task.status == 'running':
                self.cancel_task(task.id)


# Task class is now imported from models.task


# Global executor instance
executor = None

def get_executor() -> ClaudeExecutor:
    """Get or create the global executor instance."""
    global executor
    if executor is None:
        from config import Config
        executor = ClaudeExecutor(
            claude_path=Config.CLAUDE_CODE_PATH,
            max_concurrent=Config.MAX_CONCURRENT_TASKS
        )
    return executor