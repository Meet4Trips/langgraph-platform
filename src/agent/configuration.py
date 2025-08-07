"""Define the configurable parameters for the agent."""

from typing import Annotated, Literal
from pydantic import Field

from src.agent.prompts import TRIP_PLANNER_WITH_TOOLS_PROMPT

class Configuration:
    """The configuration for the agent."""

    model: Annotated[
            Literal[
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "openai/gpt-4.1",
                "openai/gpt-4.1-mini",
            ], 
            {"__template_metadata__": {"kind": "llm"}}
        ] = Field(
            default="openai/gpt-4o-mini",
            description="The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
    )

    system_prompt: str = Field(
        default_factory=lambda: TRIP_PLANNER_WITH_TOOLS_PROMPT,
        description="The system prompt to use for the agent's interactions. "
        "This prompt sets the context and behavior for the agent."
    )

    selected_tools: list[Literal["search_weather", "search_flights", "search_hotels", "search_attractions", "search_restaurants"]] = Field(
        default_factory=lambda: ["search_weather", "search_flights", "search_hotels", "search_attractions", "search_restaurants"],
        description="The list of tools to use for the agent's interactions. "
        "This list should contain the names of the tools to use."
    )