import getpass
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from agent.archive.trip_types import TripState
from src.agent.trip_tools import (
    COORDINATOR_TOOLS,
    DESTINATION_TOOLS,
    ITINERARY_TOOLS,
    BUDGET_TOOLS,
    LOGISTICS_TOOLS,
    POI_TOOLS,
    RESTAURANT_TOOLS,
    WEATHER_TOOLS
)

class BaseAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.output_parser = StrOutputParser()
        self.tools = []
        self.llm_with_tools = None

    def bind_tools(self):
        """Bind tools to the LLM."""
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the state and return updated state."""
        if not self.llm_with_tools:
            self.bind_tools()
        
        # Update current_agent in state using the class name
        agent_name = self.__class__.__name__
        state["current_agent"] = agent_name
        
        # Get the last message from the state
        messages = state.get("messages", [])
        if not messages:
            return state
        
        # Process the message with the LLM
        response = self.llm_with_tools.invoke(self.prompt.invoke(messages))
        
        # Update the state with the response
        return {"messages": [response], "current_agent": agent_name}

class CoordinatorAgent(BaseAgent):
    """Main coordinator that manages the overall trip planning process."""
    
    def __init__(self, llm: BaseChatModel):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a travel planning coordinator. Your role is to:
            1. Understand the user's travel requirements
            2. Break down the planning into specific tasks
            3. Coordinate with other agents to gather necessary information
            4. Ensure all aspects of the trip are covered
            5. Make decisions about the next steps in the planning process"""),
            ("user", "{input}")
        ])
        self.tools = COORDINATOR_TOOLS
        self.bind_tools()

class DestinationAnalyzer(BaseAgent):
    """Analyzes potential destinations based on user preferences."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Destination Analyzer agent. Your role is to:
1. Analyze user preferences and requirements
2. Search for suitable destinations
3. Provide detailed information about each destination
4. Consider factors like weather, culture, and activities

When using tools:
1. Always wait for tool responses before proceeding
2. Use the search_destinations tool to find information
3. Use the search_weather tool to check weather conditions
4. Format your responses clearly and include all relevant details"""),
            ("user", "{input}")
        ])
        self.tools = ITINERARY_TOOLS
        self.bind_tools()

class ItineraryPlanner(BaseAgent):
    """Creates detailed day-by-day itineraries."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an itinerary planning expert. Your role is to:
            1. Create detailed day-by-day schedules
            2. Balance activities and rest time
            3. Consider travel times between locations
            4. Account for opening hours and local customs
            5. Optimize the schedule for the best experience"""),
            ("user", "{input}")
        ])
        self.tools = ITINERARY_TOOLS
        self.bind_tools()

class BudgetEstimator(BaseAgent):
    """Estimates and manages trip costs."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a travel budget expert. Your role is to:
            1. Calculate estimated costs for all trip components
            2. Consider currency exchange rates
            3. Account for seasonal price variations
            4. Provide cost-saving recommendations
            5. Create a detailed budget breakdown"""),
            ("user", "{input}")
        ])
        self.tools = BUDGET_TOOLS
        self.bind_tools()

class LogisticsAgent(BaseAgent):
    """Handles transportation and accommodation bookings."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are the LogisticsAgent.  
                Your primary responsibility is to find accommodation and transportation options based on the user's preferences flights, trains, car rental, hotels.  
                Please only respond to queries about accommodation and transportation searching and recommendations.  
                If a request is outside your scope, explain your primary responsibility and reply with:  
                I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent."""),
            ("user", "{input}")
        ])
        self.tools = LOGISTICS_TOOLS
        self.bind_tools()

class POIRecommender(BaseAgent):
    """Recommends points of interest and attractions."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a local attractions expert. Your role is to:
            1. Research points of interest
            2. Consider user preferences and interests
            3. Evaluate attraction ratings and reviews
            4. Account for seasonal availability
            5. Provide personalized recommendations"""),
            ("user", "{input}")
        ])
        self.tools = POI_TOOLS
        self.bind_tools()

class RestaurantFinder(BaseAgent):
    """Finds and recommends restaurants."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate([
            SystemMessage(content="""You are the RestaurantFinder.  
                Your primary responsibility is to find restaurants based on the user's preferences such as cuisine, price range, and location.  
                Please only respond to queries about restaurants searching and recommendations.  
                If a request is outside your scope, explain your primary responsibility and reply with:  
                I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent."""),
            ("user", "{input}")
        ])
        self.tools = RESTAURANT_TOOLS
        self.bind_tools()

class WeatherAgent(BaseAgent):
    """Provides weather forecasts and climate information."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a weather and climate expert. Your role is to:
            1. Research historical weather patterns
            2. Provide seasonal climate information
            3. Consider weather impacts on activities
            4. Recommend appropriate clothing and gear
            5. Suggest weather-appropriate activities"""),
            ("user", "{input}")
        ])
        self.tools = WEATHER_TOOLS
        self.bind_tools()

class TripAssembler(BaseAgent):
    """Assembles the final trip plan."""
    
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a travel plan assembler. Your role is to:
            1. Combine all gathered information
            2. Create a cohesive travel plan
            3. Ensure all components work together
            4. Format the output for easy understanding
            5. Provide a complete trip summary"""),
            ("user", "{input}")
        ])
        # Trip assembler doesn't need tools as it works with existing data
        self.tools = []
        self.bind_tools() 

class DynamicToolNode:
    """A node that dynamically filters tools based on the calling agent."""

    def __init__(self, all_tools: list) -> None:
        self.all_tools = all_tools
        self.tools_by_name = {tool.name: tool for tool in all_tools}
        self.agent_tool_mapping = {
            "CoordinatorAgent": COORDINATOR_TOOLS,
            "DestinationAnalyzer": DESTINATION_TOOLS,
            "ItineraryPlanner": ITINERARY_TOOLS,
            "BudgetEstimator": BUDGET_TOOLS,
            "LogisticsAgent": LOGISTICS_TOOLS,
            "POIRecommender": POI_TOOLS,
            "RestaurantFinder": RESTAURANT_TOOLS,
            "WeatherAgent": WEATHER_TOOLS
        }

    def get_available_tools(self, agent_name: str) -> list:
        """Get the list of tools available for a specific agent."""
        return self.agent_tool_mapping.get(agent_name, [])

    def __call__(self, state: TripState):
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        # Get the agent name from the state
        agent_name = state.get("current_agent", "CoordinatorAgent")
        available_tools = self.get_available_tools(agent_name)
        available_tool_names = {tool.name for tool in available_tools}

        print(f"Agent name: {agent_name}")
        print(f"Available tool names: {available_tool_names}")

        outputs = []
        for tool_call in message.tool_calls:
            tool_name = tool_call["name"]
            if tool_name not in available_tool_names:
                outputs.append(
                    ToolMessage(
                        content=json.dumps({
                            "error": f"Tool {tool_name} is not available for {agent_name}"
                        }),
                        name=tool_name,
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

            tool_result = self.tools_by_name[tool_name].invoke(
                tool_call["args"]
            )
            
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}  # Return both messages and updated state