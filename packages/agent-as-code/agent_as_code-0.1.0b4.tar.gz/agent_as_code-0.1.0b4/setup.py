#!/usr/bin/env python3
"""
Setup script for Agent as Code (AaC) framework
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Agent as Code (AaC) - Declarative AI agent configuration framework"

setup(
    name="agent-as-code",
    version="0.1.0b4",
    description="Declarative configuration system for AI agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Partha Sarathi Kundu",
    author_email="inboxpartha@outlook.com",
    url="https://agent-as-code.myagentregistry.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'agent_as_code': [
            'proto/*.proto',
            'templates/*/*',
            'config/*.json',
        ],
    },
    install_requires=[
        "grpcio>=1.59.0",
        "grpcio-tools>=1.59.0",
        "requests>=2.31.0",
        "numpy>=1.21.0",
        "openai>=0.28.0",
        "anthropic>=0.34.0",
        "google-generativeai>=0.7.2",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agent=agent_as_code.cli.agent_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    keywords="ai, agent, configuration, declarative, docker-like",
    project_urls={
        "Website": "https://agent-as-code.myagentregistry.com/",
        "Getting Started": "https://agent-as-code.myagentregistry.com/getting-started",
        "Getting Started - Prerequisites": "https://agent-as-code.myagentregistry.com/getting-started#prerequisites",
        "Getting Started - Installation": "https://agent-as-code.myagentregistry.com/getting-started#installation",
        "Getting Started - Quick Start": "https://agent-as-code.myagentregistry.com/getting-started#quick-start",
        "Getting Started - First Agent": "https://agent-as-code.myagentregistry.com/getting-started#first-agent",
        "Getting Started - Registry Ops": "https://agent-as-code.myagentregistry.com/getting-started#registry-operations",
        "Getting Started - Deployment": "https://agent-as-code.myagentregistry.com/getting-started#deployment-options",
        "Documentation": "https://agent-as-code.myagentregistry.com/documentation",
        "Docs - Agentfile": "https://agent-as-code.myagentregistry.com/documentation#agentfile",
        "Docs - Parser": "https://agent-as-code.myagentregistry.com/documentation#parser",
        "Docs - Builder": "https://agent-as-code.myagentregistry.com/documentation#builder",
        "Docs - Runtime": "https://agent-as-code.myagentregistry.com/documentation#runtime",
        "Docs - Deployment Strategies": "https://agent-as-code.myagentregistry.com/documentation#deployment-strategies",
        "Docs - Agent Runtime Strategies": "https://agent-as-code.myagentregistry.com/documentation#agent-runtime-strategies",
        "Docs - Cloud Agnostic Runtime": "https://agent-as-code.myagentregistry.com/documentation#cloud-agnostic-runtime",
        "Docs - Bulletproof Runtimes": "https://agent-as-code.myagentregistry.com/documentation#bulletproof-runtimes",
        "Docs - PAT System": "https://agent-as-code.myagentregistry.com/documentation#pat-system",
        "Docs - PAT Technical": "https://agent-as-code.myagentregistry.com/documentation#pat-technical-implementation",
        "Docs - PAT Documentation": "https://agent-as-code.myagentregistry.com/documentation#pat-documentation",
        "Docs - PAT Quick Reference": "https://agent-as-code.myagentregistry.com/documentation#pat-quick-reference",
        "CLI": "https://agent-as-code.myagentregistry.com/cli",
        "CLI - Overview": "https://agent-as-code.myagentregistry.com/cli#overview",
        "CLI - Installation": "https://agent-as-code.myagentregistry.com/cli#installation",
        "CLI - Global Options": "https://agent-as-code.myagentregistry.com/cli#global-options",
        "CLI - Core Commands": "https://agent-as-code.myagentregistry.com/cli#core-commands",
        "CLI - agent init": "https://agent-as-code.myagentregistry.com/cli#agent-init",
        "CLI - agent build": "https://agent-as-code.myagentregistry.com/cli#agent-build",
        "CLI - agent run": "https://agent-as-code.myagentregistry.com/cli#agent-run",
        "CLI - agent test": "https://agent-as-code.myagentregistry.com/cli#agent-test",
        "CLI - agent inspect": "https://agent-as-code.myagentregistry.com/cli#agent-inspect",
        "CLI - Registry Commands": "https://agent-as-code.myagentregistry.com/cli#registry-commands",
        "CLI - agent push": "https://agent-as-code.myagentregistry.com/cli#agent-push",
        "CLI - agent pull": "https://agent-as-code.myagentregistry.com/cli#agent-pull",
        "CLI - agent images": "https://agent-as-code.myagentregistry.com/cli#agent-images",
        "CLI - agent rmi": "https://agent-as-code.myagentregistry.com/cli#agent-rmi",
        "CLI - Configuration": "https://agent-as-code.myagentregistry.com/cli#configuration",
        "CLI - agent configure": "https://agent-as-code.myagentregistry.com/cli#agent-configure",
        "CLI - Workflow Examples": "https://agent-as-code.myagentregistry.com/cli#workflow-examples",
        "Registry": "https://agent-as-code.myagentregistry.com/registry",
        "Registry - Overview": "https://agent-as-code.myagentregistry.com/registry#overview",
        "Registry - Architecture": "https://agent-as-code.myagentregistry.com/registry#architecture",
        "Registry - Operations": "https://agent-as-code.myagentregistry.com/registry#registry-operations",
        "Registry - Discovery": "https://agent-as-code.myagentregistry.com/registry#agent-discovery",
        "Registry - Configuration": "https://agent-as-code.myagentregistry.com/registry#configuration",
        "Registry - Metadata": "https://agent-as-code.myagentregistry.com/registry#agent-metadata",
        "Registry - Versioning": "https://agent-as-code.myagentregistry.com/registry#version-management",
        "Registry - Access Control": "https://agent-as-code.myagentregistry.com/registry#access-control",
        "Registry - Security": "https://agent-as-code.myagentregistry.com/registry#security",
        "Registry - Monitoring": "https://agent-as-code.myagentregistry.com/registry#monitoring",
        "Examples": "https://agent-as-code.myagentregistry.com/examples",
        "Examples - Weather Monitoring": "https://agent-as-code.myagentregistry.com/examples#weather-monitoring",
        "Examples - Text Generation": "https://agent-as-code.myagentregistry.com/examples#text-generation",
        "Examples - Sentiment Analysis": "https://agent-as-code.myagentregistry.com/examples#sentiment-analysis",
        "Examples - Data Analysis": "https://agent-as-code.myagentregistry.com/examples#data-analysis",
        "Examples - Use Cases": "https://agent-as-code.myagentregistry.com/examples#use-cases",
        "Examples - Content Creation": "https://agent-as-code.myagentregistry.com/examples#content-creation",
        "Examples - Data Processing": "https://agent-as-code.myagentregistry.com/examples#data-processing",
        "Examples - Monitoring": "https://agent-as-code.myagentregistry.com/examples#monitoring",
        "Examples - Development": "https://agent-as-code.myagentregistry.com/examples#development",
        "Examples - Communication": "https://agent-as-code.myagentregistry.com/examples#communication",
        "Registry_Home": "https://www.myagentregistry.com",
        "Developed_By": "https://github.com/pxkundu",
        "PyPI": "https://pypi.org/project/agent-as-code/",
    },
) 