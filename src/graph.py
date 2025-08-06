from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt.chat_agent_executor import create_react_agent

from agent.utils.configuration import Configuration
from langchain_openai import ChatOpenAI

# Try both import strategies to work in both local and deployment environments
try:
    from prompt.prompts import TRIP_PLANNER_WITH_TOOLS_PROMPT
    from tool.tools import search_attractions, search_hotels, search_restaurants
except ImportError:
    from src.prompt.prompts import TRIP_PLANNER_WITH_TOOLS_PROMPT
    from src.tool.tools import search_attractions, search_hotels, search_restaurants

from langchain_core.messages import ToolMessage
import json

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

def create_trip_planner_graph():    
    # Get configuration
    configuration = Configuration.from_context()

    tools = [search_restaurants, search_hotels, search_attractions] 

    # Define the trip_planner node
    trip_planner = create_react_agent(
        model=ChatOpenAI(model=configuration.model),
        tools=tools,
        prompt=TRIP_PLANNER_WITH_TOOLS_PROMPT,
        name="trip_planner",
    )

    # Define the tools node
    tool_node = BasicToolNode(tools)
     
    # Define the route_tools function for conditional_edge
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
    
    # Compile the graph
    graph = (
        StateGraph(MessagesState)
        .add_node("trip_planner", trip_planner)
        .add_node("tools", tool_node)
        .add_edge(START, "trip_planner")
        .add_edge("tools", "trip_planner")
        .add_conditional_edges(
            "trip_planner",
            route_tools,
            {
                "tools": "tools", END: END
            },
        )
        .compile(name="trip_planner_agent"))
    return graph

# Create the graph instance
graph = create_trip_planner_graph() 