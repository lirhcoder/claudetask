# Unit Tests for ClaudeTask Backend

This directory contains unit tests for the ClaudeTask backend application.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_repository.py` - Tests for Repository model and manager
- `test_dashboard_api.py` - Tests for Dashboard API endpoints
- `test_auth.py` - Tests for authentication functionality

## Running Tests

### With pytest (recommended):
```bash
cd backend
python run_tests.py
```

### Simple test runner (no dependencies):
```bash
cd backend
python simple_test_runner.py
```

## Key Test Cases

1. **Repository Model Tests**
   - Verifies Repository objects don't have a 'get' method
   - Tests to_dict() conversion
   - Tests repository creation and listing

2. **Dashboard API Tests**  
   - Tests authentication requirements
   - Tests empty data responses
   - Tests repository sorting logic
   - Performance tests with multiple repositories

3. **Authentication Tests**
   - Login/logout functionality
   - Password validation
   - Session management
   - User creation and lookup
