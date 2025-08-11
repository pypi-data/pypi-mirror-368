"""
Test cases for the @config decorator functionality
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import bubbletea as bt
from bubbletea.decorators import _config_function


class TestConfigDecorator:
    """Test cases for config decorator"""
    
    def setup_method(self):
        """Reset module-level state before each test"""
        global _config_function
        import bubbletea.decorators
        bubbletea.decorators._config_function = None
    
    def test_config_decorator_with_parentheses(self):
        """Test @config() with parentheses"""
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Test Bot",
                url="http://localhost:8000",
                is_streaming=True
            )
        
        # Check that decorator registered the function
        assert _config_function is not None
        func, path = _config_function
        assert func == get_config
        assert path == "/config"
    
    def test_config_decorator_without_parentheses(self):
        """Test @config without parentheses"""
        @bt.config
        def get_config():
            return bt.BotConfig(
                name="Test Bot",
                url="http://localhost:8000",
                is_streaming=False
            )
        
        # Check that decorator registered the function
        assert _config_function is not None
        func, path = _config_function
        assert func == get_config
        assert path == "/config"
    
    def test_config_decorator_custom_path(self):
        """Test @config with custom path"""
        @bt.config("/bot/info")
        def get_config():
            return bt.BotConfig(
                name="Custom Path Bot",
                url="http://localhost:8000",
                is_streaming=True
            )
        
        # Check custom path was registered
        assert _config_function is not None
        func, path = _config_function
        assert func == get_config
        assert path == "/bot/info"
    
    def test_config_returns_dict(self):
        """Test config function returning dict instead of BotConfig"""
        @bt.config()
        def get_config():
            return {
                "name": "Dict Bot",
                "url": "http://localhost:8000",
                "is_streaming": True,
                "emoji": "🤖",
                "initial_text": "Hello from dict!"
            }
        
        # Create bot and server
        @bt.chatbot()
        def test_bot(message: str):
            return bt.Text("Response")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(test_bot, port=8001)
        
        # Test the endpoint
        with TestClient(server.app) as client:
            response = client.get("/config")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Dict Bot"
            assert data["emoji"] == "🤖"
    
    def test_config_with_optional_fields(self):
        """Test config with optional fields using defaults"""
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Minimal Bot",
                url="http://localhost:8000",
                is_streaming=False
                # emoji and initial_text should use defaults
            )
        
        config = get_config()
        assert config.emoji == "🤖"
        assert config.initial_text == "Hi! How can I help you today?"
    
    def test_config_async_function(self):
        """Test config decorator with async function"""
        @bt.config()
        async def get_config():
            # Simulate async operation
            await asyncio.sleep(0.001)
            return bt.BotConfig(
                name="Async Bot",
                url="http://localhost:8000",
                is_streaming=True,
                emoji="⚡",
                initial_text="Async bot ready!"
            )
        
        # Run async function
        config = asyncio.run(get_config())
        assert config.name == "Async Bot"
        assert config.emoji == "⚡"


class TestConfigEndpoint:
    """Test cases for config endpoint integration"""
    
    def test_server_with_config(self):
        """Test server creates config endpoint when decorator is used"""
        # Reset and setup config
        import bubbletea.decorators
        bubbletea.decorators._config_function = None
        
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Endpoint Test Bot",
                url="http://localhost:8000",
                is_streaming=True,
                emoji="🧪",
                initial_text="Testing endpoint"
            )
        
        @bt.chatbot()
        def test_bot(message: str):
            return bt.Text("Test response")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(test_bot, port=8002)
        
        with TestClient(server.app) as client:
            # Test config endpoint exists and returns correct data
            response = client.get("/config")
            assert response.status_code == 200
            
            data = response.json()
            assert data["name"] == "Endpoint Test Bot"
            assert data["url"] == "http://localhost:8000"
            assert data["is_streaming"] == True
            assert data["emoji"] == "🧪"
            assert data["initial_text"] == "Testing endpoint"
    
    def test_server_without_config(self):
        """Test server works without config decorator"""
        # Reset module state
        import bubbletea.decorators
        bubbletea.decorators._config_function = None
        
        @bt.chatbot()
        def test_bot(message: str):
            return bt.Text("No config bot")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(test_bot, port=8003)
        
        with TestClient(server.app) as client:
            # Config endpoint should not exist
            response = client.get("/config")
            assert response.status_code == 404
            
            # But chat endpoint should still work
            response = client.post("/chat", json={
                "type": "user",
                "message": "Hello"
            })
            assert response.status_code == 200
    
    def test_custom_config_path(self):
        """Test server with custom config path"""
        import bubbletea.decorators
        bubbletea.decorators._config_function = None
        
        @bt.config("/api/bot-info")
        def get_config():
            return bt.BotConfig(
                name="Custom Path Bot",
                url="http://localhost:8000",
                is_streaming=False
            )
        
        @bt.chatbot()
        def test_bot(message: str):
            return bt.Text("Custom path response")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(test_bot, port=8004)
        
        with TestClient(server.app) as client:
            # Default path should not exist
            response = client.get("/config")
            assert response.status_code == 404
            
            # Custom path should work
            response = client.get("/api/bot-info")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Custom Path Bot"