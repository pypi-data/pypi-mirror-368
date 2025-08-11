#!/usr/bin/env python3
"""
Test Suite for Agent as Code (AaC) Parser
==========================================

This test suite validates the AaC parser functionality, ensuring:
- Correct parsing of Agentfile directives
- Proper validation of configurations
- Accurate dependency resolution
- Schema generation for UAPI integration

The tests cover both happy path scenarios and edge cases to ensure
the parser is robust and reliable for production use.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open
from parser.aac_parser import AaCParser, AgentConfig, ValidationResult, DirectiveType

class TestAaCParser(unittest.TestCase):
    """
    Test cases for the AaC Parser
    
    Tests cover:
    - Agentfile parsing
    - Configuration validation
    - Dependency resolution
    - Schema generation
    - Error handling
    """
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = AaCParser()
        
        # Sample valid Agentfile content
        self.valid_agentfile_content = """
# Test Agentfile
FROM agent/python:3.9

CAPABILITY text-generation
CAPABILITY sentiment-analysis

MODEL gpt-4
CONFIG temperature=0.7
CONFIG max_tokens=200

DEPENDENCY torch==1.9.0
DEPENDENCY transformers==4.11.3

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

COPY ./agent /app/agent
EXPOSE 50051

ENTRYPOINT python /app/agent/main.py

LABEL version="1.0.0"
LABEL author="test@example.com"
LABEL description="Test agent"
        """
    
    def test_parse_valid_agentfile(self):
        """Test parsing a valid Agentfile"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.agentfile', delete=False) as f:
            f.write(self.valid_agentfile_content)
            f.flush()
            
            config = self.parser.parse_agentfile(f.name)
            
            # Verify basic configuration
            self.assertEqual(config.runtime, "agent/python:3.9")
            self.assertIn("text-generation", config.capabilities)
            self.assertIn("sentiment-analysis", config.capabilities)
            self.assertEqual(config.model, "gpt-4")
            self.assertEqual(config.model_config["temperature"], 0.7)
            self.assertEqual(config.model_config["max_tokens"], 200)
            self.assertIn("torch==1.9.0", config.dependencies)
            self.assertEqual(config.environment["LOG_LEVEL"], "INFO")
            self.assertEqual(config.entrypoint, "python /app/agent/main.py")
            
            # Clean up
            os.unlink(f.name)
    
    def test_parse_invalid_agentfile(self):
        """Test parsing an invalid Agentfile"""
        invalid_content = """
FROM agent/python:3.9
INVALID_DIRECTIVE some_value
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.agentfile', delete=False) as f:
            f.write(invalid_content)
            f.flush()
            
            # Should not raise an exception for unknown directives
            config = self.parser.parse_agentfile(f.name)
            self.assertEqual(config.runtime, "agent/python:3.9")
            
            # Clean up
            os.unlink(f.name)
    
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_agentfile("nonexistent.agentfile")
    
    def test_validate_valid_config(self):
        """Test validation of a valid configuration"""
        config = AgentConfig(
            runtime="agent/python:3.9",
            capabilities=["text-generation"],
            model="gpt-4",
            model_config={"temperature": 0.7, "max_tokens": 200},
            dependencies=["torch==1.9.0"],
            environment={"OPENAI_API_KEY": "test-api-key-123"},
            files_to_copy=[],
            exposed_ports=[50051],
            entrypoint="python main.py",
            labels={},
            agentic_capabilities={},
            health_check=None,
            run_commands=[],
            metadata={}
        )
        
        validation = self.parser.validate_config(config)
        self.assertTrue(validation.is_valid)
        self.assertEqual(len(validation.errors), 0)
    
    def test_validate_invalid_config(self):
        """Test validation of an invalid configuration"""
        config = AgentConfig(
            runtime="",  # Missing runtime
            capabilities=[],  # No capabilities
            model="",  # Missing model
            model_config={"temperature": 2.5},  # Invalid temperature
            dependencies=[],
            environment={},  # Missing required env vars
            files_to_copy=[],
            exposed_ports=[],
            entrypoint="",  # Missing entrypoint
            labels={},
            agentic_capabilities={},
            health_check=None,
            run_commands=[],
            metadata={}
        )
        
        validation = self.parser.validate_config(config)
        self.assertFalse(validation.is_valid)
        self.assertGreater(len(validation.errors), 0)
        self.assertIn("Runtime (FROM directive) is required", validation.errors)
        self.assertIn("Model (MODEL directive) is required", validation.errors)
        self.assertIn("Entrypoint (ENTRYPOINT directive) is required", validation.errors)
    
    def test_resolve_dependencies(self):
        """Test dependency resolution"""
        config = AgentConfig(
            runtime="agent/python:3.9",
            capabilities=["text-generation"],
            model="gpt-4",
            model_config={},
            dependencies=[
                "torch==1.9.0",  # Python dependency
                "apt-get install curl",  # System dependency
                "gpt-4"  # Model dependency
            ],
            environment={},
            files_to_copy=[],
            exposed_ports=[],
            entrypoint="python main.py",
            labels={},
            agentic_capabilities={},
            health_check=None,
            run_commands=[],
            metadata={}
        )
        
        resolved_deps = self.parser.resolve_dependencies(config)
        
        self.assertIn("torch==1.9.0", resolved_deps["python"])
        self.assertIn("apt-get install curl", resolved_deps["system"])
        self.assertIn("gpt-4", resolved_deps["models"])
    
    def test_generate_schema(self):
        """Test schema generation for UAPI"""
        config = AgentConfig(
            runtime="agent/python:3.9",
            capabilities=["text-generation", "sentiment-analysis"],
            model="gpt-4",
            model_config={"temperature": 0.7},
            dependencies=["torch==1.9.0"],
            environment={"OPENAI_API_KEY": "test-api-key-123"},
            files_to_copy=[],
            exposed_ports=[50051],
            entrypoint="python main.py",
            labels={
                "name": "test-agent",
                "version": "1.0.0",
                "description": "Test agent"
            },
            agentic_capabilities={"auto-optimize": True},
            health_check=None,
            run_commands=[],
            metadata={}
        )
        
        schema = self.parser.generate_schema(config)
        
        # Verify schema structure
        self.assertEqual(schema["name"], "test-agent")
        self.assertEqual(schema["version"], "1.0.0")
        self.assertEqual(schema["description"], "Test agent")
        self.assertIn("text-generation", schema["capabilities"])
        self.assertEqual(schema["model"], "gpt-4")
        self.assertEqual(schema["runtime"], "agent/python:3.9")
        self.assertEqual(schema["entrypoint"], "python main.py")
        self.assertEqual(schema["ports"], [50051])
        self.assertTrue(schema["agentic_capabilities"]["auto-optimize"])
    
    def test_parse_directive(self):
        """Test parsing individual directives"""
        # Test valid directives
        directive = self.parser._parse_directive("FROM agent/python:3.9", 1)
        self.assertIsNotNone(directive)
        self.assertEqual(directive.type, DirectiveType.FROM)
        self.assertEqual(directive.value, "agent/python:3.9")
        
        # Test invalid directive
        directive = self.parser._parse_directive("INVALID_DIRECTIVE value", 1)
        self.assertIsNone(directive)
        
        # Test comment
        directive = self.parser._parse_directive("# This is a comment", 1)
        self.assertIsNone(directive)
        
        # Test empty line
        directive = self.parser._parse_directive("", 1)
        self.assertIsNone(directive)
    
    def test_parse_config_values(self):
        """Test parsing CONFIG directive values"""
        key, value = self.parser._parse_config("temperature=0.7")
        self.assertEqual(key, "temperature")
        self.assertEqual(value, 0.7)
        
        key, value = self.parser._parse_config("max_tokens=200")
        self.assertEqual(key, "max_tokens")
        self.assertEqual(value, 200)
        
        key, value = self.parser._parse_config("model_name=gpt-4")
        self.assertEqual(key, "model_name")
        self.assertEqual(value, "gpt-4")
    
    def test_parse_env_values(self):
        """Test parsing ENV directive values"""
        key, value = self.parser._parse_env("OPENAI_API_KEY=test-api-key-123")
        self.assertEqual(key, "OPENAI_API_KEY")
        self.assertEqual(value, "test-api-key-123")
        
        key, value = self.parser._parse_env("LOG_LEVEL=INFO")
        self.assertEqual(key, "LOG_LEVEL")
        self.assertEqual(value, "INFO")
    
    def test_parse_copy_values(self):
        """Test parsing COPY directive values"""
        src, dest = self.parser._parse_copy("./agent /app/agent")
        self.assertEqual(src, "./agent")
        self.assertEqual(dest, "/app/agent")
    
    def test_dependency_validation(self):
        """Test dependency format validation"""
        # Valid Python dependencies
        self.assertTrue(self.parser._is_valid_dependency("torch==1.9.0"))
        self.assertTrue(self.parser._is_valid_dependency("transformers>=4.11.3"))
        self.assertTrue(self.parser._is_valid_dependency("numpy<=1.21.0"))
        
        # Invalid dependencies
        self.assertFalse(self.parser._is_valid_dependency("invalid-package"))
        self.assertFalse(self.parser._is_valid_dependency(""))
    
    def test_dependency_categorization(self):
        """Test dependency categorization"""
        # Python dependencies
        self.assertTrue(self.parser._is_python_dependency("torch==1.9.0"))
        self.assertTrue(self.parser._is_python_dependency("transformers>=4.11.3"))
        
        # System dependencies
        self.assertTrue(self.parser._is_system_dependency("apt-get install curl"))
        self.assertTrue(self.parser._is_system_dependency("yum install python3"))
        
        # Model dependencies (neither Python nor system)
        self.assertFalse(self.parser._is_python_dependency("gpt-4"))
        self.assertFalse(self.parser._is_system_dependency("gpt-4"))

class TestAgentConfig(unittest.TestCase):
    """Test cases for AgentConfig data class"""
    
    def test_agent_config_creation(self):
        """Test creating an AgentConfig instance"""
        config = AgentConfig(
            runtime="agent/python:3.9",
            capabilities=["text-generation"],
            model="gpt-4",
            model_config={"temperature": 0.7},
            dependencies=["torch==1.9.0"],
            environment={"OPENAI_API_KEY": "test-api-key-123"},
            files_to_copy=[],
            exposed_ports=[50051],
            entrypoint="python main.py",
            labels={"version": "1.0.0"},
            agentic_capabilities={"auto-optimize": True},
            health_check="python health_check.py",
            run_commands=["pip install -r requirements.txt"],
            metadata={"author": "test@example.com"}
        )
        
        self.assertEqual(config.runtime, "agent/python:3.9")
        self.assertIn("text-generation", config.capabilities)
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.model_config["temperature"], 0.7)
        self.assertIn("torch==1.9.0", config.dependencies)
        self.assertEqual(config.environment["OPENAI_API_KEY"], "test-api-key-123")
        self.assertEqual(config.entrypoint, "python main.py")
        self.assertEqual(config.labels["version"], "1.0.0")
        self.assertTrue(config.agentic_capabilities["auto-optimize"])
        self.assertEqual(config.health_check, "python health_check.py")
        self.assertIn("pip install -r requirements.txt", config.run_commands)
        self.assertEqual(config.metadata["author"], "test@example.com")

class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult data class"""
    
    def test_validation_result_creation(self):
        """Test creating a ValidationResult instance"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Missing recommended environment variable: OPENAI_API_KEY"]
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("OPENAI_API_KEY", result.warnings[0])

if __name__ == "__main__":
    """
    Run the test suite
    
    Usage:
        python -m unittest test_aac_parser.py
        python -m unittest test_aac_parser.py -v  # Verbose output
    """
    unittest.main(verbosity=2) 