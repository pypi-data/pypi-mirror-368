# How to Use Agent as Code
==========================

This comprehensive guide will walk you through using the Agent as Code framework to create, build, deploy, and manage AI agents.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed
- **Docker** installed (for containerized agents)
- **Git** for version control
- **API Keys** for your chosen LLM providers (OpenAI, Anthropic, etc.)

## Installation

### 1. Install the Framework

```bash
# Install from PyPI
pip install agent-as-code

# Verify installation
agent --help
```

### 2. Configure Registry (Optional)

```bash
# Configure registry profile
agent configure profile add default --registry https://api.myagentregistry.com --pat PERSONAL-ACCESS-TOKEN-FROM-MYAGENTREGISTRY.COM --description "Default registry profile" --set-default --test

# Set as default
agent configure profile set-default production
```

## Quick Start

### 1. Create Your First Agent

```bash
# Create a new agent project
agent init my-first-agent
cd my-first-agent
```

This creates a project structure:
```
my-first-agent/
├── Agentfile              # Agent configuration
├── agent/
│   └── main.py           # Agent implementation
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

### 2. Configure Your Agent

Edit the `Agentfile` to define your agent:

```dockerfile
# Agentfile
FROM agent/python:3.11-docker

# Define capabilities
CAPABILITY text-generation

# Model configuration
MODEL gpt-4
CONFIG temperature=0.7
CONFIG max_tokens=200

# Dependencies
DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0

# Environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Entry point
ENTRYPOINT python agent/main.py

# Metadata
LABEL version="1.0.0"
LABEL author="your-email@example.com"
LABEL description="My first AI agent for text generation"
LABEL tags="ai,text-generation,first-agent"
```

### 3. Implement Your Agent

Edit `agent/main.py` to implement your agent logic:

```python
#!/usr/bin/env python3
"""
My First AI Agent
=================
A simple text generation agent using OpenAI GPT-4.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="My First AI Agent")

# Configure OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 200

class GenerateResponse(BaseModel):
    text: str
    tokens_used: int

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponse(
            text=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens
        )
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "my-first-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 4. Build Your Agent

```bash
# Build the agent
agent build -t my-first-agent:latest .

# Verify the build
agent inspect my-first-agent:latest
```

### 5. Test Your Agent

```bash
# Test the agent functionality
agent test my-first-agent:latest

# Run the agent locally
agent run my-first-agent:latest
```

### 6. Use Your Agent

Once running, you can interact with your agent:

```bash
# Test the health endpoint
curl http://localhost:8080/health

# Generate text
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short poem about AI", "temperature": 0.7}'
```

## Advanced Usage

### Creating Different Types of Agents

#### Sentiment Analysis Agent

```dockerfile
# Agentfile for sentiment analysis
FROM agent/python:3.11-docker

CAPABILITY sentiment-analysis
MODEL gpt-4
CONFIG temperature=0.3

DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

EXPOSE 8080
ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL description="Sentiment analysis agent"
LABEL tags="ai,sentiment,analysis"
```

#### Data Analysis Agent

```dockerfile
# Agentfile for data analysis
FROM agent/python:3.11-docker

CAPABILITY data-analysis
MODEL gpt-4
CONFIG temperature=0.1

DEPENDENCY openai==1.0.0
DEPENDENCY pandas==1.3.0
DEPENDENCY numpy==1.21.0
DEPENDENCY matplotlib==3.4.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV DATA_PATH=/app/data

EXPOSE 8080
ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL description="Data analysis and visualization agent"
LABEL tags="ai,data,analysis,visualization"
```

### Registry Operations

#### Push to Registry

```bash
# Push your agent to the registry
agent push my-first-agent:latest

# Push with specific version
agent push my-first-agent:1.0.0

# Push with metadata
agent push my-first-agent:latest --description "Updated text generation agent"
```

#### Pull from Registry

```bash
# Pull agent from registry
agent pull my-first-agent:latest

# Pull specific version
agent pull my-first-agent:1.0.0

# Pull to specific directory
agent pull my-first-agent:latest --directory /path/to/agents
```

#### Discover Agents

```bash
# List all agents
agent images

# Search by capability
agent images --filter "text-generation"

# Search by author
agent images --filter "author:your-email@example.com"

# Detailed search
agent images --format json
```

### Deployment Options

#### Local Development

```bash
# Run in development mode
agent run my-first-agent:latest --dev

# Run with hot reload
agent run my-first-agent:latest --dev --hot-reload

# Run with custom port
agent run my-first-agent:latest --port 9000
```

#### Production Deployment

```bash
# Deploy to Docker
docker run -d \
  --name my-first-agent \
  -p 8080:8080 \
  -e OPENAI_API_KEY=your-key \
  my-first-agent:latest

# Deploy with resource limits
docker run -d \
  --name my-first-agent \
  -p 8080:8080 \
  --memory 2GB \
  --cpus 2 \
  -e OPENAI_API_KEY=your-key \
  my-first-agent:latest
```

#### Cloud Deployment

```bash
# Deploy to AWS ECS
agent deploy my-first-agent:latest --platform aws-ecs

# Deploy to Google Cloud Run
agent deploy my-first-agent:latest --platform gcp-run

# Deploy to Azure Container Instances
agent deploy my-first-agent:latest --platform azure-aci
```

### Environment Configuration

#### Environment Variables

```bash
# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export LOG_LEVEL="INFO"

# Run with environment variables
agent run my-first-agent:latest \
  -e OPENAI_API_KEY=your-key \
  -e LOG_LEVEL=DEBUG
```

#### Configuration Files

Create `.env` file for local development:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LOG_LEVEL=INFO
MODEL_NAME=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=200
```

### Monitoring and Debugging

#### Health Monitoring

```bash
# Check agent health
curl http://localhost:8080/health

# Monitor agent metrics
agent metrics my-first-agent-01

# View agent logs
agent logs my-first-agent-01 --follow
```

#### Debugging

```bash
# Run in debug mode
agent run my-first-agent:latest --debug

# Attach debugger
agent debug my-first-agent-01

# View debug logs
agent logs my-first-agent-01 --level debug
```

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have a focused capability
- **Clear Interfaces**: Define clear input/output schemas
- **Error Handling**: Implement robust error handling
- **Logging**: Add comprehensive logging for debugging

### 2. Configuration Management

- **Environment Variables**: Use environment variables for configuration
- **No Hardcoded Secrets**: Never hardcode API keys or secrets
- **Version Control**: Track configuration changes in Git
- **Validation**: Validate configuration at startup

### 3. Security

- **API Key Management**: Use secure API key management
- **Network Security**: Implement proper network security
- **Input Validation**: Validate all inputs
- **Rate Limiting**: Implement rate limiting for API endpoints

### 4. Performance

- **Resource Limits**: Set appropriate resource limits
- **Caching**: Implement caching where appropriate
- **Monitoring**: Monitor performance metrics
- **Optimization**: Optimize for your specific use case

### 5. Testing

- **Unit Tests**: Write unit tests for agent logic
- **Integration Tests**: Test agent integration
- **Load Testing**: Test under load conditions
- **Security Testing**: Test for security vulnerabilities

## Troubleshooting

### Common Issues

#### Build Failures

```bash
# Check Agentfile syntax
agent build --validate-only -f Agentfile .

# Check dependencies
pip install -r requirements.txt

# Check Docker installation
docker --version
```

#### Runtime Errors

```bash
# Check agent logs
agent logs my-first-agent-01

# Check environment variables
env | grep OPENAI

# Check network connectivity
curl http://localhost:8080/health
```

#### Registry Issues

```bash
# Test registry connection
agent configure profile test production

# Check authentication
agent configure profile list

# Clear cache
agent configure cache clear
```

### Getting Help

- **Documentation**: Check the component-specific documentation
- **CLI Help**: Use `agent --help` and `agent <command> --help`
- **Examples**: See the examples directory for working agents
- **Community**: Join the community for support

## Next Steps

1. **Explore Examples**: Check out the examples directory for more agent types
2. **Join Community**: Connect with other developers
3. **Contribute**: Contribute to the framework development
4. **Share Agents**: Share your agents with the community

---

**Ready to build amazing AI agents?** Start creating your first agent today! 