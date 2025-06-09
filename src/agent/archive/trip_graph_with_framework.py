from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, StateGraph
from langgraph_supervisor import create_supervisor

from agent.trip_tools import ALL_TOOLS
from agent.archive.trip_types import TripState
from src.agent.trip_agents import (
    CoordinatorAgent,
    DestinationAnalyzer,
    DynamicToolNode,
    ItineraryPlanner,
    BudgetEstimator,
    LogisticsAgent,
    POIRecommender,
    RestaurantFinder,
    WeatherAgent,
    TripAssembler,
    create_logistics_agent,
    create_research_agent,
    create_restaurant_finder
)
from langchain_openai import ChatOpenAI

def create_trip_planner_graph():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4.1")
    
    # Initialize agents
    coordinator = CoordinatorAgent(llm)
    destination_analyzer = DestinationAnalyzer(llm)
    itinerary_planner = ItineraryPlanner(llm)
    budget_estimator = BudgetEstimator(llm)
    logistics_agent = LogisticsAgent(llm)
    poi_recommender = POIRecommender(llm)
    restaurant_finder = RestaurantFinder(llm)
    weather_agent = WeatherAgent(llm)
    trip_assembler = TripAssembler(llm)
    research_agent = create_research_agent(llm)
    
    # Define the graph
    graph = StateGraph(TripState)
    
    # Add nodes
    # graph.add_node("coordinator", coordinator)
    # graph.add_node("destination_analyzer", destination_analyzer)
    # graph.add_node("itinerary_planner", itinerary_planner)
    # graph.add_node("budget_estimator", budget_estimator)
    graph.add_node("logistics_agent", logistics_agent)
    # graph.add_node("poi_recommender", poi_recommender)
    graph.add_node("restaurant_finder", restaurant_finder)
    # graph.add_node("weather_agent", weather_agent)
    # graph.add_node("trip_assembler", trip_assembler)
    graph.add_node("research_agent", research_agent)
    tool_node = DynamicToolNode(ALL_TOOLS)
    graph.add_node("tools", tool_node)
    
    # Add edges
    graph.add_edge(START, "logistics_agent")
    
    graph.add_edge("logistics_agent", END)
     
    # Add conditional edges from coordinator
    # def route_from_coordinator(state: TripState) -> str:
    #     """Route from coordinator to appropriate agent based on current state."""
    #     if not state.get("destination_info"):
    #         return "destination_analyzer"
    #     elif not state.get("itinerary"):
    #         return "itinerary_planner"
    #     elif not state.get("budget"):
    #         return "budget_estimator"
    #     elif not state.get("bookings"):
    #         return "logistics_agent"
    #     elif not state.get("pois"):
    #         return "poi_recommender"
    #     elif not state.get("restaurants"):
    #         return "restaurant_finder"
    #     elif not state.get("weather"):
    #         return "weather_agent"
    #     else:
    #         return "trip_assembler"
    
    # graph.add_conditional_edges(
    #     "coordinator",
    #     route_from_coordinator,
    #     {
    #         "destination_analyzer": "destination_analyzer",
    #         "itinerary_planner": "itinerary_planner",
    #         "budget_estimator": "budget_estimator",
    #         "logistics_agent": "logistics_agent",
    #         "poi_recommender": "poi_recommender",
    #         "restaurant_finder": "restaurant_finder",
    #         "weather_agent": "weather_agent",
    #         "trip_assembler": "trip_assembler",
    #     }
    # )
    
    # Add edges back to coordinator
    #graph.add_edge("destination_analyzer", "coordinator")
    #graph.add_edge("itinerary_planner", "coordinator")
    #graph.add_edge("budget_estimator", "coordinator")
    #graph.add_edge("logistics_agent", "coordinator")
    #graph.add_edge("poi_recommender", "coordinator")
    #graph.add_edge("restaurant_finder", "coordinator")
    #graph.add_edge("weather_agent", "coordinator")
    
    # Add edge from trip assembler to end
    #graph.add_edge("trip_assembler", END)

    def create_route_tools(agent_name: str):
        """
        Create a route_tools function for a specific agent.
        Args:
            agent_name: The name of the agent that will be using the tools
        """
        def route_tools(state: TripState):
            """
            Route to the ToolNode if the last message has tool calls.
            Otherwise, route to the end.
            """
            if isinstance(state, list):
                ai_message = state[-1]
            elif messages := state.get("messages", []):
                ai_message = messages[-1]
            else:
                raise ValueError(f"No messages found in input state to tool_edge: {state}")
                
            if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                return "tools"
            return END
        
        return route_tools
    
    # Add conditional edges for each agent
    graph.add_conditional_edges(
        "logistics_agent",
        create_route_tools("logistics_agent"),
        {
            "tools": "tools", END: END
        },
    )
    
    # Example of how to add for other agents (uncomment as needed):
    # graph.add_conditional_edges(
    #     "coordinator",
    #     create_route_tools("CoordinatorAgent"),
    #     {
    #         "tools": "tools", END: END
    #     },
    # )
    # graph.add_conditional_edges(
    #     "destination_analyzer",
    #     create_route_tools("DestinationAnalyzer"),
    #     {
    #         "tools": "tools", END: END
    #     },
    # )
    
    # Compile the graph
    return graph.compile(name="Trip Planner Graph")

# Create the graph instance
trip_planner_graph = create_trip_planner_graph() 