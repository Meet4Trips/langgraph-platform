import asyncio
from agent.trip_planner import graph

async def main():
    # Example travel query
    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": "I want to plan a trip to Tokyo for 5 days in July. My budget is $3000."
            }
        ],
        "destination_info": {},
        "itinerary": [],
        "budget": {},
        "bookings": {},
        "weather": {},
        "pois": [],
        "restaurants": []
    }
    
    # Run the trip planner
    result = await graph.ainvoke(initial_state)
    
    # Print the result
    print("\nTrip Planner Response:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 