# CLI Tool
=========

The Agent as Code CLI (`agent`) is the primary interface for creating, building, and managing AI agents. It provides Docker-like commands that make agent development simple and intuitive.

## Overview

The CLI tool enables you to:
- **Create** new agent projects
- **Build** agents from Agentfile configurations
- **Run** agents locally for testing
- **Test** agent functionality
- **Manage** agent registry operations
- **Configure** registry profiles

## Installation

```bash
# Install the framework (includes CLI)
pip install agent-as-code

# Verify installation
agent --help
```

## Command Reference

### Global Options

```bash
agent [OPTIONS] COMMAND [ARGS]...

Options:
  -h, --help    Show help message and exit
  -v, --version Show version and exit
```

### Available Commands

#### `agent init`
Initialize a new agent project.

```bash
agent init [OPTIONS] PROJECT_NAME

Options:
  -t, --template TEXT    Template to use (default: python-agent)
  -d, --directory PATH   Directory to create project in
  -h, --help            Show help message and exit
```

**Examples:**
```bash
# Create a new agent project
agent init my-sentiment-agent

# Create with specific template
agent init my-agent --template python-agent

# Create in specific directory
agent init my-agent --directory /path/to/projects
```

#### `agent build`
Build an agent from Agentfile configuration.

```bash
agent build [OPTIONS] PATH

Options:
  -t, --tag TEXT        Tag for the agent (format: name:version)
  -f, --file PATH       Path to Agentfile (default: ./Agentfile)
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# Build agent from current directory
agent build -t my-agent:latest .

# Build with specific Agentfile
agent build -t my-agent:v1.0 -f /path/to/Agentfile .

# Build with custom tag
agent build -t sentiment-analyzer:1.0.0 .
```

#### `agent run`
Run an agent locally for testing.

```bash
agent run [OPTIONS] AGENT_NAME

Options:
  -p, --port INTEGER    Port to run on (default: 8080)
  -e, --env TEXT        Environment variables (format: KEY=VALUE)
  -d, --detach          Run in background
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# Run agent locally
agent run my-agent:latest

# Run on specific port
agent run my-agent:latest --port 9000

# Run with environment variables
agent run my-agent:latest -e OPENAI_API_KEY=your-key

# Run in background
agent run my-agent:latest --detach
```

#### `agent test`
Test agent functionality.

```bash
agent test [OPTIONS] AGENT_NAME

Options:
  -t, --timeout INTEGER    Test timeout in seconds (default: 30)
  -v, --verbose           Verbose output
  -h, --help             Show help message and exit
```

**Examples:**
```bash
# Test agent functionality
agent test my-agent:latest

# Test with timeout
agent test my-agent:latest --timeout 60

# Verbose testing
agent test my-agent:latest --verbose
```

#### `agent inspect`
Show detailed information about an agent.

```bash
agent inspect [OPTIONS] AGENT_NAME

Options:
  -f, --format TEXT    Output format (json, yaml, table)
  -h, --help          Show help message and exit
```

**Examples:**
```bash
# Show agent details
agent inspect my-agent:latest

# Show in JSON format
agent inspect my-agent:latest --format json

# Show in YAML format
agent inspect my-agent:latest --format yaml
```

#### `agent push`
Push an agent to the registry.

```bash
agent push [OPTIONS] AGENT_NAME

Options:
  -p, --profile TEXT    Registry profile to use
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# Push agent to registry
agent push my-agent:latest

# Push with specific profile
agent push my-agent:latest --profile production
```

#### `agent pull`
Pull an agent from the registry.

```bash
agent pull [OPTIONS] AGENT_NAME

Options:
  -p, --profile TEXT    Registry profile to use
  -d, --directory PATH  Directory to save agent in
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# Pull agent from registry
agent pull my-agent:latest

# Pull to specific directory
agent pull my-agent:latest --directory /path/to/agents

# Pull with specific profile
agent pull my-agent:latest --profile production
```

#### `agent images`
List available agents.

```bash
agent images [OPTIONS]

Options:
  -p, --profile TEXT    Registry profile to use
  -f, --filter TEXT     Filter agents by tag
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# List all agents
agent images

# List with specific profile
agent images --profile production

# Filter agents
agent images --filter "sentiment*"
```

#### `agent rmi`
Remove an agent from the registry.

```bash
agent rmi [OPTIONS] AGENT_NAME

Options:
  -p, --profile TEXT    Registry profile to use
  -f, --force          Force removal
  -h, --help           Show help message and exit
```

**Examples:**
```bash
# Remove agent from registry
agent rmi my-agent:latest

# Force removal
agent rmi my-agent:latest --force

# Remove with specific profile
agent rmi my-agent:latest --profile production
```

#### `agent configure`
Configure registry profiles.

```bash
agent configure [OPTIONS] COMMAND [ARGS]...

Commands:
  profile    Manage registry profiles
  list       List all configurations
  test       Test configuration
```

**Profile Management:**
```bash
# Add a new profile
agent configure profile add default --registry https://api.myagentregistry.com --pat PERSONAL-ACCESS-TOKEN-FROM-MYAGENTREGISTRY.COM --description "Default registry profile" --set-default --test

# List profiles
agent configure profile list

# Set default profile
agent configure profile set-default production

# Test profile
agent configure profile test production

# Remove profile
agent configure profile remove production
```

## Workflow Examples

### Complete Agent Development Workflow

```bash
# 1. Create a new agent project
agent init sentiment-analyzer
cd sentiment-analyzer

# 2. Edit the Agentfile
vim Agentfile

# 3. Build the agent
agent build -t sentiment-analyzer:latest .

# 4. Test the agent
agent test sentiment-analyzer:latest

# 5. Run locally for development
agent run sentiment-analyzer:latest

# 6. Push to registry
agent push sentiment-analyzer:latest

# 7. Pull on another machine
agent pull sentiment-analyzer:latest
```

### Registry Management Workflow

```bash
# 1. Configure registry profile
agent configure profile add production --registry https://api.myagentregistry.com --pat PERSONAL-ACCESS-TOKEN-FROM-MYAGENTREGISTRY.COM --description "Default registry profile" --set-default --test

# 2. Set as default
agent configure profile set-default production

# 3. List available agents
agent images

# 4. Push your agent
agent push my-agent:latest

# 5. Pull agent on another machine
agent pull my-agent:latest
```

## Environment Variables

The CLI tool respects these environment variables:

```bash
# Registry configuration
AGENTS_REGISTRY_URL=https://www.myagentregistry.com
AGENTS_REGISTRY_TOKEN=your-token

# Agent configuration
AGENT_BASE_IMAGE=agent/python:3.11-docker
AGENT_LOG_LEVEL=INFO

# API keys (for agent runtime)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Configuration Files

The CLI stores configuration in:
- **Global Config**: `~/.agent/config.json`
- **Project Config**: `./.agent/config.json`
- **Registry Profiles**: `~/.agent/profiles.json`

## Error Handling

The CLI provides clear error messages for common issues:

```bash
# Missing Agentfile
Error: Agentfile not found. Run 'agent init' to create a new project.

# Build failure
Error: Build failed. Check your Agentfile configuration.

# Registry authentication
Error: Authentication failed. Check your registry credentials.

# Network issues
Error: Connection failed. Check your network connection.
```

## Best Practices

### 1. Use Semantic Versioning
```bash
agent build -t my-agent:1.0.0 .
agent build -t my-agent:1.0.1 .
agent build -t my-agent:latest .
```

### 2. Test Before Pushing
```bash
agent build -t my-agent:latest .
agent test my-agent:latest
agent push my-agent:latest
```

### 3. Keep Agents Updated
```bash
agent pull my-agent:latest
agent run my-agent:latest
```

## Next Steps

1. Learn about **[Agentfile Configuration](./agentfile.md)** for writing agent definitions
2. Explore **[Examples](./examples.md)** for real-world usage patterns
3. Read the **[How to Use](./how-to-use.md)** guide for complete workflows
4. Understand the **[Registry](./registry.md)** for agent sharing and distribution 