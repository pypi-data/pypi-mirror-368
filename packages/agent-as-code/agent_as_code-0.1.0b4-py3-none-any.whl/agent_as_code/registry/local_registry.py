#!/usr/bin/env python3
"""
Local Registry Implementation
============================

Simple local registry for storing and retrieving agent packages.
This is a basic implementation for the beta release.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class RegistryPackage:
    """Represents a package stored in the registry"""
    tag: str
    manifest_path: str
    layers_path: str
    created: str
    size: int

class LocalRegistry:
    """
    Local registry for storing agent packages
    
    Provides basic push/pull functionality for local development
    and testing. This is a simplified version for beta release.
    """
    
    def __init__(self, registry_path: str = None):
        """
        Initialize local registry
        
        Args:
            registry_path: Path to registry storage (defaults to ~/.agent-registry)
        """
        if registry_path is None:
            home = Path.home()
            self.registry_path = home / ".agent-registry"
        else:
            self.registry_path = Path(registry_path)
        
        # Create registry directory structure
        self.packages_path = self.registry_path / "packages"
        self.manifests_path = self.registry_path / "manifests"
        
        for path in [self.registry_path, self.packages_path, self.manifests_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def push(self, package_tag: str, manifest_path: str, layers_dir: str) -> bool:
        """
        Push agent package to registry
        
        Args:
            package_tag: Package tag (e.g., "my-agent:latest")
            manifest_path: Path to package manifest
            layers_dir: Directory containing package layers
            
        Returns:
            bool: True if push successful
        """
        try:
            # Sanitize tag for filesystem
            safe_tag = package_tag.replace(":", "_").replace("/", "_")
            
            # Copy manifest
            manifest_dest = self.manifests_path / f"{safe_tag}.json"
            shutil.copy2(manifest_path, manifest_dest)
            
            # Copy layers
            layers_dest = self.packages_path / safe_tag
            if layers_dest.exists():
                shutil.rmtree(layers_dest)
            shutil.copytree(layers_dir, layers_dest)
            
            print(f"Successfully pushed {package_tag} to local registry")
            return True
            
        except Exception as e:
            print(f"Failed to push {package_tag}: {e}")
            return False
    
    def pull(self, package_tag: str, dest_path: str) -> bool:
        """
        Pull agent package from registry
        
        Args:
            package_tag: Package tag to pull
            dest_path: Destination path for package
            
        Returns:
            bool: True if pull successful
        """
        try:
            # Sanitize tag for filesystem
            safe_tag = package_tag.replace(":", "_").replace("/", "_")
            
            # Check if package exists
            manifest_path = self.manifests_path / f"{safe_tag}.json"
            layers_path = self.packages_path / safe_tag
            
            if not manifest_path.exists():
                print(f"Package {package_tag} not found in registry")
                return False
            
            # Copy package to destination
            dest_path = Path(dest_path)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Copy manifest
            shutil.copy2(manifest_path, dest_path / "manifest.json")
            
            # Copy layers
            layers_dest = dest_path / "layers"
            shutil.copytree(layers_path, layers_dest)
            
            print(f"Successfully pulled {package_tag} from local registry")
            return True
            
        except Exception as e:
            print(f"Failed to pull {package_tag}: {e}")
            return False
    
    def list(self) -> List[RegistryPackage]:
        """
        List all packages in registry
        
        Returns:
            List[RegistryPackage]: List of available packages
        """
        packages = []
        
        for manifest_file in self.manifests_path.glob("*.json"):
            try:
                # Extract tag from filename
                safe_tag = manifest_file.stem
                tag = safe_tag.replace("_", ":", 1)  # Replace first underscore with colon
                
                # Read manifest
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                # Calculate total size
                layers_path = self.packages_path / safe_tag
                size = self._calculate_directory_size(layers_path) if layers_path.exists() else 0
                
                package = RegistryPackage(
                    tag=tag,
                    manifest_path=str(manifest_file),
                    layers_path=str(layers_path),
                    created=manifest.get("created", "unknown"),
                    size=size
                )
                packages.append(package)
                
            except Exception as e:
                print(f"Error reading package {manifest_file}: {e}")
        
        return packages
    
    def remove(self, package_tag: str) -> bool:
        """
        Remove package from registry
        
        Args:
            package_tag: Package tag to remove
            
        Returns:
            bool: True if removal successful
        """
        try:
            # Sanitize tag for filesystem
            safe_tag = package_tag.replace(":", "_").replace("/", "_")
            
            # Remove manifest
            manifest_path = self.manifests_path / f"{safe_tag}.json"
            if manifest_path.exists():
                manifest_path.unlink()
            
            # Remove layers
            layers_path = self.packages_path / safe_tag
            if layers_path.exists():
                shutil.rmtree(layers_path)
            
            print(f"Successfully removed {package_tag} from registry")
            return True
            
        except Exception as e:
            print(f"Failed to remove {package_tag}: {e}")
            return False
    
    def _calculate_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total_size = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

# Example usage
if __name__ == "__main__":
    registry = LocalRegistry()
    
    # List packages
    packages = registry.list()
    for package in packages:
        print(f"{package.tag} - {package.size} bytes - {package.created}") 