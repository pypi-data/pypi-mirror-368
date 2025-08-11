"""
BubbleTea - A Python package for building AI chatbots
With LiteLLM support for easy LLM integration
"""

from .components import Text, Image, Markdown, Card, Cards, Done, Pill, Pills, Video, Block, Error, BaseComponent
from .decorators import chatbot, config
from .server import run_server
from .schemas import ImageInput, BotConfig

__all__ = [
    "Text", "Image", "Markdown", "Card", "Cards", "Done", "Pill", "Pills",
    "chatbot", "config", "run_server", "ImageInput", "BotConfig", "LLM", "Video", "Block", "Error", "BaseComponent"
]

def __getattr__(name):
    if name == "LLM":
        try:
            from .llm import LLM
            return LLM
        except ImportError:
            raise ImportError(
                "LiteLLM is not installed. Please install it with `pip install bubbletea[llm]`"
            )
    raise AttributeError(f"module {__name__} has no attribute {name}")
