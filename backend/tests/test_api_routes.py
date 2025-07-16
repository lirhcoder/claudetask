import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app import create_app

class TestAPIRoutes:
    """Test API routes."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    @patch('routes.api.get_executor')
    def test_execute_claude(self, mock_get_executor, client):
        """Test execute Claude Code endpoint."""
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute.return_value = 'task-123'
        mock_get_executor.return_value = mock_executor
        
        # Test successful execution
        response = client.post('/api/execute', 
            json={
                'prompt': 'Create a hello world app',
                'project_path': '/tmp/test_project'
            }
        )
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['task_id'] == 'task-123'
        assert data['status'] == 'queued'
        
        # Test missing data
        response = client.post('/api/execute', json={})
        assert response.status_code == 400
        
        # Test missing prompt
        response = client.post('/api/execute', 
            json={'project_path': '/tmp/test'}
        )
        assert response.status_code == 400
    
    @patch('routes.api.Config')
    def test_list_projects(self, mock_config, client, tmp_path):
        """Test list projects endpoint."""
        # Create test projects
        projects_dir = tmp_path / 'projects'
        projects_dir.mkdir()
        (projects_dir / 'project1').mkdir()
        (projects_dir / 'project2').mkdir()
        
        mock_config.PROJECTS_DIR = projects_dir
        
        response = client.get('/api/projects')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['projects']) == 2
        assert any(p['name'] == 'project1' for p in data['projects'])
        assert any(p['name'] == 'project2' for p in data['projects'])
    
    @patch('routes.api.Config')
    def test_create_project(self, mock_config, client, tmp_path):
        """Test create project endpoint."""
        projects_dir = tmp_path / 'projects'
        projects_dir.mkdir()
        mock_config.PROJECTS_DIR = projects_dir
        
        # Test successful creation
        response = client.post('/api/projects', 
            json={'name': 'new_project', 'initialize_readme': True}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'new_project'
        
        # Check project was created
        assert (projects_dir / 'new_project').exists()
        assert (projects_dir / 'new_project' / 'README.md').exists()
        
        # Test duplicate project
        response = client.post('/api/projects', 
            json={'name': 'new_project'}
        )
        assert response.status_code == 409
        
        # Test missing name
        response = client.post('/api/projects', json={})
        assert response.status_code == 400
    
    @patch('routes.api.Config')
    def test_get_project_details(self, mock_config, client, tmp_path):
        """Test get project details endpoint."""
        projects_dir = tmp_path / 'projects'
        projects_dir.mkdir()
        project_dir = projects_dir / 'test_project'
        project_dir.mkdir()
        (project_dir / 'file1.py').write_text('print("hello")')
        (project_dir / 'subdir').mkdir()
        (project_dir / 'subdir' / 'file2.py').write_text('pass')
        
        mock_config.PROJECTS_DIR = projects_dir
        
        response = client.get('/api/projects/test_project')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['name'] == 'test_project'
        assert 'files' in data
        assert len(data['files']) > 0
        
        # Test non-existent project
        response = client.get('/api/projects/nonexistent')
        assert response.status_code == 404
    
    @patch('routes.api.get_executor')
    def test_list_tasks(self, mock_get_executor, client):
        """Test list tasks endpoint."""
        # Mock tasks
        mock_task1 = Mock()
        mock_task1.to_dict.return_value = {
            'id': 'task1',
            'created_at': '2024-01-01T10:00:00'
        }
        mock_task2 = Mock()
        mock_task2.to_dict.return_value = {
            'id': 'task2',
            'created_at': '2024-01-01T11:00:00'
        }
        
        mock_executor = Mock()
        mock_executor.get_all_tasks.return_value = [mock_task1, mock_task2]
        mock_get_executor.return_value = mock_executor
        
        response = client.get('/api/tasks')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['tasks']) == 2
        assert data['tasks'][0]['id'] == 'task2'  # Sorted by created_at desc
    
    @patch('routes.api.get_executor')
    def test_get_task(self, mock_get_executor, client):
        """Test get task details endpoint."""
        # Mock task
        mock_task = Mock()
        mock_task.to_dict.return_value = {
            'id': 'task-123',
            'status': 'completed'
        }
        
        mock_executor = Mock()
        mock_executor.get_task.return_value = mock_task
        mock_get_executor.return_value = mock_executor
        
        response = client.get('/api/tasks/task-123')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == 'task-123'
        assert data['status'] == 'completed'
        
        # Test non-existent task
        mock_executor.get_task.return_value = None
        response = client.get('/api/tasks/nonexistent')
        assert response.status_code == 404
    
    @patch('routes.api.get_executor')
    def test_cancel_task(self, mock_get_executor, client):
        """Test cancel task endpoint."""
        mock_executor = Mock()
        mock_executor.cancel_task.return_value = True
        mock_get_executor.return_value = mock_executor
        
        response = client.post('/api/tasks/task-123/cancel')
        assert response.status_code == 200
        
        # Test failed cancellation
        mock_executor.cancel_task.return_value = False
        response = client.post('/api/tasks/task-123/cancel')
        assert response.status_code == 400
    
    @patch('routes.api.Config')
    def test_upload_file(self, mock_config, client, tmp_path):
        """Test file upload endpoint."""
        projects_dir = tmp_path / 'projects'
        projects_dir.mkdir()
        project_dir = projects_dir / 'test_project'
        project_dir.mkdir()
        
        mock_config.PROJECTS_DIR = projects_dir
        mock_config.ALLOWED_EXTENSIONS = {'.py', '.txt'}
        
        # Create test file
        data = {
            'file': (b'print("hello")', 'test.py'),
            'project': 'test_project'
        }
        
        response = client.post('/api/files/upload', 
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        assert (project_dir / 'test.py').exists()
        
        # Test invalid file type
        data = {
            'file': (b'binary data', 'test.exe'),
            'project': 'test_project'
        }
        
        response = client.post('/api/files/upload', 
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
    
    @patch('routes.api.Config')
    def test_get_file_content(self, mock_config, client, tmp_path):
        """Test get file content endpoint."""
        projects_dir = tmp_path / 'projects'
        projects_dir.mkdir()
        project_dir = projects_dir / 'test_project'
        project_dir.mkdir()
        test_file = project_dir / 'test.py'
        test_file.write_text('print("hello world")')
        
        mock_config.PROJECTS_DIR = projects_dir
        
        response = client.get('/api/files/test_project/test.py')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['content'] == 'print("hello world")'
        assert data['path'] == 'test_project/test.py'
        
        # Test download mode
        response = client.get('/api/files/test_project/test.py?download=true')
        assert response.status_code == 200
        assert response.headers['Content-Disposition'].startswith('attachment')
        
        # Test non-existent file
        response = client.get('/api/files/test_project/nonexistent.py')
        assert response.status_code == 404
        
        # Test directory instead of file
        response = client.get('/api/files/test_project')
        assert response.status_code == 400