import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from dotenv import load_dotenv
from src.lib.google_places_client import text_search_restaurants

# Load environment variables for tests
load_dotenv()


class TestGooglePlaces:
    
    @pytest.mark.asyncio
    async def test_text_search_restaurants_success(self):
        """Test successful restaurant search"""
        # Mock the Google Places client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_client.search_text.return_value = mock_response
        
        with patch('src.test_google_places.places_v1.PlacesAsyncClient', return_value=mock_client):
            result = await text_search_restaurants("Barcelona", "spanish")
            
            # Verify the client was called correctly
            mock_client.search_text.assert_called_once()
            call_args = mock_client.search_text.call_args
            assert "spanish in Barcelona" in str(call_args[1]['request'].text_query)
            assert call_args[1]['request'].min_rating == 4.0
    
    @pytest.mark.asyncio
    async def test_text_search_restaurants_no_food_type(self):
        """Test restaurant search without specifying food type"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response = MagicMock()
        mock_client.search_text.return_value = mock_response
        
        with patch('src.test_google_places.places_v1.PlacesAsyncClient', return_value=mock_client):
            result = await text_search_restaurants("Barcelona")
            
            call_args = mock_client.search_text.call_args
            assert "restaurant in Barcelona" in str(call_args[1]['request'].text_query)
    
    @pytest.mark.asyncio
    async def test_text_search_restaurants_api_error(self):
        """Test handling of API errors"""
        mock_client = AsyncMock()
        mock_client.search_text.side_effect = Exception("API Error")
        
        with patch('src.test_google_places.places_v1.PlacesAsyncClient', return_value=mock_client):
            with pytest.raises(Exception, match="API Error"):
                await text_search_restaurants("Barcelona", "spanish")


# Integration test (requires real API key)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_text_search_restaurants_integration():
    """Integration test with real API (requires GPLACES_API_KEY env var)"""
    import os
    if not os.getenv("GPLACES_API_KEY"):
        pytest.skip("GPLACES_API_KEY not set")
    
    result = await text_search_restaurants("Barcelona", "spanish")
    assert result is not None
    # Add more specific assertions based on expected response structure 