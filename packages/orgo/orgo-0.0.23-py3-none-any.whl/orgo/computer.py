"""Computer class for interacting with Orgo virtual environments"""
import os
import io
import base64
import logging
from typing import Dict, List, Any, Optional, Callable, Literal
from PIL import Image
import requests
from requests.exceptions import RequestException

from .api.client import ApiClient
from .prompt import get_provider
from .project import ProjectManager

logger = logging.getLogger(__name__)

class Computer:
    def __init__(self, 
                 project_id: Optional[str] = None, 
                 api_key: Optional[str] = None, 
                 config: Optional[Dict[str, Any]] = None, 
                 base_api_url: Optional[str] = None,
                 ram: Optional[Literal[2, 4]] = None,
                 memory: Optional[Literal[2, 4]] = None,
                 cpu: Optional[Literal[2, 4]] = None):
        """
        Initialize an Orgo virtual computer.
        
        Args:
            project_id: Existing project ID to connect to (optional)
            api_key: Orgo API key (defaults to ORGO_API_KEY env var)
            config: Configuration for new computer (optional)
            base_api_url: Custom API URL (optional)
            ram: RAM in GB for new computer (2 or 4) - only used when creating
            memory: Alternative parameter for RAM in GB (2 or 4) - only used when creating
            cpu: CPU cores for new computer (2 or 4) - only used when creating
        
        Note: If both ram and memory are provided, ram takes precedence.
        """
        self.api_key = api_key or os.environ.get("ORGO_API_KEY")
        self.base_api_url = base_api_url
        self.api = ApiClient(self.api_key, self.base_api_url)
        
        # Handle memory parameter as an alias for ram
        if ram is None and memory is not None:
            ram = memory
        
        # Look for a saved project ID if none was provided
        if project_id is None:
            project_id = ProjectManager.load_project_id()
        
        if project_id:
            try:
                self.project_id = project_id
                self._info = self.api.connect_computer(project_id)
                # Log if ram/memory/cpu were provided but ignored
                if ram is not None or memory is not None or cpu is not None:
                    logger.info("Note: ram, memory, and cpu parameters are ignored when connecting to existing computer")
            except (RequestException, ValueError) as e:
                logger.warning(f"Could not connect to saved project {project_id}: {e}")
                self._create_new_computer(config, ram, cpu)
        else:
            self._create_new_computer(config, ram, cpu)
            
    def _create_new_computer(self, config: Optional[Dict[str, Any]] = None, 
                           ram: Optional[Literal[2, 4]] = None,
                           cpu: Optional[Literal[2, 4]] = None):
        """Create a new computer instance and save its ID"""
        # Validate ram and cpu values if provided
        if ram is not None and ram not in [2, 4]:
            raise ValueError("ram/memory must be either 2 or 4 GB")
        if cpu is not None and cpu not in [2, 4]:
            raise ValueError("cpu must be either 2 or 4 cores")
        
        # Build the config with ram and cpu if provided
        if ram is not None or cpu is not None:
            if config is None:
                config = {}
            else:
                # Make a copy to avoid modifying the original
                config = config.copy()
            
            # Add ram and cpu to config
            if ram is not None:
                config['ram'] = ram
            if cpu is not None:
                config['cpu'] = cpu
        
        response = self.api.create_computer(config)
        self.project_id = response.get("name")
        self._info = response
        
        if not self.project_id:
            raise ValueError("Failed to initialize computer: No project ID returned")
            
        # Save the project ID for future use
        ProjectManager.save_project_id(self.project_id)
    
    def status(self) -> Dict[str, Any]:
        """Get current computer status"""
        return self.api.get_status(self.project_id)
    
    def start(self) -> Dict[str, Any]:
        """Start the computer"""
        return self.api.start_computer(self.project_id)
    
    def stop(self) -> Dict[str, Any]:
        """Stop the computer"""
        return self.api.stop_computer(self.project_id)
    
    def restart(self) -> Dict[str, Any]:
        """Restart the computer"""
        return self.api.restart_computer(self.project_id)
    
    def destroy(self) -> Dict[str, Any]:
        """Terminate and delete the computer instance"""
        result = self.api.delete_computer(self.project_id)
        # Clear the local project cache after destroying
        ProjectManager.clear_project_cache()
        return result
    
    # Navigation methods
    def left_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform left mouse click at specified coordinates"""
        return self.api.left_click(self.project_id, x, y)
    
    def right_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform right mouse click at specified coordinates"""
        return self.api.right_click(self.project_id, x, y)
    
    def double_click(self, x: int, y: int) -> Dict[str, Any]:
        """Perform double click at specified coordinates"""
        return self.api.double_click(self.project_id, x, y)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: str = "left", duration: float = 0.5) -> Dict[str, Any]:
        """
        Perform a smooth drag operation from start to end coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            button: Mouse button to use ("left" or "right", default: "left")
            duration: Duration of the drag in seconds (0.1 to 5.0, default: 0.5)
            
        Returns:
            Dict with operation result
        """
        return self.api.drag(self.project_id, start_x, start_y, end_x, end_y, button, duration)
    
    def scroll(self, direction: str = "down", amount: int = 1) -> Dict[str, Any]:
        """Scroll in specified direction and amount"""
        return self.api.scroll(self.project_id, direction, amount)
    
    # Input methods
    def type(self, text: str) -> Dict[str, Any]:
        """Type the specified text"""
        return self.api.type_text(self.project_id, text)
    
    def key(self, key: str) -> Dict[str, Any]:
        """Press a key or key combination (e.g., "Enter", "ctrl+c")"""
        return self.api.key_press(self.project_id, key)
    
    # View methods
    def screenshot(self) -> Image.Image:
        """Capture screenshot and return as PIL Image"""
        response = self.api.get_screenshot(self.project_id)
        image_data = response.get("image", "")
        
        # Check if it's a URL (new format) or base64 (legacy format)
        if image_data.startswith(('http://', 'https://')):
            # Download image from URL
            img_response = requests.get(image_data)
            img_response.raise_for_status()
            return Image.open(io.BytesIO(img_response.content))
        else:
            # Legacy base64 format
            img_data = base64.b64decode(image_data)
            return Image.open(io.BytesIO(img_data))
    
    def screenshot_base64(self) -> str:
        """Capture screenshot and return as base64 string"""
        response = self.api.get_screenshot(self.project_id)
        image_data = response.get("image", "")
        
        # Check if it's a URL (new format) or base64 (legacy format)
        if image_data.startswith(('http://', 'https://')):
            # Download image from URL and convert to base64
            img_response = requests.get(image_data)
            img_response.raise_for_status()
            return base64.b64encode(img_response.content).decode('utf-8')
        else:
            # Already base64
            return image_data
    
    # Execution methods
    def bash(self, command: str) -> str:
        """Execute a bash command and return output"""
        response = self.api.execute_bash(self.project_id, command)
        return response.get("output", "")
    
    def exec(self, code: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Execute Python code on the remote computer.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds (default: 10, max: 300)
            
        Returns:
            Dict with keys:
            - success: bool indicating if execution completed without errors
            - output: str containing stdout output
            - error: str containing error message if any
            - error_type: str with exception type name if error occurred
            - timeout: bool indicating if execution timed out
            
        Example:
            result = computer.exec('''
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")
            ''')
            
            if result['success']:
                print(result['output'])
            else:
                print(f"Error: {result['error']}")
        """
        response = self.api.execute_python(self.project_id, code, timeout)
        return response
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """Wait for specified number of seconds"""
        return self.api.wait(self.project_id, seconds)
    
    # AI control method
    def prompt(self, 
               instruction: str,
               provider: str = "anthropic",
               model: str = "claude-3-7-sonnet-20250219",
               display_width: int = 1024,
               display_height: int = 768,
               callback: Optional[Callable[[str, Any], None]] = None,
               thinking_enabled: bool = False,
               thinking_budget: int = 1024,
               max_tokens: int = 4096,
               max_iterations: int = 20,
               max_saved_screenshots: int = 5,
               api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Control the computer with natural language instructions using an AI assistant.
        
        Args:
            instruction: What you want the AI to do with the computer
            provider: AI provider to use (default: "anthropic")
            model: Model to use (default: "claude-3-7-sonnet-20250219")
            display_width: Screen width in pixels
            display_height: Screen height in pixels
            callback: Optional callback function for progress updates
            thinking_enabled: Enable Claude's thinking capability (default: False)
            thinking_budget: Token budget for thinking (default: 1024)
            max_tokens: Maximum tokens for model response
            max_iterations: Maximum number of agent loop iterations
            max_saved_screenshots: Maximum number of screenshots to keep in history (default: 5)
            api_key: API key for the AI provider (defaults to env var)
            
        Returns:
            List of messages from the conversation
        """
        # Get the provider instance
        provider_instance = get_provider(provider)
        
        # Execute the prompt
        return provider_instance.execute(
            computer_id=self.project_id,
            instruction=instruction,
            callback=callback,
            api_key=api_key,
            model=model,
            display_width=display_width,
            display_height=display_height,
            thinking_enabled=thinking_enabled,
            thinking_budget=thinking_budget,
            max_tokens=max_tokens,
            max_iterations=max_iterations,
            max_saved_screenshots=max_saved_screenshots,
            # Pass through the Orgo API client configuration
            orgo_api_key=self.api_key,
            orgo_base_url=self.base_api_url
        )