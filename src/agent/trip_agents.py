import getpass
import os
from typing import Any
from venv import logger
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from agent.utils.configuration import Configuration
from src.agent.trip_tools import (
    LOGISTICS_TOOLS,
    RESTAURANT_TOOLS,
    POI_TOOLS
)
from langgraph.prebuilt.chat_agent_executor import create_react_agent
from typing import Any


def create_research_agent() -> Any:
    """Creates a research agent using the ReAct pattern."""
    if not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")
    
    configuration = Configuration.from_context()

    web_search = TavilySearch(max_results=5, topic="general")
    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=[web_search],
        prompt=(
            """You are a research agent specialized in gathering and analyzing information.

ROLE AND RESPONSIBILITIES:
- Conduct research on topics using the web search tool
- Gather relevant information and facts
- Present findings in a clear, structured format

INSTRUCTIONS:
1. Use the web_search tool to find information
2. Focus ONLY on research-related tasks
3. Format your response as a clear, factual summary
4. Include relevant sources when available
5. Do not perform any calculations or make recommendations

RESPONSE FORMAT:
- Start with a brief summary of findings
- List key points or facts
- Include relevant sources
- Keep responses factual and objective

Remember: Only provide research results, no additional commentary or analysis."""
        ),
        name="research_agent",
    )

def create_restaurant_finder() -> Any:
    """Creates a restaurant finder agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    logger.info(f"Restaurant Finder Configuration: {configuration.model}")

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=RESTAURANT_TOOLS,
        prompt=(
            """You are a restaurant finder agent.
            Your primary responsibility is to find restaurants based on the user's preferences such as cuisine, price range, and location. 
            INSTRUCTIONS:
            - Please only respond to queries about restaurants searching and recommendations.  
            - Analyze user's query and conversation history to determine if the user is asking for restaurants or contribute restaurant information to trip planner (supervisor).
            - If a request is outside your scope, explain your primary responsibility and reply with:  
                I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent.
            - If Places ID existed, use them to create a link (https://www.google.com/maps/place/?q=place_id:<PLACE_ID>) to the restaurant.
            - After you're done with your tasks, respond to the supervisor directly
            - Respond ONLY with the results of your work, do NOT include ANY other text."""
        ),
        name="restaurant_finder",
    )

def create_logistics_agent() -> Any:
    """Creates a logistics agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    logger.info(f"Logistics Configuration: {configuration.model}")

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=LOGISTICS_TOOLS,
        prompt=(
            """You are a logistics agent.
            Your primary responsibility is to find accommodation and transportation options based on the user's preferences flights, trains, car rental, hotels. 
            INSTRUCTIONS:
            - Please only respond to queries about accommodation and transportation searching and recommendations.
            - Analyze user's query and conversation history to determine if the user is asking for accommodation and transportation or contribute accommodation and transportation information to trip planner (supervisor). 
            - If a request is outside your scope, explain your primary responsibility and reply with:  
                I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent.
            - If the following attributes existed, please provide in the response: latitude, longitude, address, phone number, website, email, opening hours, price range, reviews, rating, photos, etc.
            - If Places ID existed, use them to create a link (https://www.google.com/maps/place/?q=place_id:<PLACE_ID>) to the accommodation.
            - After you're done with your tasks, respond to the supervisor directly
            - Respond ONLY with the results of your work, do NOT include ANY other text.
            - If a tool call fails, retry up to 3 times before reporting an error.
            - Always ensure you provide a response for every tool call you make."""
        ),
        name="logistics_agent",
    )

def create_poi_agent() -> Any:
    """Creates a POI agent using the ReAct pattern."""
    configuration = Configuration.from_context()

    return create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=POI_TOOLS,
        prompt=(
            """You are a POI (points of interest) agent.
            Your primary responsibility is to find the best places to visit based on the user's preferences such as museums, parks, landmarks, etc. 
            INSTRUCTIONS:
            - Please only respond to queries about points of interest searching and recommendations. 
            - Analyze user's query and conversation history to determine if the user is asking for points of interest or contribute points of interest information to trip planner (supervisor).
            - If a request is outside your scope, explain your primary responsibility and reply with:  
                I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent.
            - If the following attributes existed, please provide in the response: latitude, longitude, address, phone number, website, email, opening hours, price range, reviews, rating, photos, etc.
            - If Places ID existed, use them to create a link (https://www.google.com/maps/place/?q=place_id:<PLACE_ID>) to the point of interest.
            - After you're done with your tasks, respond to the supervisor directly
            - Respond ONLY with the results of your work, do NOT include ANY other text.
            - If a tool call fails, retry up to 3 times before reporting an error.
            - Always ensure you provide a response for every tool call you make."""
        ),
        name="poi_agent",
    )
