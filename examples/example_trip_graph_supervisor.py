from langgraph_supervisor import create_supervisor

from agent.utils.configuration import Configuration
from prompt.prompts import TRIP_ASSISTANT_PROMPT
from agent.agents import (
    create_logistics_agent,
    create_poi_agent,
    create_research_agent,
    create_restaurant_finder,
)
from langchain_openai import ChatOpenAI

def create_trip_planner_graph_with_supervisor():

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    research_agent = create_research_agent()
    logistics_agent = create_logistics_agent()
    poi_recommender = create_poi_agent()
    restaurant_finder = create_restaurant_finder()
    
    # Create supervisor with basic configuration
    return create_supervisor(
            agents=[logistics_agent, restaurant_finder, poi_recommender, research_agent],
            model=llm,
            config_schema=Configuration,
            # parallel_tool_calls=True,
            # output_mode="last_message",
            include_agent_name=None,
            supervisor_name="trip_planner_supervisor",
            prompt=TRIP_ASSISTANT_PROMPT,
        ).compile()

# Create the graph instance
trip_planner_graph = create_trip_planner_graph_with_supervisor() 