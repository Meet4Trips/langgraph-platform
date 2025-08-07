from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing import Literal, Callable, Any

from src.agent.lib.google_places_client import text_search_attractions, text_search_hotels, text_search_restaurants 

@tool
def search_weather(location: str, date: str = None) -> str:
    """Search for current weather information in a specific location on a specific date."""
    tavily = TavilySearch(max_results=3)
    if date:
        return tavily.invoke(f"Weather in {location} on {date}")
    else:
        return tavily.invoke(f"Weather in {location}")

@tool
def search_flights(origin: str, destination: str, dates: str) -> str:
    """Search for flight options between two locations on specific dates."""
    tavily = TavilySearch(max_results=3)
    if dates:
        return tavily.invoke(f"Flight options from {origin} to {destination} on {dates}")
    else:
        return tavily.invoke(f"Flight options from {origin} to {destination}")

@tool
async def search_hotels(
    location: str, 
    accommodation_type: Literal['lodging', 'hotel', 'guest_house', 'bed_and_breakfast', 'resort'] = None
) -> str:
    """Search for hotels and accommodation options in a specific location."""
    return await text_search_hotels(location, accommodation_type)

@tool
async def search_attractions(location: str, attraction_type: str = "tourist_attraction") -> str:
    """Search for tourist attractions and points of interest in a specific location."""
    return await text_search_attractions(location, attraction_type)

@tool
async def search_restaurants(
    location: str, 
    cuisine: str = None
) -> str:
    """Search for restaurants and dining options in a specific location."""
    return await text_search_restaurants(location, cuisine)

def get_tools(selected_tools: list[str]) -> list[Callable[..., Any]]:
    """Convert a list of tool names to actual tool functions."""
    tools = []
    for tool in selected_tools:
        if tool == "search_weather":
            tools.append(search_weather)
        elif tool == "search_flights":
            tools.append(search_flights)
        elif tool == "search_hotels":
            tools.append(search_hotels)
        elif tool == "search_attractions":
            tools.append(search_attractions)
        elif tool == "search_restaurants":
            tools.append(search_restaurants)
        else:
            # Log unknown tool for debugging
            print(f"Warning: Unknown tool '{tool}' requested, skipping...")
    
    return tools