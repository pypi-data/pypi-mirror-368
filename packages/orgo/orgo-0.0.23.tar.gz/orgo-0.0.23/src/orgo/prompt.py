# src/orgo/prompt.py
"""
Prompt module for interacting with virtual computers using AI models.
"""

import os
import base64
from typing import Dict, List, Any, Optional, Callable, Union, Protocol


class PromptProvider(Protocol):
    """Protocol defining the interface for prompt providers."""
    
    def execute(self, 
                computer_id: str,
                instruction: str,
                callback: Optional[Callable[[str, Any], None]] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """
        Execute a prompt to control the computer.
        
        Args:
            computer_id: ID of the computer to control
            instruction: User instruction
            callback: Optional progress callback function
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of messages from the conversation
        """
        ...


class AnthropicProvider:
    """Anthropic Claude-based prompt provider."""
    
    def __init__(self):
        """Initialize the Anthropic provider."""
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Please install with 'pip install anthropic'"
            )
    
    def execute(self,
                computer_id: str,
                instruction: str,
                callback: Optional[Callable[[str, Any], None]] = None,
                api_key: Optional[str] = None,
                model: str = "claude-3-7-sonnet-20250219",
                display_width: int = 1024,
                display_height: int = 768,
                orgo_api_key: Optional[str] = None,
                orgo_base_url: Optional[str] = None,
                max_saved_screenshots: int = 2,
                **kwargs) -> List[Dict[str, Any]]:
        """
        Execute a prompt using Anthropic's Claude.
        
        Args:
            computer_id: ID of the computer to control
            instruction: User instruction
            callback: Optional progress callback
            api_key: Anthropic API key
            model: Model to use
            display_width: Display width in pixels
            display_height: Display height in pixels
            orgo_api_key: API key for Orgo (passed to ApiClient)
            orgo_base_url: Base URL for Orgo API (passed to ApiClient)
            max_saved_screenshots: Maximum number of screenshots to maintain in conversation history
            **kwargs: Additional parameters to pass to the Anthropic API
            
        Returns:
            List of messages from the conversation
        """
        # Get API key from kwargs, env var, or raise error
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable or pass api_key.")
        
        # Initialize the client
        client = self.anthropic.Anthropic(api_key=api_key)
        
        # Prepare the messages
        messages = [{"role": "user", "content": instruction}]
        
        # Set up the system prompt
        system_prompt = f"""You are Claude, an AI assistant that controls a virtual Ubuntu computer with internet access.

<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine with a display resolution of {display_width}x{display_height}.
* You can take screenshots to see the current state and control the computer by clicking, typing, pressing keys, and scrolling.
* The virtual environment is an Ubuntu system with standard applications.
* Always start by taking a screenshot to see the current state before performing any actions.
</SYSTEM_CAPABILITY>

<UBUNTU_DESKTOP_GUIDELINES>
* CRITICAL INSTRUCTION: When opening applications or files on the Ubuntu desktop, you MUST USE DOUBLE-CLICK rather than single-click.
* Single-click only selects desktop icons but DOES NOT open them. To open desktop icons, you MUST use double-click.
* Common desktop interactions:
  - Desktop icons: DOUBLE-CLICK to open applications and folders
  - Menu items: SINGLE-CLICK to select options
  - Taskbar icons: SINGLE-CLICK to open applications
  - Window buttons: SINGLE-CLICK to use close, minimize, maximize buttons
  - File browser items: DOUBLE-CLICK to open folders and files
  - When submitting, use the 'Enter' key, not the 'Return' key.
* If you see an icon on the desktop that you need to open, ALWAYS use the double_click action, never use left_click.
</UBUNTU_DESKTOP_GUIDELINES>

<SCREENSHOT_GUIDELINES>
* Be mindful of how many screenshots you take - they consume significant memory.
* Only take screenshots when you need to see the current state of the screen.
* Try to batch multiple actions before taking another screenshot.
* For better performance, limit the number of screenshots you take.
</SCREENSHOT_GUIDELINES>"""
        
        try:
            # Define the computer tool per Anthropic's documentation
            tools = [
                {
                    "type": "computer_20250124",
                    "name": "computer",
                    "display_width_px": display_width,
                    "display_height_px": display_height,
                    "display_number": 1
                }
            ]
            
            # Start the conversation with Claude
            if callback:
                callback("status", "Starting conversation with Claude")
            
            # Track whether we're in the agent loop
            iteration = 0
            max_iterations = kwargs.get("max_iterations", 20)  # Default to 20 iterations max
            
            # Create an API client with the proper settings
            from .api.client import ApiClient
            api_client = ApiClient(orgo_api_key, orgo_base_url)
            
            # Track how many screenshots we've seen so we can prune when needed
            screenshot_count = 0
            
            # Start the agent loop
            while iteration < max_iterations:
                iteration += 1
                
                # Filter to keep only the N most recent screenshots
                if screenshot_count > max_saved_screenshots:
                    self._filter_to_n_most_recent_images(messages, max_saved_screenshots)
                    screenshot_count = max_saved_screenshots
                
                # Create the request parameters
                request_params = {
                    "model": model,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "system": system_prompt,
                    "messages": messages,
                    "tools": tools,
                    "betas": ["computer-use-2025-01-24"],
                }
                
                # Add thinking parameter only if explicitly enabled
                if kwargs.get("thinking_enabled"):
                    request_params["thinking"] = {
                        "type": "enabled", 
                        "budget_tokens": kwargs.get("thinking_budget", 1024)
                    }
                
                # Create message request to Claude
                try:
                    response = client.beta.messages.create(**request_params)
                except Exception as e:
                    if "base64" in str(e).lower():
                        # If we get a base64 error, try again after more aggressively filtering images
                        if callback:
                            callback("error", f"Base64 error detected. Attempting recovery...")
                        
                        # Remove all but the most recent image and try again
                        self._filter_to_n_most_recent_images(messages, 1)
                        response = client.beta.messages.create(**request_params)
                    else:
                        # Not a base64 error, re-raise
                        raise
                
                # Extract the content from the response
                response_content = response.content
                
                # Add Claude's response to the conversation history
                assistant_message = {"role": "assistant", "content": response_content}
                messages.append(assistant_message)
                
                # Notify callback of any text content
                for block in response_content:
                    if block.type == "text" and callback:
                        callback("text", block.text)
                    elif block.type == "thinking" and callback:
                        callback("thinking", block.thinking)
                    elif block.type == "tool_use" and callback:
                        tool_params = {
                            "action": block.name.split(".")[-1],
                            **block.input
                        }
                        callback("tool_use", tool_params)
                
                # Check if Claude requested any tool actions
                tool_results = []
                for block in response_content:
                    if block.type == "tool_use":
                        # Execute the tool action
                        result = self._execute_tool(computer_id, block.input, callback, api_client)
                        
                        # Format the result for Claude
                        tool_result = {
                            "type": "tool_result",
                            "tool_use_id": block.id
                        }
                        
                        # Handle image vs text results
                        if isinstance(result, dict) and "type" in result and result["type"] == "image":
                            tool_result["content"] = [result]
                            # Increment screenshot count when we add a new screenshot
                            if block.input.get("action") == "screenshot":
                                screenshot_count += 1
                        else:
                            tool_result["content"] = [{"type": "text", "text": str(result)}]
                        
                        tool_results.append(tool_result)
                
                # If no tools were used, Claude is done - return the messages
                if not tool_results:
                    if callback:
                        callback("status", "Task completed")
                    return messages
                
                # Add tool results to messages for the next iteration
                messages.append({"role": "user", "content": tool_results})
            
            # We've reached the maximum iteration limit
            if callback:
                callback("status", f"Reached maximum iterations ({max_iterations})")
            
            return messages
            
        except Exception as e:
            if callback:
                callback("error", str(e))
            raise
    
    def _filter_to_n_most_recent_images(self, messages: List[Dict[str, Any]], max_images: int):
        """
        Keep only the N most recent images in the conversation history.
        
        Args:
            messages: The conversation history
            max_images: Maximum number of images to keep
        """
        # Find all the image blocks in the conversation history
        image_blocks = []
        
        for msg_idx, msg in enumerate(messages):
            if msg["role"] != "user":
                continue
                
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
                
            for content_idx, block in enumerate(content):
                if not isinstance(block, dict):
                    continue
                    
                if block.get("type") != "tool_result":
                    continue
                
                block_content = block.get("content", [])
                for content_item_idx, content_item in enumerate(block_content):
                    if not isinstance(content_item, dict):
                        continue
                        
                    if content_item.get("type") == "image" and "source" in content_item:
                        image_blocks.append({
                            "msg_idx": msg_idx,
                            "content_idx": content_idx,
                            "block": block,
                            "content_item_idx": content_item_idx,
                            "content_item": content_item
                        })
        
        # If we have more images than our limit, remove the oldest ones
        if len(image_blocks) > max_images:
            # Keep only the most recent ones (which are at the end of the list)
            images_to_remove = image_blocks[:-max_images]
            
            for img_block in images_to_remove:
                content_item = img_block["content_item"]
                if "source" in content_item and "data" in content_item["source"]:
                    # Replace with a minimal valid base64 image (1x1 transparent PNG)
                    content_item["source"]["data"] = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    content_item["source"]["media_type"] = "image/png"
    
    def _execute_tool(self, 
                      computer_id: str,
                      params: Dict[str, Any], 
                      callback: Optional[Callable[[str, Any], None]] = None,
                      api_client = None) -> Union[str, Dict[str, Any]]:
        """Execute a tool action via the API client."""
        action = params.get("action")
        
        if callback:
            callback("tool_executing", {"action": action, "params": params})
        
        try:
            # Use the provided API client or create a new one
            if api_client is None:
                # Import here to avoid circular imports
                from .api.client import ApiClient
                api_client = ApiClient()
            
            # Map actions to API methods
            if action == "screenshot":
                response = api_client.get_screenshot(computer_id)
                if callback:
                    callback("tool_result", {"type": "image", "action": "screenshot"})
                
                # The API now returns a URL instead of base64 data
                # We need to fetch the image from the URL and convert it to base64
                image_url = response.get("image", "")
                
                if not image_url:
                    raise ValueError("No image URL received from API")
                
                # Fetch the image from the URL
                import requests
                img_response = requests.get(image_url)
                img_response.raise_for_status()
                
                # Convert to base64
                image_base64 = base64.b64encode(img_response.content).decode('utf-8')
                
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                }
                
            elif action == "left_click":
                if not params.get("coordinate"):
                    raise ValueError("Coordinates required for left click")
                x, y = params["coordinate"]
                api_client.left_click(computer_id, x, y)
                if callback:
                    callback("tool_result", {"action": "left_click", "x": x, "y": y})
                return f"Left-clicked at ({x}, {y})"
                
            elif action == "right_click":
                if not params.get("coordinate"):
                    raise ValueError("Coordinates required for right click")
                x, y = params["coordinate"]
                api_client.right_click(computer_id, x, y)
                if callback:
                    callback("tool_result", {"action": "right_click", "x": x, "y": y})
                return f"Right-clicked at ({x}, {y})"
                
            elif action == "double_click":
                if not params.get("coordinate"):
                    raise ValueError("Coordinates required for double click")
                x, y = params["coordinate"]
                api_client.double_click(computer_id, x, y)
                if callback:
                    callback("tool_result", {"action": "double_click", "x": x, "y": y})
                return f"Double-clicked at ({x}, {y})"
                
            elif action == "type":
                if not params.get("text"):
                    raise ValueError("Text required for typing")
                text = params["text"]
                api_client.type_text(computer_id, text)
                if callback:
                    callback("tool_result", {"action": "type", "text": text})
                return f"Typed: \"{text}\""
                
            elif action == "key":
                if not params.get("text"):
                    raise ValueError("Key required for key press")
                key = params["text"]
                # Handle the 'return' key as 'enter' when needed
                if key.lower() == "return":
                    key = "enter"
                api_client.key_press(computer_id, key)
                if callback:
                    callback("tool_result", {"action": "key", "key": key})
                return f"Pressed key: {key}"
                
            elif action == "scroll":
                if not params.get("scroll_direction") or params.get("scroll_amount") is None:
                    raise ValueError("Direction and amount required for scrolling")
                direction = params["scroll_direction"]
                amount = params["scroll_amount"]
                api_client.scroll(computer_id, direction, amount)
                if callback:
                    callback("tool_result", {"action": "scroll", "direction": direction, "amount": amount})
                return f"Scrolled {direction} by {amount}"
                
            elif action == "wait":
                duration = params.get("duration", 1)
                api_client.wait(computer_id, duration)
                if callback:
                    callback("tool_result", {"action": "wait", "duration": duration})
                return f"Waited for {duration} second(s)"
                
            else:
                error_msg = f"Unsupported action: {action}"
                if callback:
                    callback("error", error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Error executing {action}: {str(e)}"
            if callback:
                callback("error", error_msg)
            return f"Error: {error_msg}"


# Default provider mapping
PROVIDER_MAPPING = {
    "anthropic": AnthropicProvider,
    # Add more providers here as needed, e.g.:
    # "openai": OpenAIProvider,
    # "fireworks": FireworksProvider,
}


def get_provider(provider_name: str = "anthropic") -> PromptProvider:
    """
    Get a prompt provider by name.
    
    Args:
        provider_name: Name of the provider
        
    Returns:
        Provider instance
    """
    if provider_name not in PROVIDER_MAPPING:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: {', '.join(PROVIDER_MAPPING.keys())}")
    
    return PROVIDER_MAPPING[provider_name]()