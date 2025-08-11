#!/usr/bin/env python3
"""
Unified Agent Builder - Micro-Service Architecture
=================================================

Builds unified agent packages that can be deployed as micro-services
with both gRPC and REST API interfaces.
"""

import os
import json
import yaml
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..parser.aac_parser import AgentConfig

@dataclass
class MicroServicePackage:
    """Represents a complete micro-service agent package"""
    name: str
    version: str
    runtime: str
    base_image: str
    ports: List[int]
    capabilities: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    build_path: str
    dockerfile_path: str
    proto_path: str
    openapi_path: str
    config_path: str

class UnifiedAgentBuilder:
    """
    Builds unified agent micro-service packages
    
    Creates agent packages that are:
    - Deployable as containers
    - Expose gRPC and REST APIs
    - Compatible with any programming language
    - Ready for production deployment
    """
    
    def __init__(self, build_dir: str = None):
        """Initialize the unified builder"""
        self.build_dir = build_dir or tempfile.mkdtemp(prefix="agent_build_")
        self.template_dir = Path(__file__).parent.parent / "templates"
        
        # Ensure build directory exists
        os.makedirs(self.build_dir, exist_ok=True)
    
    def build_microservice(self, config: AgentConfig, tag: str) -> MicroServicePackage:
        """
        Build unified agent micro-service package
        
        Args:
            config: Parsed agent configuration
            tag: Package tag (e.g., "my-agent:latest")
            
        Returns:
            MicroServicePackage: Complete micro-service package
        """
        try:
            print(f"Building unified micro-service: {tag}")
            
            # Extract package info
            package_name = tag.split(":")[0] if ":" in tag else tag
            package_version = tag.split(":")[1] if ":" in tag else "latest"
            
            # Create package directory
            package_dir = Path(self.build_dir) / package_name
            package_dir.mkdir(exist_ok=True)
            
            # 1. Generate gRPC service definitions
            print("  Generating gRPC service definitions...")
            proto_path = self._generate_proto_files(package_dir, config)
            
            # 2. Create REST API layer
            print("  Creating REST API layer...")
            openapi_path = self._create_rest_api(package_dir, config)
            
            # 3. Generate agent metadata
            print("  Generating agent metadata...")
            config_path = self._create_agent_yaml(package_dir, config, package_name, package_version)
            
            # 4. Create Dockerfile
            print("  Creating Dockerfile...")
            dockerfile_path = self._create_dockerfile(package_dir, config)
            
            # 5. Create basic deployment files
            print("  Creating deployment files...")
            self._create_deployment_files(package_dir, config, package_name)
            
            # 6. Create agent implementation
            print("  Creating agent implementation...")
            self._create_agent_implementation(package_dir, config)
            
            # 7. Create configuration files
            print("  Creating configuration files...")
            self._create_config_files(package_dir, config)
            
            # 8. Create documentation
            print("  Creating documentation...")
            self._create_documentation(package_dir, config, package_name)
            
            # Create package metadata
            package = MicroServicePackage(
                name=package_name,
                version=package_version,
                runtime=config.runtime,
                base_image=self._get_base_image(config.runtime),
                ports=config.exposed_ports,
                capabilities=config.capabilities,
                metadata=config.labels,
                build_path=str(package_dir),
                dockerfile_path=str(dockerfile_path),
                proto_path=str(proto_path),
                openapi_path=str(openapi_path),
                config_path=str(config_path)
            )
            
            print(f"  Micro-service package created successfully!")
            print(f"  Package: {package_name}:{package_version}")
            print(f"  Runtime: {config.runtime}")
            print(f"  Capabilities: {len(config.capabilities)}")
            print(f"  Ports: {config.exposed_ports}")
            
            return package
            
        except Exception as e:
            print(f"  Build failed: {e}")
            raise ValueError(f"Failed to build micro-service package: {e}")
    
    def _generate_proto_files(self, package_dir: Path, config: AgentConfig) -> Path:
        """Generate gRPC service definitions"""
        proto_dir = package_dir / "proto"
        proto_dir.mkdir(exist_ok=True)
        
        # Copy base proto file
        base_proto = Path(__file__).parent / "proto" / "agent.proto"
        if base_proto.exists():
            shutil.copy2(base_proto, proto_dir / "agent.proto")
        
        # Generate capability-specific proto files
        for capability in config.capabilities:
            self._generate_capability_proto(proto_dir, capability)
        
        return proto_dir / "agent.proto"
    
    def _generate_capability_proto(self, proto_dir: Path, capability: str):
        """Generate capability-specific proto definitions"""
        # This would generate specific proto files for each capability
        # For now, we use the base proto file
        pass
    
    def _create_rest_api(self, package_dir: Path, config: AgentConfig) -> Path:
        """Create REST API layer with OpenAPI specification"""
        api_dir = package_dir / "api"
        api_dir.mkdir(exist_ok=True)
        
        # Create OpenAPI specification
        openapi_spec = self._generate_openapi_spec(config)
        openapi_path = api_dir / "openapi.yaml"
        
        with open(openapi_path, 'w') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        
        # Create REST server implementation
        rest_server = self._generate_rest_server(config)
        rest_server_path = api_dir / "rest_server.py"
        
        with open(rest_server_path, 'w') as f:
            f.write(rest_server)
        
        return openapi_path
    
    def _generate_openapi_spec(self, config: AgentConfig) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": f"{config.labels.get('name', 'Agent')} API",
                "version": config.labels.get('version', '1.0.0'),
                "description": config.labels.get('description', 'AI Agent API')
            },
            "servers": [
                {"url": "http://localhost:8080", "description": "Development server"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {
                                "description": "Agent is healthy",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "message": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/execute": {
                    "post": {
                        "summary": "Execute agent capability",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "capability": {"type": "string"},
                                            "input": {"type": "string"},
                                            "parameters": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Execution successful",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "output": {"type": "string"},
                                                "metadata": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def _generate_rest_server(self, config: AgentConfig) -> str:
        """Generate REST server implementation"""
        return f'''#!/usr/bin/env python3
"""
REST API Server for {config.labels.get('name', 'Agent')}
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import grpc
from concurrent.futures import ThreadPoolExecutor

# Import generated gRPC stubs
from proto import agent_pb2, agent_pb2_grpc

app = FastAPI(
    title="{config.labels.get('name', 'Agent')} API",
    version="{config.labels.get('version', '1.0.0')}",
    description="{config.labels.get('description', 'AI Agent REST API')}"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gRPC client
grpc_client = None
executor = ThreadPoolExecutor(max_workers=10)

@app.on_event("startup")
async def startup_event():
    """Initialize gRPC client on startup"""
    global grpc_client
    channel = grpc.aio.insecure_channel('localhost:50051')
    grpc_client = agent_pb2_grpc.AgentServiceStub(channel)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if grpc_client:
            response = await grpc_client.HealthCheck(
                agent_pb2.HealthRequest(check_type="liveness")
            )
            return {{
                "status": response.status,
                "message": response.message,
                "details": dict(response.details)
            }}
        return {{"status": "SERVING", "message": "REST API is healthy"}}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/execute")
async def execute_capability(request: Dict[str, Any]):
    """Execute agent capability"""
    try:
        capability = request.get("capability")
        input_data = request.get("input", "")
        parameters = request.get("parameters", {{}})
        
        if not capability:
            raise HTTPException(status_code=400, detail="capability is required")
        
        # Convert to gRPC request
        grpc_request = agent_pb2.ExecuteRequest(
            capability=capability,
            input_data=input_data.encode(),
            parameters=parameters
        )
        
        # Execute via gRPC
        response = await grpc_client.Execute(grpc_request)
        
        return {{
            "success": response.success,
            "output": response.output_data.decode() if response.output_data else None,
            "error_message": response.error_message,
            "metadata": dict(response.metadata),
            "execution_time_ms": response.execution_time_ms
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    try:
        if grpc_client:
            response = await grpc_client.GetCapabilities(
                agent_pb2.GetCapabilitiesRequest()
            )
            return {{
                "capabilities": [
                    {{
                        "name": cap.name,
                        "description": cap.description,
                        "version": cap.version,
                        "parameters": dict(cap.parameters),
                        "input_formats": list(cap.input_formats),
                        "output_formats": list(cap.output_formats)
                    }}
                    for cap in response.capabilities
                ]
            }}
        return {{"capabilities": {config.capabilities}}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
'''
    
    def _create_agent_yaml(self, package_dir: Path, config: AgentConfig, name: str, version: str) -> Path:
        """Create agent metadata YAML file"""
        agent_yaml = {
            "metadata": {
                "name": name,
                "version": version,
                "description": config.labels.get("description", ""),
                "author": config.labels.get("author", ""),
                "tags": config.labels.get("tags", "").split(",") if config.labels.get("tags") else []
            },
            "runtime": {
                "type": "docker" if "docker" in config.runtime else "venv",
                "base_image": self._get_base_image(config.runtime),
                "ports": config.exposed_ports,
                "environment": config.environment
            },
            "capabilities": [
                {
                    "name": capability,
                    "description": f"{capability} capability",
                    "version": "1.0.0",
                    "parameters": {},
                    "input_formats": ["text", "json"],
                    "output_formats": ["text", "json"]
                }
                for capability in config.capabilities
            ],
            "dependencies": {
                "python": config.dependencies,
                "system": []
            },
            "entrypoint": {
                "command": config.entrypoint,
                "args": []
            }
        }
        
        config_path = package_dir / "agent.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(agent_yaml, f, default_flow_style=False)
        
        return config_path
    
    def _create_dockerfile(self, package_dir: Path, config: AgentConfig) -> Path:
        """Create Dockerfile for the agent"""
        base_image = self._get_base_image(config.runtime)
        
        dockerfile_content = f'''# Agent Micro-Service Dockerfile
FROM {base_image}

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
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
{self._generate_env_vars(config.environment)}

# Expose ports
{self._generate_expose_ports(config.exposed_ports)}

# Basic health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Start the agent
CMD {config.entrypoint}
'''
        
        dockerfile_path = package_dir / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        return dockerfile_path
    
    def _generate_env_vars(self, environment: Dict[str, str]) -> str:
        """Generate ENV statements for Dockerfile"""
        env_lines = []
        for key, value in environment.items():
            env_lines.append(f'ENV {key}={value}')
        return '\n'.join(env_lines)
    
    def _generate_expose_ports(self, ports: List[int]) -> str:
        """Generate EXPOSE statements for Dockerfile"""
        expose_lines = []
        for port in ports:
            expose_lines.append(f'EXPOSE {port}')
        return '\n'.join(expose_lines)
    
    def _get_base_image(self, runtime: str) -> str:
        """Get base Docker image for runtime"""
        if "python" in runtime:
            version = "3.11"  # Default to 3.11 as specified
            return f"agent/python:{version}-docker"
        elif "node" in runtime:
            version = "18"
            return f"agent/node:{version}-docker"
        else:
            # Use environment variable or default
            return os.getenv('AGENT_BASE_IMAGE', "agent/python:3.11-docker")
    
    def _create_deployment_files(self, package_dir: Path, config: AgentConfig, name: str):
        """Create basic deployment files"""
        deploy_dir = package_dir / "deploy"
        deploy_dir.mkdir(exist_ok=True)
        
        # Simple docker-compose file
        docker_compose = f'''version: '3.8'
services:
  {name}:
    build: .
    ports:
      - "50051:50051"  # gRPC
      - "8080:8080"    # REST
    environment:
{chr(10).join([f"      - {key}={value}" for key, value in config.environment.items()])}
    restart: unless-stopped
'''
        
        compose_path = deploy_dir / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(docker_compose)
        
        # Simple run script
        run_script = f'''#!/bin/bash
# Simple run script for {name}

echo "Building {name}..."
docker build -t {name}:latest .

echo "Running {name}..."
docker run -d \\
  --name {name} \\
  -p 50051:50051 \\
  -p 8080:8080 \\
{chr(10).join([f"  -e {key}={value} \\" for key, value in config.environment.items()])} \\
  {name}:latest

echo "{name} is running!"
echo "gRPC: localhost:50051"
echo "REST: http://localhost:8080"
echo "Health: http://localhost:8080/health"
'''
        
        run_path = deploy_dir / "run.sh"
        with open(run_path, 'w') as f:
            f.write(run_script)
        
        # Make run script executable
        os.chmod(run_path, 0o755)
    
    def _create_agent_implementation(self, package_dir: Path, config: AgentConfig):
        """Create agent implementation files"""
        src_dir = package_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create main agent service
        main_service = self._generate_main_service(config)
        main_path = src_dir / "main.py"
        with open(main_path, 'w') as f:
            f.write(main_service)
        
        # Create agent service implementation
        agent_service = self._generate_agent_service(config)
        service_path = src_dir / "agent_service.py"
        with open(service_path, 'w') as f:
            f.write(agent_service)
        
        # Create requirements.txt
        requirements = self._generate_requirements(config)
        req_path = package_dir / "requirements.txt"
        with open(req_path, 'w') as f:
            f.write(requirements)
    
    def _generate_main_service(self, config: AgentConfig) -> str:
        """Generate main service entry point"""
        return f'''#!/usr/bin/env python3
"""
Main entry point for {config.labels.get('name', 'Agent')} micro-service
"""

import asyncio
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
import grpc
from grpc import aio

# Import generated gRPC stubs
from proto import agent_pb2, agent_pb2_grpc

# Import agent service implementation
from agent_service import AgentServiceImplementation

class AgentServer:
    def __init__(self, port: int = 50051):
        self.port = port
        self.server = None
        self.agent_service = AgentServiceImplementation()
    
    async def start(self):
        """Start the gRPC server"""
        self.server = aio.server(ThreadPoolExecutor(max_workers=10))
        
        # Add agent service
        agent_pb2_grpc.add_AgentServiceServicer_to_server(
            self.agent_service, self.server
        )
        
        # Listen on port
        listen_addr = f'[::]:{{self.port}}'
        self.server.add_insecure_port(listen_addr)
        
        print(f"Starting agent server on {{listen_addr}}")
        await self.server.start()
        
        # Wait for termination
        await self.server.wait_for_termination()
    
    async def stop(self):
        """Stop the server gracefully"""
        if self.server:
            await self.server.stop(grace=5)

async def main():
    """Main entry point"""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    
    server = AgentServer(port)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print("\\nShutting down agent server...")
        asyncio.create_task(server.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _generate_agent_service(self, config: AgentConfig) -> str:
        """Generate agent service implementation"""
        capabilities_impl = []
        for capability in config.capabilities:
            if capability == "sentiment-analysis":
                capabilities_impl.append(self._generate_sentiment_analysis())
            elif capability == "text-generation":
                capabilities_impl.append(self._generate_text_generation())
            # Add more capabilities as needed
        
        return f'''#!/usr/bin/env python3
"""
Agent service implementation for {config.labels.get('name', 'Agent')}
"""

import time
import json
import asyncio
from typing import Dict, Any
from grpc import aio

# Import generated gRPC stubs
from proto import agent_pb2, agent_pb2_grpc

class AgentServiceImplementation(agent_pb2_grpc.AgentServiceServicer):
    def __init__(self):
        self.initialized = False
        self.config = {{
            "model": "{config.model}",
            "capabilities": {config.capabilities},
            "environment": {config.environment}
        }}
    
    async def Initialize(self, request, context):
        """Initialize the agent"""
        try:
            # Merge request config with default config
            self.config.update(request.config)
            self.initialized = True
            
            return agent_pb2.InitializeResponse(
                success=True,
                message="Agent initialized successfully",
                metadata=self.config
            )
        except Exception as e:
            return agent_pb2.InitializeResponse(
                success=False,
                message=f"Initialization failed: {{str(e)}}"
            )
    
    async def Execute(self, request, context):
        """Execute agent capability"""
        start_time = time.time()
        
        try:
            if not self.initialized:
                return agent_pb2.ExecuteResponse(
                    success=False,
                    error_message="Agent not initialized"
                )
            
            capability = request.capability
            input_data = request.input_data.decode() if request.input_data else ""
            parameters = request.parameters
            
            # Route to capability-specific handler
            if capability == "sentiment-analysis":
                result = await self._handle_sentiment_analysis(input_data, parameters)
            elif capability == "text-generation":
                result = await self._handle_text_generation(input_data, parameters)
            else:
                result = {{"error": f"Unknown capability: {{capability}}"}}
            
            execution_time = int((time.time() - start_time) * 1000)
            
            if "error" in result:
                return agent_pb2.ExecuteResponse(
                    success=False,
                    error_message=result["error"],
                    request_id=request.request_id,
                    execution_time_ms=execution_time
                )
            
            return agent_pb2.ExecuteResponse(
                success=True,
                output_data=json.dumps(result).encode(),
                metadata=result.get("metadata", {{}}),
                request_id=request.request_id,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return agent_pb2.ExecuteResponse(
                success=False,
                error_message=str(e),
                request_id=request.request_id,
                execution_time_ms=execution_time
            )
    
    async def HealthCheck(self, request, context):
        """Health check endpoint"""
        return agent_pb2.HealthResponse(
            status="SERVING" if self.initialized else "NOT_SERVING",
            message="Agent is healthy" if self.initialized else "Agent not initialized",
            details={{"initialized": str(self.initialized).lower()}}
        )
    
    async def GetCapabilities(self, request, context):
        """Get agent capabilities"""
        capabilities = []
        for capability in self.config["capabilities"]:
            capabilities.append(agent_pb2.Capability(
                name=capability,
                description=f"{{capability}} capability",
                version="1.0.0",
                parameters={{}},
                input_formats=["text", "json"],
                output_formats=["text", "json"]
            ))
        
        return agent_pb2.GetCapabilitiesResponse(capabilities=capabilities)
    
    async def GetMetadata(self, request, context):
        """Get agent metadata"""
        return agent_pb2.GetMetadataResponse(
            metadata=agent_pb2.AgentMetadata(
                name="{config.labels.get('name', 'Agent')}",
                version="{config.labels.get('version', '1.0.0')}",
                description="{config.labels.get('description', '')}",
                author="{config.labels.get('author', '')}",
                tags={config.labels.get('tags', '').split(',') if config.labels.get('tags') else []},
                runtime="{config.runtime}",
                base_image="{self._get_base_image(config.runtime)}",
                ports={config.exposed_ports},
                environment=self.config["environment"],
                capabilities=[
                    agent_pb2.Capability(
                        name=cap,
                        description=f"{{cap}} capability",
                        version="1.0.0"
                    )
                    for cap in self.config["capabilities"]
                ]
            )
        )
    
    # Capability-specific handlers
    async def _handle_sentiment_analysis(self, text: str, parameters: Dict[str, str]):
        """Handle sentiment analysis capability"""
        # This would integrate with actual AI model
        # For now, return mock response
        return {{
            "sentiment": "positive",
            "confidence": 0.85,
            "scores": {{"positive": 0.85, "negative": 0.10, "neutral": 0.05}},
            "metadata": {{"model": parameters.get("model", "{config.model}")}}
        }}
    
    async def _handle_text_generation(self, prompt: str, parameters: Dict[str, str]):
        """Handle text generation capability"""
        # This would integrate with actual AI model
        # For now, return mock response
        return {{
            "generated_text": f"Generated response to: {{prompt}}",
            "confidence": 0.90,
            "metadata": {{"model": parameters.get("model", "{config.model}")}}
        }}
    
    # Additional capability handlers
    async def SentimentAnalysis(self, request, context):
        """Direct sentiment analysis endpoint"""
        result = await self._handle_sentiment_analysis(request.text, {{"model": request.model}})
        return agent_pb2.SentimentResponse(
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=result["scores"]
        )
    
    async def TextGeneration(self, request, context):
        """Direct text generation endpoint"""
        result = await self._handle_text_generation(request.prompt, request.parameters)
        return agent_pb2.TextResponse(
            generated_text=result["generated_text"],
            metadata=result["metadata"],
            confidence=result["confidence"]
        )
'''
    
    def _generate_sentiment_analysis(self) -> str:
        """Generate sentiment analysis implementation"""
        return """
    async def _handle_sentiment_analysis(self, text: str, parameters: Dict[str, str]):
        # Implement sentiment analysis logic here
        pass
"""
    
    def _generate_text_generation(self) -> str:
        """Generate text generation implementation"""
        return """
    async def _handle_text_generation(self, prompt: str, parameters: Dict[str, str]):
        # Implement text generation logic here
        pass
"""
    
    def _generate_requirements(self, config: AgentConfig) -> str:
        """Generate requirements.txt"""
        base_requirements = [
            "grpcio==1.59.0",
            "grpcio-tools==1.59.0",
            "fastapi==0.104.0",
            "uvicorn==0.24.0",
            "pydantic==2.5.0",
            "requests==2.31.0",
            "numpy==1.21.0"
        ]
        
        # Add user dependencies
        user_deps = [dep for dep in config.dependencies if "==" in dep]
        
        all_requirements = base_requirements + user_deps
        return '\n'.join(all_requirements)
    
    def _create_config_files(self, package_dir: Path, config: AgentConfig):
        """Create configuration files"""
        config_dir = package_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Runtime configuration
        runtime_config = {
            "grpc_port": 50051,
            "rest_port": 8080,
            "log_level": "INFO",
            "model_config": config.model_config,
            "capabilities": config.capabilities
        }
        
        runtime_path = config_dir / "runtime_config.yaml"
        with open(runtime_path, 'w') as f:
            yaml.dump(runtime_config, f, default_flow_style=False)
    
    def _create_documentation(self, package_dir: Path, config: AgentConfig, name: str):
        """Create documentation"""
        docs_dir = package_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # README
        readme_content = f'''# {name}

{config.labels.get('description', 'AI Agent Micro-Service')}

## Quick Start

### Using Docker
```bash
# Build the agent
docker build -t {name}:latest .

# Run the agent
docker run -p 50051:50051 -p 8080:8080 {name}:latest
```

### Using Kubernetes
```bash
# Run locally
cd deploy && ./run.sh

# Check deployment
kubectl get pods -l app={name}
```

## API Usage

### gRPC API
```python
import grpc
from proto import agent_pb2, agent_pb2_grpc

with grpc.insecure_channel('localhost:50051') as channel:
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    response = stub.Execute(agent_pb2.ExecuteRequest(
        capability="sentiment-analysis",
        input_data="I love this product!".encode()
    ))
    print(response.output_data.decode())
```

### REST API
```bash
# Health check
curl http://localhost:8080/health

# Execute capability
curl -X POST http://localhost:8080/execute \\
  -H "Content-Type: application/json" \\
  -d '{{"capability": "sentiment-analysis", "input": "I love this product!"}}'
```

## Capabilities

{chr(10).join([f"- **{cap}**: {cap} capability" for cap in config.capabilities])}

## Configuration

The agent can be configured via environment variables:

{chr(10).join([f"- `{key}`: {value}" for key, value in config.environment.items()])}

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Generate gRPC stubs
python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/agent.proto

# Run agent
python src/main.py
```
'''
        
        readme_path = docs_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        # API documentation
        api_docs = f'''# {name} API Documentation

## gRPC API

### AgentService

#### Initialize
Initialize the agent with configuration.

#### Execute
Execute a capability with input data.

#### HealthCheck
Check agent health status.

#### GetCapabilities
Get list of available capabilities.

#### GetMetadata
Get agent metadata.

## REST API

### Health Check
`GET /health`

### Execute Capability
`POST /execute`

Request body:
```json
{{
  "capability": "sentiment-analysis",
  "input": "I love this product!",
  "parameters": {{"model": "gpt-4"}}
}}
```

Response:
```json
{{
  "success": true,
  "output": "positive",
  "metadata": {{"model": "gpt-4"}},
  "execution_time_ms": 150
}}
```

## Capabilities

{chr(10).join([f"### {cap.title()}\n{cap} capability implementation." for cap in config.capabilities])}
'''
        
        api_path = docs_dir / "api.md"
        with open(api_path, 'w') as f:
            f.write(api_docs) 