import pytest
from app import create_app, socketio

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()

@pytest.fixture
def socket_client(app, client):
    """Create a test Socket.IO client."""
    return socketio.test_client(app, flask_test_client=client)

def test_app_creation(app):
    """Test that the app is created with correct configuration."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['DEBUG'] is True
    
def test_config_loading():
    """Test different configuration environments."""
    dev_app = create_app('development')
    assert dev_app.config['DEBUG'] is True
    assert dev_app.config['TESTING'] is False
    
    prod_app = create_app('production')
    assert prod_app.config['DEBUG'] is False
    assert prod_app.config['TESTING'] is False
    
def test_cors_configuration(app):
    """Test CORS is properly configured."""
    assert 'CORS_ORIGINS' in app.config
    assert isinstance(app.config['CORS_ORIGINS'], list)