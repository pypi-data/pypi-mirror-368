# Agentfile Configuration
========================

The Agentfile is the core configuration file for defining AI agents in the Agent as Code framework. It uses a declarative syntax similar to Dockerfile, making it easy to specify agent capabilities, dependencies, and runtime configuration.

## Overview

An Agentfile defines:
- **Base Runtime**: The foundation environment for the agent
- **Capabilities**: What the agent can do
- **Dependencies**: Required libraries and packages
- **Environment**: Configuration variables and settings
- **Deployment**: Ports, health checks, and metadata

## Basic Syntax

```dockerfile
# Agentfile - Basic Structure
FROM agent/python:3.11-docker

# Define capabilities
CAPABILITY text-generation
CAPABILITY sentiment-analysis

# Model configuration
MODEL gpt-4
CONFIG temperature=0.7
CONFIG max_tokens=200

# Dependencies
DEPENDENCY openai==1.0.0
DEPENDENCY numpy==1.21.0

# Environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Entry point
ENTRYPOINT python src/main.py

# Metadata
LABEL version="1.0.0"
LABEL author="your-email@example.com"
LABEL description="AI agent for text generation and sentiment analysis"
LABEL tags="ai,text-generation,sentiment"
```

## Configuration Directives

### FROM
Specifies the base runtime environment for the agent.

```dockerfile
FROM agent/python:3.11-docker    # Python 3.11 with Docker support
FROM agent/node:18-docker        # Node.js 18 with Docker support
FROM agent/java:17-docker        # Java 17 with Docker support
```

### CAPABILITY
Defines what the agent can do. Multiple capabilities can be specified.

```dockerfile
CAPABILITY text-generation        # Generate text using LLMs
CAPABILITY sentiment-analysis     # Analyze text sentiment
CAPABILITY image-generation       # Generate images
CAPABILITY code-generation        # Generate code
CAPABILITY data-analysis          # Analyze data
CAPABILITY translation            # Translate text
CAPABILITY summarization          # Summarize text
```

### MODEL
Specifies the AI model to use for the agent's capabilities.

```dockerfile
MODEL gpt-4                       # OpenAI GPT-4
MODEL gpt-3.5-turbo              # OpenAI GPT-3.5 Turbo
MODEL claude-3-opus              # Anthropic Claude 3 Opus
MODEL claude-3-sonnet            # Anthropic Claude 3 Sonnet
MODEL local                      # Local model
```

### CONFIG
Configures model parameters and behavior.

```dockerfile
CONFIG temperature=0.7           # Creativity level (0.0-1.0)
CONFIG max_tokens=200            # Maximum response length
CONFIG top_p=0.9                 # Nucleus sampling
CONFIG frequency_penalty=0.0     # Frequency penalty
CONFIG presence_penalty=0.0      # Presence penalty
```

### DEPENDENCY
Specifies required Python packages and their versions.

```dockerfile
DEPENDENCY openai==1.0.0         # OpenAI Python client
DEPENDENCY numpy==1.21.0         # Numerical computing
DEPENDENCY pandas==1.3.0         # Data manipulation
DEPENDENCY requests==2.31.0      # HTTP library
```

### ENV
Sets environment variables for the agent.

```dockerfile
ENV OPENAI_API_KEY=${OPENAI_API_KEY}    # API key from environment
ENV LOG_LEVEL=INFO                       # Logging level
ENV MODEL_NAME=gpt-4                     # Model name
ENV MAX_TOKENS=200                       # Max tokens
```

### EXPOSE
Defines which ports the agent will listen on.

```dockerfile
EXPOSE 8080                    # REST API port
EXPOSE 50051                   # gRPC port
EXPOSE 9090                    # Metrics port
```

### HEALTHCHECK
Specifies how to check if the agent is healthy.

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1
```

### ENTRYPOINT
Defines the command to start the agent.

```dockerfile
ENTRYPOINT python src/main.py           # Python entry point
ENTRYPOINT node src/index.js            # Node.js entry point
ENTRYPOINT java -jar agent.jar          # Java entry point
```

### LABEL
Adds metadata to the agent.

```dockerfile
LABEL version="1.0.0"                   # Agent version
LABEL author="your-email@example.com"   # Author contact
LABEL description="Agent description"   # What the agent does
LABEL tags="ai,text,generation"         # Searchable tags
```

## Advanced Configuration

### Multi-Stage Builds
Create complex agents with multiple stages.

```dockerfile
# Stage 1: Model preparation
FROM agent/python:3.11-docker as model-prep
CAPABILITY model-training
DEPENDENCY torch==1.9.0
DEPENDENCY transformers==4.11.3
RUN python train_model.py

# Stage 2: Agent runtime
FROM agent/python:3.11-docker
CAPABILITY text-generation
COPY --from=model-prep /app/model /app/model
DEPENDENCY torch==1.9.0
ENTRYPOINT python src/main.py
```

### Conditional Configuration
Use environment variables for conditional settings.

```dockerfile
FROM agent/python:3.11-docker

# Conditional model selection
ENV MODEL_TYPE=${MODEL_TYPE:-gpt-4}
CONFIG model=${MODEL_TYPE}

# Conditional capabilities
ENV ENABLE_SENTIMENT=${ENABLE_SENTIMENT:-true}
RUN if [ "$ENABLE_SENTIMENT" = "true" ]; then \
      echo "CAPABILITY sentiment-analysis" >> /app/config; \
    fi
```

## Best Practices

### 1. Keep It Simple
- Use clear, descriptive capability names
- Minimize dependencies to essential packages
- Use environment variables for configuration

### 2. Version Control
- Always specify version numbers for dependencies
- Use semantic versioning for agent versions
- Tag releases with meaningful labels

### 3. Security
- Never hardcode API keys in Agentfile
- Use environment variables for sensitive data
- Implement proper health checks

### 4. Documentation
- Add descriptive labels
- Include usage examples in description
- Use meaningful tags for discovery

## Example Agentfiles

### Text Generation Agent
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY text-generation
MODEL gpt-4
CONFIG temperature=0.7
CONFIG max_tokens=500

DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

ENTRYPOINT python src/main.py

LABEL version="1.0.0"
LABEL author="ai-team@example.com"
LABEL description="Advanced text generation agent using GPT-4"
LABEL tags="ai,text-generation,gpt-4"
```

### Data Analysis Agent
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY data-analysis
MODEL gpt-4
CONFIG temperature=0.3

DEPENDENCY pandas==1.3.0
DEPENDENCY numpy==1.21.0
DEPENDENCY matplotlib==3.4.0
DEPENDENCY seaborn==0.11.0

ENV LOG_LEVEL=INFO
ENV DATA_PATH=/app/data

EXPOSE 8080

ENTRYPOINT python src/main.py

LABEL version="1.0.0"
LABEL author="data-team@example.com"
LABEL description="Data analysis and visualization agent"
LABEL tags="ai,data-analysis,visualization"
```

## Validation

The AaC Parser validates your Agentfile for:
- **Syntax**: Correct directive format
- **Dependencies**: Compatible package versions
- **Configuration**: Valid model parameters
- **Security**: No hardcoded secrets
- **Completeness**: Required directives present

## Next Steps

1. Learn about the **[CLI Tool](./cli.md)** for building and running agents
2. Explore **[Examples](./examples.md)** for more Agentfile patterns
3. Read the **[How to Use](./how-to-use.md)** guide for complete workflows 