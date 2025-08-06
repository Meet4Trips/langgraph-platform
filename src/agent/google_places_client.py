import os
from typing import Optional, List
from dotenv import load_dotenv
from google.maps import places_v1

# Load environment variables from .env file
load_dotenv()

async def _text_search_places(
    location: str, 
    category: str, 
    subcategory: Optional[str] = None,
    min_rating: float = 4.0
) -> List[places_v1.Place]:
    """
    Generic text search function for places using Google Places API.
    
    Args:
        location: The location to search in
        category: The main category (e.g., 'restaurants', 'hotels', 'attractions')
        subcategory: Optional subcategory (e.g., 'italian' for restaurants, 'museum' for attractions)
        min_rating: Minimum rating filter (default: 4.0)
    
    Returns:
        List of places matching the search criteria
    """
    # Build search query
    if subcategory:
        search_query = f"{subcategory} {category} in {location}"
    else:
        search_query = f"{category} in {location}"
    
    client = places_v1.PlacesAsyncClient(
        client_options={"api_key": os.getenv("GPLACES_API_KEY")}
    )
    
    # Create the search request
    request = places_v1.SearchTextRequest(
        text_query=search_query,
        min_rating=min_rating,
    )

    # Set the field mask
    field_mask = "places.formattedAddress,places.displayName,places.id,places.location,places.googleMapsUri"
    
    # Send the request
    response = await client.search_text(request=request, metadata=[("x-goog-fieldmask", field_mask)])
    return response.places

async def text_search_restaurants(location: str, food_type: Optional[str] = None) -> List[places_v1.Place]:
    """
    Search for restaurants in a specific location.
    
    Args:
        location: The location to search in
        food_type: Optional food type/cuisine (e.g., 'italian', 'chinese')
    
    Returns:
        List of restaurant places
    """
    return await _text_search_places(location, "restaurants", food_type)

async def text_search_hotels(location: str, hotel_type: Optional[str] = None) -> List[places_v1.Place]:
    """
    Search for hotels in a specific location.
    
    Args:
        location: The location to search in
        hotel_type: Optional hotel type (e.g., 'luxury', 'budget', 'boutique')
    
    Returns:
        List of hotel places
    """
    return await _text_search_places(location, "hotels", hotel_type)

async def text_search_attractions(location: str, attraction_type: Optional[str] = None) -> List[places_v1.Place]:
    """
    Search for attractions/points of interest in a specific location.
    
    Args:
        location: The location to search in
        attraction_type: Optional attraction type (e.g., 'museum', 'amusement park', 'landmark')
    
    Returns:
        List of attraction places
    """
    return await _text_search_places(location, "attractions", attraction_type)

# Convenience functions for specific attraction types
async def text_search_museums(location: str) -> List[places_v1.Place]:
    """Search for museums in a specific location."""
    return await _text_search_places(location, "attractions", "museum")

async def text_search_landmarks(location: str) -> List[places_v1.Place]:
    """Search for landmarks in a specific location."""
    return await _text_search_places(location, "attractions", "landmark")

async def text_search_amusement_parks(location: str) -> List[places_v1.Place]:
    """Search for amusement parks in a specific location."""
    return await _text_search_places(location, "attractions", "amusement park")