# Parser
=======

The AaC Parser is the core component responsible for reading, validating, and processing Agentfile configurations. It ensures that agent definitions are syntactically correct, semantically valid, and ready for building.

## Overview

The parser performs several critical functions:
- **Syntax Validation**: Ensures Agentfile follows correct format
- **Semantic Validation**: Validates configuration logic and relationships
- **Dependency Resolution**: Checks package compatibility and versions
- **Security Validation**: Prevents hardcoded secrets and vulnerabilities
- **Schema Generation**: Creates OpenAPI and gRPC schemas for UAPI integration

## How It Works

### 1. File Reading
The parser reads the Agentfile and processes it line by line:

```dockerfile
# Agentfile Example
FROM agent/python:3.11-docker
CAPABILITY text-generation
MODEL gpt-4
CONFIG temperature=0.7
DEPENDENCY openai==1.0.0
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
EXPOSE 8080
ENTRYPOINT python src/main.py
```

### 2. Directive Parsing
Each directive is parsed and validated:

```python
# Parser extracts directives
directives = {
    'FROM': 'agent/python:3.11-docker',
    'CAPABILITY': ['text-generation'],
    'MODEL': 'gpt-4',
    'CONFIG': {'temperature': '0.7'},
    'DEPENDENCY': ['openai==1.0.0'],
    'ENV': {'OPENAI_API_KEY': '${OPENAI_API_KEY}'},
    'EXPOSE': [8080],
    'ENTRYPOINT': 'python src/main.py'
}
```

### 3. Validation Process

#### Syntax Validation
- **Directive Format**: Ensures directives follow correct syntax
- **Value Types**: Validates data types (strings, numbers, lists)
- **Required Fields**: Checks for mandatory directives

#### Semantic Validation
- **Capability-Model Compatibility**: Ensures model supports specified capabilities
- **Dependency Compatibility**: Checks package version compatibility
- **Environment Variables**: Validates environment variable references

#### Security Validation
- **No Hardcoded Secrets**: Prevents API keys in Agentfile
- **Safe Commands**: Validates entrypoint commands
- **Port Security**: Checks exposed port configurations

### 4. Schema Generation
The parser generates schemas for UAPI integration:

```python
# OpenAPI Schema Generation
openapi_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Text Generation Agent",
        "version": "1.0.0"
    },
    "paths": {
        "/generate": {
            "post": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## Validation Rules

### Required Directives
Every Agentfile must contain:
- `FROM`: Base runtime specification
- `CAPABILITY`: At least one capability
- `ENTRYPOINT`: Command to start the agent

### Capability Validation
```dockerfile
# Valid capabilities
CAPABILITY text-generation
CAPABILITY sentiment-analysis
CAPABILITY image-generation

# Invalid capabilities
CAPABILITY invalid-capability  # Error: Unknown capability
```

### Model Validation
```dockerfile
# Valid models
MODEL gpt-4
MODEL gpt-3.5-turbo
MODEL claude-3-opus

# Invalid models
MODEL invalid-model  # Error: Unknown model
```

### Configuration Validation
```dockerfile
# Valid configurations
CONFIG temperature=0.7
CONFIG max_tokens=200
CONFIG top_p=0.9

# Invalid configurations
CONFIG temperature=invalid  # Error: Must be number
CONFIG invalid_param=value  # Error: Unknown parameter
```

### Dependency Validation
```dockerfile
# Valid dependencies
DEPENDENCY openai==1.0.0
DEPENDENCY numpy>=1.21.0
DEPENDENCY requests~=2.31.0

# Invalid dependencies
DEPENDENCY invalid-package  # Error: Package not found
DEPENDENCY openai==invalid  # Error: Invalid version
```

### Environment Variable Validation
```dockerfile
# Valid environment variables
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO
ENV MODEL_NAME=gpt-4

# Invalid environment variables
ENV API_KEY=hardcoded-key  # Error: Hardcoded secret
ENV INVALID_VAR=value      # Error: Invalid variable name
```

## Error Handling

The parser provides detailed error messages:

```bash
# Syntax Error
Error: Invalid directive 'INVALID' at line 5
  Expected: FROM, CAPABILITY, MODEL, CONFIG, DEPENDENCY, ENV, EXPOSE, ENTRYPOINT, LABEL

# Semantic Error
Error: Model 'gpt-4' does not support capability 'image-generation'
  Supported capabilities: text-generation, sentiment-analysis, code-generation

# Security Error
Error: Hardcoded API key detected at line 8
  Use environment variables: ENV API_KEY=${API_KEY}

# Dependency Error
Error: Package 'invalid-package' not found in PyPI
  Available alternatives: valid-package, another-package
```

## Integration Points

### Builder Integration
The parser provides structured data to the builder:

```python
# Parser output for builder
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
    'dependencies': ['openai==1.0.0'],
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

### UAPI Integration
Generated schemas enable UAPI registration:

```python
# gRPC Schema for UAPI
grpc_schema = {
    'service': 'TextGenerationService',
    'methods': {
        'GenerateText': {
            'request': 'GenerateTextRequest',
            'response': 'GenerateTextResponse'
        }
    },
    'messages': {
        'GenerateTextRequest': {
            'fields': {'prompt': 'string'}
        },
        'GenerateTextResponse': {
            'fields': {'text': 'string'}
        }
    }
}
```

## Performance Considerations

### Caching
The parser caches validation results:
- **Schema Cache**: Reuses generated schemas
- **Dependency Cache**: Caches package information
- **Model Cache**: Caches model capability mappings

### Optimization
- **Lazy Loading**: Loads dependencies only when needed
- **Parallel Processing**: Validates multiple directives concurrently
- **Incremental Parsing**: Only re-parses changed sections

## Extensibility

### Custom Capabilities
Developers can extend the parser with custom capabilities:

```python
# Register custom capability
parser.register_capability(
    name='custom-analysis',
    supported_models=['gpt-4', 'claude-3'],
    required_dependencies=['custom-package'],
    schema_generator=custom_schema_generator
)
```

### Custom Validators
Add custom validation rules:

```python
# Custom validator
def validate_custom_rule(agent_config):
    if agent_config.get('custom_field'):
        # Custom validation logic
        pass

parser.add_validator(validate_custom_rule)
```

## Best Practices

### 1. Clear Error Messages
- Provide specific error locations
- Suggest fixes for common issues
- Include examples in error messages

### 2. Comprehensive Validation
- Validate all aspects of configuration
- Check for security vulnerabilities
- Ensure compatibility across components

### 3. Performance Optimization
- Cache validation results
- Use efficient parsing algorithms
- Minimize external API calls

### 4. Extensibility
- Support custom capabilities
- Allow custom validators
- Maintain backward compatibility

## Next Steps

1. Learn about the **[Builder](./builder.md)** for agent packaging
2. Understand **[Runtime](./runtime.md)** for agent execution
3. Explore **[Examples](./examples.md)** for validation patterns
4. Read the **[How to Use](./how-to-use.md)** guide for complete workflows 