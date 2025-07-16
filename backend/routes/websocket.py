from flask_socketio import emit, join_room, leave_room, rooms
from flask import request
from services.claude_executor import get_executor
from utils.validators import validate_prompt, validate_project_path
import logging

logger = logging.getLogger(__name__)

def register_socketio_handlers(socketio):
    """Register Socket.IO event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {
            'message': 'Connected to Claude Code Web Socket',
            'session_id': request.sid
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle room joining for project-specific updates."""
        room = data.get('project_id')
        if room:
            join_room(room)
            emit('joined_room', {'room': room})
            logger.info(f"Client {request.sid} joined room: {room}")
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle room leaving."""
        room = data.get('project_id')
        if room:
            leave_room(room)
            emit('left_room', {'room': room})
            logger.info(f"Client {request.sid} left room: {room}")
    
    @socketio.on('execute_code')
    def handle_execute_code(data):
        """Execute Claude Code via WebSocket."""
        prompt = data.get('prompt')
        project_path = data.get('project_path')
        
        # Validate inputs
        prompt_error = validate_prompt(prompt)
        if prompt_error:
            emit('execution_error', {'error': prompt_error})
            return
            
        path_error = validate_project_path(project_path)
        if path_error:
            emit('execution_error', {'error': path_error})
            return
        
        # Create output callback for real-time updates
        def output_callback(task_id, line):
            """Send output lines to client in real-time."""
            socketio.emit('task_output', {
                'task_id': task_id,
                'line': line,
                'timestamp': datetime.utcnow().isoformat()
            }, room=request.sid)
        
        # Create completion callback
        def completion_callback(task):
            """Send completion notification."""
            socketio.emit('task_complete', {
                'task_id': task.id,
                'status': task.status,
                'exit_code': task.exit_code,
                'duration': task._calculate_duration(),
                'output': task.output
            }, room=request.sid)
        
        # Execute task
        executor = get_executor()
        task_id = executor.execute(
            prompt=prompt,
            project_path=project_path,
            output_callback=output_callback,
            completion_callback=completion_callback
        )
        
        # Send initial response
        emit('execution_started', {
            'task_id': task_id,
            'message': 'Task execution started'
        })
    
    @socketio.on('subscribe_task')
    def handle_subscribe_task(data):
        """Subscribe to task updates."""
        task_id = data.get('task_id')
        if not task_id:
            emit('subscription_error', {'error': 'Task ID is required'})
            return
        
        executor = get_executor()
        task = executor.get_task(task_id)
        
        if not task:
            emit('subscription_error', {'error': 'Task not found'})
            return
        
        # Join task-specific room
        join_room(f"task_{task_id}")
        
        # Send current task state
        emit('task_state', task.to_dict())
        
        # If task is still running, set up callbacks
        if task.status in ['pending', 'running']:
            def output_callback(task_id, line):
                socketio.emit('task_output', {
                    'task_id': task_id,
                    'line': line
                }, room=f"task_{task_id}")
            
            def completion_callback(task):
                socketio.emit('task_complete', task.to_dict(), room=f"task_{task_id}")
            
            # Update callbacks if task hasn't started yet
            if task_id in executor.output_callbacks:
                executor.output_callbacks[task_id] = output_callback
            if hasattr(task, 'completion_callback'):
                task.completion_callback = completion_callback
    
    @socketio.on('unsubscribe_task')
    def handle_unsubscribe_task(data):
        """Unsubscribe from task updates."""
        task_id = data.get('task_id')
        if task_id:
            leave_room(f"task_{task_id}")
            emit('unsubscribed', {'task_id': task_id})
    
    @socketio.on('cancel_task')
    def handle_cancel_task(data):
        """Cancel a running task via WebSocket."""
        task_id = data.get('task_id')
        if not task_id:
            emit('cancellation_error', {'error': 'Task ID is required'})
            return
        
        executor = get_executor()
        success = executor.cancel_task(task_id)
        
        if success:
            emit('task_cancelled', {'task_id': task_id})
            # Notify all subscribers
            socketio.emit('task_cancelled', {'task_id': task_id}, room=f"task_{task_id}")
        else:
            emit('cancellation_error', {'error': 'Failed to cancel task'})

from datetime import datetime