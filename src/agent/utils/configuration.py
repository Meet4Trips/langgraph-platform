"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated
import logging
import json

from langchain_core.runnables import ensure_config
from langgraph.config import get_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
            default="gpt-4o-mini",
            metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    @classmethod
    def from_context(cls) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        logger.info("Attempting to get configuration from context...")
        try:
            config = get_config()
            logger.info("Successfully retrieved config from context")
            logger.info(f"Raw config: {json.dumps(config.get('configurable', {}), indent=2, default=str)}")
        except RuntimeError as e:
            logger.warning(f"Failed to get config from context: {str(e)}")
            config = None
        
        config = ensure_config(config)
        logger.info(f"Ensured config: {json.dumps(config, indent=2, default=str)}")
        
        configurable = config.get("configurable") or {}
        logger.info(f"Configurable parameters: {json.dumps(configurable, indent=2, default=str)}")
        
        _fields = {f.name for f in fields(cls) if f.init}
        logger.info(f"Available fields: {_fields}")
        
        final_config = {k: v for k, v in configurable.items() if k in _fields}
        logger.info(f"Final configuration: {json.dumps(final_config, indent=2, default=str)}")
        
        return cls(**final_config)