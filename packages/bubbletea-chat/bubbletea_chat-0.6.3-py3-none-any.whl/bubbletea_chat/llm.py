"""
LiteLLM integration for easy LLM calls in BubbleTea bots
"""

from typing import List, Dict, Optional, AsyncGenerator, Union
import litellm
from litellm import acompletion, completion, image_generation, aimage_generation
from litellm.assistants.main import (
    create_thread,
    add_message,
    run_thread,
    create_assistants,
    get_messages,
)
from .schemas import ImageInput
from datetime import datetime


class LLM:
    """
    Simple wrapper around LiteLLM for easy LLM calls
    
    Example:
        llm = LLM(model="gpt-3.5-turbo")
        response = llm.complete("Hello, how are you?")
        
        # Streaming
        async for chunk in llm.stream("Tell me a story"):
            yield Text(chunk)
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model
        self.default_params = kwargs
        self.llm_provider = kwargs.get("llm_provider", None)
        self.assistant_id = kwargs.get("assistant_id", None)

        # Initialize assistant if not provided
        if not self.assistant_id:
            self._initialize_assistant()

    def _format_message_with_images(
        self, content: str, images: Optional[List[ImageInput]] = None
    ) -> Union[str, List[Dict]]:
        """Format message content with images for multimodal models"""
        if not images:
            return content
        
        # Create multimodal content array
        content_parts = [{"type": "text", "text": content}]
        
        for img in images:
            if img.url:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": img.url}
                })
            elif img.base64:
                if img.base64.startswith("data:"):
                    # If base64 already starts with 'data:', use it directly
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": img.base64}
                    })
                else:
                    # Format base64 image with proper data URI
                    mime_type = img.mime_type or "image/jpeg"
                    image_url = f"data:{mime_type};base64,{img.base64}"
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })
        
        return content_parts
    
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters to pass to litellm
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def acomplete(self, prompt: str, **kwargs) -> str:
        """
        Async version of complete()
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters to pass to litellm
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def with_messages(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Get a completion with full message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to pass to litellm
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def astream_with_messages(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion with full message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to pass to litellm
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def complete_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> str:
        """
        Get a completion from the LLM with images
        
        Args:
            prompt: The text prompt
            images: List of ImageInput objects (URLs or base64)
            **kwargs: Additional parameters
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def acomplete_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> str:
        """
        Async version of complete_with_images()
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def stream_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM with images
        
        Args:
            prompt: The text prompt
            images: List of ImageInput objects
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generate an image using an image generation model like DALL·E.
        Returns the image URL.
        """
        params = {**self.default_params, **kwargs}
        response = image_generation(prompt=prompt, **params)
        return response.data[0].url

    async def agenerate_image(self, prompt: str, **kwargs) -> str:
        """
        Async version of generate_image.
        """
        params = {**self.default_params, **kwargs}
        response = await aimage_generation(prompt=prompt, **params)
        return response.data[0].url

    def _initialize_assistant(
        self,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List] = None,
        **kwargs,
    ):
        """Create the assistant using LiteLLM"""
        try:
            params = {
                "custom_llm_provider": self.llm_provider or "openai",
                "model": self.model,
                "name": name or f"BubbleTea Assistant - {datetime.now().isoformat()}",
                "instructions": instructions
                or "You are a helpful assistant created by BubbleTea.",
            }

            if tools:
                params["tools"] = tools

            # Add any additional parameters
            params.update(kwargs)

            response = create_assistants(**params)

            # Extract assistant ID from response
            if isinstance(response, dict) and "id" in response:
                self.assistant_id = response["id"]
            elif hasattr(response, "id"):
                self.assistant_id = response.id
            else:
                # If response is a string, it might be the full object representation
                # Try to extract the ID from the string
                response_str = str(response)
                if "id=" in response_str:
                    # Extract ID from string like "Assistant(id='asst_xxx', ...)"
                    import re

                    match = re.search(r"id='([^']+)'", response_str)
                    if match:
                        self.assistant_id = match.group(1)
                    else:
                        print(
                            f"Could not extract assistant ID from response: {response_str[:100]}"
                        )
                        self.assistant_id = None
                else:
                    print(f"Unexpected response format: {response_str[:100]}")
                    self.assistant_id = None

            print(f"Extracted assistant ID: {self.assistant_id}")

        except Exception as e:
            print(f"Error creating assistant: {e}")
            self.assistant_id = None

    def create_thread(self, user_uuid: str) -> Optional[str]:
        """Get existing thread or create new one for user"""
        try:
            new_thread = create_thread(
                custom_llm_provider="openai", messages=[]  # Start with empty thread
            )
            print(f"Created thread: {new_thread}")

            # Handle different response formats
            if isinstance(new_thread, dict):
                thread_id = new_thread.get("id")
            elif hasattr(new_thread, "id"):
                thread_id = new_thread.id
            else:
                thread_id = str(new_thread)

            if thread_id:
                return thread_id
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    def add_user_message(self, thread_id: str, message: str) -> bool:
        """Add user message to their thread"""
        if not thread_id:
            return False

        try:
            result = add_message(
                thread_id=thread_id,
                role="user",
                content=message,
                custom_llm_provider=self.llm_provider,
            )
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False

    def get_assistant_response(self, thread_id: str, message: str) -> Optional[str]:
        """Get assistant response for the user's thread"""
        if not self.assistant_id:
            print("No assistant ID available")
            return None

        if not thread_id:
            print("No thread ID available")
            return None

        try:
            result = add_message(
                thread_id=thread_id,
                role="user",
                content=message,
                custom_llm_provider=self.llm_provider,
            )

            run_response = run_thread(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                custom_llm_provider=self.llm_provider,
            )

            messages = get_messages(
                thread_id=thread_id, custom_llm_provider=self.llm_provider
            )

            if hasattr(messages, "data") and messages.data:
                assistant_messages = [
                    msg for msg in messages.data if msg.role == "assistant"
                ]
                if assistant_messages:
                    last_msg = assistant_messages[-1]
                    if last_msg.content and len(last_msg.content) > 0:
                        return last_msg.content[0].text.value

            # Fallback: handle different response structures
            if isinstance(run_response, str):
                return run_response
            elif isinstance(run_response, dict):
                # Check for data field (OpenAI format)
                if "data" in run_response:
                    response_messages = run_response["data"]
                    if response_messages and len(response_messages) > 0:
                        last_msg = response_messages[-1]
                        if isinstance(last_msg, dict) and "content" in last_msg:
                            content = last_msg["content"]
                            if isinstance(content, list) and len(content) > 0:
                                return content[0].get("text", {}).get("value")
                            elif isinstance(content, str):
                                return content
                # Check for direct message field
                elif "message" in run_response:
                    return run_response["message"]
                # Check for content field
                elif "content" in run_response:
                    return run_response["content"]
            return None
        except Exception as e:
            print(f"Error getting response: {e}")
            return None
