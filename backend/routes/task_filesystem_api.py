"""
任务文件系统 API 路由
"""
from flask import Blueprint, jsonify, request, session
from models.task_filesystem import TaskFileSystem, TaskNode
from services.claude_executor import get_executor
import logging

logger = logging.getLogger(__name__)

task_fs_bp = Blueprint('task_fs', __name__)
task_fs = TaskFileSystem()

@task_fs_bp.route('/tree', methods=['GET'])
def get_task_tree():
    """获取任务树结构"""
    try:
        path = request.args.get('path', '/')
        max_depth = request.args.get('max_depth', -1, type=int)
        
        tree = task_fs.get_task_tree(path, max_depth)
        return jsonify(tree), 200
    except Exception as e:
        logger.error(f"Error getting task tree: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/list', methods=['GET'])
def list_directory():
    """列出目录内容"""
    try:
        path = request.args.get('path', '/')
        tasks = task_fs.list_directory(path)
        
        return jsonify({
            'path': path,
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        logger.error(f"Error listing directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/task', methods=['GET'])
def get_task():
    """获取单个任务详情"""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({'error': 'Path is required'}), 400
        
        task = task_fs.get_task_by_path(path)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
            
        # 获取任务的文档和资源
        # TODO: 从数据库加载文档和资源
        
        return jsonify(task.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/create', methods=['POST'])
def create_task():
    """创建任务或文件夹"""
    try:
        data = request.get_json()
        parent_path = data.get('parent_path', '/')
        name = data.get('name')
        task_type = data.get('type', 'folder')  # 'folder' or 'task'
        prompt = data.get('prompt', '')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # 创建任务文件夹
        task = task_fs.create_task_folder(
            parent_path=parent_path,
            name=name,
            prompt=prompt,
            description=description
        )
        
        # 如果是可执行任务，设置为叶子节点
        if task_type == 'task':
            task.is_folder = False
            # TODO: 更新数据库
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/move', methods=['POST'])
def move_task():
    """移动任务"""
    try:
        data = request.get_json()
        source_path = data.get('source_path')
        dest_parent_path = data.get('dest_parent_path')
        new_name = data.get('new_name')
        
        if not source_path or not dest_parent_path:
            return jsonify({'error': 'Source and destination paths are required'}), 400
        
        success = task_fs.move_task(source_path, dest_parent_path, new_name)
        if success:
            return jsonify({'message': 'Task moved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to move task'}), 400
            
    except Exception as e:
        logger.error(f"Error moving task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/delete', methods=['DELETE'])
def delete_task():
    """删除任务"""
    try:
        path = request.args.get('path')
        recursive = request.args.get('recursive', 'false').lower() == 'true'
        
        if not path:
            return jsonify({'error': 'Path is required'}), 400
        
        success = task_fs.delete_task(path, recursive)
        if success:
            return jsonify({'message': 'Task deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete task'}), 400
            
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/execute', methods=['POST'])
def execute_task():
    """执行任务"""
    try:
        data = request.get_json()
        path = data.get('path')
        
        if not path:
            return jsonify({'error': 'Path is required'}), 400
        
        # 获取任务
        task = task_fs.get_task_by_path(path)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # 使用现有的执行器
        executor = get_executor()
        task_id = executor.execute(
            prompt=task.prompt,
            project_path=path,  # 使用任务路径作为项目路径
            user_id=session.get('user_id')
        )
        
        # 更新任务状态
        # TODO: 更新数据库中的任务状态
        
        return jsonify({
            'message': 'Task execution started',
            'task_id': task_id,
            'status': 'running'
        }), 202
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_fs_bp.route('/search', methods=['GET'])
def search_tasks():
    """搜索任务"""
    try:
        query = request.args.get('q', '')
        path = request.args.get('path', '/')
        
        # TODO: 实现搜索功能
        # 搜索任务名称、描述、prompt等
        
        return jsonify({
            'query': query,
            'results': []
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500