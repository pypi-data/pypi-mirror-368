# BubbleTea Python SDK

Build AI chatbots for the BubbleTea platform with simple Python functions.

**Now with LiteLLM support!** 🎉 Easily integrate with OpenAI, Anthropic Claude, Google Gemini, and 100+ other LLMs.

**NEW: Vision & Image Generation!** 📸🎨 Build multimodal bots that can analyze images and generate new ones using AI.

**NEW: User & Conversation Tracking!** 🔍 Chat requests now include `user_uuid` and `conversation_uuid` for better context awareness.

## Installation

### Basic Installation
```bash
pip install bubbletea-chat
```

### With LLM Support
To include LiteLLM integration for AI models (OpenAI, Claude, Gemini, and 100+ more):
```bash
pip install 'bubbletea-chat[llm]'
```

## Quick Start

Create a simple chatbot in `my_bot.py`:

```python
import bubbletea_chat as bt

@bt.chatbot
def my_chatbot(message: str):
    # Your bot logic here
    if "image" in message.lower():
        yield bt.Image("https://picsum.photos/400/300")
        yield bt.Text("Here's a random image for you!")
    else:
        yield bt.Text(f"You said: {message}")

if __name__ == "__main__":
    # Run the chatbot server
    bt.run_server(my_chatbot, port=8000, host="0.0.0.0")

```

Run it locally:

```bash
python my_bot.py
```

This will start a server at `http://localhost:8000` with your chatbot available at the `/chat` endpoint.


### Configuration with `@config` Decorator

BubbleTea provides a `@config` decorator to define and expose bot configurations via a dedicated endpoint. This is essential for:
- Setting up bot metadata (name, URL, description)
- Enabling subscriptions and payments
- Configuring app store-style listing information
- Managing access control and visibility

#### Example: Using the `@config` Decorator


```python
import bubbletea_chat as bt

# Define bot configuration
@bt.config()
def get_config():
    return bt.BotConfig(
        # Required fields
        name="weather-bot",  # URL-safe handle (no spaces)
        url="http://localhost:8000",
        is_streaming=True,
        
        # App store metadata
        display_name="Weather Bot",  # User-facing name (max 20 chars)
        subtitle="Real-time weather updates",  # Brief description (max 30 chars)
        icon_emoji="🌤️",  # Or use icon_url for custom icon
        description="Get accurate weather forecasts for any city worldwide.",
        
        # Subscription/Payment (in cents)
        subscription_monthly_price=499,  # $4.99/month (0 = free)
        
        # Access control
        visibility="public",  # "public" or "private"
        authorized_emails=["admin@example.com"],  # For private bots
        
        # User experience
        initial_text="Hello! I can help you check the weather. Which city would you like to know about?"
    )

# Define the chatbot
@bt.chatbot(name="Weather Bot", stream=True)
def weather_bot(message: str):
    if "new york" in message.lower():
        yield bt.Text("🌤️ New York: Partly cloudy, 72°F")
    else:
        yield bt.Text("Please specify a city to check the weather.")
```

When the bot server is running, the configuration can be accessed at the `/config` endpoint. For example:

```bash
curl http://localhost:8000/config
```

This will return the bot's configuration as a JSON object.

**Note on URL Paths:** If your bot runs on a custom path (e.g., `/pillsbot`), BubbleTea will automatically append `/config` to that path. For example:
- Bot URL: `http://localhost:8010/pillsbot` → Config endpoint: `http://localhost:8010/pillsbot/config`
- Bot URL: `http://localhost:8000/my-bot` → Config endpoint: `http://localhost:8000/my-bot/config`
- Bot URL: `http://localhost:8000` → Config endpoint: `http://localhost:8000/config`

#### Dynamic Bot Creation Using `/config`

BubbleTea agents can dynamically create new chatbots by utilizing the `/config` endpoint. For example, if you provide a command like:

```bash
create new bot 'bot-name' with url 'http://example.com'
```

The agent will automatically fetch the configuration from `http://example.com/config` and create a new chatbot based on the metadata defined in the configuration. This allows for seamless integration and creation of new bots without manual setup.

### Complete BotConfig Reference

The `BotConfig` class supports extensive configuration options for your bot:

#### Required Fields
- `name` (str): URL-safe bot handle (no spaces, used in URLs)
- `url` (str): Bot hosting URL
- `is_streaming` (bool): Enable streaming responses

#### App Store Metadata
- `display_name` (str): User-facing name (max 20 characters)
- `subtitle` (str): Brief tagline (max 30 characters)
- `description` (str): Full Markdown description
- `icon_url` (str): 1024x1024 PNG icon URL
- `icon_emoji` (str): Alternative emoji icon
- `preview_video_url` (str): Demo video URL

#### Subscription & Payment
- `subscription_monthly_price` (int): Price in cents
  - Example: `999` = $9.99/month
  - Set to `0` for free bots
  - Users are automatically billed monthly
  - Subscription status is passed to your bot

#### Access Control
- `visibility` (str): "public" or "private"
- `authorized_emails` (List[str]): Whitelist for private bots
- `authorization` (str): Deprecated, use `visibility`

#### User Experience
- `initial_text` (str): Welcome message
- `cors_config` (dict): Custom CORS settings



### Payment & Subscription Example

```python
@bt.config()
def get_config():
    return bt.BotConfig(
        # Basic configuration
        name="premium-assistant",
        url="https://your-bot.com",
        is_streaming=True,
        
        # Enable subscription
        subscription_monthly_price=1999,  # $19.99/month
        
        # Premium-only access
        visibility="public",  # Anyone can see it
        # But only subscribers can use it
    )

@bt.chatbot
async def premium_bot(message: str, user_email: str = None, subscription_status: str = None):
    """Subscription status is automatically provided by BubbleTea"""
    if subscription_status == "active":
        # Full premium features
        llm = LLM(model="gpt-4")
        response = await llm.acomplete(message)
        yield bt.Text(response)
    else:
        # Limited features for non-subscribers
        yield bt.Text("Subscribe to access premium features!")
        yield bt.Markdown("""
        ## 💎 Premium Features
        - Advanced AI responses
        - Priority support
        - And much more!
        
        **Only $19.99/month**
        """)
```

## Features

### 🤖 LiteLLM Integration

BubbleTea now includes built-in support for LiteLLM, allowing you to easily use any LLM provider. We use LiteLLM on the backend, which supports 100+ LLM models from various providers.

```python
from bubbletea_chat import LLM

# Use any model supported by LiteLLM
llm = LLM(model="gpt-4")
llm = LLM(model="claude-3-sonnet-20240229")
llm = LLM(model="gemini/gemini-pro")

# Simple completion
response = await llm.acomplete("Hello, how are you?")

# Streaming
async for chunk in llm.stream("Tell me a story"):
    yield bt.Text(chunk)
```

**📚 Supported Models**: Check out the full list of supported models and providers at [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers)

**💡 DIY Alternative**: You can also implement your own LLM connections using the LiteLLM library directly in your bots if you need more control over the integration.

### 📸 Vision/Image Analysis

BubbleTea supports multimodal interactions! Your bots can receive and analyze images:

```python
from bubbletea_chat import chatbot, Text, LLM, ImageInput

@chatbot
async def vision_bot(prompt: str, images: list = None):
    """A bot that can see and analyze images"""
    if images:
        llm = LLM(model="gpt-4-vision-preview")
        response = await llm.acomplete_with_images(prompt, images)
        yield Text(response)
    else:
        yield Text("Send me an image to analyze!")
```

**Supported Image Formats:**
- URL images: Direct links to images
- Base64 encoded images: For local/uploaded images
- Multiple images: Analyze multiple images at once

**Compatible Vision Models:**
- OpenAI: GPT-4 Vision (`gpt-4-vision-preview`)
- Anthropic: Claude 3 models (Opus, Sonnet, Haiku)
- Google: Gemini Pro Vision (`gemini/gemini-pro-vision`)
- And more vision-enabled models via LiteLLM

### 🎨 Image Generation

Generate images from text descriptions using AI models:

```python
from bubbletea_chat import chatbot, Image, LLM

@chatbot
async def art_bot(prompt: str):
    """Generate images from descriptions"""
    llm = LLM(model="dall-e-3")  # or any image generation model
    
    # Generate an image
    image_url = await llm.agenerate_image(prompt)
    yield Image(image_url)
```

**Image Generation Features:**
- Text-to-image generation
- Support for DALL-E, Stable Diffusion, and other models
- Customizable parameters (size, quality, style)

### 📦 Components

**Video Component Features:**
- Embed videos from any URL (MP4, WebM, etc.)
- Works in web and mobile BubbleTea clients

**Video API:**
```python
Video(url: str)
```

#### Video Component Example
```python
@chatbot
async def video_bot(message: str):
    yield Text("Here's a video for you:")
    yield Video(
        url="https://www.w3schools.com/html/mov_bbb.mp4"
    )
    yield Text("Did you enjoy the video?")
```

#### Card Component Example

```python
from bubbletea_chat import chatbot, Card, Image, Text

@chatbot
async def card_bot(message: str):
    yield Text("Here's a card for you:")
    yield Card(
        image=Image(url="https://picsum.photos/id/237/200/300", alt="A dog"),
        text="This is a dog card.",
        card_value="dog_card_clicked"
    )
```

#### Pills Component Example

```python
from bubbletea_chat import chatbot, Pill, Pills, Text

@chatbot
async def pills_bot(message: str):
    yield Text("Choose your favorite fruit:")
    yield Pills(pills=[
        Pill(text="Apple", pill_value="apple_selected"),
        Pill(text="Banana", pill_value="banana_selected"),
        Pill(text="Orange", pill_value="orange_selected")
    ])
```

#### Error Component Example

```python
from bubbletea_chat import chatbot, Error, Text

@chatbot
async def error_handling_bot(message: str):
    if "error" in message.lower():
        # Return an error component with details
        return Error(
            title="Service Unavailable",
            description="The requested service is temporarily unavailable. Please try again later.",
            code="ERR_503"
        )
    elif "fail" in message.lower():
        # Simple error without description
        return Error(
            title="Operation Failed",
            code="ERR_001"
        )
    else:
        return Text("Try saying 'error' or 'fail' to see error messages.")
```

**Error Component Features:**
- **title** (required): The main error message to display
- **description** (optional): Additional context or instructions
- **code** (optional): Error code for debugging/support

The Error component is automatically styled with:
- Warning icon (⚠️)
- Red-themed design for visibility
- Clear formatting to distinguish from regular messages
- Support for retry functionality (when implemented by the frontend)

**Common Use Cases:**
- API failures
- Authentication errors
- Validation errors
- Service unavailability
- Rate limiting messages

### 🔄 Streaming Support

BubbleTea automatically detects generator functions and streams responses:

```python
@bt.chatbot
async def streaming_bot(message: str):
    yield bt.Text("Processing your request...")
    
    # Simulate some async work
    import asyncio
    await asyncio.sleep(1)
    
    yield bt.Markdown("## Here's your response")
    yield bt.Image("https://example.com/image.jpg")
    yield bt.Text("All done!")
```

### 🔍 User & Conversation Context

Starting with version 0.2.0, BubbleTea chat requests include UUID fields for tracking users and conversations:

```python
@bt.chatbot
def echo_bot(message: str, user_uuid: str = None, conversation_uuid: str = None, user_email: str = None):
    """A simple bot that echoes back the user's message"""
    response = f"You said: {message}"
    if user_uuid:
        response += f"\nYour User UUID: {user_uuid}"
    if conversation_uuid:
        response += f"\nYour Conversation UUID: {conversation_uuid}"
    if user_email:
        response += f"\nYour Email: {user_email}"

    return bt.Text(response)
```

The optional parameters that BubbleTea automatically includes in requests when available are:
- **user_uuid**: A unique identifier for the user making the request
- **conversation_uuid**: A unique identifier for the conversation/chat session
- **user_email**: The email address of the user making the request

You can use these to:
- Maintain conversation history
- Personalize responses based on user preferences
- Track usage analytics
- Implement stateful conversations
- Provide user-specific features based on email

### 🧵 Thread-based Conversation Support

BubbleTea now supports thread-based conversations using LiteLLM's threading capabilities. This allows for maintaining conversation context across multiple messages with support for OpenAI Assistants API and fallback for other models.

#### How It Works

1. **Backend Integration**: The backend stores a `thread_id` with each conversation
2. **Thread Creation**: On first message, if no thread exists, the bot creates one
3. **Thread Persistence**: The thread_id is stored in the backend for future messages
4. **Context Maintenance**: All messages in a thread maintain full conversation context


### 💬 Chat History

BubbleTea now supports passing chat history to your bots for context-aware conversations:

```python
@bt.chatbot
async def context_aware_bot(message: str, chat_history: list = None):
    """A bot that uses conversation history for context"""
    if chat_history:
        # chat_history is a list of 5 user messages and 5 bot messages dictionaries with metadata
        yield bt.Text(f"I see we have {previous_messages} previous messages in our conversation.")
        
        # You can use the history to provide contextual responses
        llm = LLM(model="gpt-4")
        context_prompt = f"Based on our conversation history: {chat_history}\n\nUser: {message}"
        response = await llm.acomplete(context_prompt)
        yield bt.Text(response)
    else:
        yield bt.Text("This seems to be the start of our conversation!")
```

### Multiple Bots with Unique Routes

You can create multiple bots in the same application, each with its own unique route:

```python
import bubbletea_chat as bt

# Bot 1: Available at /support
@bt.chatbot("support")
def support_bot(message: str):
    return bt.Text("Welcome to support! How can I help you?")

# Bot 2: Available at /sales
@bt.chatbot("sales")
def sales_bot(message: str):
    return bt.Text("Hi! I'm here to help with sales inquiries.")

# Bot 3: Default route at /chat
@bt.chatbot()
def general_bot(message: str):
    return bt.Text("Hello! I'm the general assistant.")

# This would raise ValueError - duplicate route!
# @bt.chatbot("support")
# def another_support_bot(message: str):
#     yield bt.Text("This won't work!")

if __name__ == "__main__":
    # Get all registered bots
    bt.run_server(port=8000)
```

**Important Notes:**
- Routes are case-sensitive: `/Bot1` is different from `/bot1`
- Each bot must have a unique route
- The default route is `/chat` if no route is specified
- Routes automatically get a leading `/` if not provided

## Examples

### AI-Powered Bots with LiteLLM

#### OpenAI GPT Bot

```python
import bubbletea_chat as bt
from bubbletea_chat import LLM

@bt.chatbot
async def gpt_assistant(message: str):
    # Make sure to set OPENAI_API_KEY environment variable
    llm = LLM(model="gpt-4")
    
    # Stream the response
    async for chunk in llm.stream(message):
        yield bt.Text(chunk)
```

#### Claude Bot

```python
@bt.chatbot
async def claude_bot(message: str):
    # Set ANTHROPIC_API_KEY environment variable
    llm = LLM(model="claude-3-sonnet-20240229")
    
    response = await llm.acomplete(message)
    yield bt.Text(response)
```

#### Gemini Bot

```python
@bt.chatbot
async def gemini_bot(message: str):
    # Set GEMINI_API_KEY environment variable
    llm = LLM(model="gemini/gemini-pro")
    
    async for chunk in llm.stream(message):
        yield bt.Text(chunk)
```

### Vision-Enabled Bot

Build bots that can analyze images using multimodal LLMs:

```python
from bubbletea_chat import chatbot, Text, Markdown, LLM, ImageInput

@chatbot
async def vision_bot(prompt: str, images: list = None):
    """
    A vision-enabled bot that can analyze images
    """
    llm = LLM(model="gpt-4-vision-preview", max_tokens=1000)
    
    if images:
        yield Text("I can see you've shared some images. Let me analyze them...")
        response = await llm.acomplete_with_images(prompt, images)
        yield Markdown(response)
    else:
        yield Markdown("""
## 📸 Vision Bot

I can analyze images! Try sending me:
- Screenshots to explain
- Photos to describe
- Diagrams to interpret
- Art to analyze

Just upload an image along with your question!

**Supported formats**: JPEG, PNG, GIF, WebP
        """)
```

**Key Features:**
- Accepts images along with text prompts
- Supports both URL and base64-encoded images
- Works with multiple images at once
- Compatible with various vision models

### Image Generation Bot

Create images from text descriptions:

```python
from bubbletea_chat import chatbot, Text, Markdown, LLM, Image

@chatbot
async def image_generator(prompt: str):
    """
    Generate images from text descriptions
    """
    llm = LLM(model="dall-e-3")  # Default image generation model
    
    if prompt:
        yield Text(f"🎨 Creating: {prompt}")
        # Generate image from the text prompt
        image_url = await llm.agenerate_image(prompt)
        yield Image(image_url)
        yield Text("✨ Your image is ready!")
    else:
        yield Markdown("""
## 🎨 AI Image Generator

I can create images from your text prompts!

Try prompts like:
- *"A futuristic cityscape at sunset"*
- *"A cute robot playing guitar in a forest"*
- *"An ancient map with fantasy landmarks"*

👉 Just type your description and I'll generate an image for you!
        """)
```

### Simple Echo Bot

```python
import bubbletea_chat as bt

@bt.chatbot
def echo_bot(message: str):
    return bt.Text(f"Echo: {message}")
```

### Multi-Modal Bot

```python
import bubbletea_chat as bt

@bt.chatbot
def multimodal_bot(message: str):
    yield bt.Markdown("# Welcome to the Multi-Modal Bot!")
    
    yield bt.Text("I can show you different types of content:")
    
    yield bt.Markdown("""
    - 📝 **Text** messages
    - 🖼️ **Images** with descriptions  
    - 📊 **Markdown** formatting
    """)
    
    yield bt.Image(
        "https://picsum.photos/400/300",
        alt="A random beautiful image"
    )
    
    yield bt.Text("Pretty cool, right? 😎")
```

### Streaming Bot

```python
import bubbletea_chat as bt
import asyncio

@bt.chatbot
async def streaming_bot(message: str):
    yield bt.Text("Hello! Let me process your message...")
    await asyncio.sleep(1)
    
    words = message.split()
    yield bt.Text("You said: ")
    for word in words:
        yield bt.Text(f"{word} ")
        await asyncio.sleep(0.3)
    
    yield bt.Markdown("## Analysis Complete!")
```

## API Reference

### Decorators

- `@bt.chatbot` - Create a chatbot from a function
- `@bt.chatbot(name="custom-name")` - Set a custom bot name
- `@bt.chatbot(stream=False)` - Force non-streaming mode
- `@bt.chatbot("route-name")` - Create a chatbot with a custom URL route (e.g., `/route-name`)

**Route Validation**: Each chatbot must have a unique URL path. If you try to register multiple bots with the same route, a `ValueError` will be raised.

**Optional Parameters**: Your chatbot functions can accept these optional parameters that BubbleTea provides automatically:
```python
@bt.chatbot
async def my_bot(
    message: str,                                    # Required: The user's message
    images: list = None,                            # Optional: List of ImageInput objects
    user_uuid: str = None,                          # Optional: Unique user identifier
    conversation_uuid: str = None,                  # Optional: Unique conversation identifier
    user_email: str = None,                         # Optional: User's email address
    chat_history: Union[List[Dict], str] = None     # Optional: Conversation history
):
    # Your bot logic here
    pass
```

### Components

- `bt.Text(content: str)` - Plain text message
- `bt.Image(url: str, alt: str = None)` - Image component
- `bt.Markdown(content: str)` - Markdown formatted text
- `bt.Card(image: Image, text: Optional[str] = None, markdown: Optional[Markdown] = None, card_value: Optional[str] = None)` - A single card component.
- `bt.Cards(cards: List[Card], orient: Literal["wide", "tall"] = "wide")` - A collection of cards.
- `bt.Pill(text: str, pill_value: Optional[str] = None)` - A single pill component.
- `bt.Pills(pills: List[Pill])` - A collection of pill items.
- `bt.Video(url: str)` - Video component
- `bt.Error(title: str, description: Optional[str] = None, code: Optional[str] = None)` - Error message component

### LLM Class

- `LLM(model: str, **kwargs)` - Initialize an LLM client
  - `model`: Any model supported by LiteLLM (e.g., "gpt-4", "claude-3-sonnet-20240229")
  - `assistant_id`: Optional assistant ID for thread-based conversations
  - `**kwargs`: Additional parameters (temperature, max_tokens, etc.)

#### Text Generation Methods:
- `complete(prompt: str, **kwargs) -> str` - Get a completion
- `acomplete(prompt: str, **kwargs) -> str` - Async completion
- `stream(prompt: str, **kwargs) -> AsyncGenerator[str, None]` - Stream a completion
- `with_messages(messages: List[Dict], **kwargs) -> str` - Use full message history
- `astream_with_messages(messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]` - Stream with messages

#### Vision/Image Analysis Methods:
- `complete_with_images(prompt: str, images: List[ImageInput], **kwargs) -> str` - Completion with images
- `acomplete_with_images(prompt: str, images: List[ImageInput], **kwargs) -> str` - Async with images
- `stream_with_images(prompt: str, images: List[ImageInput], **kwargs) -> AsyncGenerator` - Stream with images

#### Image Generation Methods:
- `generate_image(prompt: str, **kwargs) -> str` - Generate image (sync), returns URL
- `agenerate_image(prompt: str, **kwargs) -> str` - Generate image (async), returns URL

#### Thread-based Conversation Methods:
- `create_thread() -> Dict` - Create a new conversation thread
- `add_message(thread_id, content, role="user") -> Dict` - Add message to thread
- `run_thread(thread_id, instructions=None) -> str` - Run thread and get response
- `get_thread_messages(thread_id) -> List[Dict]` - Get all messages in thread
- `get_thread_status(thread_id, run_id) -> str` - Check thread run status

#### Assistant Creation Methods:
- `create_assistant(name, instructions, tools, **kwargs) -> str` - Create assistant (sync)
- `acreate_assistant(name, instructions, tools, **kwargs) -> str` - Create assistant (async)

### ThreadManager Class

A high-level thread management utility that simplifies thread operations:

```python
from bubbletea_chat import ThreadManager

# Initialize manager
manager = ThreadManager(
    assistant_id="asst_xxx",  # Optional: use existing assistant
    model="gpt-4",
    storage_path="threads.json"
)

# Get or create thread for user
thread_id = manager.get_or_create_thread("user_123")

# Add message
manager.add_user_message("user_123", "Hello!")

# Get response
response = manager.get_assistant_response("user_123")
```

Features:
- Automatic thread creation and management
- Persistent thread storage
- User-to-thread mapping
- Async support
- Message history retrieval
- Assistant creation and management

Methods:
- `create_assistant(name, instructions, tools, **kwargs) -> str` - Create assistant
- `async_create_assistant(name, instructions, tools, **kwargs) -> str` - Create assistant (async)
- `get_or_create_thread(user_id) -> str` - Get or create thread for user
- `add_user_message(user_id, message) -> bool` - Add user message
- `get_assistant_response(user_id, instructions=None) -> str` - Get AI response
- `get_thread_messages(user_id) -> List[Dict]` - Get conversation history
- `clear_user_thread(user_id)` - Clear a user's thread
- `clear_all_threads()` - Clear all threads

### ImageInput Class

Represents an image input that can be either a URL or base64 encoded:
```python
from bubbletea_chat import ImageInput

# URL image
ImageInput(url="https://example.com/image.jpg")

# Base64 image
ImageInput(
    base64="iVBORw0KGgoAAAANS...",
    mime_type="image/jpeg"  # Optional
)
```

### Server
```
if __name__ == "__main__":
    # Run the chatbot server
    bt.run_server(my_bot, port=8000, host="0.0.0.0")
```

- Runs a chatbot server on port 8000 and binds to host 0.0.0.0
  - Automatically creates a `/chat` endpoint for your bot
  - The `/chat` endpoint accepts POST requests with chat messages
  - Supports both streaming and non-streaming responses

## Environment Variables

To use different LLM providers, set the appropriate API keys:

```bash
# OpenAI
export OPENAI_API_KEY=your-openai-api-key

# Anthropic Claude
export ANTHROPIC_API_KEY=your-anthropic-api-key

# Google Gemini
export GEMINI_API_KEY=your-gemini-api-key

# Or use a .env file with python-dotenv
```

For more providers and configuration options, see the [LiteLLM documentation](https://docs.litellm.ai/docs/providers).

## Custom LLM Integration

While BubbleTea provides the `LLM` class for convenience, you can also use LiteLLM directly in your bots for more control:

```python
import bubbletea_chat as bt
from litellm import acompletion

@bt.chatbot
async def custom_llm_bot(message: str):
    # Direct LiteLLM usage
    response = await acompletion(
        model="gpt-4",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        # Add any custom parameters
        api_base="https://your-custom-endpoint.com",  # Custom endpoints
        custom_llm_provider="openai",  # Custom providers
    )
    
    yield bt.Text(response.choices[0].message.content)
```

This approach gives you access to:
- Custom API endpoints
- Advanced parameters
- Direct response handling
- Custom error handling
- Any LiteLLM feature

## Testing Your Bot

Start your bot:

```bash
python my_bot.py
```

Your bot will automatically create a `/chat` endpoint that accepts POST requests. This is the standard endpoint for all BubbleTea chatbots.

Test with curl:

```bash
# Text only
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"type": "user", "message": "Hello bot!"}'

# Test config endpoint
curl http://localhost:8000/config

# For bots on custom paths
# If your bot runs at /pillsbot:
curl -X POST "http://localhost:8000/pillsbot" \
  -H "Content-Type: application/json" \
  -d '{"type": "user", "message": "Hello bot!"}'

# Config endpoint for custom path bot
curl http://localhost:8000/pillsbot/config

# With image URL
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user",
    "message": "What is in this image?",
    "images": [{"url": "https://example.com/image.jpg"}]
  }'

# With base64 image
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user",
    "message": "Describe this",
    "images": [{"base64": "iVBORw0KGgoAAAANS...", "mime_type": "image/png"}]
  }'
```

## 🌐 CORS Support

BubbleTea includes automatic CORS (Cross-Origin Resource Sharing) support out of the box! This means your bots will work seamlessly with web frontends without any additional configuration.

### Default Behavior
```python
# CORS is enabled by default with permissive settings for development
bt.run_server(my_bot, port=8000)
```

### Custom CORS Configuration
```python
# For production - restrict to specific origins
bt.run_server(my_bot, port=8000, cors_config={
    "allow_origins": ["https://bubbletea.app", "https://yourdomain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["Content-Type", "Authorization"]
})
```

### Disable CORS
```python
# Not recommended, but possible
bt.run_server(my_bot, port=8000, cors=False)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
