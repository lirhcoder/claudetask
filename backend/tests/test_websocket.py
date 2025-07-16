import pytest
from unittest.mock import Mock, patch, MagicMock
from app import create_app, socketio
from services.claude_executor import Task

class TestWebSocketHandlers:
    """Test WebSocket event handlers."""
    
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
    
    def test_connect(self, socket_client):
        """Test client connection."""
        received = socket_client.get_received()
        
        assert len(received) == 1
        assert received[0]['name'] == 'connected'
        assert 'message' in received[0]['args'][0]
        assert 'session_id' in received[0]['args'][0]
    
    def test_join_leave_room(self, socket_client):
        """Test joining and leaving rooms."""
        # Join room
        socket_client.emit('join_room', {'project_id': 'test-project'})
        received = socket_client.get_received()
        
        assert len(received) == 1
        assert received[0]['name'] == 'joined_room'
        assert received[0]['args'][0]['room'] == 'test-project'
        
        # Leave room
        socket_client.emit('leave_room', {'project_id': 'test-project'})
        received = socket_client.get_received()
        
        assert len(received) == 1
        assert received[0]['name'] == 'left_room'
        assert received[0]['args'][0]['room'] == 'test-project'
    
    @patch('routes.websocket.get_executor')
    def test_execute_code(self, mock_get_executor, socket_client):
        """Test code execution via WebSocket."""
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute.return_value = 'task-123'
        mock_get_executor.return_value = mock_executor
        
        # Test successful execution
        socket_client.emit('execute_code', {
            'prompt': 'Create hello world',
            'project_path': '/tmp/test'
        })
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'execution_started'
        assert received[0]['args'][0]['task_id'] == 'task-123'
        
        # Verify executor was called with callbacks
        mock_executor.execute.assert_called_once()
        call_args = mock_executor.execute.call_args
        assert call_args.kwargs['output_callback'] is not None
        assert call_args.kwargs['completion_callback'] is not None
    
    def test_execute_code_validation_error(self, socket_client):
        """Test code execution with validation errors."""
        # Test missing prompt
        socket_client.emit('execute_code', {
            'project_path': '/tmp/test'
        })
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'execution_error'
        assert 'error' in received[0]['args'][0]
    
    @patch('routes.websocket.get_executor')
    def test_subscribe_task(self, mock_get_executor, socket_client):
        """Test subscribing to task updates."""
        # Mock task
        mock_task = Mock(spec=Task)
        mock_task.id = 'task-123'
        mock_task.status = 'running'
        mock_task.to_dict.return_value = {
            'id': 'task-123',
            'status': 'running'
        }
        
        mock_executor = Mock()
        mock_executor.get_task.return_value = mock_task
        mock_executor.output_callbacks = {}
        mock_get_executor.return_value = mock_executor
        
        # Subscribe to task
        socket_client.emit('subscribe_task', {'task_id': 'task-123'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'task_state'
        assert received[0]['args'][0]['id'] == 'task-123'
        
        # Test non-existent task
        mock_executor.get_task.return_value = None
        socket_client.emit('subscribe_task', {'task_id': 'nonexistent'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'subscription_error'
    
    def test_unsubscribe_task(self, socket_client):
        """Test unsubscribing from task updates."""
        socket_client.emit('unsubscribe_task', {'task_id': 'task-123'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'unsubscribed'
        assert received[0]['args'][0]['task_id'] == 'task-123'
    
    @patch('routes.websocket.get_executor')
    def test_cancel_task(self, mock_get_executor, socket_client):
        """Test cancelling task via WebSocket."""
        mock_executor = Mock()
        mock_executor.cancel_task.return_value = True
        mock_get_executor.return_value = mock_executor
        
        socket_client.emit('cancel_task', {'task_id': 'task-123'})
        
        received = socket_client.get_received()
        assert len(received) >= 1
        assert any(r['name'] == 'task_cancelled' for r in received)
        
        # Test failed cancellation
        mock_executor.cancel_task.return_value = False
        socket_client.emit('cancel_task', {'task_id': 'task-123'})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'cancellation_error'
    
    def test_cancel_task_missing_id(self, socket_client):
        """Test cancelling task without ID."""
        socket_client.emit('cancel_task', {})
        
        received = socket_client.get_received()
        assert len(received) == 1
        assert received[0]['name'] == 'cancellation_error'
        assert 'Task ID is required' in received[0]['args'][0]['error']