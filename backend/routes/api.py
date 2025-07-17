from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from services.claude_executor import get_executor
from utils.validators import validate_project_path, validate_prompt
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Claude Code Web API is running'}), 200

@api_bp.route('/execute', methods=['POST'])
def execute_claude():
    """Execute Claude Code with given prompt."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    prompt = data.get('prompt')
    project_path = data.get('project_path')
    
    # Validate inputs
    prompt_error = validate_prompt(prompt)
    if prompt_error:
        return jsonify({'error': prompt_error}), 400
        
    path_error = validate_project_path(project_path)
    if path_error:
        return jsonify({'error': path_error}), 400
    
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
                    'path': str(item),
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

@api_bp.route('/projects/<project_name>', methods=['GET'])
def get_project_details(project_name):
    """Get project details."""
    from config import Config
    project_path = Config.PROJECTS_DIR / secure_filename(project_name)
    
    if not project_path.exists():
        return jsonify({'error': 'Project not found'}), 404
    
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
        'path': str(project_path),
        'files': get_file_tree(project_path)
    }
    
    return jsonify(project_info), 200

@api_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """Get all tasks."""
    executor = get_executor()
    tasks = executor.get_all_tasks()
    
    # Convert to dict and sort by created_at
    task_list = [task.to_dict() for task in tasks]
    task_list.sort(key=lambda x: x['created_at'] or '', reverse=True)
    
    return jsonify({'tasks': task_list}), 200

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
                content = full_path.read_text()
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
            full_path.write_text(data['content'])
            
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