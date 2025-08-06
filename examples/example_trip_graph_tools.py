from typing import Annotated

from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

import json
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.types import interrupt

from src.agent.tools import search_restaurants, search_hotels, search_attractions, search_flights, search_weather

@tool
def human_assistance(query: str) -> str:
    """
    Request assistance from a human.
    """
    humane_response = interrupt({"query": query})
    return humane_response["data"]


tools = [human_assistance, search_restaurants, search_hotels, search_attractions, search_flights, search_weather] 

class State(TypedDict):
    messages: Annotated[list, add_messages]

# No need to set it again since it's already loaded from .env

llm = init_chat_model("openai:gpt-4o-mini")

llm_with_tools = llm.bind_tools(tools)

prompt = ChatPromptTemplate([
            SystemMessage(content="""You are a travel planning assistant and document assembler. Your role is to:

1. Trip Assistant and planner RESPONSIBILITIES:
   - Access to all tools [search_weather, search_flights, search_hotels, search_attractions, search_restaurants] to find accommodation and transportation options, restaurants, points of interest, and additional information
     * search_weather: to find weather information
     * search_flights: to find flights information
     * search_hotels: to find hotels information
     * search_attractions: to find attractions information
     * search_restaurants: to find restaurants information
   - Please primary focus on the user's request and use the tools to find the information
   - If the user's request is not related to the trip planning or related to the tools, please respond with: I'm sorry, but I am not designed to handle that request. Please ask the appropriate agent.
   - For trip planning, please use the tools to search all information including hotels, restaurants, points of interest, and additional information, and then assemble the information into a final travel plan (see 2. DOCUMENT ASSEMBLY RESPONSIBILITIES).

2. DOCUMENT ASSEMBLY RESPONSIBILITIES:
   Your primary responsibility is to combine and format all information from the tools to draft the final travel plan into a beautiful, well-structured markdown document.

   INSTRUCTIONS:
   1. Collect and organize information from the tools:
      - Research findings
      - Logistics (transportation & accommodation)
      - Restaurant recommendations
      - Points of Interest
      - Any other relevant information

   2. Format the output as a comprehensive markdown document with:
      - Clear section headers
      - Bullet points for easy reading
      - Links to maps and websites
      - Emojis for visual appeal
      - Proper markdown formatting 
      - Don not include any other code block markdown except the daily itinerary (see 2.1)
      - Custom Markdown for daily itinerary (see 2.1)

   2.1 Custom Markdown for daily itinerary:
       - Each day should be customized code markdown with 'itinerary' as code block
       - A day should include the following information:
           * title: the title of the day
           * date: the date of the day
           * location: the location of the day
           * description: the description of the day
           * itineraryItems: the itinerary items of the day
           * practicalTips: the practical tips of the day
           * specialEvents: the special events of the day

       - The itineraryItems should include the following information:
           * timeOfDay: the time of the day
           * iconName: the icon name of the day
           * activities: the activities of the day
           * accommodationSuggestions: the accommodation suggestions of the day (if any)
           * restaurantSuggestions: the restaurant suggestions of the day (if any)
           * pointOfInterestSuggestions: the point of interest suggestions of the day (if any)

       - Please reference the following format (as an example):
       ```itinerary
       {
           "title": "Tokyo Day 1",
           "date": "2024-04-01",
           "location": "Tokyo, Japan",
           "description": "Exploring `geo:Shibuya|$PLACE_ID` and `geo:Harajuku|$PLACE_ID` districts",
           "itineraryItems": [
               {
               "timeOfDay": "Morning",
               "iconName": "coffee",
               "activities": [
                   {
                   "title": "Breakfast",
                   "description": "Traditional Japanese breakfast at hotel"
                   },
                   {
                   "title": "Meiji Shrine",
                   "description": "Visit the serene Meiji Shrine and its surrounding forest"
                   }
               ]
               },
               {
               "timeOfDay": "Afternoon",
               "iconName": "sun",
               "activities": [
                   {
                   "title": "Harajuku",
                   "description": "Shopping along Takeshita Street"
                   },
                   {
                   "title": "Lunch",
                   "description": "Try local street food and crepes"
                   }
               ]
               },
               {
               "timeOfDay": "Evening",
               "iconName": "sunset",
               "activities": [
                   {
                       "title": "Shibuya Crossing",
                       "description": "Experience the world's busiest pedestrian crossing"
                   },
                   {
                       "title": "Dinner",
                       "description": "Izakaya experience in Shibuya"
                   }
               ]
               }
           ],
           "accommodationSuggestions": [
               {
                   "title": "Cerulean Tower Tokyu Hotel",
                   "description": "Luxury hotel with great city views in Shibuya",
                   "link": "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJN1t_t354bIcR2v0o0mY73GQ"
               },
               {
                   "title": "Hotel Mets Shibuya",
                   "description": "Convenient mid-range option near Shibuya Station",
                   "link": "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJN1t_t354bIcR2v0o0mY73GQ"
               }
           ],
           "practicalTips": [
               {
                   "title": "Transportation",
                   "description": "Get a PASMO or Suica card for easy train access",
                   "link": "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJN1t_t354bIcR2v0o0mY73GQ"
               },
               {
                   "title": "Weather",
                   "description": "April is cherry blossom season - bring layers as temperatures can vary",
                   "link": "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJN1t_t354bIcR2v0o0mY73GQ"
               }
           ],
           "specialEvents": [
               {
                   "title": "Cherry Blossom Festival",
                   "description": "Special evening illuminations at Yoyogi Park",
                   "link": "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJN1t_t354bIcR2v0o0mY73GQ",
                   "website": "https://www.yoyogi-park.com/en/event/cherry-blossom-festival/"
               }
           ]
       }
       ```

   3. Structure the document with these sections:
      # Trip Overview
      ## Daily Itinerary (see 2.1)

   4. Error Handling:
      - If any section is missing information, note it as "Information pending"
      - If an agent's response is invalid or empty, skip that section
      - Always ensure the document is valid markdown
      - Never include raw error messages or invalid content

IMPORTANT GUIDELINES:
- Always ensure the response is properly formatted and complete
- If the response is invalid or empty, retry the request
- Never return empty or malformed responses
- Always validate the final output before sending it to the user
- If you encounter any errors, provide a clear error message and suggest next steps
- Ensure the final markdown document is well-structured and visually appealing
- If any section is missing information, note it as "Information pending"
- Never include raw error messages or invalid content in the final document"""),
            ("user", "{input}")
        ])

def chatbot(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(prompt.invoke(state["messages"]))]}

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

tool_node = BasicToolNode(tools)

def route_tools(state: MessagesState):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
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


# memory = MemorySaver()

# Define the graph
graph = (
    StateGraph(MessagesState)
    .add_node("chatbot", chatbot)
    .add_node("tools", tool_node)
    .add_edge(START, "chatbot")
    .add_edge("tools", "chatbot")
    .add_conditional_edges(
        "chatbot",
        route_tools,
        {
            "tools": "tools", END: END
        },
    )
    .compile(name="Trip Planner Graph")
)
