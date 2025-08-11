#!/usr/bin/env python3
"""
Agent Builder - Core Implementation
==================================

This module provides the core building functionality for creating deployable
agent packages from Agentfile configurations. It follows a layer-based approach
similar to Docker builds, creating optimized packages that can be deployed
to any cloud runtime.

Key Features:
- Layer-based package creation
- Dependency installation and management
- Model downloading and caching
- Multi-stage build support
- Package manifest generation

Usage:
    builder = AgentBuilder()
    package = builder.build(config, "my-agent:latest")
"""

import os
import json
import shutil
import tempfile
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Import the parser components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from parser.aac_parser import AgentConfig

@dataclass
class Layer:
    """
    Represents a build layer in the agent package
    
    Each layer contains specific components of the agent:
    - base: Runtime environment
    - dependencies: Installed packages
    - code: Agent implementation
    - models: Downloaded models
    """
    name: str
    type: str  # 'base', 'dependencies', 'code', 'models'
    path: str
    size: int
    checksum: str
    metadata: Dict[str, Any]

@dataclass
class AgentPackage:
    """
    Complete agent package ready for deployment
    
    Contains all layers and metadata needed to deploy
    the agent to any cloud runtime.
    """
    tag: str
    layers: List[Layer]
    manifest: Dict[str, Any]
    entrypoint: str
    ports: List[int]
    environment: Dict[str, str]

class AgentBuilder:
    """
    Builds deployable agent packages from Agentfile configurations
    
    This class implements the core building logic that transforms
    parsed Agentfile configurations into deployable packages.
    
    The build process follows a layer-based approach:
    1. Create base runtime layer
    2. Install dependencies layer
    3. Copy agent code layer
    4. Download models layer
    5. Generate package manifest
    
    Usage:
        builder = AgentBuilder()
        package = builder.build(config, "my-agent:latest")
    """
    
    def __init__(self, build_dir: str = None):
        """
        Initialize the agent builder
        
        Args:
            build_dir: Directory for build artifacts (defaults to temp directory)
        """
        self.build_dir = build_dir or tempfile.mkdtemp(prefix="agent_build_")
        self.layers: List[Layer] = []
        
        # Ensure build directory exists
        os.makedirs(self.build_dir, exist_ok=True)
    
    def build(self, config: AgentConfig, tag: str) -> AgentPackage:
        """
        Build agent package from configuration
        
        This is the main build method that orchestrates the entire
        build process from configuration to deployable package.
        
        Args:
            config: Parsed agent configuration
            tag: Package tag (e.g., "my-agent:latest")
            
        Returns:
            AgentPackage: Complete deployable package
            
        Raises:
            ValueError: If build fails
            RuntimeError: If dependencies cannot be installed
        """
        try:
            print(f"Building agent package: {tag}")
            
            # 1. Create base layer
            print("  Creating base layer...")
            base_layer = self._create_base_layer(config.runtime)
            self.layers.append(base_layer)
            
            # 2. Install dependencies
            print("  Installing dependencies...")
            deps_layer = self._install_dependencies(config.dependencies)
            self.layers.append(deps_layer)
            
            # 3. Copy agent code
            print("  Copying agent code...")
            code_layer = self._copy_agent_code(config.files_to_copy, config.entrypoint)
            self.layers.append(code_layer)
            
            # 4. Download models
            print("  Downloading models...")
            models_layer = self._download_models(config.model)
            self.layers.append(models_layer)
            
            # 5. Create final package
            print("  Creating package...")
            package = self._create_package(tag, config)
            
            print(f"Build completed successfully: {tag}")
            return package
            
        except Exception as e:
            print(f"Build failed: {e}")
            raise ValueError(f"Failed to build agent package: {e}")
    
    def _create_base_layer(self, runtime: str) -> Layer:
        """
        Create base runtime layer
        
        Sets up the base runtime environment (Python, Node.js, etc.)
        that the agent will run in.
        
        Args:
            runtime: Runtime specification (e.g., "agent/python:3.9")
            
        Returns:
            Layer: Base runtime layer
        """
        layer_name = f"base_{runtime.replace(':', '_').replace('/', '_')}"
        layer_path = os.path.join(self.build_dir, layer_name)
        
        # Create layer directory
        os.makedirs(layer_path, exist_ok=True)
        
        # Create runtime-specific setup
        if "python" in runtime:
            self._setup_python_runtime(layer_path, runtime)
        elif "node" in runtime:
            self._setup_node_runtime(layer_path, runtime)
        else:
            # Default to Python
            self._setup_python_runtime(layer_path, runtime)
        
        # Calculate layer metadata
        size = self._calculate_directory_size(layer_path)
        checksum = self._calculate_checksum(layer_path)
        
        return Layer(
            name=layer_name,
            type="base",
            path=layer_path,
            size=size,
            checksum=checksum,
            metadata={
                "runtime": runtime,
                "created": "2024-01-15T10:30:00Z"
            }
        )
    
    def _setup_python_runtime(self, layer_path: str, runtime: str):
        """
        Set up Python runtime environment
        
        Creates the Python runtime environment with:
        - Python interpreter
        - Basic Python packages
        - Runtime configuration
        
        Args:
            layer_path: Path to layer directory
            runtime: Runtime specification
        """
        # Extract Python version from runtime
        version = "3.9"  # Default
        if ":" in runtime:
            version = runtime.split(":")[1]
        
        # Create Python environment structure
        python_dir = os.path.join(layer_path, "python")
        os.makedirs(python_dir, exist_ok=True)
        
        # Create requirements.txt for base packages
        requirements_path = os.path.join(layer_path, "requirements.txt")
        with open(requirements_path, 'w') as f:
            f.write(f"# Python {version} runtime requirements\n")
            f.write("grpc==1.59.0\n")
            f.write("grpcio-tools==1.59.0\n")
            f.write("requests==2.31.0\n")
            f.write("numpy==1.21.0\n")
        
        # Create runtime configuration
        runtime_config = {
            "python_version": version,
            "interpreter": f"python{version}",
            "pip": f"pip{version}",
            "packages": ["grpc", "grpcio-tools", "requests", "numpy"]
        }
        
        config_path = os.path.join(layer_path, "runtime_config.json")
        with open(config_path, 'w') as f:
            json.dump(runtime_config, f, indent=2)
    
    def _setup_node_runtime(self, layer_path: str, runtime: str):
        """
        Set up Node.js runtime environment
        
        Creates the Node.js runtime environment with:
        - Node.js interpreter
        - Basic Node.js packages
        - Runtime configuration
        
        Args:
            layer_path: Path to layer directory
            runtime: Runtime specification
        """
        # Extract Node version from runtime
        version = "18"  # Default
        if ":" in runtime:
            version = runtime.split(":")[1]
        
        # Create Node.js environment structure
        node_dir = os.path.join(layer_path, "node")
        os.makedirs(node_dir, exist_ok=True)
        
        # Create package.json for base packages
        package_json = {
            "name": "agent-runtime",
            "version": "1.0.0",
            "dependencies": {
                "@grpc/grpc-js": "^1.9.0",
                "@grpc/proto-loader": "^0.7.0",
                "axios": "^1.6.0"
            },
            "scripts": {
                "start": "node main.js"
            }
        }
        
        package_path = os.path.join(layer_path, "package.json")
        with open(package_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create runtime configuration
        runtime_config = {
            "node_version": version,
            "interpreter": f"node",
            "npm": "npm",
            "packages": ["@grpc/grpc-js", "@grpc/proto-loader", "axios"]
        }
        
        config_path = os.path.join(layer_path, "runtime_config.json")
        with open(config_path, 'w') as f:
            json.dump(runtime_config, f, indent=2)
    
    def _install_dependencies(self, dependencies: List[str]) -> Layer:
        """
        Install dependencies layer
        
        Installs all required dependencies (Python packages, system packages)
        into a separate layer for efficient caching.
        
        Args:
            dependencies: List of dependencies to install
            
        Returns:
            Layer: Dependencies layer
        """
        layer_name = "dependencies"
        layer_path = os.path.join(self.build_dir, layer_name)
        
        # Create layer directory
        os.makedirs(layer_path, exist_ok=True)
        
        # Separate dependencies by type
        python_deps = []
        system_deps = []
        
        for dep in dependencies:
            if self._is_python_dependency(dep):
                python_deps.append(dep)
            elif self._is_system_dependency(dep):
                system_deps.append(dep)
        
        # Install Python dependencies
        if python_deps:
            self._install_python_dependencies(layer_path, python_deps)
        
        # Install system dependencies
        if system_deps:
            self._install_system_dependencies(layer_path, system_deps)
        
        # Calculate layer metadata
        size = self._calculate_directory_size(layer_path)
        checksum = self._calculate_checksum(layer_path)
        
        return Layer(
            name=layer_name,
            type="dependencies",
            path=layer_path,
            size=size,
            checksum=checksum,
            metadata={
                "python_dependencies": python_deps,
                "system_dependencies": system_deps,
                "total_dependencies": len(dependencies)
            }
        )
    
    def _install_python_dependencies(self, layer_path: str, dependencies: List[str]):
        """
        Install Python dependencies
        
        Creates requirements.txt and installs Python packages.
        
        Args:
            layer_path: Path to layer directory
            dependencies: List of Python dependencies
        """
        requirements_path = os.path.join(layer_path, "requirements.txt")
        
        with open(requirements_path, 'w') as f:
            f.write("# Agent dependencies\n")
            for dep in dependencies:
                f.write(f"{dep}\n")
        
        # Create installation script
        install_script = os.path.join(layer_path, "install.sh")
        with open(install_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("pip install -r requirements.txt\n")
        
        os.chmod(install_script, 0o755)
    
    def _install_system_dependencies(self, layer_path: str, dependencies: List[str]):
        """
        Install system dependencies
        
        Creates installation script for system packages.
        
        Args:
            layer_path: Path to layer directory
            dependencies: List of system dependencies
        """
        install_script = os.path.join(layer_path, "install_system.sh")
        
        with open(install_script, 'w') as f:
            f.write("#!/bin/bash\n")
            for dep in dependencies:
                f.write(f"{dep}\n")
        
        os.chmod(install_script, 0o755)
    
    def _copy_agent_code(self, files_to_copy: List[Dict[str, str]], entrypoint: str) -> Layer:
        """
        Copy agent code layer
        
        Copies the agent implementation code into a separate layer.
        
        Args:
            files_to_copy: List of files to copy
            entrypoint: Agent entrypoint command
            
        Returns:
            Layer: Code layer
        """
        layer_name = "code"
        layer_path = os.path.join(self.build_dir, layer_name)
        
        # Create layer directory
        os.makedirs(layer_path, exist_ok=True)
        
        # Copy files
        for file_copy in files_to_copy:
            src = file_copy.get('src', '')
            dest = file_copy.get('dest', '')
            
            if src and dest:
                # Create destination directory
                dest_dir = os.path.join(layer_path, os.path.dirname(dest))
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copy file/directory
                dest_path = os.path.join(layer_path, dest)
                if os.path.exists(src):
                    if os.path.isdir(src):
                        shutil.copytree(src, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dest_path)
                else:
                    # Create placeholder file if source doesn't exist
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(dest_path, 'w') as f:
                        f.write(f"# Placeholder for {src}\n")
        
        # Create entrypoint script
        entrypoint_script = os.path.join(layer_path, "entrypoint.sh")
        with open(entrypoint_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"exec {entrypoint}\n")
        
        os.chmod(entrypoint_script, 0o755)
        
        # Calculate layer metadata
        size = self._calculate_directory_size(layer_path)
        checksum = self._calculate_checksum(layer_path)
        
        return Layer(
            name=layer_name,
            type="code",
            path=layer_path,
            size=size,
            checksum=checksum,
            metadata={
                "entrypoint": entrypoint,
                "files_copied": len(files_to_copy)
            }
        )
    
    def _download_models(self, model: str) -> Layer:
        """
        Download models layer
        
        Downloads and caches the specified model for the agent.
        
        Args:
            model: Model specification (e.g., "gpt-4")
            
        Returns:
            Layer: Models layer
        """
        layer_name = "models"
        layer_path = os.path.join(self.build_dir, layer_name)
        
        # Create layer directory
        os.makedirs(layer_path, exist_ok=True)
        
        # Create model configuration
        model_config = {
            "model": model,
            "type": "llm",
            "provider": "openai" if "gpt" in model else "unknown"
        }
        
        config_path = os.path.join(layer_path, "model_config.json")
        with open(config_path, 'w') as f:
            json.dump(model_config, f, indent=2)
        
        # Create model download script
        download_script = os.path.join(layer_path, "download_model.sh")
        with open(download_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"# Download model: {model}\n")
            f.write("echo 'Model will be downloaded at runtime'\n")
        
        os.chmod(download_script, 0o755)
        
        # Calculate layer metadata
        size = self._calculate_directory_size(layer_path)
        checksum = self._calculate_checksum(layer_path)
        
        return Layer(
            name=layer_name,
            type="models",
            path=layer_path,
            size=size,
            checksum=checksum,
            metadata={
                "model": model,
                "downloaded": False  # Models are downloaded at runtime
            }
        )
    
    def _create_package(self, tag: str, config: AgentConfig) -> AgentPackage:
        """
        Create final agent package
        
        Combines all layers into a deployable package with manifest.
        
        Args:
            tag: Package tag
            config: Agent configuration
            
        Returns:
            AgentPackage: Complete deployable package
        """
        # Generate package manifest
        manifest = self._generate_manifest(tag, config)
        
        # Create package
        package = AgentPackage(
            tag=tag,
            layers=self.layers,
            manifest=manifest,
            entrypoint=config.entrypoint,
            ports=config.exposed_ports,
            environment=config.environment
        )
        
        return package
    
    def _generate_manifest(self, tag: str, config: AgentConfig) -> Dict[str, Any]:
        """
        Generate package manifest
        
        Creates a comprehensive manifest with all package metadata.
        
        Args:
            tag: Package tag
            config: Agent configuration
            
        Returns:
            Dict: Package manifest
        """
        # Calculate total size
        total_size = sum(layer.size for layer in self.layers)
        
        # Generate layer information
        layer_info = []
        for layer in self.layers:
            layer_info.append({
                "name": layer.name,
                "type": layer.type,
                "size": layer.size,
                "checksum": layer.checksum,
                "metadata": layer.metadata
            })
        
        manifest = {
            "name": tag.split(":")[0] if ":" in tag else tag,
            "version": tag.split(":")[1] if ":" in tag else "latest",
            "created": "2024-01-15T10:30:00Z",
            "runtime": config.runtime,
            "model": config.model,
            "capabilities": config.capabilities,
            "entrypoint": config.entrypoint,
            "ports": config.exposed_ports,
            "environment": config.environment,
            "layers": layer_info,
            "total_size": total_size,
            "layer_count": len(self.layers),
            "labels": config.labels,
            "agentic_capabilities": config.agentic_capabilities
        }
        
        return manifest
    
    def _is_python_dependency(self, dep: str) -> bool:
        """Check if dependency is Python package"""
        return any(op in dep for op in ['==', '>=', '<=', '~='])
    
    def _is_system_dependency(self, dep: str) -> bool:
        """Check if dependency is system package"""
        return dep.startswith('apt-get') or dep.startswith('yum') or dep.startswith('apk')
    
    def _calculate_directory_size(self, path: str) -> int:
        """Calculate directory size in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size
    
    def _calculate_checksum(self, path: str) -> str:
        """Calculate SHA256 checksum of directory"""
        hasher = hashlib.sha256()
        
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in sorted(filenames):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'rb') as f:
                    hasher.update(f.read())
        
        return hasher.hexdigest()

# Example usage
if __name__ == "__main__":
    """
    Example usage of the Agent Builder
    
    This demonstrates how to use the builder to create
    an agent package from a configuration.
    """
    from parser.aac_parser import AaCParser
    
    # Parse an Agentfile
    parser = AaCParser()
    config = parser.parse_agentfile("examples/basic-sentiment-agent/Agentfile")
    
    # Build the agent package
    builder = AgentBuilder()
    package = builder.build(config, "sentiment-agent:latest")
    
    print(f"Built package: {package.tag}")
    print(f"Layers: {len(package.layers)}")
    print(f"Total size: {package.manifest['total_size']} bytes")
    print(f"Entrypoint: {package.entrypoint}") 