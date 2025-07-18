"""
任务链执行器 - 支持父子任务的连续执行
"""
import logging
from typing import List, Optional
import sys
from pathlib import Path

# 添加父目录到 Python 路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.task import Task, TaskManager

logger = logging.getLogger(__name__)

class TaskChainExecutor:
    """执行任务链，支持上下文传递和自动执行子任务"""
    
    def __init__(self, executor, task_manager: TaskManager):
        self.executor = executor
        self.task_manager = task_manager
        
    def create_task_chain(self, parent_prompt: str, child_prompts: List[str], 
                         project_path: str, user_id: Optional[str] = None) -> Task:
        """创建任务链"""
        import uuid
        
        # 如果没有 user_id，尝试从项目路径推断并创建用户
        if not user_id:
            from utils.user_inference import infer_user_from_project_path, construct_email
            from models.user import UserManager
            
            user_info = infer_user_from_project_path(project_path)
            if user_info:
                username, domain = user_info
                inferred_email = construct_email(username, domain)
                
                # 检查用户是否存在，不存在则创建
                user_manager = UserManager()
                user = user_manager.get_user_by_email(inferred_email)
                
                if not user:
                    logger.info(f"Creating new user from task chain: {inferred_email}")
                    # 创建新用户，密码为用户名+默认后缀
                    password = username.split('@')[0] + '123456'
                    user = user_manager.create_user(
                        email=inferred_email,
                        password=password,
                        username=username.split('@')[0]
                    )
                    if user:
                        user_id = user.id
                        logger.info(f"Created user {inferred_email} with ID {user_id}")
                else:
                    user_id = user.id
                    logger.info(f"Found existing user {inferred_email} with ID {user_id}")
        
        # 创建父任务
        parent_id = str(uuid.uuid4())
        parent_task = Task(
            id=parent_id,
            prompt=parent_prompt,
            project_path=project_path,
            user_id=user_id
        )
        parent_task.task_type = 'parent'
        
        # 创建子任务
        for i, child_prompt in enumerate(child_prompts):
            child_id = str(uuid.uuid4())
            child_task = Task(
                id=child_id,
                prompt=child_prompt,
                project_path=project_path,
                parent_task_id=parent_id,
                user_id=user_id
            )
            child_task.task_type = 'child'
            child_task.sequence_order = i + 1
            parent_task.children.append(child_task)
            
            # 保存子任务到数据库
            self.task_manager.add_task(child_task)
        
        # 保存父任务
        self.task_manager.add_task(parent_task)
        
        return parent_task
    
    def execute_chain(self, parent_task: Task):
        """执行任务链"""
        logger.info(f"开始执行任务链: {parent_task.id}")
        
        # 设置完成回调
        original_callback = parent_task.completion_callback
        parent_task.completion_callback = lambda task: self._on_parent_complete(task, original_callback)
        
        # 执行父任务
        self.executor.execute(
            parent_task.prompt,
            parent_task.project_path,
            output_callback=self._create_output_callback(parent_task.id),
            completion_callback=parent_task.completion_callback
        )
    
    def _on_parent_complete(self, parent_task: Task, original_callback=None):
        """父任务完成后的处理"""
        logger.info(f"父任务完成: {parent_task.id}, 状态: {parent_task.status}")
        
        # 调用原始回调
        if original_callback:
            original_callback(parent_task)
        
        # 如果父任务失败，不执行子任务
        if parent_task.status != 'completed':
            logger.warning(f"父任务失败，跳过子任务执行")
            return
        
        # 获取并执行子任务
        children = sorted(parent_task.children, key=lambda t: t.sequence_order)
        if children:
            self._execute_next_child(parent_task, children, 0)
    
    def _execute_next_child(self, parent_task: Task, children: List[Task], index: int):
        """执行下一个子任务"""
        if index >= len(children):
            logger.info(f"所有子任务执行完成")
            return
        
        child_task = children[index]
        logger.info(f"执行子任务 {index + 1}/{len(children)}: {child_task.id}")
        
        # 构建包含上下文的提示
        contextual_prompt = self._build_contextual_prompt(child_task, parent_task)
        child_task.prompt = contextual_prompt
        child_task.context = self._extract_context(parent_task)
        
        # 设置完成回调以执行下一个子任务
        child_task.completion_callback = lambda task: self._on_child_complete(
            task, parent_task, children, index
        )
        
        # 执行子任务
        self.executor.execute(
            child_task.prompt,
            child_task.project_path,
            output_callback=self._create_output_callback(child_task.id),
            completion_callback=child_task.completion_callback
        )
    
    def _on_child_complete(self, child_task: Task, parent_task: Task, 
                          children: List[Task], current_index: int):
        """子任务完成后的处理"""
        logger.info(f"子任务完成: {child_task.id}, 状态: {child_task.status}")
        
        # 更新父任务的上下文
        if hasattr(parent_task, 'context_summary'):
            parent_task.context_summary += f"\n\n子任务 {current_index + 1} 结果摘要:\n"
            parent_task.context_summary += self._summarize_output(child_task.output)
        else:
            parent_task.context_summary = self._summarize_output(child_task.output)
        
        # 执行下一个子任务
        self._execute_next_child(parent_task, children, current_index + 1)
    
    def _build_contextual_prompt(self, child_task: Task, parent_task: Task) -> str:
        """构建包含上下文的提示"""
        context_parts = []
        
        # 添加父任务信息
        context_parts.append(f"基于之前的任务继续执行：")
        context_parts.append(f"初始任务：{parent_task.prompt}")
        
        # 添加父任务输出摘要
        if parent_task.output:
            summary = self._summarize_output(parent_task.output)
            context_parts.append(f"初始任务结果摘要：{summary}")
        
        # 添加之前子任务的上下文
        if hasattr(parent_task, 'context_summary'):
            context_parts.append(parent_task.context_summary)
        
        # 添加当前任务
        context_parts.append(f"\n当前任务：{child_task.prompt}")
        context_parts.append("\n请基于上述上下文继续执行当前任务。不要重复已完成的工作。")
        
        return "\n".join(context_parts)
    
    def _extract_context(self, task: Task) -> str:
        """从任务输出中提取关键上下文"""
        if not task.output:
            return ""
        
        context_info = []
        
        # 提取创建的文件
        lines = task.output.split('\n')
        for line in lines:
            if 'created' in line.lower() or 'wrote' in line.lower():
                context_info.append(line.strip())
            elif 'error' in line.lower() or 'failed' in line.lower():
                context_info.append(f"错误: {line.strip()}")
        
        return "\n".join(context_info[-10:])  # 只保留最近的10条信息
    
    def _summarize_output(self, output: str) -> str:
        """生成输出摘要"""
        if not output:
            return "无输出"
        
        lines = output.strip().split('\n')
        
        # 如果输出很短，直接返回
        if len(lines) <= 5:
            return output
        
        # 提取关键行
        summary_lines = []
        
        # 保留前两行和后三行
        summary_lines.extend(lines[:2])
        summary_lines.append("...")
        summary_lines.extend(lines[-3:])
        
        return "\n".join(summary_lines)
    
    def _create_output_callback(self, task_id: str):
        """创建输出回调函数"""
        def callback(task_id: str, output: str):
            # 这里可以添加WebSocket推送等实时更新逻辑
            logger.debug(f"Task {task_id}: {output}")
        return callback