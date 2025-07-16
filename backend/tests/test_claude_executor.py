import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.claude_executor import ClaudeExecutor, Task, get_executor

class TestTask:
    """Test Task class."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            id='test-123',
            prompt='Create a hello world app',
            project_path='/test/path'
        )
        
        assert task.id == 'test-123'
        assert task.prompt == 'Create a hello world app'
        assert task.project_path == '/test/path'
        assert task.status == 'pending'
        assert task.created_at is not None
        assert task.started_at is None
        assert task.completed_at is None
        
    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            id='test-123',
            prompt='Test prompt',
            project_path='/test'
        )
        task.output = 'Test output'
        task.exit_code = 0
        
        task_dict = task.to_dict()
        
        assert task_dict['id'] == 'test-123'
        assert task_dict['prompt'] == 'Test prompt'
        assert task_dict['project_path'] == '/test'
        assert task_dict['status'] == 'pending'
        assert task_dict['output'] == 'Test output'
        assert task_dict['exit_code'] == 0
        assert task_dict['duration'] is None
        
    def test_task_duration_calculation(self):
        """Test task duration calculation."""
        task = Task('test', 'prompt', '/path')
        task.started_at = datetime(2024, 1, 1, 10, 0, 0)
        task.completed_at = datetime(2024, 1, 1, 10, 0, 30)
        
        assert task._calculate_duration() == 30.0


class TestClaudeExecutor:
    """Test ClaudeExecutor class."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance for testing."""
        executor = ClaudeExecutor(claude_path='claude', max_concurrent=2)
        yield executor
        executor.cleanup()
    
    def test_executor_initialization(self, executor):
        """Test executor initialization."""
        assert executor.claude_path == 'claude'
        assert executor.max_concurrent == 2
        assert len(executor.workers) == 2
        assert executor.task_queue.empty()
        assert len(executor.active_tasks) == 0
        
    def test_execute_creates_task(self, executor):
        """Test that execute creates and queues a task."""
        task_id = executor.execute(
            prompt='Test prompt',
            project_path='/test/path'
        )
        
        assert task_id is not None
        assert task_id in executor.active_tasks
        
        task = executor.active_tasks[task_id]
        assert task.prompt == 'Test prompt'
        assert task.project_path == '/test/path'
        assert task.status == 'pending'
        
    @patch('subprocess.Popen')
    def test_execute_with_callbacks(self, mock_popen, executor):
        """Test execute with output and completion callbacks."""
        # Mock process
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ['Line 1\n', 'Line 2\n']
        mock_popen.return_value = mock_process
        
        output_callback = Mock()
        completion_callback = Mock()
        
        task_id = executor.execute(
            prompt='Test',
            project_path='/test',
            output_callback=output_callback,
            completion_callback=completion_callback
        )
        
        # Wait for task to complete
        time.sleep(0.1)
        
        # Check callbacks were registered
        assert output_callback.called or completion_callback.called
        
    def test_cancel_task(self, executor):
        """Test cancelling a task."""
        task_id = executor.execute('Test', '/test')
        task = executor.get_task(task_id)
        
        # Mock running task
        task.status = 'running'
        task.process = MagicMock()
        
        result = executor.cancel_task(task_id)
        
        assert result is True
        assert task.process.terminate.called
        assert task.status == 'cancelled'
        
    def test_cancel_nonexistent_task(self, executor):
        """Test cancelling a non-existent task."""
        result = executor.cancel_task('nonexistent')
        assert result is False
        
    def test_get_task(self, executor):
        """Test getting a task by ID."""
        task_id = executor.execute('Test', '/test')
        
        task = executor.get_task(task_id)
        assert task is not None
        assert task.id == task_id
        
        # Test non-existent task
        assert executor.get_task('nonexistent') is None
        
    def test_get_all_tasks(self, executor):
        """Test getting all tasks."""
        # Create multiple tasks
        task_id1 = executor.execute('Test 1', '/test1')
        task_id2 = executor.execute('Test 2', '/test2')
        
        all_tasks = executor.get_all_tasks()
        assert len(all_tasks) == 2
        
        task_ids = [task.id for task in all_tasks]
        assert task_id1 in task_ids
        assert task_id2 in task_ids
        
    @patch('subprocess.Popen')
    def test_worker_processes_task(self, mock_popen, executor):
        """Test worker thread processes tasks correctly."""
        # Mock successful process
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ['Success\n']
        mock_popen.return_value = mock_process
        
        task_id = executor.execute('Test prompt', '/test/path')
        
        # Wait for task processing
        time.sleep(0.2)
        
        task = executor.get_task(task_id)
        assert task.status in ['running', 'completed']
        assert mock_popen.called
        
    def test_cleanup(self, executor):
        """Test executor cleanup."""
        # Add a task
        task_id = executor.execute('Test', '/test')
        
        # Cleanup
        executor.cleanup()
        
        # Check workers are stopped
        for worker in executor.workers:
            worker.join(timeout=1)
            assert not worker.is_alive()


class TestGetExecutor:
    """Test get_executor function."""
    
    @patch('services.claude_executor.executor', None)
    def test_get_executor_creates_instance(self):
        """Test get_executor creates new instance when none exists."""
        executor = get_executor()
        assert executor is not None
        assert isinstance(executor, ClaudeExecutor)
        
    def test_get_executor_returns_same_instance(self):
        """Test get_executor returns same instance."""
        executor1 = get_executor()
        executor2 = get_executor()
        assert executor1 is executor2