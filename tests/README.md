# NASA MCP Server Tests

This directory contains comprehensive unit tests for the NASA MCP Server tools.

## File Structure

```
tests/
├── README.md           # This file
├── __init__.py         # Package initialization
├── pytest.ini         # Pytest configuration
├── run_tests.py        # Test runner script
├── setup_tests.py      # Test environment setup
└── test_server.py      # Main test file
```

## Test Structure

### Test Classes

1. **TestAPODTool** - Tests for Astronomy Picture of the Day tool

   - Default parameters
   - Specific date requests
   - Date range requests
   - Random count requests

2. **TestMarsImageTool** - Tests for Mars Rover Images tool

   - Default parameters (sol=1000)
   - Earth date filtering
   - Sol (Martian day) filtering
   - Camera type filtering
   - Combined parameter tests

3. **TestNEOFeedTool** - Tests for Near Earth Objects tool

   - Default parameters (next 7 days)
   - Custom date ranges
   - Custom limit per day

4. **TestEarthImageTool** - Tests for Earth Images (EPIC) tool

   - Default parameters (natural color, latest)
   - Specific date requests
   - Different image types (natural, enhanced, aerosol, cloud)
   - Custom image limits

5. **TestGIBSImageTool** - Tests for GIBS Satellite Imagery tool

   - Default parameters (Terra true color, world view)
   - Different satellite layers
   - Custom bounding boxes
   - Custom image dimensions
   - Specific dates

6. **TestGIBSLayersTool** - Tests for GIBS Layers Information tool

   - Layer information retrieval

7. **TestImageAnalyzeTool** - Tests for Image Analysis tool

   - URL image fetching and analysis
   - Different image formats
   - NASA-specific URLs

8. **TestIntegrationScenarios** - Integration tests
   - APOD + Image Analysis workflow
   - Real-world usage scenarios

## Running Tests

### Prerequisites

First, install the test dependencies:

```bash
python tests/setup_tests.py
```

Or manually install:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Option 1: Using the simple test runner (from project root)
python test.py

# Option 2: Using pytest directly (from project root)
python -m pytest tests/

# Option 3: Using the test runner (from project root)
python tests/run_tests.py

# Option 4: Using the test runner from tests directory
cd tests
python run_tests.py

# With verbose output
python test.py -v
# or
python tests/run_tests.py -v
```

### Run Specific Tests

```bash
# Run tests for a specific tool (from project root)
python -m pytest tests/test_server.py::TestAPODTool

# Run a specific test method (from project root)
python -m pytest tests/test_server.py::TestAPODTool::test_get_apod_default

# Run tests with pattern matching (from project root)
python -m pytest tests/ -k "apod"
```

### Test Configuration

The tests use `tests/pytest.ini` for configuration:

- Async tests are automatically handled
- Short traceback format for cleaner output
- Warnings are filtered for cleaner output

## Test Features

### Mocking

All tests use mocking to avoid making actual API calls:

- `unittest.mock.patch` for API function mocking
- `AsyncMock` for async function mocking
- Consistent mock return values for predictable testing

### Async Support

Tests use `pytest-asyncio` for async/await support:

- `@pytest.mark.asyncio` decorator for async tests
- Proper async context handling
- Async mock support

### Coverage

The tests cover:

- All 7 MCP tools
- Default parameter behavior
- Custom parameter combinations
- Error handling scenarios
- Integration workflows

## Test Data

Tests use realistic parameter values:

- Valid date formats (YYYY-MM-DD)
- Valid camera types for Mars rover
- Valid image types for Earth images
- Valid bounding boxes for GIBS imagery
- Valid URLs for image analysis

## Environment Variables

Tests run independently of environment variables:

- API keys are mocked
- No real API calls are made
- Consistent behavior across environments

## Extending Tests

To add new tests:

1. Create a new test class for new tools
2. Use the existing pattern with `@pytest.mark.asyncio`
3. Mock the corresponding API function
4. Test default and custom parameters
5. Add integration scenarios if needed

Example:

```python
class TestNewTool:
    @pytest.mark.asyncio
    async def test_new_tool_default(self):
        with patch('nasa_mcp.nasa_api.new_tool_definition') as mock_api:
            mock_api.return_value = "Mock result"
            result = await new_tool()
            assert result == "Mock result"
            mock_api.assert_called_once_with()
```
