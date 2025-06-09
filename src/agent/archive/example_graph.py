from typing import Annotated

from langchain_tavily import TavilySearch
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

import os
import json
from langchain.chat_models import init_chat_model

from langchain_core.tools import tool
from langgraph.types import interrupt, Command

@tool
def human_assistance(query: str) -> str:
    """
    Request assistance from a human.
    """
    humane_response = interrupt({"query": query})
    return humane_response["data"]


tool = TavilySearch(max_results=2)
tools = [tool] 

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Load API key from environment variable
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# No need to set it again since it's already loaded from .env

llm = init_chat_model("openai:gpt-4.1")

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

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

def route_tools(state: State):
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


memory = MemorySaver()

# Define the graph
graph = (
    StateGraph(State)
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
    .compile(name="Test Graph", checkpointer=memory)
)
