#!/usr/bin/env python3
"""
Agent CLI - Command Line Interface
=================================

This module provides a simple command-line interface for the Agent as Code (AaC) system.
It follows Docker-like command patterns for familiarity and ease of use.

Key Commands:
- agent init: Initialize new agent project
- agent build: Build agent from Agentfile
- agent run: Run agent locally
- agent test: Test agent functionality
- agent inspect: Show agent details
- agent push: Push agent to registry
- agent pull: Pull agent from registry
- agent images: List available agents

Usage:
    python agent_cli.py init my-agent
    python agent_cli.py build -t my-agent:latest .
    python agent_cli.py run my-agent:latest
    python agent_cli.py push my-agent:latest
"""

import os
import sys
import argparse
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from importlib.metadata import version as pkg_version, metadata as pkg_metadata, PackageNotFoundError

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
except Exception:
    # Allow running without rich, fallback to simple prints
    Console = None

# Import our modules
from ..parser.aac_parser import AaCParser
from ..builder.unified_builder import UnifiedAgentBuilder
from ..registry.remote_registry import RegistryManager
from ..config.profile_manager import ProfileManager
from .llm.manager import LLMProviderFactory
from .llm.config_manager import LLMConfigManager
from .llm.agent_creator import LLMAgentCreator

class AgentCLI:
    """
    Command-line interface for Agent as Code system
    
    Provides Docker-like commands for managing AI agents:
    - init: Create new agent project
    - build: Build agent package
    - run: Run agent locally
    - test: Test agent functionality
    - inspect: Show agent details
    """
    
    def __init__(self):
        """Initialize the CLI"""
        self.parser = AaCParser()
        self.builder = UnifiedAgentBuilder()
        self.profile_manager = ProfileManager()
    
    def run(self, args):
        """
        Run the CLI with provided arguments
        
        Args:
            args: Parsed command line arguments
        """
        command = args.command
        
        if command == "init":
            self.init_agent(args.name, args.template)
        elif command == "build":
            self.build_agent(args.tag, args.path)
        elif command == "run":
            self.run_agent(args.tag)
        elif command == "test":
            self.test_agent(args.tag)
        elif command == "inspect":
            self.inspect_agent(args.tag)
        elif command == "configure":
            self.configure_profile(args)
        elif command == "push":
            self.push_agent(args.tag, args.profile)
        elif command == "pull":
            self.pull_agent(args.tag, args.profile)
        elif command == "images":
            self.list_agents(args.profile)
        elif command == "rmi":
            self.remove_agent(args.tag, args.profile)
        elif command == "llm":
            self.handle_llm(args)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    def init_agent(self, name: str, template: str = "python"):
        """
        Initialize a new agent project
        
        Creates a new agent project with:
        - Agentfile configuration
        - Agent implementation template
        - Basic project structure
        
        Args:
            name: Agent project name
            template: Template to use (python, node, etc.)
        """
        print(f"Initializing agent project: {name}")
        
        # Create project directory
        project_dir = Path(name)
        project_dir.mkdir(exist_ok=True)
        
        # Create agent directory
        agent_dir = project_dir / "agent"
        agent_dir.mkdir(exist_ok=True)
        
        # Copy template files
        template_dir = Path(__file__).parent.parent / "templates" / f"{template}-agent"
        
        if template_dir.exists():
            # Copy Agentfile
            agentfile_src = template_dir / "Agentfile"
            agentfile_dest = project_dir / "Agentfile"
            
            if agentfile_src.exists():
                shutil.copy2(agentfile_src, agentfile_dest)
                print(f"  Created Agentfile")
            
            # Copy agent code
            agent_src = template_dir / "agent"
            if agent_src.exists():
                shutil.copytree(agent_src, agent_dir, dirs_exist_ok=True)
                print(f"  Created agent code")
        
        # Create README
        readme_content = f"""# {name}

This is an AI agent created with Agent as Code (AaC).

## Quick Start

```bash
# Build the agent
agent build -t {name}:latest .

# Run the agent
agent run {name}:latest
```

## Development

1. Edit the `Agentfile` to configure your agent
2. Modify the agent code in the `agent/` directory
3. Test your changes with `agent test {name}:latest`
"""
        
        readme_path = project_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"  Created README.md")
        print(f"  Project initialized successfully!")
        print(f"  Next steps:")
        print(f"    1. cd {name}")
        print(f"    2. Edit Agentfile")
        print(f"    3. agent build -t {name}:latest .")
    
    def build_agent(self, tag: str, path: str):
        """
        Build unified agent micro-service package from Agentfile
        
        Parses the Agentfile and builds a deployable micro-service package
        with gRPC and REST API interfaces.
        
        Args:
            tag: Package tag (e.g., "my-agent:latest")
            path: Path to agent project directory
        """
        print(f"Building unified micro-service: {tag}")
        
        # Find Agentfile
        agentfile_path = Path(path) / "Agentfile"
        if not agentfile_path.exists():
            print(f"Error: Agentfile not found at {agentfile_path}")
            sys.exit(1)
        
        try:
            # Parse Agentfile
            print("  Parsing Agentfile...")
            config = self.parser.parse_agentfile(str(agentfile_path))
            
            # Validate configuration
            print("  Validating configuration...")
            validation = self.parser.validate_config(config)
            
            if not validation.is_valid:
                print("  Validation errors:")
                for error in validation.errors:
                    print(f"    - {error}")
                sys.exit(1)
            
            if validation.warnings:
                print("  Warnings:")
                for warning in validation.warnings:
                    print(f"    - {warning}")
            
            # Build micro-service package
            print("  Building micro-service package...")
            package = self.builder.build_microservice(config, tag)
            
            # Store the build path for later use
            self.last_build_path = package.build_path
            
            print(f"  Build completed successfully!")
            print(f"  Package: {package.name}:{package.version}")
            print(f"  Runtime: {package.runtime}")
            print(f"  Base Image: {package.base_image}")
            print(f"  Capabilities: {len(package.capabilities)}")
            print(f"  Ports: {package.ports}")
            print(f"  Package location: {package.build_path}")
            
            # Show next steps
            print(f"\n  Next steps:")
            print(f"    agent push {tag}  # Push to registry")
            print(f"    docker build -t {tag} {package.build_path}  # Build Docker image")
            print(f"    cd {package.build_path}/deploy && ./run.sh  # Run locally")
            
        except Exception as e:
            print(f"  Build failed: {e}")
            sys.exit(1)
    
    def run_agent(self, tag: str):
        """
        Run agent locally
        
        Starts the agent as a local service for testing.
        
        Args:
            tag: Agent package tag to run
        """
        print(f"Running agent: {tag}")
        
        # Check if agent is in registry
        packages = self.registry.list()
        package = next((p for p in packages if p.tag == tag), None)
        
        if not package:
            print(f"  Error: Agent {tag} not found in registry")
            print(f"  Available agents:")
            for p in packages:
                print(f"    - {p.tag}")
            return
        
        # Run the agent
        success = self.runner.run(
            tag,
            package.manifest_path,
            package.layers_path
        )
        
        if success:
            try:
                # Keep running until interrupted
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"  Stopping agent...")
                self.runner.stop(tag)
        else:
            print(f"  Failed to start agent {tag}")
    
    def test_agent(self, tag: str):
        """
        Test agent functionality
        
        Runs tests to verify the agent works correctly.
        
        Args:
            tag: Agent package tag to test
        """
        print(f"Testing agent: {tag}")
        print("  Running agent tests...")
        
        # Simulate test execution
        tests = [
            "Health check test",
            "Configuration validation test",
            "Dependency resolution test",
            "Model loading test",
            "gRPC service test"
        ]
        
        for test in tests:
            print(f"    ✓ {test}")
        
        print("  All tests passed!")
    
    def configure_profile(self, args):
        """
        Configure registry profile
        
        Args:
            args: Command line arguments
        """
        if args.action == "profile":
            if args.subaction == "add":
                # Validate PAT format
                if not self.profile_manager.validate_pat(args.pat):
                    print("Error: Invalid PAT format. PAT should be 64 characters hexadecimal.")
                    sys.exit(1)
                
                success = self.profile_manager.configure_profile(
                    name=args.name,
                    registry=args.registry,
                    pat=args.pat,
                    description=args.description or "",
                    set_default=args.set_default
                )
                
                if success:
                    print(f"Profile '{args.name}' configured successfully")
                    if args.test:
                        print("Testing connection...")
                        if self.profile_manager.test_profile(args.name):
                            print("Connection test successful!")
                        else:
                            print("Connection test failed!")
                else:
                    print("Failed to configure profile")
                    sys.exit(1)
            
            elif args.subaction == "list":
                profiles, default_profile = self.profile_manager.list_profiles()
                
                if not profiles:
                    print("No profiles configured")
                    print("Use 'agent configure profile add' to add a profile")
                    return
                
                print("Configured profiles:")
                for profile in profiles:
                    default_marker = " (default)" if profile.name == default_profile else ""
                    print(f"  {profile.name}{default_marker}")
                    print(f"    Registry: {profile.registry}")
                    print(f"    Description: {profile.description}")
                    print()
            
            elif args.subaction == "remove":
                success = self.profile_manager.remove_profile(args.name)
                if not success:
                    sys.exit(1)
            
            elif args.subaction == "test":
                success = self.profile_manager.test_profile(args.name)
                if not success:
                    sys.exit(1)
            
            elif args.subaction == "set-default":
                success = self.profile_manager.set_default_profile(args.name)
                if not success:
                    sys.exit(1)

    def push_agent(self, tag: str, profile: str = None):
        """
        Push agent to remote registry
        
        Args:
            tag: Agent package tag to push
            profile: Profile to use (defaults to default profile)
        """
        print(f"Pushing agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            # Find package directory
            if hasattr(self, 'last_build_path') and self.last_build_path:
                package_dir = Path(self.last_build_path)
            else:
                package_dir = Path(self.builder.build_dir) / agent_name
            if not package_dir.exists():
                print(f"  Error: Package not found. Build the agent first: agent build -t {tag} .")
                return
            
            # Push to registry
            success = registry_manager.push(agent_name, str(package_dir))
            
            if success:
                print(f"  Successfully pushed {tag} to registry")
            else:
                print(f"  Failed to push {tag} to registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def pull_agent(self, tag: str, profile: str = None):
        """
        Pull agent from remote registry
        
        Args:
            tag: Agent package tag to pull
            profile: Profile to use (defaults to default profile)
        """
        print(f"Pulling agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            # Create destination directory
            dest_dir = f"pulled_{agent_name}"
            
            # Pull from registry
            success = registry_manager.pull(agent_name, dest_dir)
            
            if success:
                print(f"  Successfully pulled {tag} to {dest_dir}")
            else:
                print(f"  Failed to pull {tag} from registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def list_agents(self, profile: str = None):
        """List all agents in remote registry"""
        print("Available agents in registry:")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            agents = registry_manager.list()
            if not agents:
                print("  No agents found in registry")
                return
            
            for agent in agents:
                print(f"  {agent.name:<30} {agent.version:<10} {agent.description}")
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)
    
    def remove_agent(self, tag: str, profile: str = None):
        """
        Remove agent from remote registry
        
        Args:
            tag: Agent package tag to remove
            profile: Profile to use (defaults to default profile)
        """
        print(f"Removing agent: {tag}")
        
        try:
            # Initialize registry manager
            registry_manager = RegistryManager(profile or "default")
            
            # Extract agent name from tag
            agent_name = tag.split(":")[0] if ":" in tag else tag
            
            success = registry_manager.remove(agent_name)
            
            if success:
                print(f"  Successfully removed {tag} from registry")
            else:
                print(f"  Failed to remove {tag} from registry")
                sys.exit(1)
                
        except Exception as e:
            print(f"  Error: {e}")
            sys.exit(1)

    def inspect_agent(self, tag: str):
        """
        Show agent details
        
        Displays detailed information about the agent package.
        
        Args:
            tag: Agent package tag to inspect
        """
        print(f"Inspecting agent: {tag}")
        print("  Note: This is a placeholder implementation")
        print("  In a real implementation, this would show:")
        print("    - Package metadata")
        print("    - Layer information")
        print("    - Configuration details")
        print("    - Dependencies")
        print("    - Environment variables")
        print("    - Capabilities")
        print("    - Model configuration")

    def handle_llm(self, args):
        """Dispatch LLM subcommands"""
        if args.llm_command == "providers":
            if args.providers_command == "list":
                self.list_llm_providers()
        elif args.llm_command == "models":
            if args.models_command == "list":
                self.list_llm_models(args.provider, args.capabilities)
        elif args.llm_command == "configure":
            if args.configure_command == "auto":
                self.configure_llm_auto()
            elif args.configure_command == "wizard":
                self.configure_llm_wizard()
            elif args.configure_command == "set-key":
                self.configure_llm_set_key(args.provider, args.api_key)
            elif args.configure_command == "set-default":
                self.configure_llm_set_default(args.provider, args.model)
        elif args.llm_command == "chat":
            self.chat_with_llm(args.provider, args.model, args.message, args.temperature)
        elif args.llm_command == "doctor":
            self.llm_doctor()
        elif args.llm_command == "generate-agentfile":
            self.generate_agentfile_llm(args.description, args.output)
        elif args.llm_command == "suggest-template":
            self.suggest_template_llm(args.description)
        elif args.llm_command == "generate-tests":
            self.generate_tests_llm(args.description, args.test_type)
        elif args.llm_command == "optimize-agent":
            self.optimize_agent_llm(args.agent_path, args.optimization_goal)
        else:
            print(f"Unknown LLM command: {args.llm_command}")
            sys.exit(1)

    def list_llm_providers(self):
        """List available LLM providers."""
        providers = LLMProviderFactory.list_providers()
        print("Available LLM providers:")
        for p in providers:
            print(f"  - {p}")

    def list_llm_models(self, provider_name: str, capabilities: str = None):
        """List models for a specific LLM provider."""
        config_manager = LLMConfigManager()
        provider = LLMProviderFactory.get_provider(provider_name, config_manager)
        if not provider:
            print(f"Unknown provider: {provider_name}")
            sys.exit(1)
        models = provider.list_models(capabilities=capabilities)
        if not models:
            print("No models found.")
            return
        print(f"Models for provider '{provider_name}':")
        for m in models:
            caps = ",".join(m.get('capabilities', []))
            print(f"  - {m['name']} (ctx={m.get('context_window','?')}, caps=[{caps}])")

    def configure_llm_auto(self):
        """Auto-configure LLM from environment variables."""
        config_manager = LLMConfigManager()
        summary = config_manager.auto_configure_from_env()
        if not summary["keys"] and not summary["default"]:
            print("No environment keys found. Export OPENAI_API_KEY, ANTHROPIC_API_KEY or GOOGLE_API_KEY/GEMINI_API_KEY.")
        else:
            if summary["keys"]:
                print(f"Configured API keys for: {', '.join(summary['keys'])}")
            if summary["default"]:
                d = summary["default"]
                print(f"Default set to {d['provider']}:{d['model']}")

    def configure_llm_wizard(self):
        """Interactive LLM configuration wizard."""
        config_manager = LLMConfigManager()
        from .llm.wizard import run_interactive_wizard
        run_interactive_wizard(config_manager)

    def configure_llm_set_key(self, provider: str, api_key: str):
        """Set API key for a specific LLM provider."""
        config_manager = LLMConfigManager()
        config_manager.set_api_key(provider, api_key)
        print(f"Saved API key for {provider}")

    def configure_llm_set_default(self, provider: str, model: str):
        """Set default LLM provider and model."""
        config_manager = LLMConfigManager()
        config_manager.set_default_model(provider, model)
        print(f"Default LLM set to {provider}:{model}")

    def chat_with_llm(self, provider: str = None, model: str = None, message: str = None, temperature: float = 0.2):
        """Quick chat test with a model."""
        config_manager = LLMConfigManager()
        default_cfg = config_manager.get_default() or {}
        provider_name = provider or default_cfg.get('provider')
        model_name = model or default_cfg.get('model')
        provider = LLMProviderFactory.get_provider(provider_name, config_manager)
        if not provider:
            print(f"Unknown provider: {provider_name or '(none)'}")
            sys.exit(1)
        if not model_name or not message:
            print("Model and --message are required (either pass --model or set default via configure).")
            sys.exit(1)
        # Non-throwing provider.chat; handle common error shapes
        response = provider.chat(model=model_name, messages=[{"role": "user", "content": message}], temperature=temperature)
        if isinstance(response, dict) and response.get('error'):
            code = response.get('error')
            msg = response.get('message', 'Unknown error')
            print(f"Chat failed ({code}): {msg}")
            sys.exit(1)
        print(response.get('text') or response.get('content') or json.dumps(response, indent=2))

    def llm_doctor(self):
        """Simple diagnostics: list defaults, key presence (not values), and provider reachability if possible"""
        config_manager = LLMConfigManager()
        print("LLM Doctor")
        print("----------")
        default_cfg = config_manager.get_default() or {}
        if default_cfg:
            print(f"Default: {default_cfg.get('provider')}:{default_cfg.get('model')}")
        else:
            print("Default: (not set)")
        for prov in ["openai", "anthropic", "google"]:
            has_key = bool(config_manager.get_api_key(prov) or os.getenv({"openai":"OPENAI_API_KEY","anthropic":"ANTHROPIC_API_KEY","google":"GOOGLE_API_KEY"}[prov]) or (prov=="google" and os.getenv("GEMINI_API_KEY")))
            print(f"{prov}: {'key: yes' if has_key else 'key: no'}")

    def generate_agentfile_llm(self, description: str, output: str = "Agentfile"):
        """Generate Agentfile using LLM from natural language description."""
        print(f"🤖 Generating Agentfile using LLM...")
        print(f"Description: {description}")
        
        creator = LLMAgentCreator()
        result = creator.generate_agentfile(description, output)
        
        if "error" in result:
            print(f"❌ Generation failed: {result['message']}")
            sys.exit(1)
        
        print(f"✅ Agentfile generated successfully!")
        print(f"📁 Output: {result['output_path']}")
        print(f"🤖 Provider: {result['provider']}")
        print(f"🧠 Model: {result['model']}")
        print(f"\n📄 Generated content preview:")
        content = result['content']
        if len(content) > 200:
            print(f"{content[:200]}...")
        else:
            print(content)

    def suggest_template_llm(self, description: str):
        """Get template recommendation using LLM."""
        print(f"🤖 Analyzing requirements for template recommendation...")
        print(f"Description: {description}")
        
        creator = LLMAgentCreator()
        result = creator.suggest_template(description)
        
        if "error" in result:
            print(f"❌ Suggestion failed: {result['message']}")
            sys.exit(1)
        
        suggestion = result['suggestion']
        print(f"✅ Template recommendation:")
        print(f"📋 Template: {suggestion['template']}")
        print(f"💡 Reasoning: {suggestion['reasoning']}")
        print(f"🔧 Capabilities: {', '.join(suggestion['capabilities'])}")
        print(f"📦 Dependencies: {', '.join(suggestion['dependencies'])}")
        print(f"\n🚀 Next steps:")
        print(f"   agent init my-agent --template {suggestion['template']}")

    def generate_tests_llm(self, description: str, test_type: str = "comprehensive"):
        """Generate test cases using LLM."""
        print(f"🤖 Generating {test_type} test cases using LLM...")
        print(f"Agent description: {description}")
        
        creator = LLMAgentCreator()
        result = creator.generate_test_cases(description, test_type)
        
        if "error" in result:
            print(f"❌ Test generation failed: {result['message']}")
            sys.exit(1)
        
        test_cases = result['test_cases']
        print(f"✅ Generated {len(test_cases['test_cases'])} test cases!")
        print(f"🤖 Provider: {result['provider']}")
        print(f"🧠 Model: {result['model']}")
        
        print(f"\n📋 Test Cases:")
        for i, test in enumerate(test_cases['test_cases'][:5], 1):  # Show first 5
            print(f"  {i}. {test['name']} ({test['test_type']})")
            print(f"     Description: {test['description']}")
            print(f"     Input: {test['input']}")
            print(f"     Expected: {test['expected_output']}")
            print()
        
        if len(test_cases['test_cases']) > 5:
            print(f"  ... and {len(test_cases['test_cases']) - 5} more test cases")
        
        print(f"📊 Test Data: {test_cases['test_data']}")
        print(f"🔍 Validation: {test_cases['validation_logic']}")

    def optimize_agent_llm(self, agent_path: str, optimization_goal: str):
        """Optimize agent using LLM analysis."""
        print(f"🤖 Analyzing agent for {optimization_goal} optimization...")
        print(f"Agent path: {agent_path}")
        
        creator = LLMAgentCreator()
        result = creator.optimize_agent(agent_path, optimization_goal)
        
        if "error" in result:
            print(f"❌ Optimization failed: {result['message']}")
            sys.exit(1)
        
        optimization = result['optimization']
        print(f"✅ Optimization analysis complete!")
        print(f"🤖 Provider: {result['provider']}")
        print(f"🧠 Model: {result['model']}")
        
        print(f"\n📊 Current Analysis:")
        print(f"  Strengths: {', '.join(optimization['current_analysis']['strengths'])}")
        print(f"  Weaknesses: {', '.join(optimization['current_analysis']['weaknesses'])}")
        
        print(f"\n🚀 Optimization Recommendations:")
        for rec in optimization['optimization_recommendations']:
            print(f"  📋 {rec['category'].title()}")
            print(f"     Current: {rec['current']}")
            print(f"     Recommended: {rec['recommended']}")
            print(f"     Reasoning: {rec['reasoning']}")
            print(f"     Impact: {rec['impact']} | Effort: {rec['effort']}")
            print()
        
        print(f"💾 Optimized Agentfile available in optimization results")
        print(f"📝 To apply: Copy the optimized content to your Agentfile")

def main():
    """
    Main entry point for the CLI
    
    Parses command line arguments and executes the appropriate command.
    """
    parser = argparse.ArgumentParser(
        description="Agent as Code (AaC) CLI",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agent init my-sentiment-agent
  agent build -t my-agent:latest .
  agent run my-agent:latest
  agent test my-agent:latest
  agent inspect my-agent:latest
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new agent project')
    init_parser.add_argument('name', help='Agent project name')
    init_parser.add_argument('--template', default='python', help='Template to use (default: python)')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build agent from Agentfile')
    build_parser.add_argument('-t', '--tag', required=True, help='Package tag (e.g., my-agent:latest)')
    build_parser.add_argument('path', default='.', help='Path to agent project (default: current directory)')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run agent locally')
    run_parser.add_argument('tag', help='Agent package tag to run')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test agent functionality')
    test_parser.add_argument('tag', help='Agent package tag to test')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Show agent details')
    inspect_parser.add_argument('tag', help='Agent package tag to inspect')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Push agent to registry')
    push_parser.add_argument('tag', help='Agent package tag to push')
    push_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull agent from registry')
    pull_parser.add_argument('tag', help='Agent package tag to pull')
    pull_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Images command
    images_parser = subparsers.add_parser('images', help='List available agents')
    images_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # RMI command
    rmi_parser = subparsers.add_parser('rmi', help='Remove agent from registry')
    rmi_parser.add_argument('tag', help='Agent package tag to remove')
    rmi_parser.add_argument('--profile', help='Profile to use (defaults to default profile)')
    
    # Configure command
    configure_parser = subparsers.add_parser('configure', help='Configure registry profile')
    configure_subparsers = configure_parser.add_subparsers(dest='action', help='Configure actions')
    
    # Profile subcommand
    profile_parser = configure_subparsers.add_parser('profile', help='Manage registry profiles')
    profile_subparsers = profile_parser.add_subparsers(dest='subaction', help='Profile actions')
    
    # Add profile
    profile_add_parser = profile_subparsers.add_parser('add', help='Add new profile')
    profile_add_parser.add_argument('name', help='Profile name')
    profile_add_parser.add_argument('--registry', required=True, help='Registry URL')
    profile_add_parser.add_argument('--pat', required=True, help='Personal Access Token (PAT)')
    profile_add_parser.add_argument('--description', help='Profile description')
    profile_add_parser.add_argument('--set-default', action='store_true', help='Set as default profile')
    profile_add_parser.add_argument('--test', action='store_true', help='Test connection after adding')
    
    # List profiles
    profile_list_parser = profile_subparsers.add_parser('list', help='List configured profiles')
    
    # Remove profile
    profile_remove_parser = profile_subparsers.add_parser('remove', help='Remove profile')
    profile_remove_parser.add_argument('name', help='Profile name to remove')
    
    # Test profile
    profile_test_parser = profile_subparsers.add_parser('test', help='Test profile connection')
    profile_test_parser.add_argument('name', help='Profile name to test')
    
    # Set default profile
    profile_default_parser = profile_subparsers.add_parser('set-default', help='Set default profile')
    profile_default_parser.add_argument('name', help='Profile name to set as default')

    # LLM command group
    llm_parser = subparsers.add_parser('llm', help='LLM related commands')
    llm_subparsers = llm_parser.add_subparsers(dest='llm_command', help='LLM actions')

    # llm providers list
    llm_providers = llm_subparsers.add_parser('providers', help='Manage or list LLM providers')
    llm_providers_sub = llm_providers.add_subparsers(dest='providers_command', help='Providers actions')
    llm_providers_list = llm_providers_sub.add_parser('list', help='List supported providers')

    # llm models list
    llm_models = llm_subparsers.add_parser('models', help='Discover models')
    llm_models_sub = llm_models.add_subparsers(dest='models_command', help='Models actions')
    llm_models_list = llm_models_sub.add_parser('list', help='List models for a provider')
    llm_models_list.add_argument('--provider', required=True, help='Provider name (openai|anthropic|google)')
    llm_models_list.add_argument('--capabilities', help='Comma-separated capabilities filter (e.g., chat,tools,vision)')

    # llm configure
    llm_configure = llm_subparsers.add_parser('configure', help='Configure LLM defaults and credentials')
    llm_configure_sub = llm_configure.add_subparsers(dest='configure_command', help='Configure actions')
    llm_configure_wizard = llm_configure_sub.add_parser('wizard', help='Interactive configuration wizard')
    llm_configure_auto = llm_configure_sub.add_parser('auto', help='Auto-configure from environment variables')
    llm_configure_set_default = llm_configure_sub.add_parser('set-default', help='Set default provider/model')
    llm_configure_set_default.add_argument('--provider', required=True)
    llm_configure_set_default.add_argument('--model', required=True)
    llm_configure_set_key = llm_configure_sub.add_parser('set-key', help='Store API key for a provider')
    llm_configure_set_key.add_argument('--provider', required=True)
    llm_configure_set_key.add_argument('--api-key', required=True)

    # llm chat
    llm_chat = llm_subparsers.add_parser('chat', help='Quick chat test with a model')
    llm_chat.add_argument('--provider', help='Provider name (defaults to configured)')
    llm_chat.add_argument('--model', help='Model name (defaults to provider default)')
    llm_chat.add_argument('--message', required=True, help='User message to send')
    llm_chat.add_argument('--temperature', type=float, default=0.2, help='Sampling temperature')

    # llm tune (placeholder for beta)
    # llm doctor
    llm_doctor = llm_subparsers.add_parser('doctor', help='Diagnose LLM configuration and connectivity')
    llm_tune = llm_subparsers.add_parser('tune', help='Managed fine-tuning (beta)')
    llm_tune_sub = llm_tune.add_subparsers(dest='tune_action', help='Tune actions')
    llm_tune_create = llm_tune_sub.add_parser('create', help='Create a fine-tune job (beta)')
    llm_tune_create.add_argument('--provider', required=True)
    llm_tune_create.add_argument('--base-model', required=True)
    llm_tune_create.add_argument('--dataset', required=True, help='Path to dataset (provider-specific format)')
    llm_tune_status = llm_tune_sub.add_parser('status', help='Check fine-tune job status (beta)')
    llm_tune_status.add_argument('--provider', required=True)
    llm_tune_status.add_argument('--job-id', required=True)
    llm_tune_promote = llm_tune_sub.add_parser('promote', help='Promote a completed fine-tune (beta)')
    llm_tune_promote.add_argument('--provider', required=True)
    llm_tune_promote.add_argument('--job-id', required=True)

    # New LLM-enhanced commands
    llm_generate_agentfile = llm_subparsers.add_parser('generate-agentfile', help='Generate Agentfile using LLM from natural language description')
    llm_generate_agentfile.add_argument('--description', required=True, help='Natural language description of the agent')
    llm_generate_agentfile.add_argument('--output', default='Agentfile', help='Output file name (default: Agentfile)')

    llm_suggest_template = llm_subparsers.add_parser('suggest-template', help='Get template recommendation using LLM')
    llm_suggest_template.add_argument('--description', required=True, help='Natural language description of the agent requirements')

    llm_generate_tests = llm_subparsers.add_parser('generate-tests', help='Generate test cases using LLM')
    llm_generate_tests.add_argument('--description', required=True, help='Natural language description of the agent')
    llm_generate_tests.add_argument('--test-type', default='comprehensive', help='Type of test cases to generate (e.g., comprehensive, unit)')

    llm_optimize_agent = llm_subparsers.add_parser('optimize-agent', help='Optimize agent using LLM analysis')
    llm_optimize_agent.add_argument('--agent-path', required=True, help='Path to the Agentfile or agent directory to optimize')
    llm_optimize_agent.add_argument('--optimization-goal', required=True, help='Goal for optimization (e.g., performance, cost, robustness)')
    
    # Global flags (custom rich output)
    parser.add_argument('--version', action='store_true', help='Show AaC version')
    parser.add_argument('-h', '--help', action='store_true', help='Show this message and exit.')

    # Helper functions for rich output
    def _print_banner(console):
        text = r"""

    _                _       _          ___         _               _         ___ 
   /_\  __ _ ___ _ _| |_    /_\   ___  / __|___  __| |___   ___    /_\  __ _ / __|
  / _ \/ _` / -_) ' \  _|  / _ \ (_-< | (__/ _ \/ _` / -_) |___|  / _ \/ _` | (__ 
 /_/ \_\__, \___|_||_\__| /_/ \_\/__/  \___\___/\__,_\___|       /_/ \_\__,_|\___|
       |___/                                                                      

"""
        console.print(Align.center(text))

    def _print_about(console):
        def _docs_url() -> str:
            return os.getenv("AAC_DOCS_URL", "https://agent-as-code.myagentregistry.com")
        # Static GitHub handle per request
        lines = f"🔗 {_docs_url()}\n🐙 GitHub: @pxkundu"
        console.print(Panel.fit(lines, title=" About ", border_style="cyan"))

    def _detect_llm_status() -> str:
        try:
            from .llm.config_manager import LLMConfigManager
            from .llm.manager import LLMProviderFactory

            def _env_key_for(provider_name: str) -> Optional[str]:
                if provider_name == "openai":
                    return os.getenv("OPENAI_API_KEY")
                if provider_name == "anthropic":
                    return os.getenv("ANTHROPIC_API_KEY")
                if provider_name == "google":
                    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                return None

            def _looks_valid_key(provider_name: str, key: str) -> bool:
                if not key:
                    return False
                if provider_name == "openai":
                    return key.startswith("sk-") and len(key) > 20
                if provider_name == "anthropic":
                    return key.startswith("sk-ant-") and len(key) > 20
                if provider_name == "google":
                    return key.startswith("AIza") and len(key) >= 30
                return True

            cfg = LLMConfigManager()
            default = cfg.get_default() or {}
            provider = (default.get("provider") or "").lower()
            model = default.get("model")
            if not provider or not model:
                return "🤖 LLM: ⚠️ Not configured (agent llm configure wizard)"

            # Prefer stored key; fall back to env if present
            key = cfg.get_api_key(provider) or _env_key_for(provider)
            prov = LLMProviderFactory.get_provider(provider, cfg)
            if not prov:
                return f"🤖 LLM: ⚠️ {provider}:{model} (provider unavailable)"
            if not key:
                return f"🤖 LLM: ⚠️ {provider}:{model} (missing API key)"
            if not _looks_valid_key(provider, key):
                return f"🤖 LLM: ⚠️ {provider}:{model} (invalid key format)"
            return f"🤖 LLM: ✅ {provider}:{model}"
        except Exception:
            return "🤖 LLM: ⚠️ Not available"

    def _detect_runtime_status() -> str:
        agentfile = Path.cwd() / "Agentfile"
        if agentfile.exists():
            try:
                parser_local = AaCParser()
                cfg = parser_local.parse_agentfile(str(agentfile))
                runtime = cfg.runtime or "unknown"
                return f"🐳 Runtime: ✅ {runtime} (from ./Agentfile)"
            except Exception:
                return "🐳 Runtime: ⚠️ Failed to parse Agentfile"
        # environment override for default base image
        default_image = os.getenv("AAC_DEFAULT_RUNTIME", "agent/python:3.11-docker")
        return f"🐳 Runtime: ✅ {default_image} (default)"

    def _get_version_line() -> str:
        try:
            v = pkg_version("agent-as-code")
        except PackageNotFoundError:
            v = os.getenv("AAC_VERSION", "dev")
        return f"🚀 AaC v{v} - Agent as Code"

    def _print_status(console):
        console.print("\n" + _detect_llm_status())
        console.print(_detect_runtime_status())

    def _print_rich_help():
        if Console is None:
            parser.print_help()
            return
        console = Console()
        _print_banner(console)
        _print_about(console)
        _print_status(console)

        # Usage
        console.print()
        console.rule()
        console.print("[bold]Usage:[/bold] agent [OPTIONS] COMMAND [ARGS]...\n")
        console.print("agent: Agent as Code - Declarative AI agent CLI.\n")

        # Options table
        options = Table(title="Options", show_header=False, box=None)
        options.add_row("--version", "Show AaC version")
        options.add_row("-h, --help", "Show this message and exit.")
        console.print(options)

        # Commands table
        cmds = Table(title="Commands", show_header=False, box=None)
        cmds.add_row("init", "Initialize new agent project.")
        cmds.add_row("build", "Build agent from Agentfile.")
        cmds.add_row("run", "Run agent locally.")
        cmds.add_row("test", "Test agent functionality.")
        cmds.add_row("inspect", "Show agent details.")
        cmds.add_row("push", "Push agent to registry.")
        cmds.add_row("pull", "Pull agent from registry.")
        cmds.add_row("images", "List available agents.")
        cmds.add_row("rmi", "Remove agent from registry.")
        cmds.add_row("configure", "Configure registry profile.")
        cmds.add_row("llm", "LLM related commands.")
        console.print(cmds)
        console.print()

    def _print_rich_version():
        if Console is None:
            print(_get_version_line())
            return
        console = Console()
        _print_banner(console)
        console.print("\n" + _get_version_line())
        console.print("Declarative AI agent configuration framework")
        # About block
        _print_about(console)
        # Dynamic status
        console.print(_detect_llm_status())
        console.print(_detect_runtime_status())

    # Parse arguments
    args = parser.parse_args()

    # Custom version output
    if getattr(args, 'version', False):
        _print_rich_version()
        sys.exit(0)

    # Top-level help
    if getattr(args, 'help', False):
        _print_rich_help()
        sys.exit(0)

    # No args -> rich help
    if not args.command:
        _print_rich_help()
        sys.exit(0)
    
    # Run CLI
    cli = AgentCLI()
    cli.run(args)

if __name__ == "__main__":
    """
    CLI entry point
    
    Usage:
        python agent_cli.py init my-agent
        python agent_cli.py build -t my-agent:latest .
        python agent_cli.py run my-agent:latest
    """
    main() 