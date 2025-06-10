from langgraph_supervisor import create_supervisor

from src.agent.trip_agents import (
    create_logistics_agent,
    create_poi_agent,
    create_research_agent,
    create_restaurant_finder,
    create_assembler_agent
)
from langchain_openai import ChatOpenAI

def create_trip_planner_graph_with_supervisor():
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4")

    research_agent = create_research_agent(llm)
    logistics_agent = create_logistics_agent(llm)
    restaurant_finder = create_restaurant_finder(llm)
    poi_agent = create_poi_agent(llm)
    assembler_agent = create_assembler_agent(llm)
    
    # Create supervisor with basic configuration
    return create_supervisor(
            agents=[logistics_agent, restaurant_finder, poi_agent, assembler_agent, research_agent],
            model=llm,
            supervisor_name="trip_planner_supervisor",
            parallel_tool_calls=True,
            prompt="""You are a travel planning supervisor. Your role is to:
1. Coordinate between different specialized agents
2. Ensure all aspects of the trip are covered
3. Make decisions about which agent should handle each task
4. Maintain context and continuity in the planning process
5. Provide clear and organized responses to the user
6. Use the assembler_agent to create a final, well-formatted markdown document which includes all the information from the other agents
7. Please DO NOT repeat the same information from the other agents in the final document

IMPORTANT GUIDELINES:
- Always ensure each agent's response is properly formatted and complete
- If an agent fails to provide a valid response, retry the request
- Never return empty or malformed responses
- Always validate the final output before sending it to the user
- If you encounter any errors, provide a clear error message and suggest next steps""",
        ).compile()

# Create the graph instance
trip_planner_graph = create_trip_planner_graph_with_supervisor() 