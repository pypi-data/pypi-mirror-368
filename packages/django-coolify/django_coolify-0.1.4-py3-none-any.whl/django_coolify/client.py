"""
Coolify API client for Django integration
"""
import json
import os
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import requests


class CoolifyAPIError(Exception):
    """Custom exception for Coolify API errors"""
    pass


class CoolifyClient:
    """Client for interacting with Coolify API"""
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize Coolify client
        
        Args:
            base_url: Base URL of the Coolify instance (e.g., "https://coolify.example.com")
            api_token: API token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.api_base = f"{self.base_url}/api/v1"
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Coolify API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            CoolifyAPIError: If the request fails
        """
        url = urljoin(self.api_base + "/", endpoint.lstrip("/"))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                
                raise CoolifyAPIError(f"Coolify API error: {error_msg}")
            
            return response.json()
            
        except requests.RequestException as e:
            raise CoolifyAPIError(f"Request failed: {str(e)}")
    
    def create_project(self, name: str, description: str = "") -> Dict:
        """
        Create a new project in Coolify
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project data with UUID
        """
        data = {
            "name": name,
            "description": description
        }
        
        return self._make_request("POST", "/projects", data=data)
    
    def list_projects(self) -> List[Dict]:
        """
        List all projects
        
        Returns:
            List of projects
        """
        return self._make_request("GET", "/projects")
    
    def get_project(self, project_uuid: str) -> Dict:
        """
        Get project by UUID
        
        Args:
            project_uuid: Project UUID
            
        Returns:
            Project data
        """
        return self._make_request("GET", f"/projects/{project_uuid}")
    
    def create_public_application(
        self,
        project_uuid: str,
        server_uuid: str,
        name: str,
        git_repository: str,
        git_branch: str = "main",
        build_pack: str = "dockerfile",
        environment_name: str = "production",
        **kwargs
    ) -> Dict:
        """
        Create a public application from a Git repository
        
        Args:
            project_uuid: UUID of the project to create the app in
            server_uuid: UUID of the server to deploy to
            name: Application name
            git_repository: Git repository URL
            git_branch: Git branch to deploy from
            build_pack: Build pack to use (dockerfile, nixpacks, etc.)
            environment_name: Environment name (default: production)
            **kwargs: Additional application configuration
            
        Returns:
            Application data with UUID
        """
        data = {
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "name": name,
            "git_repository": git_repository,
            "git_branch": git_branch,
            "build_pack": build_pack,
            "environment_name": environment_name,
            **kwargs
        }
        
        return self._make_request("POST", "/applications/public", data=data)
    
    def deploy_application(self, uuid: str, force: bool = False) -> Dict:
        """
        Deploy application by UUID
        
        Args:
            uuid: Application UUID
            force: Force rebuild without cache
            
        Returns:
            Deployment data
        """
        params = {"uuid": uuid}
        if force:
            params["force"] = "true"
            
        return self._make_request("GET", "/deploy", params=params)
    
    def list_servers(self) -> List[Dict]:
        """
        List all servers
        
        Returns:
            List of servers
        """
        return self._make_request("GET", "/servers")
    
    def get_application(self, app_uuid: str) -> Dict:
        """
        Get application by UUID
        
        Args:
            app_uuid: Application UUID
            
        Returns:
            Application data
        """
        return self._make_request("GET", f"/applications/{app_uuid}")
    
    def list_applications(self) -> List[Dict]:
        """
        List all applications
        
        Returns:
            List of applications
        """
        return self._make_request("GET", "/applications")
    
    def list_environments(self, project_uuid: str) -> List[Dict]:
        """
        List environments in a project
        
        Args:
            project_uuid: Project UUID
            
        Returns:
            List of environments
        """
        return self._make_request("GET", f"/projects/{project_uuid}/environments")
    
    def set_environment_variable(self, app_uuid: str, key: str, value: str) -> Dict:
        """
        Set environment variable for an application
        
        Args:
            app_uuid: Application UUID
            key: Environment variable key
            value: Environment variable value
            
        Returns:
            Response data
        """
        data = {
            "key": key,
            "value": value,
            "is_build_time": False,
            "is_preview": False
        }
        
        try:
            # Try POST first (create new env var)
            return self._make_request("POST", f"/applications/{app_uuid}/envs", data=data)
        except CoolifyAPIError as e:
            if "already exists" in str(e):
                # If env var exists, try to update it with PATCH
                try:
                    # Get existing env vars to find the ID
                    env_vars = self.list_environment_variables(app_uuid)
                    env_var_id = None
                    for env_var in env_vars:
                        if env_var.get('key') == key:
                            env_var_id = env_var.get('id')
                            break
                    
                    if env_var_id:
                        return self._make_request("PATCH", f"/applications/{app_uuid}/envs/{env_var_id}", data=data)
                    else:
                        raise CoolifyAPIError(f"Could not find existing environment variable: {key}")
                except Exception as update_error:
                    raise CoolifyAPIError(f"Failed to update existing environment variable: {update_error}")
            else:
                raise e
    
    def list_environment_variables(self, app_uuid: str) -> List[Dict]:
        """
        List environment variables for an application
        
        Args:
            app_uuid: Application UUID
            
        Returns:
            List of environment variables
        """
        return self._make_request("GET", f"/applications/{app_uuid}/envs")
    
    def set_application_domain(self, app_uuid: str, domain: str) -> Dict:
        """
        Set domain for an application
        
        Args:
            app_uuid: Application UUID
            domain: Domain to set
            
        Returns:
            Response data
        """
        data = {
            "domains": domain
        }
        return self._make_request("POST", f"/applications/{app_uuid}/domains", data=data)
    
    def update_application_settings(self, app_uuid: str, settings: Dict) -> Dict:
        """
        Update application settings
        
        Args:
            app_uuid: Application UUID  
            settings: Settings to update
            
        Returns:
            Response data
        """
        return self._make_request("PATCH", f"/applications/{app_uuid}", data=settings)
