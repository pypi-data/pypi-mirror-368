#!/usr/bin/env python3
"""
Remote Registry Client - PAT Authentication
==========================================

Client for interacting with the remote Agents Registry API using PAT authentication.
Based on the PAT system documentation.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

class RegistryAgent:
    """Represents an agent in the remote registry"""
    
    def __init__(self, **kwargs):
        """Initialize with flexible field handling"""
        # Required fields
        self.id = kwargs.get('id') or kwargs.get('agent_id')
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self.version = kwargs.get('version', '1.0.0')
        self.capabilities = kwargs.get('capabilities', [])
        self.runtime = kwargs.get('runtime', 'python')
        self.created_at = kwargs.get('created_at', '')
        self.updated_at = kwargs.get('updated_at', '')
        self.metadata = kwargs.get('metadata', {})
        
        # Store any additional fields in metadata
        for key, value in kwargs.items():
            if key not in ['id', 'agent_id', 'name', 'description', 'version', 
                          'capabilities', 'runtime', 'created_at', 'updated_at', 'metadata']:
                self.metadata[key] = value

class RemoteRegistryClient:
    """
    Client for remote Agents Registry API
    
    Provides authenticated access to the registry using PAT tokens.
    Supports all CRUD operations for agents.
    """
    
    def __init__(self, base_url: str = None, pat: str = None):
        # Use environment variable or default
        if base_url is None:
            base_url = os.getenv('AGENTS_REGISTRY_URL', "https://api.myagentregistry.com")
        """
        Initialize registry client
        
        Args:
            base_url: Registry API base URL
            pat: Personal Access Token (if not provided, will try to get from config)
        """
        self.base_url = base_url.rstrip('/')
        self.pat = pat or self._get_pat_from_config()
        
        if not self.pat:
            raise ValueError("PAT token is required. Use agent configure profile to set it up.")
        
        self.headers = {
            'Authorization': f'Bearer {self.pat}',
            'Content-Type': 'application/json'
        }
    
    def _get_pat_from_config(self) -> Optional[str]:
        """Get PAT from configuration file"""
        config_path = Path.home() / ".agent" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('profiles', {}).get('default', {}).get('pat')
            except Exception:
                pass
        return None
    
    def test_connection(self) -> bool:
        """
        Test connection to registry
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            return response.status_code == 200
        except Exception:
            return False
    
    def create_agent(self, name: str, description: str = "", category: str = "automation") -> RegistryAgent:
        """
        Create a new agent in the registry
        
        Args:
            name: Agent name
            description: Agent description
            category: Agent category
            
        Returns:
            RegistryAgent: Created agent
        """
        data = {
            "name": name,
            "description": description,
            "category": category
        }
        
        response = requests.post(
            f"{self.base_url}/agents",
            headers=self.headers,
            json=data
        )
        
        if response.status_code == 201:
            agent_data = response.json()
            return RegistryAgent(**agent_data)
        else:
            raise Exception(f"Failed to create agent: {response.text}")
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> List[RegistryAgent]:
        """
        List agents in the registry
        
        Args:
            limit: Maximum number of agents to return
            offset: Number of agents to skip
            
        Returns:
            List[RegistryAgent]: List of agents
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        response = requests.get(
            f"{self.base_url}/agents",
            headers=self.headers,
            params=params
        )
        
        if response.status_code == 200:
            agents_data = response.json()
            return [RegistryAgent(**agent) for agent in agents_data.get("agents", [])]
        else:
            raise Exception(f"Failed to list agents: {response.text}")
    
    def get_agent(self, agent_id: str) -> RegistryAgent:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            RegistryAgent: Agent details
        """
        response = requests.get(
            f"{self.base_url}/agents/{agent_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            agent_data = response.json()
            return RegistryAgent(**agent_data)
        else:
            raise Exception(f"Failed to get agent: {response.text}")
    
    def update_agent(self, agent_id: str, **updates) -> RegistryAgent:
        """
        Update agent
        
        Args:
            agent_id: Agent ID
            **updates: Fields to update
            
        Returns:
            RegistryAgent: Updated agent
        """
        response = requests.put(
            f"{self.base_url}/agents/{agent_id}",
            headers=self.headers,
            json=updates
        )
        
        if response.status_code == 200:
            agent_data = response.json()
            return RegistryAgent(**agent_data)
        else:
            raise Exception(f"Failed to update agent: {response.text}")
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            bool: True if deletion successful
        """
        print(f"Deleting agent: {agent_id}")
        response = requests.delete(
            f"{self.base_url}/agents/{agent_id}",
            headers=self.headers
        )
        
        print(f"Delete response status: {response.status_code}")
        print(f"Delete response: {response.text}")
        
        return response.status_code in [200, 204]
    
    def push_agent_package(self, agent_id: str, package_path: str) -> bool:
        """
        Push agent package to registry
        
        Args:
            agent_id: Agent ID
            package_path: Path to agent package directory
            
        Returns:
            bool: True if push successful
        """
        package_path = Path(package_path)
        print(f"Creating package archive from: {package_path}")
        
        # Create package archive
        import tempfile
        import tarfile
        import base64
        
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
            print(f"Creating archive: {tmp_file.name}")
            with tarfile.open(tmp_file.name, 'w:gz') as tar:
                tar.add(package_path, arcname='.')
            
            # Read and encode file to base64
            with open(tmp_file.name, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Upload package using JSON format
            print(f"Uploading package to: {self.base_url}/agents/{agent_id}/package")
            payload = {
                'file_data': file_data,
                'filename': 'agent_package.tar.gz',
                'content_type': 'application/gzip'
            }
            
            response = requests.post(
                f"{self.base_url}/agents/{agent_id}/package",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.pat}'
                },
                json=payload
            )
            
            print(f"Upload response status: {response.status_code}")
            print(f"Upload response: {response.text}")
            
            # Clean up
            os.unlink(tmp_file.name)
        
        return response.status_code == 200
    
    def pull_agent_package(self, agent_id: str, dest_path: str) -> bool:
        """
        Pull agent package from registry
        
        Args:
            agent_id: Agent ID
            dest_path: Destination path for package
            
        Returns:
            bool: True if pull successful
        """
        response = requests.get(
            f"{self.base_url}/agents/{agent_id}/package",
            headers=self.headers
        )
        
        if response.status_code == 200:
            dest_path = Path(dest_path)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Parse JSON response
            data = response.json()
            
            if not data.get('success'):
                raise Exception(f"Package download failed: {data.get('message', 'Unknown error')}")
            
            # Decode base64 file data
            import base64
            import tempfile
            import tarfile
            
            file_data = base64.b64decode(data['file_data'])
            
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp_file:
                tmp_file.write(file_data)
                tmp_file.flush()
                
                with tarfile.open(tmp_file.name, 'r:gz') as tar:
                    tar.extractall(dest_path)
                
                os.unlink(tmp_file.name)
            
            return True
        else:
            raise Exception(f"Failed to pull agent package: {response.text}")
    
    def search_agents(self, query: str, category: str = None) -> List[RegistryAgent]:
        """
        Search agents
        
        Args:
            query: Search query
            category: Filter by category
            
        Returns:
            List[RegistryAgent]: Matching agents
        """
        params = {"q": query}
        if category:
            params["category"] = category
        
        response = requests.get(
            f"{self.base_url}/agents/search",
            headers=self.headers,
            params=params
        )
        
        if response.status_code == 200:
            agents_data = response.json()
            return [RegistryAgent(**agent) for agent in agents_data.get("agents", [])]
        else:
            raise Exception(f"Failed to search agents: {response.text}")
    
    def get_agent_versions(self, agent_id: str) -> List[str]:
        """
        Get available versions for an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List[str]: Available versions
        """
        response = requests.get(
            f"{self.base_url}/agents/{agent_id}/versions",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("versions", [])
        else:
            raise Exception(f"Failed to get agent versions: {response.text}")

class RegistryManager:
    """
    High-level registry manager for CLI operations
    """
    
    def __init__(self, profile: str = "default"):
        """
        Initialize registry manager
        
        Args:
            profile: Configuration profile to use
        """
        self.profile = profile
        self.client = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_path = Path.home() / ".agent" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    profile_config = config.get('profiles', {}).get(self.profile, {})
                    
                    if profile_config:
                        self.client = RemoteRegistryClient(
                            base_url=profile_config.get('registry'),
                            pat=profile_config.get('pat')
                        )
            except Exception as e:
                raise Exception(f"Failed to load configuration: {e}")
        else:
            raise Exception(f"Configuration not found. Run 'agent configure profile' first.")
    
    def push(self, agent_name: str, package_path: str) -> bool:
        """
        Push agent to registry
        
        Args:
            agent_name: Agent name
            package_path: Path to agent package
            
        Returns:
            bool: True if push successful
        """
        if not self.client:
            raise Exception("Registry client not initialized")
        
        print(f"Starting push process for {agent_name}...")
        
        # Create agent if it doesn't exist
        try:
            print(f"Attempting to create agent: {agent_name}")
            agent = self.client.create_agent(agent_name, f"Agent: {agent_name}")
            print(f"Created new agent: {agent.name} with ID: {agent.id}")
        except Exception as e:
            print(f"Agent creation failed, trying to find existing agent: {e}")
            # Agent might already exist, try to find it
            agents = self.client.list_agents()
            agent = next((a for a in agents if a.name == agent_name), None)
            if not agent:
                print(f"Could not find or create agent: {agent_name}")
                return False
            else:
                print(f"Found existing agent: {agent.name} with ID: {agent.id}")
        
        # Push package
        print(f"Pushing package from: {package_path}")
        success = self.client.push_agent_package(agent.id, package_path)
        print(f"Package push result: {success}")
        return success
    
    def pull(self, agent_name: str, dest_path: str) -> bool:
        """
        Pull agent from registry
        
        Args:
            agent_name: Agent name
            dest_path: Destination path
            
        Returns:
            bool: True if pull successful
        """
        if not self.client:
            raise Exception("Registry client not initialized")
        
        # Find agent
        agents = self.client.list_agents()
        agent = next((a for a in agents if a.name == agent_name), None)
        
        if not agent:
            raise Exception(f"Agent not found: {agent_name}")
        
        # Pull package
        return self.client.pull_agent_package(agent.id, dest_path)
    
    def list(self) -> List[RegistryAgent]:
        """
        List agents in registry
        
        Returns:
            List[RegistryAgent]: List of agents
        """
        if not self.client:
            raise Exception("Registry client not initialized")
        
        return self.client.list_agents()
    
    def remove(self, agent_name: str) -> bool:
        """
        Remove agent from registry
        
        Args:
            agent_name: Agent name
            
        Returns:
            bool: True if removal successful
        """
        if not self.client:
            raise Exception("Registry client not initialized")
        
        # Find agent
        agents = self.client.list_agents()
        agent = next((a for a in agents if a.name == agent_name), None)
        
        if not agent:
            raise Exception(f"Agent not found: {agent_name}")
        
        # Delete agent
        return self.client.delete_agent(agent.id) 