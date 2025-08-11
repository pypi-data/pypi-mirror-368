"""
Request and response schemas for BubbleTea
"""

from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, validator
from .components import Component, BaseComponent


class ImageInput(BaseModel):
    """Image input that can be either a URL or base64 encoded data"""
    text: Optional[str] = Field(None, description="Text description of the image")
    url: Optional[str] = Field(None, description="URL of the image")
    base64: Optional[str] = Field(None, description="Base64 encoded image data")
    mime_type: Optional[str] = Field(None, description="MIME type of the image (e.g., image/jpeg, image/png)")


class ComponentChatRequest(BaseModel):
    """Incoming chat request from BubbleTea"""
    type: Literal["user"]
    message: str
    images: Optional[List[ImageInput]] = Field(None, description="Optional images to include with the message")
    user_uuid: Optional[str] = Field(None, description="UUID of the user making the request")
    conversation_uuid: Optional[str] = Field(None, description="UUID of the conversation")
    user_email: Optional[str] = Field(None, description="Email of the user making the request")
    chat_history: Optional[Union[List[Dict[str, Any]], str]] = Field(None, description="Detailed message history with metadata (list) or context string")
    thread_id: Optional[str] = Field(None, description="Thread ID of user conversation")


class ComponentChatResponse(BaseModel):
    """Non-streaming response containing list of components"""
    responses: List[Union[Component, BaseComponent]]


class BotConfig(BaseModel):
    """Configuration for a BubbleTea bot"""
    # Required fields
    name: str = Field(..., description="Handle - unique identifier used in URLs (no spaces)", pattern=r'^[a-zA-Z0-9_-]+$')
    url: str = Field(..., description="URL where the bot is hosted")
    is_streaming: bool = Field(..., description="Whether the bot supports streaming responses")
    
    # App Store-like metadata
    display_name: Optional[str] = Field(None, max_length=20, description="Display name (max 20 chars)")
    subtitle: Optional[str] = Field(None, max_length=30, description="Subtitle (max 30 chars)")
    icon_url: Optional[str] = Field(None, description="1024x1024 PNG icon URL")
    icon_emoji: Optional[str] = Field(None, max_length=10, description="Emoji icon alternative")
    preview_video_url: Optional[str] = Field(None, description="Preview video URL")
    description: Optional[str] = Field(None, description="Markdown description")
    visibility: Optional[Literal["public", "private"]] = Field("public", description="Bot visibility")
    discoverable: Optional[bool] = Field(True, description="Whether the bot is discoverable")
    entrypoint: Optional[str] = Field(None, description="Launch context page/action")
    
    # Legacy fields (kept for backward compatibility)
    emoji: Optional[str] = Field("🤖", description="Emoji to represent the bot (deprecated, use icon_emoji)")
    initial_text: Optional[str] = Field("Hi! How can I help you today?", description="Initial greeting message")
    authorization: Optional[Literal["public", "private"]] = Field("public", description="Authorization type (deprecated, use visibility)")
    authorized_emails: Optional[List[str]] = Field(None, description="List of authorized emails for private bots")
    subscription_monthly_price: Optional[int] = Field(0, description="Monthly subscription price in cents")
    
    # CORS configuration (optional)
    cors_config: Optional[Dict[str, Any]] = Field(None, description="Custom CORS configuration")
    
    # Example chats for bot
    example_chats: Optional[List[str]] = Field(None, description="List of example chat messages for the bot")
    
    @validator('name')
    def validate_handle(cls, v):
        if ' ' in v:
            raise ValueError('Bot handle cannot contain spaces')
        return v.lower()
    
    @validator('icon_url', 'preview_video_url')
    def validate_media_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Media URLs must start with http:// or https://')
        return v
