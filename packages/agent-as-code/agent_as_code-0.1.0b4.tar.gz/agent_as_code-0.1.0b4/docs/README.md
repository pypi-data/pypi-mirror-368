# Agent as Code (AaC) Documentation
====================================

Welcome to the Agent as Code (AaC) framework documentation. This guide will help you understand and use the framework to create, build, and deploy AI agents using declarative configuration.

## What is Agent as Code?

Agent as Code (AaC) is a declarative configuration system for AI agents, inspired by Docker and Infrastructure as Code (IaC). It enables developers to define AI agents using simple, version-controlled configuration files.

**Think of it as "Docker for AI agents"** - just like Dockerfile makes it easy to define and build containers, Agentfile makes it easy to define and build AI agents.

## Core Philosophy

- **Declarative**: Define what the agent should do, not how to do it
- **Version Controlled**: Track agent configurations in Git
- **Reusable**: Share and reuse agent configurations
- **Simple**: Easy to understand and modify
- **Portable**: Work across different environments and clouds

## Quick Start

```bash
# Install the framework
pip install agent-as-code

# Create your first agent
agent init my-first-agent

# Build the agent
agent build -t my-first-agent:latest .

# Run the agent
agent run my-first-agent:latest
```

## Documentation Sections

### Core Components

1. **[Agentfile Configuration](./agentfile.md)** - Learn how to write Agentfile configurations
2. **[CLI Tool](./cli.md)** - Master the `agent` command-line interface
3. **[Parser](./parser.md)** - Understand how Agentfile parsing works
4. **[Builder](./builder.md)** - Learn about agent building and packaging
5. **[Registry](./registry.md)** - Discover agent storage and sharing
6. **[Runtime](./runtime.md)** - Understand agent execution environments

### Usage Guides

7. **[How to Use](./how-to-use.md)** - Complete guide to using the framework
8. **[Examples](./examples.md)** - Real-world examples and use cases

## Framework Goals

### Primary Objectives

1. **Simplify AI Agent Development**
   - Reduce complexity of agent creation
   - Provide standardized patterns
   - Enable rapid prototyping

2. **Enable Declarative Configuration**
   - Version-controlled agent definitions
   - Infrastructure as Code principles
   - Reproducible deployments

3. **Facilitate Agent Sharing**
   - Centralized registry for agents
   - Easy distribution and discovery
   - Community-driven development

4. **Support Multiple Runtimes**
   - Docker containerization
   - Kubernetes deployment
   - Cloud-native architectures

### Key Benefits

- **Developer Experience**: Familiar Docker-like commands
- **Portability**: Run agents anywhere
- **Scalability**: Cloud-native micro-service architecture
- **Collaboration**: Share agents through registry
- **Automation**: CI/CD pipeline integration

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agentfile     │───▶│   AaC Parser    │───▶│  Agent Builder  │
│  (Config)       │    │  (Validation)   │    │  (Packaging)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Registry      │◀───│   Agent CLI     │◀───│  Agent Runtime  │
│  (Storage)      │    │  (Commands)     │    │  (Execution)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Getting Help

- **Documentation**: This guide and component-specific docs
- **Examples**: See the examples directory for working agents
- **CLI Help**: Run `agent --help` for command reference
- **Issues**: Report bugs or request features on GitHub

## Next Steps

1. Read the **[How to Use](./how-to-use.md)** guide
2. Explore **[Examples](./examples.md)** for inspiration
3. Create your first agent with `agent init`
4. Join the community and share your agents!

---

**Ready to build your first AI agent?** Start with the [How to Use](./how-to-use.md) guide!
