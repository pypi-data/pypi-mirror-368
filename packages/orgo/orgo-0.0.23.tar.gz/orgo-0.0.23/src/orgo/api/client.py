"""API client for Orgo service"""

import requests
from typing import Dict, Any, Optional

from orgo.utils.auth import get_api_key

class ApiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = get_api_key(api_key)
        self.base_url = base_url or "https://www.orgo.ai/api"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            else:
                response = self.session.request(method, url, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_message = f"API error: {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_message += f" - {error_data['error']}"
                except ValueError:
                    pass
                raise Exception(error_message) from e
            raise Exception(f"Connection error: {str(e)}") from e
    
    # Computer lifecycle methods
    def create_computer(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new project with desktop instance"""
        payload = {}
        if config:
            payload["config"] = config
        return self._request("POST", "projects", payload if payload else None)
    
    def connect_computer(self, project_id: str) -> Dict[str, Any]:
        return self._request("GET", f"projects/by-name/{project_id}")
    
    def get_status(self, project_id: str) -> Dict[str, Any]:
        return self._request("GET", f"projects/by-name/{project_id}")
    
    def start_computer(self, project_name: str) -> Dict[str, Any]:
        # Get the actual project ID from the name
        project = self.get_status(project_name)
        project_id = project.get("id")
        if not project_id:
            raise ValueError(f"Could not find ID for project {project_name}")
        return self._request("POST", f"projects/{project_id}/start")
    
    def stop_computer(self, project_name: str) -> Dict[str, Any]:
        # Get the actual project ID from the name
        project = self.get_status(project_name)
        project_id = project.get("id")
        if not project_id:
            raise ValueError(f"Could not find ID for project {project_name}")
        return self._request("POST", f"projects/{project_id}/stop")
    
    def restart_computer(self, project_name: str) -> Dict[str, Any]:
        # Get the actual project ID from the name
        project = self.get_status(project_name)
        project_id = project.get("id")
        if not project_id:
            raise ValueError(f"Could not find ID for project {project_name}")
        return self._request("POST", f"projects/{project_id}/restart")
    
    def delete_computer(self, project_name: str) -> Dict[str, Any]:
        # Get the actual project ID from the name
        project = self.get_status(project_name)
        project_id = project.get("id")
        if not project_id:
            raise ValueError(f"Could not find ID for project {project_name}")
        return self._request("POST", f"projects/{project_id}/delete")
    
    # Computer control methods
    def left_click(self, project_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/click", {
            "button": "left", "x": x, "y": y
        })
    
    def right_click(self, project_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/click", {
            "button": "right", "x": x, "y": y
        })
    
    def double_click(self, project_id: str, x: int, y: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/click", {
            "button": "left", "x": x, "y": y, "double": True
        })
    
    def drag(self, project_id: str, start_x: int, start_y: int, 
             end_x: int, end_y: int, button: str = "left", 
             duration: float = 0.5) -> Dict[str, Any]:
        """Perform a drag operation from start to end coordinates"""
        return self._request("POST", f"computers/{project_id}/drag", {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "button": button,
            "duration": duration
        })
    
    def scroll(self, project_id: str, direction: str, amount: int) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/scroll", {
            "direction": direction, "amount": amount
        })
    
    def type_text(self, project_id: str, text: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/type", {
            "text": text
        })
    
    def key_press(self, project_id: str, key: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/key", {
            "key": key
        })
    
    def get_screenshot(self, project_id: str) -> Dict[str, Any]:
        return self._request("GET", f"computers/{project_id}/screenshot")
    
    def execute_bash(self, project_id: str, command: str) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/bash", {
            "command": command
        })
    
    def execute_python(self, project_id: str, code: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute Python code on the computer"""
        return self._request("POST", f"computers/{project_id}/exec", {
            "code": code,
            "timeout": timeout
        })
    
    def wait(self, project_id: str, seconds: float) -> Dict[str, Any]:
        return self._request("POST", f"computers/{project_id}/wait", {
            "seconds": seconds
        })