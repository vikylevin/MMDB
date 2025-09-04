# Unit Testing Documentation for MMDB Project

## What are Unit Tests?

Unit tests are automated tests that verify individual components (functions, methods, classes) of your application work correctly in isolation. They are essential for:

- **Quality Assurance**: Ensure code works as expected
- **Regression Prevention**: Catch bugs when code changes
- **Documentation**: Serve as examples of how code should be used
- **Refactoring Safety**: Allow confident code improvements

## Test Structure

Our project includes three main test modules:

### 1. `test_tmdb.py` - TMDB API Functions
Tests the external API integration functions:
- `fetch_movie_details()` - Fetching individual movie data
- `search_movies()` - Movie search functionality
- `get_popular_movies()` - Popular movies with filters
- `get_upcoming_movies()` - Upcoming movies with date filtering
- Error handling for API failures

### 2. `test_routes.py` - Flask API Endpoints
Tests the web API endpoints:
- Movie endpoints (`/api/movie/*`)
- User authentication (`/api/auth/*`)
- Rating and review functionality
- Authorization and access control

### 3. `test_models.py` - Database Models
Tests the database layer:
- User model and password hashing
- Movie, Rating, Review models
- Database relationships and constraints
- Data validation

## Running the Tests

### Method 1: Run All Tests
```bash
cd backend
python run_tests.py
```

### Method 2: Run Specific Test File
```bash
python run_tests.py tmdb
python run_tests.py routes
python run_tests.py models
```

### Method 3: Using unittest directly
```bash
python -m unittest test_tmdb.py
python -m unittest test_routes.py
python -m unittest test_models.py
```

### Method 4: Using pytest (if installed)
```bash
pytest test_*.py -v
pytest test_tmdb.py::TestTMDBFunctions::test_fetch_movie_details_success -v
```

## Test Coverage

To check test coverage:
```bash
pip install coverage
coverage run -m unittest discover
coverage report
coverage html  # Generates HTML report
```

## Example Test Output

```
MMDB PROJECT UNIT TEST RESULTS
======================================================================

test_fetch_movie_details_success (test_tmdb.TestTMDBFunctions) ... ok
test_search_movies_success (test_tmdb.TestTMDBFunctions) ... ok
test_user_registration (test_routes.TestUserAPI) ... ok
test_user_model_creation (test_models.TestDatabaseModels) ... ok

----------------------------------------------------------------------
Ran 20 tests in 2.341s

OK

TEST SUMMARY:
Tests run: 20
Failures: 0
Errors: 0
Skipped: 0
```

## Writing New Tests

### Test Structure
```python
import unittest
from unittest.mock import patch, Mock

class TestYourFeature(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        pass
    
    def tearDown(self):
        """Clean up after each test"""
        pass
    
    def test_your_function_success(self):
        """Test successful case"""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_your_function_error(self):
        """Test error case"""
        pass
```

### Mocking External Dependencies
```python
@patch('module.external_function')
def test_with_mock(self, mock_external):
    mock_external.return_value = {'status': 'success'}
    result = your_function()
    self.assertEqual(result['status'], 'success')
```

## Best Practices

1. **Test Naming**: Use descriptive names like `test_function_name_expected_behavior`
2. **AAA Pattern**: Arrange, Act, Assert
3. **Mock External Services**: Don't make real API calls in tests
4. **Test Edge Cases**: Empty inputs, invalid data, error conditions
5. **Keep Tests Independent**: Each test should be able to run alone
6. **Test One Thing**: Each test should verify one specific behavior

## Integration with CI/CD

Add to your deployment pipeline:
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "All tests passed, proceeding with deployment"
else
    echo "Tests failed, stopping deployment"
    exit 1
fi
```

## Common Test Scenarios for MMDB

### API Testing
- Valid movie ID returns correct data
- Invalid movie ID returns error
- API timeout handling
- Authentication required endpoints

### Database Testing
- User registration and login
- Movie rating and review creation
- Data validation and constraints
- Relationship integrity

### Business Logic Testing
- Rating calculation
- Search filtering
- User permissions
- Data formatting

This testing framework ensures the MMDB application is reliable, maintainable, and ready for production deployment.
