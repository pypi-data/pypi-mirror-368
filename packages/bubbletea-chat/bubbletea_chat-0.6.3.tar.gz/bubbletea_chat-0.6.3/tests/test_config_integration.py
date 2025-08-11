"""
Integration tests for bots using both @chatbot and @config decorators
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import bubbletea as bt


class TestConfigIntegration:
    """Integration tests for full bot functionality with config"""
    
    def setup_method(self):
        """Reset module-level state before each test"""
        import bubbletea.decorators
        bubbletea.decorators._config_function = None
    
    def test_full_bot_with_config(self):
        """Test a complete bot with both chat and config functionality"""
        # Define config
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Integration Test Bot",
                url="http://localhost:8000",
                is_streaming=False,
                emoji="🧪",
                initial_text="Welcome to the integration test bot!"
            )
        
        # Define chatbot
        @bt.chatbot(name="Integration Test Bot")
        def test_bot(message: str):
            if "hello" in message.lower():
                return bt.Text("Hello! I'm the integration test bot.")
            elif "config" in message.lower():
                return bt.Text("You can check my config at /config endpoint!")
            else:
                return bt.Text("I don't understand. Try saying 'hello' or 'config'.")
        
        # Create server
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(test_bot, port=8005)
        
        with TestClient(server.app) as client:
            # Test config endpoint
            config_response = client.get("/config")
            assert config_response.status_code == 200
            config_data = config_response.json()
            assert config_data["name"] == "Integration Test Bot"
            assert config_data["emoji"] == "🧪"
            assert config_data["initial_text"] == "Welcome to the integration test bot!"
            
            # Test chat endpoint
            chat_response = client.post("/chat", json={
                "type": "user",
                "message": "Hello"
            })
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            assert len(chat_data["responses"]) == 1
            assert chat_data["responses"][0]["content"] == "Hello! I'm the integration test bot."
            
            # Test health endpoint still works
            health_response = client.get("/health")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            assert health_data["bot_name"] == "Integration Test Bot"
    
    def test_streaming_bot_with_config(self):
        """Test streaming bot with config"""
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Streaming Test Bot",
                url="http://localhost:8000",
                is_streaming=True,
                emoji="🌊",
                initial_text="I'm a streaming bot!"
            )
        
        @bt.chatbot(stream=True)
        def streaming_bot(message: str):
            yield bt.Text("Starting stream...")
            yield bt.Text("Processing your message...")
            yield bt.Text(f"You said: {message}")
            yield bt.Text("Stream complete!")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(streaming_bot, port=8006)
        
        with TestClient(server.app) as client:
            # Test config
            config_response = client.get("/config")
            assert config_response.status_code == 200
            config_data = config_response.json()
            assert config_data["is_streaming"] == True
            assert config_data["emoji"] == "🌊"
            
            # Test streaming chat (TestClient doesn't support SSE, so we just check it returns)
            chat_response = client.post("/chat", json={
                "type": "user",
                "message": "Test stream"
            })
            assert chat_response.status_code == 200
    
    def test_multimodal_bot_with_config(self):
        """Test bot that handles images with config"""
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Multimodal Bot",
                url="http://localhost:8000",
                is_streaming=False,
                emoji="🖼️",
                initial_text="Send me text or images!"
            )
        
        @bt.chatbot()
        def multimodal_bot(message: str, images: list = None):
            if images:
                return bt.Text(f"Received {len(images)} image(s) with message: {message}")
            else:
                return bt.Text(f"Text only message: {message}")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(multimodal_bot, port=8007)
        
        with TestClient(server.app) as client:
            # Test config
            config_response = client.get("/config")
            assert config_response.status_code == 200
            config_data = config_response.json()
            assert config_data["emoji"] == "🖼️"
            
            # Test chat with images
            chat_response = client.post("/chat", json={
                "type": "user",
                "message": "Look at this",
                "images": [
                    {"url": "https://example.com/image1.jpg"},
                    {"base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="}
                ]
            })
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            assert "2 image(s)" in chat_data["responses"][0]["content"]
    
    def test_bot_with_all_component_types(self):
        """Test bot using all component types with config"""
        @bt.config()
        def get_config():
            return bt.BotConfig(
                name="Component Demo Bot",
                url="http://localhost:8000",
                is_streaming=True,
                emoji="🎨",
                initial_text="I can show you different component types!"
            )
        
        @bt.chatbot(stream=True)
        def component_bot(message: str):
            if "text" in message.lower():
                yield bt.Text("This is a text component")
            elif "image" in message.lower():
                yield bt.Image("https://example.com/demo.jpg", alt="Demo image")
            elif "markdown" in message.lower():
                yield bt.Markdown("# Markdown Header\\n\\n**Bold** and *italic* text")
            else:
                yield bt.Text("Ask me about: text, image, or markdown")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(component_bot, port=8008)
        
        with TestClient(server.app) as client:
            # Verify config
            config_response = client.get("/config")
            assert config_response.status_code == 200
            assert config_response.json()["emoji"] == "🎨"
    
    def test_error_handling_in_config(self):
        """Test error handling when config function fails"""
        @bt.config()
        def get_config():
            # This will raise an error due to missing required field
            return bt.BotConfig(
                name="Error Bot",
                # url is missing - required field
                is_streaming=True
            )
        
        @bt.chatbot()
        def error_bot(message: str):
            return bt.Text("This is the error bot")
        
        from bubbletea.server import BubbleTeaServer
        server = BubbleTeaServer(error_bot, port=8009)
        
        with TestClient(server.app) as client:
            # Config endpoint should return error
            config_response = client.get("/config")
            assert config_response.status_code == 422  # Validation error