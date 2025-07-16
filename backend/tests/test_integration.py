import pytest
import json
import time
from threading import Thread
from unittest.mock import Mock, patch
from app import create_app, socketio
from services.claude_executor import Task

class TestRealtimeIntegration:
    """Test real-time communication between frontend and backend."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def socket_client(self, app, client):
        """Create Socket.IO test client."""
        return socketio.test_client(app, flask_test_client=client)
    
    @patch('services.claude_executor.get_executor')
    def test_realtime_task_execution(self, mock_get_executor, socket_client):
        """Test real-time task execution flow."""
        # Mock executor
        mock_executor = Mock()
        mock_task_id = 'test-task-123'
        
        # Track callbacks
        output_callback = None
        completion_callback = None
        
        def capture_execute(**kwargs):
            nonlocal output_callback, completion_callback
            output_callback = kwargs.get('output_callback')
            completion_callback = kwargs.get('completion_callback')
            return mock_task_id
        
        mock_executor.execute.side_effect = capture_execute
        mock_get_executor.return_value = mock_executor
        
        # Execute code via WebSocket
        socket_client.emit('execute_code', {
            'prompt': 'Test prompt',
            'project_path': '/test/path'
        })
        
        # Check execution started
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'execution_started'
        assert received[0]['args'][0]['task_id'] == mock_task_id
        
        # Simulate output callback
        if output_callback:
            output_callback(mock_task_id, 'Output line 1')
            output_callback(mock_task_id, 'Output line 2')
        
        # Get output events
        received = socket_client.get_received()
        assert len(received) == 2
        assert all(r['name'] == 'task_output' for r in received)
        assert received[0]['args'][0]['line'] == 'Output line 1'
        assert received[1]['args'][0]['line'] == 'Output line 2'
        
        # Simulate completion
        if completion_callback:
            mock_task = Mock(spec=Task)
            mock_task.id = mock_task_id
            mock_task.status = 'completed'
            mock_task.exit_code = 0
            mock_task._calculate_duration.return_value = 5.5
            mock_task.output = 'Complete output'
            completion_callback(mock_task)
        
        # Get completion event
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'task_complete'
        assert received[0]['args'][0]['task_id'] == mock_task_id
        assert received[0]['args'][0]['status'] == 'completed'
        assert received[0]['args'][0]['duration'] == 5.5
    
    @patch('services.claude_executor.get_executor')
    def test_task_subscription(self, mock_get_executor, socket_client):
        """Test subscribing to task updates."""
        # Mock task
        mock_task = Mock(spec=Task)
        mock_task.id = 'task-456'
        mock_task.status = 'running'
        mock_task.to_dict.return_value = {
            'id': 'task-456',
            'status': 'running',
            'prompt': 'Test prompt'
        }
        
        mock_executor = Mock()
        mock_executor.get_task.return_value = mock_task
        mock_executor.output_callbacks = {}
        mock_get_executor.return_value = mock_executor
        
        # Subscribe to task
        socket_client.emit('subscribe_task', {'task_id': 'task-456'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'task_state'
        assert received[0]['args'][0]['id'] == 'task-456'
        assert received[0]['args'][0]['status'] == 'running'
    
    @patch('routes.api.get_executor')
    def test_api_websocket_coordination(self, mock_get_executor, client, socket_client):
        """Test coordination between REST API and WebSocket."""
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute.return_value = 'task-789'
        mock_get_executor.return_value = mock_executor
        
        # Execute via REST API
        response = client.post('/api/execute', json={
            'prompt': 'API test prompt',
            'project_path': '/api/test'
        })
        
        assert response.status_code == 202
        data = json.loads(response.data)
        task_id = data['task_id']
        
        # Subscribe via WebSocket
        mock_task = Mock(spec=Task)
        mock_task.id = task_id
        mock_task.status = 'pending'
        mock_task.to_dict.return_value = {'id': task_id, 'status': 'pending'}
        mock_executor.get_task.return_value = mock_task
        
        socket_client.emit('subscribe_task', {'task_id': task_id})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['args'][0]['id'] == task_id
    
    def test_multiple_clients_room_isolation(self, app, client):
        """Test that task updates are isolated to correct clients."""
        # Create two socket clients
        client1 = socketio.test_client(app, flask_test_client=client)
        client2 = socketio.test_client(app, flask_test_client=client)
        
        # Client 1 joins project room
        client1.emit('join_room', {'project_id': 'project1'})
        received1 = client1.get_received()
        assert received1[0]['name'] == 'joined_room'
        
        # Client 2 joins different project room
        client2.emit('join_room', {'project_id': 'project2'})
        received2 = client2.get_received()
        assert received2[0]['name'] == 'joined_room'
        
        # Verify isolation (would need actual room broadcasting to fully test)
        assert len(client1.get_received()) == 0
        assert len(client2.get_received()) == 0
    
    @patch('services.claude_executor.get_executor')
    def test_error_handling_flow(self, mock_get_executor, socket_client):
        """Test error handling in real-time communication."""
        # Test validation error
        socket_client.emit('execute_code', {
            'prompt': '',  # Empty prompt
            'project_path': '/test'
        })
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'execution_error'
        assert 'error' in received[0]['args'][0]
        
        # Test task cancellation
        mock_executor = Mock()
        mock_executor.cancel_task.return_value = False
        mock_get_executor.return_value = mock_executor
        
        socket_client.emit('cancel_task', {'task_id': 'nonexistent'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'cancellation_error'