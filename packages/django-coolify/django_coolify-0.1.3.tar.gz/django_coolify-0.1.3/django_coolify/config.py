"""
Configuration management for django-coolify
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional

from django.conf import settings


class CoolifyConfig:
    """Manages coolify.json configuration file"""
    
    DEFAULT_CONFIG = {
        "coolify_url": "",
        "api_token": "",
        "project_name": "",
        "project_uuid": "",
        "app_name": "",
        "app_uuid": "",
        "server_uuid": "",
        "git_repository": "",
        "git_branch": "main",
        "build_pack": "dockerfile",
        "environment_name": "production",
        "ports_exposes": "8000",
        "domains": "",
        "environment_variables": {},
        "health_check_enabled": False,
        "health_check_path": "/health/"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to coolify.json file. Defaults to project root.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Try to find project root by looking for manage.py
            current_dir = Path.cwd()
            manage_py_path = None
            
            # Look for manage.py in current directory and parent directories
            for parent in [current_dir] + list(current_dir.parents):
                if (parent / "manage.py").exists():
                    manage_py_path = parent
                    break
            
            if manage_py_path:
                self.config_path = manage_py_path / "coolify.json"
            else:
                self.config_path = current_dir / "coolify.json"
    
    def load(self) -> Dict:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = self.DEFAULT_CONFIG.copy()
                    merged_config.update(config)
                    return merged_config
            except (json.JSONDecodeError, IOError) as e:
                raise ValueError(f"Error reading config file {self.config_path}: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self, config: Dict) -> None:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
        except IOError as e:
            raise ValueError(f"Error writing config file {self.config_path}: {e}")
    
    def exists(self) -> bool:
        """
        Check if configuration file exists
        
        Returns:
            True if config file exists, False otherwise
        """
        return self.config_path.exists()
    
    def get_django_project_name(self) -> str:
        """
        Get Django project name from settings
        
        Returns:
            Django project name
        """
        try:
            # Try to get from Django settings
            if hasattr(settings, 'ROOT_URLCONF'):
                return settings.ROOT_URLCONF.split('.')[0]
        except:
            pass
        
        # Fallback to directory name where manage.py is located
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            if (parent / "manage.py").exists():
                return parent.name
        
        return current_dir.name
    
    def get_git_repository_url(self) -> Optional[str]:
        """
        Get Git repository URL from the current directory
        
        Returns:
            Git repository URL or None if not found
        """
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            
            # Get remote URL
            if repo.remotes:
                remote_url = repo.remotes.origin.url
                
                # Convert SSH URL to HTTPS if needed
                if remote_url.startswith('git@github.com:'):
                    remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                if remote_url.endswith('.git'):
                    remote_url = remote_url[:-4]
                
                return remote_url
        except:
            pass
        
        return None
    
    def get_current_git_branch(self) -> str:
        """
        Get current Git branch
        
        Returns:
            Current branch name, defaults to 'main'
        """
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            return repo.active_branch.name
        except:
            return "main"
    
    def generate_default_config(self) -> Dict:
        """
        Generate default configuration with auto-detected values
        
        Returns:
            Default configuration dictionary
        """
        config = self.DEFAULT_CONFIG.copy()
        
        # Auto-detect project name
        config["project_name"] = self.get_django_project_name()
        config["app_name"] = f"{config['project_name']}-app"
        
        # Auto-detect Git repository
        git_repo = self.get_git_repository_url()
        if git_repo:
            config["git_repository"] = git_repo
            config["git_branch"] = self.get_current_git_branch()
        
        return config
