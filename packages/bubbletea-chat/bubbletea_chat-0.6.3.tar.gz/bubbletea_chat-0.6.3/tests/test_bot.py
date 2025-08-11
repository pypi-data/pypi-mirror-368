"""
Test bot to demonstrate BubbleTea functionality (minimal version)
"""

import bubbletea as bt

@bt.chatbot
def test_bot(message: str):
    """A simple test bot"""
    yield bt.Text(f"Hello! You said: {message}")
    
    if "help" in message.lower():
        yield bt.Markdown("""
## Available Commands
- Say "image" to see an image
- Say "markdown" to see formatted text
- Say anything else for an echo response
        """)
    elif "image" in message.lower():
        yield bt.Text("Here's a nice image for you:")
        yield bt.Image("https://picsum.photos/400/300", alt="Random image")
    elif "markdown" in message.lower():
        yield bt.Markdown("""
# Markdown Example
This is **bold** and this is *italic*.

Here's a code block:
```python
print("Hello, BubbleTea!")
```
        """)
    else:
        yield bt.Text("Thanks for chatting!")
        yield bt.Text("Get help")


if __name__ == "__main__":
    print("Starting test bot on http://localhost:8000")
    print("Test with: curl -X POST 'http://localhost:8000/chat' -H 'Content-Type: application/json' -d '{\"type\": \"user\", \"message\": \"Hello!\"}'")
    bt.run_server(test_bot)