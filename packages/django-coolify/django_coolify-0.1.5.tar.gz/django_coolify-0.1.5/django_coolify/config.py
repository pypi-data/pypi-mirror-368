"""
Configuration management for django-coolify
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional

from django.conf import settings


class CoolifyConfig:
    """Manages coolify.json configuration file and .env for sensitive data"""
    
    DEFAULT_CONFIG = {
        "coolify_url": "",
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
        "health_check_path": "/django-coolify/health/"
    }
    
    # Sensitive fields that should be stored in .env file
    SENSITIVE_FIELDS = {
        "api_token": "COOLIFY_API_TOKEN"
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
                self.env_path = manage_py_path / ".env"
            else:
                self.config_path = current_dir / "coolify.json"
                self.env_path = current_dir / ".env"
    
    def load_env_vars(self) -> Dict[str, str]:
        """
        Load environment variables from .env file
        
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if self.env_path.exists():
            try:
                with open(self.env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"\'')
                            env_vars[key.strip()] = value
            except IOError as e:
                print(f"Warning: Error reading .env file {self.env_path}: {e}")
        
        return env_vars
    
    def save_env_vars(self, env_vars: Dict[str, str]) -> None:
        """
        Save environment variables to .env file
        
        Args:
            env_vars: Dictionary of environment variables to save
        """
        try:
            # Ensure directory exists
            self.env_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing .env content to preserve other variables
            existing_content = []
            coolify_vars = set(self.SENSITIVE_FIELDS.values())
            
            if self.env_path.exists():
                with open(self.env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Keep lines that are not Coolify-related
                        if line and '=' in line:
                            key = line.split('=', 1)[0].strip()
                            if key not in coolify_vars:
                                existing_content.append(line)
                        elif line and (not line.strip() or line.startswith('#')):
                            existing_content.append(line)
            
            # Write .env file
            with open(self.env_path, 'w') as f:
                # Write existing content first
                if existing_content:
                    f.write('\n'.join(existing_content))
                    f.write('\n\n')
                
                # Write Coolify configuration header
                f.write('# Coolify Configuration\n')
                for key, value in env_vars.items():
                    f.write(f'{key}="{value}"\n')
                    
        except IOError as e:
            raise ValueError(f"Error writing .env file {self.env_path}: {e}")
    
    def load(self) -> Dict:
        """
        Load configuration from file and environment variables
        
        Returns:
            Configuration dictionary
        """
        # Load base config from coolify.json
        config = self.DEFAULT_CONFIG.copy()
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                raise ValueError(f"Error reading config file {self.config_path}: {e}")
        
        # Load sensitive data from .env file
        env_vars = self.load_env_vars()
        for field, env_key in self.SENSITIVE_FIELDS.items():
            if env_key in env_vars:
                config[field] = env_vars[env_key]
            else:
                config[field] = ""
        
        return config
    
    def save(self, config: Dict) -> None:
        """
        Save configuration to files (non-sensitive to coolify.json, sensitive to .env)
        
        Args:
            config: Configuration dictionary to save
        """
        # Separate sensitive and non-sensitive data
        non_sensitive_config = {}
        sensitive_env_vars = {}
        
        for key, value in config.items():
            if key in self.SENSITIVE_FIELDS:
                if value:  # Only save non-empty values
                    env_key = self.SENSITIVE_FIELDS[key]
                    sensitive_env_vars[env_key] = value
            else:
                non_sensitive_config[key] = value
        
        try:
            # Save non-sensitive config to coolify.json
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(non_sensitive_config, f, indent=2, sort_keys=True)
            
            # Save sensitive data to .env
            if sensitive_env_vars:
                self.save_env_vars(sensitive_env_vars)
                
        except IOError as e:
            raise ValueError(f"Error writing config files: {e}")
    
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
