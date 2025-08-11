#!/usr/bin/env python3
"""
Agent as Code (AaC) Parser
===========================

This module provides the core parsing functionality for Agentfile configurations.
It follows the same principles as Dockerfile parsing but is specifically designed
for AI agent configurations.

Key Features:
- Parse Agentfile directives (FROM, CAPABILITY, MODEL, etc.)
- Validate configuration syntax and dependencies
- Generate agent schemas for UAPI registration
- Resolve dependencies (Python, system, models)

Usage:
    parser = AaCParser()
    config = parser.parse_agentfile("Agentfile")
    validation = parser.validate_config(config)
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DirectiveType(Enum):
    """
    Supported Agentfile directives
    
    Each directive type corresponds to a specific configuration aspect:
    - FROM: Base runtime environment
    - CAPABILITY: Agent capabilities (text-generation, sentiment-analysis, etc.)
    - MODEL: LLM model selection
    - CONFIG: Model parameters (temperature, max_tokens, etc.)
    - DEPENDENCY: Python/system dependencies
    - ENV: Environment variables
    - COPY: File copying operations
    - EXPOSE: Port exposure
    - ENTRYPOINT: Agent startup command
    - LABEL: Metadata labels
    - AGENTIC: Agentic capabilities (self-improvement, learning, etc.)
    - HEALTHCHECK: Health check configuration
    - RUN: Runtime commands
    """
    FROM = "FROM"
    CAPABILITY = "CAPABILITY"
    MODEL = "MODEL"
    CONFIG = "CONFIG"
    DEPENDENCY = "DEPENDENCY"
    ENV = "ENV"
    COPY = "COPY"
    EXPOSE = "EXPOSE"
    ENTRYPOINT = "ENTRYPOINT"
    LABEL = "LABEL"
    AGENTIC = "AGENTIC"
    HEALTHCHECK = "HEALTHCHECK"
    RUN = "RUN"

@dataclass
class Directive:
    """
    Represents a single Agentfile directive
    
    Attributes:
        type: The directive type (FROM, CAPABILITY, etc.)
        value: The directive value (e.g., "agent/python:3.9")
        line_number: Line number in the Agentfile for error reporting
        raw_line: Original line text for debugging
    """
    type: DirectiveType
    value: str
    line_number: int
    raw_line: str

@dataclass
class AgentConfig:
    """
    Complete agent configuration built from parsed directives
    
    This is the main output of the parser, containing all the information
    needed to build and run an AI agent.
    
    Attributes:
        runtime: Base runtime environment (e.g., "agent/python:3.9")
        capabilities: List of agent capabilities (e.g., ["text-generation", "sentiment-analysis"])
        model: LLM model name (e.g., "gpt-4")
        model_config: Model parameters (temperature, max_tokens, etc.)
        dependencies: List of dependencies (Python packages, system packages)
        environment: Environment variables
        files_to_copy: Files to copy during build
        exposed_ports: Ports to expose
        entrypoint: Agent startup command
        labels: Metadata labels
        agentic_capabilities: Agentic features (self-improvement, learning, etc.)
        health_check: Health check configuration
        run_commands: Runtime commands to execute
        metadata: Additional metadata
    """
    runtime: str
    capabilities: List[str]
    model: str
    model_config: Dict[str, Any]
    dependencies: List[str]
    environment: Dict[str, str]
    files_to_copy: List[Dict[str, str]]
    exposed_ports: List[int]
    entrypoint: str
    labels: Dict[str, str]
    agentic_capabilities: Dict[str, bool]
    health_check: Optional[str]
    run_commands: List[str]
    metadata: Dict[str, Any]

@dataclass
class ValidationResult:
    """
    Result of configuration validation
    
    Attributes:
        is_valid: Whether the configuration is valid
        errors: List of validation errors (must be fixed)
        warnings: List of validation warnings (should be addressed)
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class AaCParser:
    """
    Parser for Agentfile configurations
    
    This class provides the main parsing functionality for Agentfiles.
    It follows a simple, line-by-line parsing approach similar to Dockerfile parsing.
    
    Usage:
        parser = AaCParser()
        config = parser.parse_agentfile("Agentfile")
        validation = parser.validate_config(config)
    """
    
    def __init__(self):
        """
        Initialize the parser
        
        Sets up empty lists for directives and configuration.
        The parser will populate these during parsing.
        """
        self.directives: List[Directive] = []
        self.config: Optional[AgentConfig] = None
    
    def parse_agentfile(self, file_path: str) -> AgentConfig:
        """
        Parse Agentfile and return structured configuration
        
        This is the main entry point for parsing an Agentfile. It reads the file
        line by line, parses each directive, and builds a complete configuration.
        
        Args:
            file_path: Path to the Agentfile to parse
            
        Returns:
            AgentConfig: Complete agent configuration
            
        Raises:
            FileNotFoundError: If Agentfile doesn't exist
            ValueError: If Agentfile is invalid
            
        Example:
            parser = AaCParser()
            config = parser.parse_agentfile("my-agent/Agentfile")
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Agentfile not found: {file_path}")
        
        # Parse all directives from the file
        self._parse_directives(file_path)
        
        # Build complete configuration from directives
        self.config = self._build_config()
        
        return self.config
    
    def validate_config(self, config: AgentConfig) -> ValidationResult:
        """
        Validate configuration syntax and dependencies
        
        Performs comprehensive validation of the parsed configuration:
        - Required fields (runtime, model, entrypoint)
        - Model parameter validation (temperature, max_tokens)
        - Dependency format validation
        - Environment variable validation
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult: Validation results with errors and warnings
            
        Example:
            validation = parser.validate_config(config)
            if not validation.is_valid:
                print("Errors:", validation.errors)
        """
        errors = []
        warnings = []
        
        # Validate required fields
        if not config.runtime:
            errors.append("Runtime (FROM directive) is required")
        
        if not config.capabilities:
            warnings.append("No capabilities defined - agent may have limited functionality")
        
        if not config.model:
            errors.append("Model (MODEL directive) is required")
        
        if not config.entrypoint:
            errors.append("Entrypoint (ENTRYPOINT directive) is required")
        
        # Validate model configuration parameters
        if config.model_config:
            for key, value in config.model_config.items():
                if key == "temperature" and not (0 <= value <= 2):
                    errors.append(f"Temperature must be between 0 and 2, got {value}")
                elif key == "max_tokens" and value <= 0:
                    errors.append(f"Max tokens must be positive, got {value}")
        
        # Validate dependency formats
        for dep in config.dependencies:
            if not self._is_valid_dependency(dep):
                warnings.append(f"Potentially invalid dependency format: {dep}")
        
        # Check for recommended environment variables
        required_env_vars = ["OPENAI_API_KEY"]
        for var in required_env_vars:
            if var not in config.environment:
                warnings.append(f"Recommended environment variable not set: {var}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def resolve_dependencies(self, config: AgentConfig) -> Dict[str, List[str]]:
        """
        Resolve and validate all dependencies
        
        Categorizes dependencies into Python packages, system packages, and models.
        This helps the builder know how to install each type of dependency.
        
        Args:
            config: Configuration with dependencies to resolve
            
        Returns:
            Dict[str, List[str]]: Resolved dependency graph by type
            
        Example:
            deps = parser.resolve_dependencies(config)
            print("Python deps:", deps["python"])
            print("System deps:", deps["system"])
        """
        resolved_deps = {
            "python": [],
            "system": [],
            "models": []
        }
        
        # Categorize each dependency
        for dep in config.dependencies:
            if self._is_python_dependency(dep):
                resolved_deps["python"].append(dep)
            elif self._is_system_dependency(dep):
                resolved_deps["system"].append(dep)
            else:
                resolved_deps["models"].append(dep)
        
        return resolved_deps
    
    def generate_schema(self, config: AgentConfig) -> Dict[str, Any]:
        """
        Generate agent schema for UAPI registration
        
        Creates a standardized schema that can be used by the UAPI to:
        - Register the agent with the service discovery system
        - Generate gRPC service definitions
        - Provide API documentation
        
        Args:
            config: Agent configuration to generate schema from
            
        Returns:
            Dict[str, Any]: Agent schema for UAPI registration
            
        Example:
            schema = parser.generate_schema(config)
            uapi.register_agent(schema)
        """
        schema = {
            "name": config.labels.get("name", "unnamed-agent"),
            "version": config.labels.get("version", "1.0.0"),
            "description": config.labels.get("description", ""),
            "capabilities": config.capabilities,
            "model": config.model,
            "model_config": config.model_config,
            "runtime": config.runtime,
            "entrypoint": config.entrypoint,
            "ports": config.exposed_ports,
            "environment": config.environment,
            "agentic_capabilities": config.agentic_capabilities,
            "metadata": config.metadata
        }
        
        return schema
    
    def _parse_directives(self, file_path: str):
        """
        Parse all directives from Agentfile
        
        Reads the Agentfile line by line and parses each directive.
        Skips comments and empty lines.
        
        Args:
            file_path: Path to the Agentfile to parse
        """
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                directive = self._parse_directive(line.strip(), line_num)
                if directive:
                    self.directives.append(directive)
    
    def _parse_directive(self, line: str, line_number: int) -> Optional[Directive]:
        """
        Parse a single directive line
        
        Parses a line like "FROM agent/python:3.9" into a Directive object.
        Skips comments (lines starting with #) and empty lines.
        
        Args:
            line: Line to parse
            line_number: Line number for error reporting
            
        Returns:
            Directive: Parsed directive or None if line should be skipped
        """
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            return None
        
        # Split line into directive type and value
        parts = line.split(' ', 1)
        if len(parts) < 2:
            return None
        
        directive_type_str = parts[0].upper()
        value = parts[1]
        
        try:
            directive_type = DirectiveType(directive_type_str)
            return Directive(
                type=directive_type,
                value=value,
                line_number=line_number,
                raw_line=line
            )
        except ValueError:
            # Unknown directive type - skip silently
            return None
    
    def _build_config(self) -> AgentConfig:
        """
        Build AgentConfig from parsed directives
        
        Converts the list of parsed directives into a structured configuration.
        Each directive type is processed and added to the appropriate configuration field.
        
        Returns:
            AgentConfig: Complete agent configuration
        """
        # Initialize configuration with default values
        config = {
            'runtime': '',
            'capabilities': [],
            'model': '',
            'model_config': {},
            'dependencies': [],
            'environment': {},
            'files_to_copy': [],
            'exposed_ports': [],
            'entrypoint': '',
            'labels': {},
            'agentic_capabilities': {},
            'health_check': None,
            'run_commands': [],
            'metadata': {}
        }
        
        # Process each directive and populate configuration
        for directive in self.directives:
            if directive.type == DirectiveType.FROM:
                config['runtime'] = directive.value
            elif directive.type == DirectiveType.CAPABILITY:
                config['capabilities'].append(directive.value)
            elif directive.type == DirectiveType.MODEL:
                config['model'] = directive.value
            elif directive.type == DirectiveType.CONFIG:
                key, value = self._parse_config(directive.value)
                config['model_config'][key] = value
            elif directive.type == DirectiveType.DEPENDENCY:
                config['dependencies'].append(directive.value)
            elif directive.type == DirectiveType.ENV:
                key, value = self._parse_env(directive.value)
                config['environment'][key] = value
            elif directive.type == DirectiveType.COPY:
                src, dest = self._parse_copy(directive.value)
                config['files_to_copy'].append({'src': src, 'dest': dest})
            elif directive.type == DirectiveType.EXPOSE:
                config['exposed_ports'].append(int(directive.value))
            elif directive.type == DirectiveType.ENTRYPOINT:
                config['entrypoint'] = directive.value
            elif directive.type == DirectiveType.LABEL:
                key, value = self._parse_label(directive.value)
                config['labels'][key] = value
            elif directive.type == DirectiveType.AGENTIC:
                key, value = self._parse_agentic(directive.value)
                config['agentic_capabilities'][key] = value
            elif directive.type == DirectiveType.HEALTHCHECK:
                config['health_check'] = directive.value
            elif directive.type == DirectiveType.RUN:
                config['run_commands'].append(directive.value)
        
        return AgentConfig(**config)
    
    def _parse_config(self, config_str: str) -> tuple[str, Any]:
        """
        Parse CONFIG directive value
        
        Parses values like "temperature=0.7" into key-value pairs.
        Attempts to convert values to appropriate types (int, float, or string).
        
        Args:
            config_str: Configuration string to parse
            
        Returns:
            tuple: (key, value) pair
        """
        if '=' in config_str:
            key, value = config_str.split('=', 1)
            # Try to convert to appropriate type
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # Keep as string if conversion fails
            return key.strip(), value
        return config_str.strip(), True
    
    def _parse_env(self, env_str: str) -> tuple[str, str]:
        """
        Parse ENV directive value
        
        Parses environment variable assignments like "OPENAI_API_KEY=test-api-key-123".
        
        Args:
            env_str: Environment variable string to parse
            
        Returns:
            tuple: (key, value) pair
        """
        if '=' in env_str:
            key, value = env_str.split('=', 1)
            return key.strip(), value.strip()
        return env_str.strip(), ""
    
    def _parse_copy(self, copy_str: str) -> tuple[str, str]:
        """
        Parse COPY directive value
        
        Parses file copy operations like "src dest".
        
        Args:
            copy_str: Copy string to parse
            
        Returns:
            tuple: (source, destination) paths
        """
        parts = copy_str.split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        return copy_str, ""
    
    def _parse_label(self, label_str: str) -> tuple[str, str]:
        """
        Parse LABEL directive value
        
        Parses label assignments like "version=1.0.0".
        
        Args:
            label_str: Label string to parse
            
        Returns:
            tuple: (key, value) pair
        """
        return self._parse_env(label_str)
    
    def _parse_agentic(self, agentic_str: str) -> tuple[str, bool]:
        """
        Parse AGENTIC directive value
        
        Parses agentic capability assignments like "auto-optimize=true".
        
        Args:
            agentic_str: Agentic string to parse
            
        Returns:
            tuple: (capability, enabled) pair
        """
        key, value = self._parse_env(agentic_str)
        return key, value.lower() == 'true'
    
    def _is_valid_dependency(self, dep: str) -> bool:
        """
        Check if dependency format is valid
        
        Validates Python dependency formats like "package==1.0.0".
        
        Args:
            dep: Dependency string to validate
            
        Returns:
            bool: True if format is valid
        """
        # Basic validation for Python dependencies
        if '==' in dep or '>=' in dep or '<=' in dep:
            return True
        return False
    
    def _is_python_dependency(self, dep: str) -> bool:
        """
        Check if dependency is Python package
        
        Identifies Python dependencies by version operators.
        
        Args:
            dep: Dependency string to check
            
        Returns:
            bool: True if Python dependency
        """
        return any(op in dep for op in ['==', '>=', '<=', '~='])
    
    def _is_system_dependency(self, dep: str) -> bool:
        """
        Check if dependency is system package
        
        Identifies system dependencies by package manager commands.
        
        Args:
            dep: Dependency string to check
            
        Returns:
            bool: True if system dependency
        """
        return dep.startswith('apt-get') or dep.startswith('yum') or dep.startswith('apk')

# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of the AaC Parser
    
    This demonstrates how to use the parser to parse an Agentfile,
    validate the configuration, and generate a schema.
    """
    parser = AaCParser()
    
    # Parse example Agentfile
    config = parser.parse_agentfile("examples/basic-sentiment-agent/Agentfile")
    
    # Validate configuration
    validation = parser.validate_config(config)
    
    print(f"Configuration valid: {validation.is_valid}")
    if validation.errors:
        print("Errors:", validation.errors)
    if validation.warnings:
        print("Warnings:", validation.warnings)
    
    # Generate schema for UAPI registration
    schema = parser.generate_schema(config)
    print("Generated schema:", json.dumps(schema, indent=2)) 