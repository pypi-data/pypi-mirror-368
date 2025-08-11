# src/orgo/project.py
"""Project management for Orgo virtual environments"""
import os
import json
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ProjectManager:
    """Manages project persistence for Orgo computers"""
    
    @staticmethod
    def load_project_id() -> Optional[str]:
        """Load project ID from local config file"""
        config_path = ProjectManager._get_config_path()
        
        if not os.path.exists(config_path):
            return None
            
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('project_id')
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.warning(f"Error loading project config: {str(e)}")
            return None
    
    @staticmethod
    def save_project_id(project_id: str) -> None:
        """Save project ID to local config file"""
        config_dir = ProjectManager._get_project_dir()
        config_path = ProjectManager._get_config_path()
        
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({'project_id': project_id}, f, indent=2)
        except (IOError, OSError) as e:
            logger.error(f"Failed to save project ID: {str(e)}")
            raise RuntimeError(f"Failed to save project configuration: {str(e)}") from e
    
    @staticmethod
    def clear_project_cache() -> None:
        """Clear the .orgo folder and all its contents"""
        project_dir = ProjectManager._get_project_dir()
        
        if os.path.exists(project_dir):
            try:
                shutil.rmtree(project_dir)
                logger.info(f"Cleared project cache at {project_dir}")
            except (IOError, OSError) as e:
                logger.warning(f"Failed to clear project cache: {str(e)}")
    
    @staticmethod
    def _get_project_dir() -> str:
        """Get the project directory path"""
        return os.path.join(os.getcwd(), ".orgo")
    
    @staticmethod
    def _get_config_path() -> str:
        """Get the full path to the config file"""
        return os.path.join(ProjectManager._get_project_dir(), "project.json")