from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from services.claude_executor import get_executor
from services.task_chain_executor import TaskChainExecutor
from services.local_launcher import LocalLauncher
from services.script_generator import TaskScriptGenerator
from utils.validators import validate_project_path, validate_prompt
from datetime import datetime
from models.task import Task, TaskManager

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Claude Code Web API is running'}), 200

@api_bp.route('/debug/validate-path', methods=['POST'])
def debug_validate_path():
    """Debug endpoint to validate project paths."""
    data = request.get_json()
    project_path = data.get('project_path', '')
    
    # Original path
    result = {
        'original_path': project_path,
        'has_backslashes': '\\' in project_path,
        'is_windows_path': len(project_path) > 2 and project_path[1:3] == ':\\'
    }
    
    # Convert if needed
    converted_path = project_path
    if '\\' in project_path:
        if project_path[1:3] == ':\\':
            drive_letter = project_path[0].lower()
            path_part = project_path[3:].replace('\\', '/')
            converted_path = f'/mnt/{drive_letter}/{path_part}'
        else:
            converted_path = project_path.replace('\\', '/')
    
    result['converted_path'] = converted_path
    
    # Validate
    from pathlib import Path
    try:
        path = Path(converted_path)
        result['path_exists'] = path.exists()
        result['is_directory'] = path.is_dir() if path.exists() else False
        result['is_absolute'] = path.is_absolute()
        result['resolved_path'] = str(path.resolve()) if path.exists() else None
    except Exception as e:
        result['path_error'] = str(e)
    
    # Run validator
    error = validate_project_path(project_path)
    result['validation_error'] = error
    result['is_valid'] = error is None
    
    return jsonify(result), 200

@api_bp.route('/execute', methods=['POST'])
def execute_claude():
    """Execute Claude Code with given prompt."""
    import logging
    logger = logging.getLogger(__name__)
    
    data = request.get_json()
    logger.info(f"Execute request received: {data}")
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    prompt = data.get('prompt')
    project_path = data.get('project_path')
    
    logger.info(f"Prompt: {prompt[:50]}..." if prompt else "No prompt")
    logger.info(f"Project path: {project_path}")
    
    # Validate inputs
    prompt_error = validate_prompt(prompt)
    if prompt_error:
        logger.error(f"Prompt validation error: {prompt_error}")
        return jsonify({'error': prompt_error}), 400
        
    path_error = validate_project_path(project_path)
    if path_error:
        logger.error(f"Path validation error: {path_error}")
        return jsonify({'error': path_error}), 400
    
    # Convert Windows path to WSL path if needed
    original_path = project_path
    if project_path and '\\' in project_path:
        if len(project_path) > 2 and project_path[1:3] == ':\\':
            drive_letter = project_path[0].lower()
            path_part = project_path[3:].replace('\\', '/')
            project_path = f'/mnt/{drive_letter}/{path_part}'
        else:
            project_path = project_path.replace('\\', '/')
        logger.info(f"Converted Windows path from '{original_path}' to '{project_path}'")
    
    # Convert relative path to absolute if needed
    path = Path(project_path)
    if not path.is_absolute():
        from config import Config
        path = Config.PROJECTS_DIR / path
        project_path = str(path)
    
    # Execute task
    executor = get_executor()
    task_id = executor.execute(
        prompt=prompt,
        project_path=project_path
    )
    
    return jsonify({
        'task_id': task_id,
        'status': 'queued',
        'message': 'Task queued for execution'
    }), 202

@api_bp.route('/projects', methods=['GET'])
def list_projects():
    """List all projects."""
    from config import Config
    projects_dir = Config.PROJECTS_DIR
    
    projects = []
    if projects_dir.exists():
        for item in projects_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                project_info = {
                    'name': item.name,
                    'path': str(item.relative_to(Config.PROJECTS_DIR.parent)),
                    'absolute_path': str(item.absolute()).replace('\\', '/'),
                    'created_at': datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                projects.append(project_info)
    
    return jsonify({'projects': projects}), 200

@api_bp.route('/projects', methods=['POST'])
def create_project():
    """Create a new project."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    project_name = secure_filename(data['name'])
    if not project_name:
        return jsonify({'error': 'Invalid project name'}), 400
    
    from config import Config
    project_path = Config.PROJECTS_DIR / project_name
    
    if project_path.exists():
        return jsonify({'error': 'Project already exists'}), 409
    
    try:
        project_path.mkdir(parents=True)
        
        # Initialize with README if requested
        if data.get('initialize_readme', False):
            readme_path = project_path / 'README.md'
            readme_path.write_text(f'# {project_name}\n\nCreated with Claude Code Web')
        
        return jsonify({
            'name': project_name,
            'path': str(project_path),
            'message': 'Project created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500

@api_bp.route('/projects/<project_name>', methods=['GET', 'DELETE', 'PUT'])
def project_details(project_name):
    """Get or delete project."""
    from config import Config
    project_path = Config.PROJECTS_DIR / secure_filename(project_name)
    
    if not project_path.exists():
        return jsonify({'error': 'Project not found'}), 404
    
    if request.method == 'DELETE':
        # Delete project
        try:
            import shutil
            shutil.rmtree(str(project_path))
            return jsonify({'message': 'Project deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to delete project: {str(e)}'}), 500
    
    elif request.method == 'PUT':
        # Update project (rename/move)
        data = request.get_json()
        new_path = data.get('new_path')
        
        if not new_path:
            return jsonify({'error': 'New path is required'}), 400
        
        try:
            new_path = Path(new_path)
            if not new_path.is_absolute():
                new_path = Config.PROJECTS_DIR / new_path
            
            # Ensure parent directory exists
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move project
            import shutil
            shutil.move(str(project_path), str(new_path))
            
            return jsonify({
                'message': 'Project updated successfully',
                'new_name': new_path.name,
                'new_path': str(new_path)
            }), 200
        except Exception as e:
            return jsonify({'error': f'Failed to update project: {str(e)}'}), 500
    
    # Get file tree
    def get_file_tree(path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return None
            
        tree = []
        for item in sorted(path.iterdir()):
            if item.name.startswith('.'):
                continue
                
            node = {
                'name': item.name,
                'type': 'directory' if item.is_dir() else 'file',
                'path': str(item.relative_to(Config.PROJECTS_DIR))
            }
            
            if item.is_dir():
                children = get_file_tree(item, max_depth, current_depth + 1)
                if children:
                    node['children'] = children
                    
            tree.append(node)
            
        return tree
    
    project_info = {
        'name': project_name,
        'path': str(project_path.relative_to(Config.PROJECTS_DIR.parent)),
        'absolute_path': str(project_path.absolute()).replace('\\', '/'),
        'files': get_file_tree(project_path)
    }
    
    return jsonify(project_info), 200

@api_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """Get all tasks."""
    try:
        executor = get_executor()
        tasks = executor.get_all_tasks()
        
        # Convert to dict and sort by created_at
        task_list = []
        for task in tasks:
            try:
                task_dict = task.to_dict()
                task_list.append(task_dict)
            except Exception as e:
                import logging
                logging.error(f"Error converting task to dict: {e}")
                continue
        
        task_list.sort(key=lambda x: x.get('created_at') or '', reverse=True)
        
        return jsonify({'tasks': task_list}), 200
    except Exception as e:
        import logging
        logging.error(f"Error in list_tasks: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task details."""
    executor = get_executor()
    task = executor.get_task(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task.to_dict()), 200

@api_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task."""
    executor = get_executor()
    success = executor.cancel_task(task_id)
    
    if success:
        return jsonify({'message': 'Task cancelled successfully'}), 200
    else:
        return jsonify({'error': 'Failed to cancel task or task not found'}), 400

@api_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """Upload a file to a project."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    project_name = request.form.get('project')
    file_path = request.form.get('path', '')
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    from config import Config
    
    # Validate file extension
    file_ext = Path(file.filename).suffix
    if file_ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'error': f'File type {file_ext} not allowed'}), 400
    
    # Construct save path
    project_path = Config.PROJECTS_DIR / secure_filename(project_name)
    if not project_path.exists():
        return jsonify({'error': 'Project not found'}), 404
    
    save_path = project_path / secure_filename(file_path) / secure_filename(file.filename)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        file.save(str(save_path))
        return jsonify({
            'message': 'File uploaded successfully',
            'path': str(save_path.relative_to(Config.PROJECTS_DIR))
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

@api_bp.route('/files/<path:file_path>', methods=['GET', 'PUT'])
def get_file_content(file_path):
    """Get or update file content."""
    from config import Config
    
    full_path = Config.PROJECTS_DIR / file_path
    
    # Security check
    try:
        full_path.resolve().relative_to(Config.PROJECTS_DIR.resolve())
    except ValueError:
        return jsonify({'error': 'Invalid file path'}), 403
    
    if request.method == 'GET':
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        if not full_path.is_file():
            return jsonify({'error': 'Not a file'}), 400
        
        # Return file content
        try:
            if request.args.get('download') == 'true':
                return send_file(str(full_path), as_attachment=True)
            else:
                # Try multiple encodings
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                content = None
                
                for encoding in encodings:
                    try:
                        content = full_path.read_text(encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # If all encodings fail, read as binary and try to decode
                    content = full_path.read_bytes().decode('utf-8', errors='ignore')
                return jsonify({
                    'path': file_path,
                    'content': content,
                    'size': full_path.stat().st_size
                }), 200
        except Exception as e:
            return jsonify({'error': f'Failed to read file: {str(e)}'}), 500
            
    elif request.method == 'PUT':
        # Update file content
        try:
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400
                
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            full_path.write_text(data['content'], encoding='utf-8')
            
            return jsonify({
                'message': 'File saved successfully',
                'path': file_path,
                'size': full_path.stat().st_size
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

@api_bp.route('/files/<path:file_path>', methods=['DELETE'])
def delete_file(file_path):
    """Delete a file."""
    from config import Config
    
    # Validate path
    try:
        full_path = Config.PROJECTS_DIR / file_path
        full_path = full_path.resolve()
        
        # Security check - ensure path is within projects directory
        if not str(full_path).startswith(str(Config.PROJECTS_DIR.resolve())):
            return jsonify({'error': 'Invalid file path'}), 403
            
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
            
        if full_path.is_dir():
            return jsonify({'error': 'Cannot delete directories through this endpoint'}), 400
            
        # Delete the file
        full_path.unlink()
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@api_bp.route('/task-chains', methods=['POST'])
def create_task_chain():
    """Create and execute a task chain."""
    data = request.get_json()
    
    # Validate input
    project_path = data.get('project_path')
    tasks = data.get('tasks', [])
    
    if not project_path or not tasks:
        return jsonify({'error': 'Project path and tasks are required'}), 400
    
    if len(tasks) < 2:
        return jsonify({'error': 'Task chain must have at least 2 tasks'}), 400
    
    # Convert Windows paths if needed
    if '\\' in project_path:
        project_path = project_path.replace('\\', '/')
    
    # Validate project path
    error_msg = validate_project_path(project_path)
    if error_msg:
        return jsonify({'error': error_msg}), 400
    
    try:
        executor = get_executor()
        task_manager = TaskManager()
        chain_executor = TaskChainExecutor(executor, task_manager)
        
        # Extract prompts from tasks
        parent_prompt = tasks[0].get('prompt', '')
        child_prompts = [task.get('prompt', '') for task in tasks[1:]]
        
        # Validate prompts
        for prompt in [parent_prompt] + child_prompts:
            error_msg = validate_prompt(prompt)
            if error_msg:
                return jsonify({'error': f'Invalid prompt: {error_msg}'}), 400
        
        # Create task chain
        parent_task = chain_executor.create_task_chain(
            parent_prompt=parent_prompt,
            child_prompts=child_prompts,
            project_path=project_path
        )
        
        # Execute the chain
        chain_executor.execute_chain(parent_task)
        
        return jsonify({
            'message': 'Task chain created and execution started',
            'parent_task_id': parent_task.id,
            'total_tasks': len(tasks),
            'task_chain': parent_task.to_dict()
        }), 201
        
    except Exception as e:
        import logging
        logging.error(f"Error creating task chain: {str(e)}")
        return jsonify({'error': f'Failed to create task chain: {str(e)}'}), 500

@api_bp.route('/tasks/<task_id>/children', methods=['GET'])
def get_task_children(task_id):
    """Get children of a task."""
    try:
        task_manager = TaskManager()
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Get children from database
        children = []
        if hasattr(task, 'children'):
            for child in task.children:
                children.append(child.to_dict())
        
        return jsonify({
            'task_id': task_id,
            'children': children,
            'count': len(children)
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error getting task children: {str(e)}")
        return jsonify({'error': f'Failed to get task children: {str(e)}'}), 500

@api_bp.route('/tasks/<task_id>/add-child', methods=['POST'])
def add_child_task(task_id):
    """Add a child task to an existing task."""
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        executor = get_executor()
        task_manager = TaskManager()
        parent_task = task_manager.get_task(task_id)
        
        if not parent_task:
            return jsonify({'error': 'Parent task not found'}), 404
        
        # Create child task
        import uuid
        child_id = str(uuid.uuid4())
        child_task = Task(
            id=child_id,
            prompt=prompt,
            project_path=parent_task.project_path,
            parent_task_id=task_id
        )
        child_task.task_type = 'child'
        child_task.sequence_order = len(parent_task.children) + 1 if hasattr(parent_task, 'children') else 1
        
        # Save child task
        task_manager.add_task(child_task)
        
        # Update parent task
        if not hasattr(parent_task, 'children'):
            parent_task.children = []
        parent_task.children.append(child_task)
        
        return jsonify({
            'message': 'Child task added',
            'child_task': child_task.to_dict()
        }), 201
        
    except Exception as e:
        import logging
        logging.error(f"Error adding child task: {str(e)}")
        return jsonify({'error': f'Failed to add child task: {str(e)}'}), 500

@api_bp.route('/tasks/<task_id>/local-result', methods=['POST'])
def update_local_result(task_id):
    """接收本地执行的结果"""
    try:
        data = request.get_json()
        
        # 获取任务
        task_manager = TaskManager()
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # 更新任务状态和结果
        task.status = data.get('status', 'completed')
        task.output = data.get('output', '')
        task.completed_at = data.get('completed_at')
        task.exit_code = data.get('exit_code', 0)
        task.execution_time = data.get('duration', 0)
        
        # 如果任务被中断
        if data.get('interrupted'):
            task.error_message = "任务被用户中断"
        elif task.exit_code != 0:
            task.error_message = f"任务执行失败，退出代码: {task.exit_code}"
        
        # 保存更新
        task_manager.update_task(task)
        
        # 如果有 WebSocket 连接，通知前端
        from app import socketio
        socketio.emit('task_update', {
            'task_id': task_id,
            'status': task.status,
            'output': task.output,
            'completed': True
        }, room=task_id)
        
        return jsonify({
            'message': 'Result updated successfully',
            'task_id': task_id,
            'status': task.status
        }), 200
        
    except Exception as e:
        import logging
        import traceback
        logging.error(f"Error updating local result: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Failed to update result: {str(e)}'}), 500

@api_bp.route('/tasks/<task_id>/launch-local', methods=['POST'])
def launch_local_execution(task_id):
    """Launch task in local terminal for interactive execution."""
    try:
        task_manager = TaskManager()
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Create launcher and script generator
        launcher = LocalLauncher()
        generator = TaskScriptGenerator()
        
        # Create task script
        script_path = launcher.create_task_script(
            task_id=task.id,
            prompt=task.prompt,
            project_path=task.project_path
        )
        
        # Create task info file
        info_path = launcher.create_task_info(
            task_id=task.id,
            prompt=task.prompt,
            project_path=task.project_path
        )
        
        # Launch terminal
        success = launcher.launch_terminal(
            script_path=script_path,
            title=f"Claude Task - {task_id[:8]}"
        )
        
        if success:
            return jsonify({
                'message': 'Task launched in local terminal',
                'task_id': task_id,
                'script_path': str(script_path),
                'info_path': str(info_path)
            }), 200
        else:
            return jsonify({'error': 'Failed to launch terminal'}), 500
            
    except Exception as e:
        import logging
        import traceback
        logging.error(f"Error launching local execution: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Failed to launch: {str(e)}'}), 500

@api_bp.route('/execute-local', methods=['POST'])
def execute_local():
    """Create a new task and launch it in local terminal."""
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    project_path = data.get('project_path')
    
    # Validate input
    if not prompt or not project_path:
        return jsonify({'error': 'Prompt and project path are required'}), 400
    
    # Convert Windows paths
    if '\\' in project_path:
        project_path = project_path.replace('\\', '/')
    
    # Validate project path
    error_msg = validate_project_path(project_path)
    if error_msg:
        return jsonify({'error': error_msg}), 400
    
    # Validate prompt
    error_msg = validate_prompt(prompt)
    if error_msg:
        return jsonify({'error': error_msg}), 400
    
    try:
        # Create task record
        import uuid
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            prompt=prompt,
            project_path=project_path
        )
        
        # Initialize additional fields
        task.parent_task_id = None
        task.context = None
        task.sequence_order = 0
        task.task_type = 'single'
        
        task_manager = TaskManager()
        task_manager.add_task(task)
        
        # Launch in local terminal
        launcher = LocalLauncher()
        script_path = launcher.create_task_script(task_id, prompt, project_path)
        success = launcher.launch_terminal(script_path, f"Claude Task - {task_id[:8]}")
        
        if success:
            return jsonify({
                'message': 'Task created and launched in local terminal',
                'task_id': task_id,
                'task': task.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Failed to launch terminal'}), 500
            
    except Exception as e:
        import logging
        import traceback
        logging.error(f"Error creating local task: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500