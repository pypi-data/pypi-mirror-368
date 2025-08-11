"""
Agent as Code (AaC) Framework
============================

A declarative configuration system for AI agents, inspired by Docker and Infrastructure as Code.
"""

__version__ = "0.1.0b4"
__author__ = "Partha Sarathi Kundu"
__email__ = "inboxpartha@outlook.com"

# Main components
from .parser.aac_parser import AaCParser
from .builder.unified_builder import UnifiedAgentBuilder
from .cli.agent_cli import AgentCLI

# Public API
__all__ = [
    "AaCParser",
    "UnifiedAgentBuilder",
    "AgentCLI",
    "__version__",
    "__author__",
    "__email__",
]
