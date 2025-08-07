import pytest
from dotenv import load_dotenv
from langgraph_sdk import get_client

# Load environment variables for tests
load_dotenv()


# Integration test (requires running langgraph server)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_assistant_integration():
    """Integration test with real langgraph server (requires server to be running)"""
    import os
    
    try:
        client = get_client(url="http://localhost:2024")
        
        # Test basic connectivity by listing assistants
        print("Attempting to connect to LangGraph server...")
        assistants = await client.assistants.search(headers={"name": "trip_planner:gpt-4o-mini"})
        print(f"""Found {len(assistants)} assistants""")
        
    except Exception as e:
        print(f"Error connecting to server: {e}")
        pytest.skip(f"Integration test skipped: {e}")