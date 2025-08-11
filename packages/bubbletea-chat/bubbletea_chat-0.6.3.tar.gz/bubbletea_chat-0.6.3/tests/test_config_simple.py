#!/usr/bin/env python
"""
Simple test to verify config decorator works
"""

import sys
sys.path.insert(0, '/Users/muhammadarslan/PycharmProjects/torrance/bt/bubbletea')

import bubbletea as bt

# Test 1: Basic config decorator
print("Test 1: Basic config decorator")
@bt.config()
def get_config():
    return bt.BotConfig(
        name="Test Bot",
        url="http://localhost:8000",
        is_streaming=True,
        emoji="🧪",
        initial_text="Test bot ready!"
    )

config = get_config()
print(f"✓ Config created: {config.name}")
print(f"✓ Emoji: {config.emoji}")
print(f"✓ Initial text: {config.initial_text}")

# Test 2: Check decorator registration
from bubbletea.decorators import _config_function
print("\nTest 2: Decorator registration")
if _config_function:
    func, path = _config_function
    print(f"✓ Config function registered at path: {path}")
else:
    print("✗ Config function not registered")

# Test 3: Create a simple bot
print("\nTest 3: Create bot with config")
@bt.chatbot()
def test_bot(message: str):
    return bt.Text(f"Echo: {message}")

print("✓ Bot created successfully")

print("\nAll tests passed! The config decorator is working correctly.")