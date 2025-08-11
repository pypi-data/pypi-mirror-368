"""
FastAPI server implementation for BubbleTea chatbots
"""

import json
import asyncio
from typing import Optional, AsyncGenerator, List, Dict, Any, Callable
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .decorators import ChatbotFunction
from . import decorators
from .schemas import ComponentChatRequest, ComponentChatResponse, BotConfig
from .components import Done


class BubbleTeaServer:
    """FastAPI server for hosting BubbleTea chatbots"""
    
    def __init__(self, chatbot: Optional[ChatbotFunction] = None, port: int = 8000, cors: bool = True, cors_config: Optional[Dict[str, Any]] = None, register_all: bool = True):
        self.app = FastAPI(title="BubbleTea Bot Server")
        self.chatbot = chatbot
        self.port = port
        self.register_all = register_all
        
        # Check if bot config has CORS settings
        if cors and not cors_config and decorators._config_function:
            config_func, _ = decorators._config_function
            try:
                # Try to get config to check for CORS settings
                if asyncio.iscoroutinefunction(config_func):
                    # Can't await here, so use default CORS
                    pass
                else:
                    config = config_func()
                    if hasattr(config, 'cors_config') and config.cors_config:
                        cors_config = config.cors_config
            except:
                pass
        
        # Setup CORS
        if cors:
            self._setup_cors(cors_config)
        
        self._setup_routes()
    
    def _setup_cors(self, cors_config: Optional[Dict[str, Any]] = None):
        """Setup CORS middleware with sensible defaults"""
        default_config = {
            "allow_origins": ["*"],  # Allow all origins in development
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["*"],
        }
        
        # Update with custom config if provided
        if cors_config:
            default_config.update(cors_config)
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            **default_config
        )
    
    def _setup_routes(self):
        """Setup chat endpoints for all registered chatbots"""
        
        # Import the registry getter
        from . import decorators
        
        # Get all registered chatbots
        if self.register_all:
            registered_bots = decorators.get_registered_chatbots()
        else:
            # Only register the primary chatbot if register_all is False
            registered_bots = {self.chatbot.url_path: self.chatbot} if self.chatbot else {}
        
        # Register each chatbot at its URL path
        for url_path, chatbot in registered_bots.items():
            # Create a closure to capture the chatbot instance
            def create_chat_endpoint(bot: ChatbotFunction):
                async def chat_endpoint(request: ComponentChatRequest):
                    """Handle chat requests"""
                    response = await bot.handle_request(request)
                    
                    if bot.stream:
                        # Streaming response
                        async def stream_generator():
                            async for component in response:
                                # Convert component to JSON and wrap in SSE format
                                data = component.model_dump_json()
                                yield f"data: {data}\n\n"
                            # Send done signal
                            done = Done()
                            yield f"data: {done.model_dump_json()}\n\n"
                        
                        return StreamingResponse(
                            stream_generator(),
                            media_type="text/event-stream"
                        )
                    else:
                        # Non-streaming response
                        return response
                return chat_endpoint
            
            # Register the endpoint
            self.app.post(url_path)(create_chat_endpoint(chatbot))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            registered_bots = decorators.get_registered_chatbots()
            bots_info = [
                {
                    "name": bot.name,
                    "url": url_path,
                    "streaming": bot.stream
                }
                for url_path, bot in registered_bots.items()
            ]
            
            return {
                "status": "healthy",
                "registered_bots": bots_info,
                "bot_count": len(registered_bots)
            }
        
        # Register bot-specific config endpoints
        bot_configs = decorators.get_bot_configs()
        for bot_url_path, config_func in bot_configs.items():
            # Create config endpoint path (e.g., /pillsbot/config)
            config_path = f"{bot_url_path}/config"
            
            # Create a closure to capture the config function
            def create_config_endpoint(func: Callable):
                async def config_endpoint():
                    """Get bot configuration"""
                    try:
                        # Check if config function is async
                        if asyncio.iscoroutinefunction(func):
                            result = await func()
                        else:
                            result = func()
                        
                        # Ensure result is a BotConfig instance
                        if isinstance(result, BotConfig):
                            return result
                        elif isinstance(result, dict):
                            return BotConfig(**result)
                        else:
                            # Try to convert to BotConfig
                            return result
                    except Exception as e:
                        # Log error for debugging
                        print(f"Error in config endpoint: {e}")
                        raise
                return config_endpoint
            
            # Register the config endpoint
            self.app.get(config_path, response_model=BotConfig)(create_config_endpoint(config_func))
        
        # Register global config endpoint if decorator was used (backward compatibility)
        if decorators._config_function:
            config_func, config_path = decorators._config_function
            
            @self.app.get(config_path, response_model=BotConfig)
            async def config_endpoint():
                """Get bot configuration"""
                # Check if config function is async
                if asyncio.iscoroutinefunction(config_func):
                    result = await config_func()
                else:
                    result = config_func()
                
                # Ensure result is a BotConfig instance
                if isinstance(result, BotConfig):
                    return result
                elif isinstance(result, dict):
                    return BotConfig(**result)
                else:
                    # Try to convert to BotConfig
                    return result
    
    def run(self, host: str = "0.0.0.0"):
        """Run the server"""
        uvicorn.run(self.app, host=host, port=self.port)


def run_server(chatbot: Optional[ChatbotFunction] = None, port: int = 8000, host: str = "0.0.0.0", cors: bool = True, cors_config: Optional[Dict[str, Any]] = None, register_all: bool = True):
    """
    Run a FastAPI server for chatbots
    
    Args:
        chatbot: Optional specific chatbot function (for backward compatibility)
                 If None and register_all=True, serves all decorated chatbots
        port: Port to run the server on
        host: Host to bind the server to
        cors: Enable CORS support (default: True)
        cors_config: Custom CORS configuration dict with keys:
            - allow_origins: List of allowed origins (default: ["*"])
            - allow_credentials: Allow credentials (default: True)
            - allow_methods: Allowed methods (default: ["GET", "POST", "OPTIONS"])
            - allow_headers: Allowed headers (default: ["*"])
        register_all: If True, registers all decorated chatbots (default: True)
                      If False, only registers the specified chatbot
    """
    server = BubbleTeaServer(chatbot, port, cors=cors, cors_config=cors_config, register_all=register_all)
    server.run(host)