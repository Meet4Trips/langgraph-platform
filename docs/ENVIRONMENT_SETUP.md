# Environment Variable Setup and Testing Guide

## Summary

This guide explains how to properly set up environment variables using `.env` files and how to test your Python scripts.

## Main Function Pattern

### ✅ Correct Pattern

```python
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def main():
    try:
        result = await your_async_function()
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### ❌ Common Mistakes

```python
# Wrong: Calling async function without await
if __name__ == "__main__":
    print(your_async_function())  # This won't work!

# Wrong: No error handling
if __name__ == "__main__":
    result = await your_async_function()  # Syntax error!
```

## Environment Variable Setup

### 1. Install python-dotenv

```bash
pip install python-dotenv
```

### 2. Create .env file

```bash
# .env
GPLACES_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Load in your Python script

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
api_key = os.getenv("GPLACES_API_KEY")
```

## Testing Approaches

### 1. Direct Execution Testing

```bash
# Test the main function directly
python src/test_google_places.py
```

### 2. Unit Testing with pytest

```bash
# Run unit tests
python -m pytest tests/test_google_places.py -v
```

### 3. Integration Testing

```bash
# Run integration tests (requires real API key)
python -m pytest tests/test_google_places.py::test_text_search_restaurants_integration -v
```

### 4. Manual Testing

```python
# test_examples.py
import asyncio
from dotenv import load_dotenv
from src.test_google_places import text_search_restaurants

load_dotenv()

async def test_function():
    result = await text_search_restaurants("Barcelona", "spanish")
    print(result)

asyncio.run(test_function())
```

## File Structure

```
langgraph-platform/
├── .env                          # Environment variables
├── src/
│   └── test_google_places.py    # Main script
├── tests/
│   └── test_google_places.py    # Unit tests
├── test_examples.py              # Manual testing examples
├── env_examples.py               # Environment variable examples
└── ENVIRONMENT_SETUP.md          # This guide
```

## Best Practices

### 1. Always use `load_dotenv()` at the top of your script

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Handle async functions properly

```python
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 3. Add error handling

```python
async def main():
    try:
        result = await your_function()
        print(result)
    except Exception as e:
        print(f"Error: {e}")
```

### 4. Validate environment variables

```python
def validate_env():
    required_vars = ["GPLACES_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing: {missing}")
```

### 5. Use default values when appropriate

```python
api_key = os.getenv("GPLACES_API_KEY", "default_key")
```

## Testing Commands

```bash
# Activate virtual environment
source ~/.venvs/langgraph-env/bin/activate

# Run main script
python src/test_google_places.py

# Run unit tests
python -m pytest tests/test_google_places.py -v

# Run examples
python test_examples.py
python env_examples.py
```

## Troubleshooting

### Issue: "No module named dotenv"

```bash
pip install python-dotenv
```

### Issue: "API key not found"

- Check that `.env` file exists
- Verify `load_dotenv()` is called
- Check variable name spelling

### Issue: "Async function not awaited"

- Use `asyncio.run()` for async functions
- Don't call async functions directly in `if __name__ == "__main__"`

### Issue: Tests failing

- Make sure `load_dotenv()` is called in test files
- Check that mocks are using correct class names
- Verify API keys are set for integration tests
