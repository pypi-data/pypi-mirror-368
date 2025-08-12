"""FastAPI Agent - Interact with your endpoints using an AI-based chat interface."""

__version__ = "0.2.0"

from .agents import AIAgent, PydanticAIAgent
from .fastapi_agent import FastAPIAgent
from .fastapi_discovery import FastAPIDiscovery
from .fastapi_depends import AuthenticationDetector

__all__ = ["FastAPIAgent", "FastAPIDiscovery", "AIAgent", "PydanticAIAgent", "AuthenticationDetector"]
