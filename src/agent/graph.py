from langgraph.prebuilt.chat_agent_executor import create_react_agent

from src.agent.configuration import Configuration
from langchain_core.runnables import RunnableConfig

from src.agent.tools import get_tools
from src.agent.prompts import ITINERARY_MARKDOWN_FORMAT, TRIP_PLANNER_WITH_TOOLS_PROMPT
from src.agent.utils import load_chat_model

async def create_trip_planner_graph(config: RunnableConfig):

    # Get name from config or use default
    configurable = config.get("configurable", {})

    # get values from configuration
    llm = configurable.get("model", "openai/gpt-4o-mini")
    selected_tools = configurable.get("selected_tools", ["search_weather", "search_flights", "search_hotels", "search_attractions", "search_restaurants"])
    system_prompt = configurable.get("system_prompt", TRIP_PLANNER_WITH_TOOLS_PROMPT)

    # if prompt contains ***itinerary_markdown_format***, replace it with ITINERARY_MARKDOWN_FORMAT
    if "***itinerary_markdown_format***" in system_prompt:
        system_prompt = system_prompt.replace("***itinerary_markdown_format***", ITINERARY_MARKDOWN_FORMAT)
    
    # specify the name for use in supervisor architecture
    name = configurable.get("name", "trip_planner")

    # Compile the builder into an executable graph
    # You can customize this by adding interrupt points for state updates
    graph = create_react_agent(
        model=load_chat_model(llm), 
        tools=get_tools(selected_tools),
        prompt=system_prompt, 
        config_schema=Configuration,
        name=name
    )

    return graph