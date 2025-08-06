from dotenv import load_dotenv
from examples.example_trip_graph_supervisor import trip_planner_graph, TripState

def test_trip_planner():
    # Load environment variables
    load_dotenv()
    
    # Initialize the state
    initial_state = TripState(
        messages=[],  # Will be populated by the system
        destination_info={},
        itinerary=[],
        budget={},
        bookings={},
        weather={},
        pois=[],
        restaurants=[]
    )
    
    # Create a test query
    test_query = "I want to plan a 5-day trip to Tokyo in July 2024. I'm interested in culture and food."
    
    # Add the user's query to messages
    initial_state["messages"].append({
        "role": "user",
        "content": test_query
    })
    
    # Run the graph
    try:
        result = trip_planner_graph.invoke(initial_state)
        
        # Print the final state
        print("\nFinal Trip Plan:")
        print("=" * 50)
        
        if result.get("destination_info"):
            print("\nDestination Information:")
            print(result["destination_info"])
        
        if result.get("itinerary"):
            print("\nItinerary:")
            for day in result["itinerary"]:
                print(f"\nDay {day.get('day', 'N/A')}:")
                print(f"Activities: {day.get('activities', [])}")
        
        if result.get("budget"):
            print("\nBudget Estimate:")
            print(result["budget"])
        
        if result.get("bookings"):
            print("\nBookings:")
            print(result["bookings"])
        
        if result.get("weather"):
            print("\nWeather Information:")
            print(result["weather"])
        
        if result.get("pois"):
            print("\nPoints of Interest:")
            for poi in result["pois"]:
                print(f"\n- {poi.get('name', 'N/A')}")
                print(f"  Description: {poi.get('description', 'N/A')}")
        
        if result.get("restaurants"):
            print("\nRestaurant Recommendations:")
            for restaurant in result["restaurants"]:
                print(f"\n- {restaurant.get('name', 'N/A')}")
                print(f"  Cuisine: {restaurant.get('cuisine', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"Error during trip planning: {str(e)}")
        return False

if __name__ == "__main__":
    test_trip_planner() 