import pytest
from app import create_app, db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with testing configuration
    app = create_app('testing')
    
    # Create a test context
    with app.app_context():
        # Create tables
        db.create_all()
        
        yield app
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()
