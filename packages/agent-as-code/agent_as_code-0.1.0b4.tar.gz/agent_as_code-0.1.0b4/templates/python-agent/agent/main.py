#!/usr/bin/env python3
"""
Python Agent Template
=====================

This is a template for creating Python-based AI agents using the Agent as Code (AaC) framework.
It provides a basic structure that can be extended for various AI agent use cases.

Key Features:
- Template structure for Python AI agents
- gRPC service interface for integration
- Health check endpoint
- Error handling and logging
- Environment variable configuration
- Extensible design for different agent types

Usage:
    python main.py

The agent will start a gRPC server on port 50051 (or PORT environment variable)
and be ready to accept requests based on your implementation.

To use this template:
1. Copy this template to your agent project
2. Modify the PythonAgent class to implement your specific functionality
3. Update the capabilities and model configuration
4. Add your business logic to the process_request method
"""

import os
import logging
import grpc
from concurrent import futures
import json
from typing import Dict, Any

# Configure logging with environment variable support
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

class PythonAgent:
    """
    Template Python agent for AI applications
    
    This is a base class that provides the structure for creating
    Python-based AI agents. You should extend this class to implement
    your specific agent functionality.
    
    The agent follows a simple pattern:
    1. Initialize with configuration
    2. Process incoming requests
    3. Return structured responses
    4. Provide health check capabilities
    
    Example Usage:
        class MyCustomAgent(PythonAgent):
            def process_request(self, request):
                # Implement your custom logic here
                return {"result": "custom response"}
    """
    
    def __init__(self):
        """
        Initialize the Python agent
        
        Sets up the agent with:
        - API key validation
        - Model configuration (from Agentfile CONFIG directives)
        - Logging setup
        - Basic error handling
        
        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        # Get API key from environment (required for most AI APIs)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Model configuration (can be overridden via Agentfile CONFIG directives)
        self.model = "gpt-4"
        self.temperature = 0.7  # Balanced temperature for general use
        self.max_tokens = 200   # Reasonable token limit
        self.top_p = 0.9
        
        logger.info("Python Agent initialized successfully")
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming request
        
        This is the main method that handles all incoming requests to the agent.
        You should override this method to implement your specific agent logic.
        
        The method takes a request dictionary and returns a response dictionary.
        This provides flexibility for different types of AI agent applications.
        
        Args:
            request: Dictionary containing the request data
                     Example: {"input": "user text", "parameters": {...}}
            
        Returns:
            Dict containing the response:
            {
                "status": "success|error",
                "message": "Response message",
                "data": {...},
                "model": "gpt-4"
            }
            
        Example:
            # For a text generation agent:
            result = agent.process_request({"input": "Write a poem"})
            
            # For a data analysis agent:
            result = agent.process_request({"data": [...], "analysis_type": "summary"})
        """
        try:
            # TODO: Implement your specific agent logic here
            # This is a template - replace with your actual implementation
            
            # Example implementation for a simple echo agent:
            input_text = request.get("input", "")
            
            response = {
                "status": "success",
                "message": "Request processed successfully",
                "data": {
                    "input": input_text,
                    "processed": f"Processed: {input_text}",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "model": self.model
            }
            
            return response
            
        except Exception as e:
            # Handle any errors during request processing
            logger.error(f"Error processing request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": request,
                "model": self.model
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint for the agent
        
        Returns basic information about the agent's status,
        including model information and capabilities.
        
        This method is used by monitoring systems to verify
        that the agent is running properly.
        
        Returns:
            Dict containing health check information:
            {
                "status": "healthy",
                "model": "gpt-4",
                "capabilities": ["text-generation"]
            }
        """
        return {
            "status": "healthy",
            "model": self.model,
            "capabilities": ["text-generation"]  # Update with your agent's capabilities
        }

# gRPC service implementation
class PythonAgentService:
    """
    gRPC service wrapper for the Python agent
    
    This class provides the gRPC interface that allows other services
    to call the Python agent over the network. It acts as a bridge
    between the gRPC protocol and your agent implementation.
    
    The service exposes methods that can be called by UAPI or other
    applications that need your agent's capabilities.
    """
    
    def __init__(self):
        """
        Initialize the gRPC service
        
        Creates an instance of the Python agent that will handle
        the actual request processing.
        """
        self.agent = PythonAgent()
    
    def ProcessRequest(self, request, context):
        """
        gRPC method for processing requests
        
        This method is called when a client sends a request to the gRPC service.
        It converts the gRPC request to a dictionary, processes it through
        the agent, and returns the response.
        
        Args:
            request: gRPC request object containing the request data
            context: gRPC context object
            
        Returns:
            gRPC response object with the processed results
            
        Note:
            This is a placeholder implementation. In a real implementation,
            you would need to define the proper gRPC proto messages.
        """
        # Convert gRPC request to dictionary format
        # In a real implementation, this would extract fields from the proto message
        request_dict = {
            "input": getattr(request, 'input', ''),
            "parameters": getattr(request, 'parameters', {})
        }
        
        # Process the request using the agent
        result = self.agent.process_request(request_dict)
        
        # Return the result
        # In a real implementation, you would create the proper gRPC response object
        return result

def serve():
    """
    Start the gRPC server
    
    This function sets up and starts the gRPC server that will:
    1. Create a server instance with thread pool for concurrent requests
    2. Add the Python agent service
    3. Bind to the specified port (from PORT environment variable or default)
    4. Start listening for requests
    5. Keep running until interrupted (Ctrl+C)
    
    The server will be accessible on the specified port and ready
    to accept requests from clients or the UAPI system.
    """
    # Create gRPC server with thread pool for handling concurrent requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # TODO: Add the Python agent service to the server
    # In a real implementation, you would need to:
    # 1. Generate gRPC code from proto files
    # 2. Import the generated modules
    # 3. Add the service to the server
    # 
    # Example:
    # from python_agent_pb2_grpc import add_PythonAgentServiceServicer_to_server
    # add_PythonAgentServiceServicer_to_server(PythonAgentService(), server)
    
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 50051))
    
    # Bind server to the specified port
    server.add_insecure_port(f'[::]:{port}')
    
    # Start the server
    server.start()
    
    logger.info(f"Python Agent server started on port {port}")
    logger.info("Server is ready to accept requests")
    
    try:
        # Keep the server running until interrupted
        server.wait_for_termination()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        logger.info("Shutting down server...")
        server.stop(0)

# Main entry point
if __name__ == "__main__":
    """
    Main entry point for the Python agent
    
    When this script is run directly, it will:
    1. Initialize the Python agent
    2. Start the gRPC server
    3. Begin accepting requests
    
    The agent can then be called by other services or applications
    that need your agent's capabilities.
    
    To customize this template:
    1. Modify the PythonAgent class to implement your specific logic
    2. Update the process_request method with your business logic
    3. Add any additional methods your agent needs
    4. Update the capabilities in the health_check method
    """
    serve() 