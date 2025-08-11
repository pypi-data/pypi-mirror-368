"""
Decorators for creating BubbleTea chatbots
"""

import asyncio
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    AsyncGenerator,
    Generator,
    Union,
    Tuple,
    Optional,
)
from functools import wraps

from .components import Component, Done, BaseComponent
from .schemas import ComponentChatRequest, ComponentChatResponse, ImageInput, BotConfig

# Module-level registry for config function (deprecated, for backward compatibility)
_config_function: Optional[Tuple[Callable, str]] = None

# Module-level registry for all chatbot functions
_chatbot_registry: Dict[str, 'ChatbotFunction'] = {}

# Module-level registry for bot-specific config functions
_bot_config_registry: Dict[str, Callable] = {}


class ChatbotFunction:
    """Wrapper for chatbot functions"""

    def __init__(self, func: Callable, name: str = None, stream: bool = None, url_path: str = None):
        self.func = func
        self.name = name or func.__name__
        self.url_path = url_path or "/chat"  # Default to /chat if not specified
        self.is_async = inspect.iscoroutinefunction(func)
        self.is_generator = inspect.isgeneratorfunction(
            func
        ) or inspect.isasyncgenfunction(func)
        self.stream = stream if stream is not None else self.is_generator
        self._config_func = None  # Store bot-specific config
    
    def config(self, func: Callable) -> Callable:
        """
        Decorator to set config for this specific bot
        
        Example:
            @bt.chatbot("pillsbot")
            def pills_bot(message: str):
                yield bt.Text("Pills bot response")
            
            @pills_bot.config
            def pills_config():
                return BotConfig(
                    name="Pills Bot",
                    description="Medication information bot"
                )
        """
        self._config_func = func
        # Register in the bot-specific config registry
        _bot_config_registry[self.url_path] = func
        return func

    async def __call__(
        self,
        message: str,
        images: List[ImageInput] = None,
        user_email: str = None,
        user_uuid: str = None,
        conversation_uuid: str = None,
        chat_history: Union[List[Dict[str, Any]], str] = None,
        thread_id: str = None
    ) -> Union[List[Component], AsyncGenerator[Component, None]]:
        """Execute the chatbot function"""
        # Check function signature to determine what parameters it accepts
        sig = inspect.signature(self.func)
        params = list(sig.parameters.keys())

        # Build kwargs based on what the function accepts
        kwargs = {}
        if "images" in params:
            kwargs["images"] = images
        if "user_email" in params:
            kwargs["user_email"] = user_email
        if "user_uuid" in params:
            kwargs["user_uuid"] = user_uuid
        if "conversation_uuid" in params:
            kwargs["conversation_uuid"] = conversation_uuid
        if "thread_id" in params:
            kwargs["thread_id"] = thread_id

        # Handle chat_history parameter compatibility
        if "chat_history" in params:
            # Check if the function signature expects a specific type
            param_annotation = sig.parameters["chat_history"].annotation
            if param_annotation == str or param_annotation == Optional[str]:
                # Function expects string, convert list to string if needed
                if isinstance(chat_history, list):
                    kwargs["chat_history"] = str(chat_history)
                else:
                    kwargs["chat_history"] = chat_history
            else:
                # Function expects list or is untyped, keep as is
                kwargs["chat_history"] = chat_history

        # Call function with appropriate parameters
        if self.is_async:
            result = await self.func(message, **kwargs)
        else:
            result = self.func(message, **kwargs)

        # Handle different return types
        if self.is_generator:
            # Generator functions yield components
            if inspect.isasyncgen(result):
                return result
            else:
                # Convert sync generator to async
                async def async_wrapper():
                    for item in result:
                        yield item

                return async_wrapper()
        else:
            # Non-generator functions return list of components
            if not isinstance(result, list):
                result = [result]
            return result

    async def handle_request(self, request: ComponentChatRequest):
        """Handle incoming chat request and return appropriate response"""
        components = await self(
            request.message,
            images=request.images,
            user_email=request.user_email,
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            chat_history=request.chat_history,
            thread_id=request.thread_id
        )

        if self.stream:
            # Return async generator for streaming
            return components
        else:
            # Return list for non-streaming
            if inspect.isasyncgen(components):
                # Collect all components from generator
                collected = []
                async for component in components:
                    if not isinstance(component, Done):
                        collected.append(component)
                return ComponentChatResponse(responses=collected)
            else:
                return ComponentChatResponse(responses=components)


def chatbot(name_or_url: Union[str, Callable] = None, stream: bool = None, name: str = None):
    """
    Decorator to create a BubbleTea chatbot from a function

    Args:
        name_or_url: Either a URL path (e.g., "pillsbot") or name for the chatbot
                     If it starts without /, it's treated as a URL path
        stream: Whether to stream responses (auto-detected from generator functions)
        name: Optional explicit name for the chatbot (defaults to function name)

    Example:
        @chatbot("pillsbot")  # Will be accessible at /pillsbot
        def my_bot(message: str):
            yield Text("Hello!")
            
        @chatbot()  # Will be accessible at /chat (default)
        def another_bot(message: str):
            return Text("Hi!")
    """

    def decorator(func: Callable) -> ChatbotFunction:
        # Determine URL path
        url_path = None
        bot_name = name
        
        if isinstance(name_or_url, str):
            # If it doesn't start with /, treat it as URL path and prepend /
            if not name_or_url.startswith("/"):
                url_path = f"/{name_or_url}"
            else:
                url_path = name_or_url
            # If no explicit name provided, derive from URL
            if not bot_name:
                bot_name = name_or_url.strip("/").replace("-", "_").replace("/", "_")
        
        chatbot_func = ChatbotFunction(func, name=bot_name, stream=stream, url_path=url_path)
        
        # Check if this URL path is already registered
        if chatbot_func.url_path in _chatbot_registry:
            raise ValueError(
                f"A chatbot is already registered at URL path '{chatbot_func.url_path}'. "
                f"Each chatbot must have a unique URL path."
            )
        
        # Register the chatbot function in the global registry
        _chatbot_registry[chatbot_func.url_path] = chatbot_func
        
        return chatbot_func

    # Allow using @chatbot without parentheses
    if callable(name_or_url):
        func = name_or_url
        chatbot_func = ChatbotFunction(func)
        
        # Check if this URL path is already registered
        if chatbot_func.url_path in _chatbot_registry:
            raise ValueError(
                f"A chatbot is already registered at URL path '{chatbot_func.url_path}'. "
                f"Each chatbot must have a unique URL path."
            )
        
        _chatbot_registry[chatbot_func.url_path] = chatbot_func
        return chatbot_func

    return decorator


def get_registered_chatbots() -> Dict[str, ChatbotFunction]:
    """Get all registered chatbot functions"""
    return _chatbot_registry.copy()


def get_bot_configs() -> Dict[str, Callable]:
    """Get all registered bot-specific config functions"""
    return _bot_config_registry.copy()


def config(path: str = "/config"):
    """
    Decorator to define bot configuration endpoint

    Args:
        path: Optional path for the config endpoint (defaults to "/config")

    Example:
        @config()
        def get_config():
            return BotConfig(
                name="My Bot",
                url="https://mybot.example.com",
                is_streaming=True,
                emoji="🤖",
                initial_text="Hello! How can I help?"
                authorization="private",
                authorized_emails=["test@example.com"]
            )
    """

    def decorator(func: Callable) -> Callable:
        global _config_function
        _config_function = (func, path)
        return func

    # Allow using @config without parentheses
    if callable(path):
        func = path
        _config_function = (func, "/config")
        return func

    return decorator
