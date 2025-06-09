import os
from dotenv import load_dotenv
from src.agent.trip_graph import trip_planner_graph, TripState

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required API keys
    required_keys = [
        "OPENAI_API_KEY",
        "TAVILY_API_KEY",
        "GOOGLE_PLACES_API_KEY"
    ]
    
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        print("Error: Missing required API keys:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add these keys to your .env file")
        return
    
    # Initialize the state
    initial_state = TripState(
        messages=[],
        destination_info={},
        itinerary=[],
        budget={},
        bookings={},
        weather={},
        pois=[],
        restaurants=[]
    )
    
    # Get user input
    print("\nWelcome to the Trip Planner!")
    print("Please describe your trip requirements:")
    user_query = input("> ")
    
    # Add the user's query to messages
    initial_state["messages"].append({
        "role": "user",
        "content": user_query
    })
    
    # Run the graph
    try:
        print("\nPlanning your trip...")
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
        
    except Exception as e:
        print(f"Error during trip planning: {str(e)}")

if __name__ == "__main__":
    main() 