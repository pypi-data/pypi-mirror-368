# Registry
==========

The Agent Registry is a centralized storage and distribution system for AI agents. It enables sharing, versioning, and discovery of agents across teams and organizations.

## Overview

The registry provides:
- **Agent Storage**: Secure storage for agent packages and metadata
- **Version Management**: Semantic versioning and release tracking
- **Distribution**: Easy sharing and discovery of agents
- **Access Control**: Authentication and authorization
- **Search & Discovery**: Find agents by capabilities, tags, and metadata

## Registry Architecture

### Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent CLI     │───▶│   Registry API  │───▶│   Storage       │
│  (Push/Pull)    │    │  (REST/gRPC)    │    │  (Packages)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Metadata DB   │
                       │  (Search/Index) │
                       └─────────────────┘
```

## Registry Operations

### Agent Push
Upload an agent to the registry:

```bash
# Push agent to registry
agent push my-agent:latest

# Push with specific profile
agent push my-agent:latest --profile production

# Push with metadata
agent push my-agent:latest --description "Advanced text generation agent"
```

**Push Process:**
1. **Validation**: Verify agent package integrity
2. **Metadata Extraction**: Extract agent metadata
3. **Storage**: Store package and metadata
4. **Indexing**: Update search indexes
5. **Notification**: Notify subscribers of new version

### Agent Pull
Download an agent from the registry:

```bash
# Pull agent from registry
agent pull my-agent:latest

# Pull specific version
agent pull my-agent:1.0.0

# Pull to specific directory
agent pull my-agent:latest --directory /path/to/agents

# Pull with specific profile
agent pull my-agent:latest --profile production
```

**Pull Process:**
1. **Authentication**: Verify user permissions
2. **Resolution**: Resolve version to specific package
3. **Download**: Download package and metadata
4. **Validation**: Verify package integrity
5. **Extraction**: Extract to local filesystem

### Agent Discovery
Search and discover agents:

```bash
# List all agents
agent images

# Search by capability
agent images --filter "text-generation"

# Search by tag
agent images --filter "sentiment*"

# Search by author
agent images --filter "author:ai-team"

# Detailed search
agent images --format json
```

**Search Capabilities:**
- **By Name**: Exact or partial name matching
- **By Capability**: Find agents with specific capabilities
- **By Tag**: Search using metadata tags
- **By Author**: Find agents by creator
- **By Version**: Search specific versions
- **By Date**: Find recently updated agents

## Registry Configuration

### Profile Management
Configure registry profiles using PAT

### Authentication
Registry supports PAT for authentication method to communicate with Agents to push and pull.

## Agent Metadata

### Package Metadata
Each agent package includes comprehensive metadata:

```json
{
  "name": "text-generator",
  "version": "1.0.0",
  "description": "Advanced text generation agent using GPT-4",
  "author": "ai-team@example.com",
  "capabilities": ["text-generation"],
  "model": "gpt-4",
  "dependencies": ["openai==1.0.0", "fastapi==0.104.0"],
  "ports": [8080],
  "health_check": "http://localhost:8080/health",
  "tags": ["ai", "text-generation", "gpt-4"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "downloads": 150,
  "rating": 4.8,
  "size": "150MB",
  "digest": "sha256:abc123...",
  "compatibility": {
    "python": ">=3.9",
    "platforms": ["linux/amd64", "linux/arm64"]
  }
}
```

### Version Management
Semantic versioning for agent releases:

```bash
# Major version (breaking changes)
agent push my-agent:2.0.0

# Minor version (new features)
agent push my-agent:1.1.0

# Patch version (bug fixes)
agent push my-agent:1.0.1

# Pre-release versions
agent push my-agent:1.0.0-alpha.1
agent push my-agent:1.0.0-beta.1
agent push my-agent:1.0.0-rc.1
```

## Registry Features

### Access Control
Role-based access control for agents:

```bash
# Public agents (anyone can pull)
agent push my-agent:latest --visibility public

# Private agents (team only)
agent push my-agent:latest --visibility private

# Organization agents (org members only)
agent push my-agent:latest --visibility org
```

## Upcoming features

### Agent Permissions
Granular permissions for agent management:

```bash
# Read permission (pull)
agent configure permission add my-agent:latest --user john --permission read

# Write permission (push)
agent configure permission add my-agent:latest --user john --permission write

# Admin permission (delete, manage)
agent configure permission add my-agent:latest --user john --permission admin
```

### Webhooks
Automated notifications for registry events:

```bash
# Configure webhook for new versions
agent configure webhook add \
  --name new-version \
  --url https://ci.example.com/webhook \
  --events push

# Configure webhook for agent updates
agent configure webhook add \
  --name agent-update \
  --url https://monitoring.example.com/webhook \
  --events push,pull
```

## Registry Security

### Package Signing
Digital signatures for package integrity:

```bash
# Sign package before push
agent push my-agent:latest --sign

# Verify package signature on pull
agent pull my-agent:latest --verify-signature
```

### Vulnerability Scanning
Automated security scanning:

```bash
# Scan for vulnerabilities
agent push my-agent:latest --security-scan

# View scan results
agent inspect my-agent:latest --security-report
```

### Rate Limiting
Protection against abuse:

```bash
# Configure rate limits
agent configure rate-limit \
  --requests-per-minute 100 \
  --burst-size 20
```

## Registry Performance

### Caching
Optimized caching for better performance:

```bash
# Enable caching
agent configure cache enable

# Set cache size
agent configure cache set-size 10GB

# Clear cache
agent configure cache clear
```

### CDN Integration
Content delivery network for global distribution:

```bash
# Configure CDN
agent configure cdn enable \
  --provider cloudflare \
  --domain cdn.example.com
```

### Mirroring
Registry mirroring for redundancy:

```bash
# Configure mirror
agent configure mirror add \
  --name backup \
  --url https://backup-registry.example.com
```

## Registry Monitoring

### Metrics
Registry performance and usage metrics:

```bash
# View registry metrics
agent registry metrics

# Monitor specific metrics
agent registry metrics --metric downloads --period 24h
```

### Logs
Registry operation logs:

```bash
# View registry logs
agent registry logs

# Filter logs
agent registry logs --level error --since 1h
```

### Health Checks
Registry health monitoring:

```bash
# Check registry health
agent registry health

# Detailed health check
agent registry health --detailed
```

## Best Practices

### 1. Version Management
- Use semantic versioning
- Tag releases appropriately
- Maintain backward compatibility

### 2. Security
- Sign packages digitally
- Scan for vulnerabilities
- Use secure authentication

### 3. Performance
- Optimize package sizes
- Use caching effectively
- Monitor registry performance

### 4. Organization
- Use meaningful names and tags
- Document agent capabilities
- Maintain clean metadata

## Next Steps

1. Learn about the **[Runtime](./runtime.md)** for agent execution
2. Explore **[Examples](./examples.md)** for registry usage patterns
3. Read the **[How to Use](./how-to-use.md)** guide for complete workflows
4. Understand **[CLI Tool](./cli.md)** for registry operations 