from typing import Dict, List, Any, TypedDict, Annotated
from langgraph.graph.message import add_messages

class TripState(TypedDict):
    messages: Annotated[list, add_messages]
    destination_info: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    budget: Dict[str, float]
    bookings: Dict[str, Any]
    weather: Dict[str, Any]
    pois: List[Dict[str, Any]]
    restaurants: List[Dict[str, Any]] 
    current_agent: str