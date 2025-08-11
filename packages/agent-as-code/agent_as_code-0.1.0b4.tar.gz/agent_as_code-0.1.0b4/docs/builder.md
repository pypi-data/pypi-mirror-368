# Builder
========

The Agent Builder is responsible for transforming validated Agentfile configurations into deployable agent packages. It handles dependency installation, code packaging, and container image generation.

## Overview

The builder performs several key functions:
- **Package Creation**: Generates deployable agent packages
- **Dependency Management**: Installs and resolves Python dependencies
- **Container Generation**: Creates Docker images for deployment
- **Schema Integration**: Embeds OpenAPI and gRPC schemas
- **Deployment Artifacts**: Generates deployment configurations

## How It Works

### 1. Configuration Processing
The builder receives validated configuration from the parser:

```python
# Input from parser
agent_config = {
    'runtime': {
        'base_image': 'agent/python:3.11-docker',
        'entrypoint': 'python src/main.py'
    },
    'capabilities': ['text-generation'],
    'model': {
        'name': 'gpt-4',
        'config': {'temperature': 0.7}
    },
    'dependencies': ['openai==1.0.0', 'fastapi==0.104.0'],
    'environment': {
        'OPENAI_API_KEY': '${OPENAI_API_KEY}',
        'LOG_LEVEL': 'INFO'
    },
    'deployment': {
        'ports': [8080],
        'health_check': '...'
    }
}
```

### 2. Package Structure Creation
The builder creates a standardized package structure:

```
agent-package/
├── src/
│   ├── main.py              # Agent entry point
│   ├── agent.py             # Agent implementation
│   └── api.py               # API layer
├── proto/
│   └── agent.proto          # gRPC definitions
├── api/
│   └── openapi.yaml         # OpenAPI specification
├── config/
│   └── agent.json           # Agent configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
├── docker-compose.yml      # Local deployment
└── deploy/
    ├── kubernetes.yaml      # Kubernetes deployment
    └── run.sh              # Simple run script
```

### 3. Dependency Resolution
The builder manages Python dependencies:

```python
# Generate requirements.txt
requirements = [
    'openai==1.0.0',
    'fastapi==0.104.0',
    'uvicorn==0.24.0',
    'pydantic==2.5.0',
    'grpcio==1.59.0',
    'grpcio-tools==1.59.0'
]

# Install dependencies
pip install -r requirements.txt
```

### 4. Code Generation
The builder generates agent code based on capabilities:

```python
# Generated main.py
from fastapi import FastAPI
from agent import TextGenerationAgent
import os

app = FastAPI(title="Text Generation Agent")
agent = TextGenerationAgent()

@app.post("/generate")
async def generate_text(request: dict):
    return await agent.generate(request["prompt"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 5. Container Generation
The builder creates Docker images:

```dockerfile
# Generated Dockerfile
FROM agent/python:3.11-docker

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY src/ ./src/
COPY proto/ ./proto/
COPY api/ ./api/
COPY config/ ./config/

# Generate gRPC stubs
RUN python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/agent.proto

# Set environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Start the agent
CMD python src/main.py
```

## Build Process

### 1. Validation Phase
```bash
# Validate Agentfile
agent build --validate-only -f Agentfile .
```

### 2. Package Generation
```bash
# Generate package
agent build -t my-agent:latest .
```

### 3. Container Build
```bash
# Build Docker image
docker build -t my-agent:latest .
```

### 4. Testing
```bash
# Test the built agent
agent test my-agent:latest
```

## Build Artifacts

### Package Files
- **Source Code**: Agent implementation and API layer
- **Dependencies**: Resolved Python packages
- **Configuration**: Agent settings and metadata
- **Schemas**: OpenAPI and gRPC definitions

### Container Images
- **Base Image**: Runtime environment
- **Agent Code**: Application implementation
- **Dependencies**: Installed packages
- **Configuration**: Environment and settings

### Deployment Configurations
- **Docker Compose**: Local development
- **Kubernetes**: Production deployment
- **Cloud Platforms**: AWS, GCP, Azure configurations

## Build Optimization

### Layer Caching
The builder optimizes Docker layer caching:

```dockerfile
# Optimized Dockerfile
FROM agent/python:3.11-docker

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code (changes frequently)
COPY src/ ./src/
COPY proto/ ./proto/

# Generate stubs (cached if proto doesn't change)
RUN python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/agent.proto

# Copy configuration (changes frequently)
COPY config/ ./config/
```

### Multi-Stage Builds
For complex agents with training or preprocessing:

```dockerfile
# Stage 1: Model preparation
FROM agent/python:3.11-docker as model-prep
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY train_model.py .
RUN python train_model.py

# Stage 2: Runtime
FROM agent/python:3.11-docker
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --from=model-prep /app/model /app/model
COPY src/ ./src/
CMD python src/main.py
```

## Build Configuration

### Build Context
The builder uses the current directory as build context:

```bash
# Build from current directory
agent build -t my-agent:latest .

# Build from specific directory
agent build -t my-agent:latest /path/to/agent
```

### Build Options
```bash
# Build with specific Agentfile
agent build -t my-agent:latest -f /path/to/Agentfile .

# Build with custom base image
agent build -t my-agent:latest --base-image custom/python:3.11 .

# Build with additional dependencies
agent build -t my-agent:latest --extra-deps "pandas==1.3.0" .
```

### Build Profiles
Different build configurations for different environments:

```yaml
# build-profiles.yaml
profiles:
  development:
    base_image: agent/python:3.11-docker
    debug: true
    hot_reload: true
    
  production:
    base_image: agent/python:3.11-docker
    debug: false
    optimization: true
    security_scan: true
```

## Integration with Registry

### Package Metadata
The builder generates metadata for registry storage:

```json
{
  "name": "my-agent",
  "version": "1.0.0",
  "capabilities": ["text-generation"],
  "model": "gpt-4",
  "dependencies": ["openai==1.0.0"],
  "ports": [8080],
  "health_check": "http://localhost:8080/health",
  "created_at": "2024-01-01T00:00:00Z",
  "size": "150MB",
  "digest": "sha256:abc123..."
}
```

### Registry Push
Built packages can be pushed to the registry:

```bash
# Build and push
agent build -t my-agent:latest .
agent push my-agent:latest
```

## Build Validation

### Security Scanning
The builder performs security checks:

```bash
# Security scan during build
agent build -t my-agent:latest --security-scan .
```

### Dependency Analysis
Analyzes dependencies for vulnerabilities:

```bash
# Dependency analysis
agent build -t my-agent:latest --analyze-deps .
```

### Size Optimization
Optimizes package and image sizes:

```bash
# Size optimization
agent build -t my-agent:latest --optimize-size .
```

## Build Performance

### Parallel Processing
The builder uses parallel processing for:
- Dependency resolution
- Code generation
- Container building
- Testing

### Caching Strategies
- **Dependency Cache**: Caches resolved dependencies
- **Layer Cache**: Caches Docker layers
- **Build Cache**: Caches build artifacts

### Incremental Builds
Only rebuilds changed components:
- Source code changes
- Dependency updates
- Configuration changes

## Best Practices

### 1. Optimize Build Time
- Use layer caching effectively
- Minimize dependency changes
- Use multi-stage builds for complex agents

### 2. Security
- Scan for vulnerabilities
- Use minimal base images
- Validate dependencies

### 3. Size Optimization
- Remove unnecessary files
- Use .dockerignore
- Optimize dependency selection

### 4. Reproducibility
- Pin dependency versions
- Use deterministic builds
- Document build environment

## Next Steps

1. Learn about the **[Runtime](./runtime.md)** for agent execution
2. Understand **[Registry](./registry.md)** for package distribution
3. Explore **[Examples](./examples.md)** for build patterns
4. Read the **[How to Use](./how-to-use.md)** guide for complete workflows 