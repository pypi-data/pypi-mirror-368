#!/usr/bin/env python3
"""
Profile Manager - Configuration Management
=========================================

Manages configuration profiles for PAT authentication, similar to AWS CLI.
Stores configuration in ~/.agent/config.json
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class Profile:
    """Represents a configuration profile"""
    name: str
    registry: str
    pat: str
    description: str = ""

class ProfileManager:
    """
    Manages configuration profiles for agent registry access
    
    Stores profiles in ~/.agent/config.json with the following structure:
    {
        "profiles": {
            "default": {
                "registry": "https://api.myagentregistry.com",
                "pat": "your_pat_token_here",
                "description": "Default profile"
            },
            "production": {
                "registry": "https://api.myagentregistry.com",
                "pat": "production_pat_token",
                "description": "Production environment"
            }
        },
        "default_profile": "default"
    }
    """
    
    def __init__(self):
        """Initialize profile manager"""
        self.config_dir = Path.home() / ".agent"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                return {"profiles": {}, "default_profile": "default"}
        else:
            return {"profiles": {}, "default_profile": "default"}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def configure_profile(self, name: str, registry: str, pat: str, description: str = "", set_default: bool = False) -> bool:
        """
        Configure a profile
        
        Args:
            name: Profile name
            registry: Registry URL
            pat: Personal Access Token
            description: Profile description
            set_default: Whether to set as default profile
            
        Returns:
            bool: True if configuration successful
        """
        try:
            config = self._load_config()
            
            # Add or update profile
            config["profiles"][name] = {
                "registry": registry,
                "pat": pat,
                "description": description
            }
            
            # Set as default if requested
            if set_default or not config.get("default_profile"):
                config["default_profile"] = name
            
            self._save_config(config)
            
            print(f"Profile '{name}' configured successfully")
            if set_default:
                print(f"Profile '{name}' set as default")
            
            return True
            
        except Exception as e:
            print(f"Failed to configure profile: {e}")
            return False
    
    def list_profiles(self) -> List[Profile]:
        """
        List all profiles
        
        Returns:
            List[Profile]: List of configured profiles
        """
        config = self._load_config()
        default_profile = config.get("default_profile", "default")
        
        profiles = []
        for name, profile_data in config.get("profiles", {}).items():
            profile = Profile(
                name=name,
                registry=profile_data.get("registry", ""),
                pat=profile_data.get("pat", ""),
                description=profile_data.get("description", "")
            )
            profiles.append(profile)
        
        # Sort by name
        profiles.sort(key=lambda p: p.name)
        
        return profiles, default_profile
    
    def get_profile(self, name: str = None) -> Optional[Profile]:
        """
        Get a specific profile
        
        Args:
            name: Profile name (if None, returns default profile)
            
        Returns:
            Profile: Profile configuration or None if not found
        """
        config = self._load_config()
        
        if name is None:
            name = config.get("default_profile", "default")
        
        profile_data = config.get("profiles", {}).get(name)
        if profile_data:
            return Profile(
                name=name,
                registry=profile_data.get("registry", ""),
                pat=profile_data.get("pat", ""),
                description=profile_data.get("description", "")
            )
        
        return None
    
    def remove_profile(self, name: str) -> bool:
        """
        Remove a profile
        
        Args:
            name: Profile name to remove
            
        Returns:
            bool: True if removal successful
        """
        try:
            config = self._load_config()
            
            if name not in config.get("profiles", {}):
                print(f"Profile '{name}' not found")
                return False
            
            # Remove profile
            del config["profiles"][name]
            
            # Update default profile if necessary
            if config.get("default_profile") == name:
                remaining_profiles = list(config["profiles"].keys())
                if remaining_profiles:
                    config["default_profile"] = remaining_profiles[0]
                    print(f"Default profile changed to '{remaining_profiles[0]}'")
                else:
                    del config["default_profile"]
                    print("No profiles remaining")
            
            self._save_config(config)
            
            print(f"Profile '{name}' removed successfully")
            return True
            
        except Exception as e:
            print(f"Failed to remove profile: {e}")
            return False
    
    def set_default_profile(self, name: str) -> bool:
        """
        Set default profile
        
        Args:
            name: Profile name to set as default
            
        Returns:
            bool: True if successful
        """
        try:
            config = self._load_config()
            
            if name not in config.get("profiles", {}):
                print(f"Profile '{name}' not found")
                return False
            
            config["default_profile"] = name
            self._save_config(config)
            
            print(f"Default profile set to '{name}'")
            return True
            
        except Exception as e:
            print(f"Failed to set default profile: {e}")
            return False
    
    def test_profile(self, name: str = None) -> bool:
        """
        Test profile connection
        
        Args:
            name: Profile name to test (if None, tests default profile)
            
        Returns:
            bool: True if connection successful
        """
        try:
            profile = self.get_profile(name)
            if not profile:
                print(f"Profile '{name or 'default'}' not found")
                return False
            
            # Test connection using registry client
            from ..registry.remote_registry import RemoteRegistryClient
            
            client = RemoteRegistryClient(
                base_url=profile.registry,
                pat=profile.pat
            )
            
            if client.test_connection():
                print(f"Profile '{profile.name}' connection successful")
                return True
            else:
                print(f"Profile '{profile.name}' connection failed")
                return False
                
        except Exception as e:
            print(f"Failed to test profile: {e}")
            return False
    
    def export_profile(self, name: str, export_path: str) -> bool:
        """
        Export profile configuration
        
        Args:
            name: Profile name to export
            export_path: Path to export file
            
        Returns:
            bool: True if export successful
        """
        try:
            profile = self.get_profile(name)
            if not profile:
                print(f"Profile '{name}' not found")
                return False
            
            export_data = {
                "name": profile.name,
                "registry": profile.registry,
                "pat": profile.pat,
                "description": profile.description
            }
            
            export_path = Path(export_path)
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"Profile '{name}' exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"Failed to export profile: {e}")
            return False
    
    def import_profile(self, import_path: str, overwrite: bool = False) -> bool:
        """
        Import profile configuration
        
        Args:
            import_path: Path to import file
            overwrite: Whether to overwrite existing profile
            
        Returns:
            bool: True if import successful
        """
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                print(f"Import file not found: {import_path}")
                return False
            
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            name = import_data.get("name")
            if not name:
                print("Invalid import file: missing profile name")
                return False
            
            config = self._load_config()
            
            # Check if profile exists
            if name in config.get("profiles", {}) and not overwrite:
                print(f"Profile '{name}' already exists. Use --overwrite to replace.")
                return False
            
            # Add profile
            config["profiles"][name] = {
                "registry": import_data.get("registry", ""),
                "pat": import_data.get("pat", ""),
                "description": import_data.get("description", "")
            }
            
            self._save_config(config)
            
            print(f"Profile '{name}' imported successfully")
            return True
            
        except Exception as e:
            print(f"Failed to import profile: {e}")
            return False
    
    def get_config_path(self) -> str:
        """Get configuration file path"""
        return str(self.config_file)
    
    def validate_pat(self, pat: str) -> bool:
        """
        Validate PAT format
        
        Args:
            pat: PAT to validate
            
        Returns:
            bool: True if PAT format is valid
        """
        # Basic validation - PAT should be 64 characters
        if not pat or len(pat) != 64:
            return False
        
        # Check if it's hexadecimal
        try:
            int(pat, 16)
            return True
        except ValueError:
            return False 