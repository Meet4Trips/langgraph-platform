import getpass
import os
from typing import Any
from venv import logger
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt.chat_agent_executor import create_react_agent
from typing import Any
from src.agent.utils.configuration import Configuration
from src.agent.prompts import (
    RESEARCH_AGENT_PROMPT,
    RESTAURANT_FINDER_PROMPT,
    LOGISTICS_AGENT_PROMPT,
    POI_AGENT_PROMPT
)
from agent.tools import search_attractions, search_hotels, search_restaurants, search_flights

def create_research_agent() -> Any:
    """Creates a research agent using the ReAct pattern."""
    if not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")
    
    configuration = Configuration.from_context()

    web_search = TavilySearch(max_results=5, topic="general")
    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=[web_search],
        prompt=RESEARCH_AGENT_PROMPT,
        name="research_agent",
    )

def create_restaurant_finder() -> Any:
    """Creates a restaurant finder agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    logger.info(f"Restaurant Finder Configuration: {configuration.model}")

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=[search_restaurants],
        prompt=RESTAURANT_FINDER_PROMPT,
        name="restaurant_finder",
    )

def create_logistics_agent() -> Any:
    """Creates a logistics agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    logger.info(f"Logistics Configuration: {configuration.model}")

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=[search_hotels, search_flights],
        prompt=LOGISTICS_AGENT_PROMPT,
        name="logistics_agent",
    )

def create_poi_agent() -> Any:
    """Creates a POI agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=[search_attractions],
        prompt=POI_AGENT_PROMPT,
        name="poi_agent",
    )
