#!/usr/bin/env python3
"""
Test script to verify all image-related features in BubbleTea package
"""

import asyncio
import os
from bubbletea_chat import chatbot, Text, Image, Markdown, LLM, ImageInput


async def test_image_generation():
    """Test image generation functionality"""
    print("\n=== Testing Image Generation ===")
    
    try:
        llm = LLM(model="dall-e-3")
        prompt = "A peaceful zen garden with cherry blossoms"
        
        print(f"Generating image: {prompt}")
        image_url = await llm.agenerate_image(prompt)
        print(f"✅ Image generated successfully: {image_url}")
        return True
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return False


async def test_vision_analysis():
    """Test vision/image analysis functionality"""
    print("\n=== Testing Vision Analysis ===")
    
    try:
        llm = LLM(model="gpt-4-vision-preview")
        
        # Test with URL image
        test_image = ImageInput(url="https://picsum.photos/400/300")
        prompt = "Describe what you see in this image"
        
        print(f"Analyzing image with prompt: {prompt}")
        response = await llm.acomplete_with_images(prompt, [test_image])
        print(f"✅ Vision analysis successful")
        print(f"Response preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Vision analysis failed: {e}")
        return False


async def test_streaming_vision():
    """Test streaming with vision"""
    print("\n=== Testing Streaming Vision ===")
    
    try:
        llm = LLM(model="gpt-4-vision-preview")
        test_image = ImageInput(url="https://picsum.photos/400/300")
        
        print("Streaming vision analysis...")
        chunks = []
        async for chunk in llm.stream_with_images("What's in this image?", [test_image]):
            chunks.append(chunk)
        
        print(f"✅ Streaming vision successful - received {len(chunks)} chunks")
        return True
    except Exception as e:
        print(f"❌ Streaming vision failed: {e}")
        return False


async def test_chatbot_with_images():
    """Test chatbot decorator with image support"""
    print("\n=== Testing Chatbot with Images ===")
    
    @chatbot
    async def test_bot(message: str, images: list = None):
        if images:
            yield Text(f"Received {len(images)} images")
            yield Text(f"Message: {message}")
        else:
            yield Text("No images received")
    
    try:
        # Test without images
        print("Testing chatbot without images...")
        result = await test_bot("Hello", None)
        if hasattr(result, '__aiter__'):
            async for component in result:
                print(f"  Component: {component}")
        
        # Test with images
        print("Testing chatbot with images...")
        test_images = [ImageInput(url="https://example.com/image.jpg")]
        result = await test_bot("Analyze this", test_images)
        if hasattr(result, '__aiter__'):
            async for component in result:
                print(f"  Component: {component}")
        
        print("✅ Chatbot image support working")
        return True
    except Exception as e:
        print(f"❌ Chatbot image test failed: {e}")
        return False


async def test_image_component():
    """Test Image component rendering"""
    print("\n=== Testing Image Component ===")
    
    try:
        # Test basic image
        img1 = Image("https://example.com/test.jpg")
        print(f"✅ Basic image component: {img1}")
        
        # Test image with alt text
        img2 = Image("https://example.com/test.jpg", alt="Test image")
        print(f"✅ Image with alt text: {img2}")
        
        return True
    except Exception as e:
        print(f"❌ Image component test failed: {e}")
        return False


async def test_base64_image():
    """Test base64 image handling"""
    print("\n=== Testing Base64 Image ===")
    
    try:
        # Create a base64 image input
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        base64_image = ImageInput(base64=base64_data, mime_type="image/png")
        
        print(f"✅ Base64 image created: {base64_image}")
        return True
    except Exception as e:
        print(f"❌ Base64 image test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 BubbleTea Image Features Test Suite")
    print("=" * 50)
    
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    print(f"API Keys detected:")
    print(f"  OpenAI: {'✅' if has_openai else '❌'}")
    print(f"  Anthropic: {'✅' if has_anthropic else '❌'}")
    
    # Run tests
    tests = [
        ("Image Component", test_image_component),
        ("Base64 Image", test_base64_image),
        ("Chatbot with Images", test_chatbot_with_images),
    ]
    
    # Only run API tests if keys are available
    if has_openai:
        tests.extend([
            ("Image Generation", test_image_generation),
            ("Vision Analysis", test_vision_analysis),
            ("Streaming Vision", test_streaming_vision),
        ])
    else:
        print("\n⚠️  Skipping API tests - no OpenAI key found")
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")


if __name__ == "__main__":
    asyncio.run(main())