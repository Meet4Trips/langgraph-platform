from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_google_community import GooglePlacesTool
from typing import Literal
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry a function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator

@tool
def search_destinations(query: str) -> str:
    """Search for travel destinations and their information."""
    tavily = TavilySearch(max_results=3)
    return tavily.invoke(query)

@tool
def search_weather(location: str) -> str:
    """Get weather forecast for a location."""
    tavily = TavilySearch(max_results=3)
    return tavily.invoke(f"Weather in {location}")

@tool
@retry_on_failure(max_retries=3)
def search_flights(origin: str, destination: str, dates: str) -> str:
    """Search for flight options."""
    tavily = TavilySearch(max_results=3)
    return tavily.invoke(f"Flight options from {origin} to {destination} on {dates}")

@tool
@retry_on_failure(max_retries=3)
def search_hotels(
    location: str, 
    *,  # Force keyword arguments after this point
    dates: str = None, 
    budget: str = None, 
    rating: str = None, 
    accommodation_type: Literal['lodging', 'hotel', 'guest_house', 'bed_and_breakfast', 'resort'] = None
) -> str:
    """Search for hotel options.
    Args:
        location: The location to search for hotels in (required).
        dates: Optional dates for the stay (e.g., '2024-07-01 to 2024-07-05').
        budget: Optional budget filter.
        rating: Optional rating filter.
        accommodation_type: Optional type of accommodation to search for. Must be one of: 'lodging', 'hotel', 'guest_house', 'bed_and_breakfast', 'resort'.
    Returns:
        A string containing hotel details.
    """
    places = GooglePlacesTool()

    try:
        # Construct query with accommodation type and filters
        query = f"{location} {accommodation_type if accommodation_type else 'hotel'} {budget if budget else ''} {rating if rating else ''}"
        result = places.run(query)
        
        if not result:
            return f"No accommodations found in {location}" + (f" for dates {dates}" if dates else "")

        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # Extract relevant hotel information
            name = result.get('name', 'Unknown')
            rating = result.get('rating', 'No rating')
            address = result.get('formatted_address', 'No address')
            types = result.get('types', [])
            price_level = result.get('price_level', 'No price level')
            
            # Extract additional hotel-specific information
            website = result.get('website', 'No website')
            phone = result.get('formatted_phone_number', 'No phone')
            reviews = result.get('reviews', [])
            review_summary = ""
            if reviews:
                review_summary = f"\nRecent Reviews:\n" + "\n".join([
                    f"- {review.get('text', 'No text')} (Rating: {review.get('rating', 'N/A')})"
                    for review in reviews[:3]  # Show top 3 reviews
                ])
            
            return f"""
Hotel: {name}
Rating: {rating}
Address: {address}
Types: {', '.join(types)}
Price Level: {'$' * price_level if isinstance(price_level, int) else price_level}
Website: {website}
Phone: {phone}
Stay Dates: {dates}{review_summary}
"""
    except Exception as e:
        print(f"Error searching for {accommodation_type}: {str(e)}")
        return f"Error occurred while searching for accommodations in {location}"

@tool
def search_attractions(location: str, attraction_type: str = "tourist_attraction") -> str:
    """Search for points of interest and attractions.
    Args:
        location: The location to search for attractions in.
        attraction_type: Type of attraction to search for (default: tourist_attraction).
                       Options: tourist_attraction, museum, art_gallery, park, landmark, point_of_interest
    Returns:
        A list of attractions with their details.
    """
    places = GooglePlacesTool()
    try:
        # Search with the specified type
        query = f"{location} {attraction_type}"
        result = places.run(query)
        return result if result else f"No {attraction_type} found in {location}"
    except Exception as e:
        return f"Error searching for {attraction_type} in {location}: {str(e)}"

@tool
def search_restaurants(
    location: str, 
    cuisine: str = None, 
    budget: str = None, 
    rating: str = None, 
    place_type: Literal['restaurant', 'food', 'cafe', 'bakery', 'bar'] = None
) -> str:
    """Search for restaurants in a location.
    Args:
        location: The location to search for restaurants in.
        cuisine: Optional cuisine type to filter by (e.g., 'italian', 'japanese', 'indian').
        budget: Optional budget filter.
        rating: Optional rating filter.
        place_type: Type of establishment to search for. Must be one of: 'restaurant', 'food', 'cafe', 'bakery', 'bar'.
    Returns:
        A list of restaurants with their details.
    """
    places = GooglePlacesTool()

    try:
        # Construct query with cuisine if provided
        query = f"{location} {cuisine if cuisine else ''} {place_type} {budget if budget else ''} {rating if rating else ''}"
        result = places.run(query)
        
        if not result:
            return f"No restaurants found in {location}" + (f" for {cuisine} cuisine" if cuisine else "")
        
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # Extract relevant restaurant information
            name = result.get('name', 'Unknown')
            rating = result.get('rating', 'No rating')
            address = result.get('formatted_address', 'No address')
            types = result.get('types', [])
            price_level = result.get('price_level', 'No price level')
            
            return f"""
Restaurant: {name}
Rating: {rating}
Address: {address}
Types: {', '.join(types)}
Price Level: {'$' * price_level if isinstance(price_level, int) else price_level}
"""
    except Exception as e:
        print(f"Error searching for {place_type}: {str(e)}")
        return f"Error occurred while searching for restaurants in {location}"

# Tool collections for different agent types
COORDINATOR_TOOLS = []
DESTINATION_TOOLS = [search_destinations]
ITINERARY_TOOLS = [search_attractions]
BUDGET_TOOLS = [search_flights, search_hotels]
LOGISTICS_TOOLS = [search_flights, search_hotels]
POI_TOOLS = [search_attractions]
RESTAURANT_TOOLS = [search_restaurants]
WEATHER_TOOLS = [search_weather] 
ALL_TOOLS = [search_destinations, search_weather, search_flights, search_hotels, search_attractions, search_restaurants]