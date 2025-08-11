#!/usr/bin/env python3
"""
Basic Sentiment Analysis Agent
==============================

This is a simple AI agent that analyzes sentiment in text using GPT-4.
It demonstrates the basic structure of an AI agent that can be built
using the Agent as Code (AaC) framework.

Key Features:
- Sentiment analysis using GPT-4
- gRPC service interface for integration
- Health check endpoint
- Error handling and logging
- Environment variable configuration

Usage:
    python main.py

The agent will start a gRPC server on port 50051 (or PORT environment variable)
and be ready to accept sentiment analysis requests.
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

class SentimentAnalysisAgent:
    """
    Basic sentiment analysis agent using GPT-4
    
    This agent provides sentiment analysis capabilities by:
    1. Taking text input from users
    2. Sending it to GPT-4 for analysis
    3. Returning structured sentiment results
    
    The agent is designed to be simple and focused, demonstrating
    how to create a single-purpose AI agent using the AaC framework.
    """
    
    def __init__(self):
        """
        Initialize the sentiment analysis agent
        
        Sets up the agent with:
        - API key validation
        - Model configuration
        - Logging setup
        
        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        # Get API key from environment (required for OpenAI API)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Model configuration (can be overridden via Agentfile CONFIG directives)
        self.model = "gpt-4"
        self.temperature = 0.3  # Low temperature for consistent sentiment analysis
        self.max_tokens = 150   # Sufficient for sentiment analysis
        self.top_p = 0.9
        
        logger.info("Sentiment Analysis Agent initialized successfully")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the given text
        
        This is the main method that performs sentiment analysis.
        It takes text input and returns a structured response with:
        - Sentiment classification (positive, negative, neutral)
        - Confidence score (0-1)
        - Explanation of the sentiment
        - Model information
        
        Args:
            text: The text to analyze for sentiment
            
        Returns:
            Dict containing sentiment analysis results:
            {
                "text": "original text",
                "sentiment": "positive|negative|neutral",
                "confidence": 0.85,
                "explanation": "This text expresses...",
                "model": "gpt-4"
            }
            
        Example:
            result = agent.analyze_sentiment("I love this product!")
            # Returns: {"sentiment": "positive", "confidence": 0.9, ...}
        """
        try:
            # Create a structured prompt for GPT-4 to analyze sentiment
            prompt = f"""
            Analyze the sentiment of the following text and return a JSON response with:
            - sentiment: positive, negative, or neutral
            - confidence: confidence score (0-1)
            - explanation: brief explanation of the sentiment
            
            Text: "{text}"
            
            Response format:
            {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.95,
                "explanation": "This text expresses..."
            }}
            """
            
            # Call OpenAI API to get sentiment analysis
            # Note: This is a simulation - replace with actual OpenAI API call
            response = self._call_openai_api(prompt)
            
            # Parse the JSON response from GPT-4
            result = json.loads(response)
            
            # Return structured response
            return {
                "text": text,
                "sentiment": result["sentiment"],
                "confidence": result["confidence"],
                "explanation": result["explanation"],
                "model": self.model
            }
            
        except Exception as e:
            # Handle any errors during sentiment analysis
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "text": text,
                "error": str(e),
                "sentiment": "unknown",
                "confidence": 0.0
            }
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call OpenAI API for sentiment analysis
        
        This method handles the actual API call to OpenAI's GPT-4 model.
        In a production environment, you would use the OpenAI Python library.
        
        Args:
            prompt: The formatted prompt to send to GPT-4
            
        Returns:
            str: JSON response from GPT-4
            
        Note:
            This is currently a simulation. To use real OpenAI API:
            1. Install openai library: pip install openai
            2. Uncomment the OpenAI API call code below
            3. Replace the simulated response
        """
        # TODO: Replace with actual OpenAI API call
        # import openai
        # openai.api_key = self.api_key
        # response = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=self.temperature,
        #     max_tokens=self.max_tokens,
        #     top_p=self.top_p
        # )
        # return response.choices[0].message.content
        
        # Simulated response for demonstration purposes
        # In a real implementation, this would be the actual GPT-4 response
        return '''
        {
            "sentiment": "positive",
            "confidence": 0.85,
            "explanation": "This text expresses positive sentiment with optimistic language."
        }
        '''
    
    def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint for the agent
        
        Returns basic information about the agent's status,
        including model information and capabilities.
        
        Returns:
            Dict containing health check information:
            {
                "status": "healthy",
                "model": "gpt-4",
                "capabilities": ["sentiment-analysis", "text-processing"]
            }
        """
        return {
            "status": "healthy",
            "model": self.model,
            "capabilities": ["sentiment-analysis", "text-processing"]
        }

# gRPC service implementation
class SentimentAnalysisService:
    """
    gRPC service wrapper for the sentiment analysis agent
    
    This class provides the gRPC interface that allows other services
    to call the sentiment analysis agent over the network.
    
    The service exposes methods that can be called by UAPI or other
    applications that need sentiment analysis capabilities.
    """
    
    def __init__(self):
        """
        Initialize the gRPC service
        
        Creates an instance of the sentiment analysis agent
        that will handle the actual sentiment analysis requests.
        """
        self.agent = SentimentAnalysisAgent()
    
    def AnalyzeSentiment(self, request, context):
        """
        gRPC method for sentiment analysis
        
        This method is called when a client sends a sentiment analysis
        request to the gRPC service.
        
        Args:
            request: gRPC request object containing the text to analyze
            context: gRPC context object
            
        Returns:
            gRPC response object with sentiment analysis results
            
        Note:
            This is a placeholder implementation. In a real implementation,
            you would need to define the proper gRPC proto messages.
        """
        # Extract text from gRPC request
        # In a real implementation, this would be: text = request.text
        text = getattr(request, 'text', '')
        
        # Perform sentiment analysis using the agent
        result = self.agent.analyze_sentiment(text)
        
        # Return gRPC response
        # In a real implementation, you would create the proper response object
        return result

def serve():
    """
    Start the gRPC server
    
    This function sets up and starts the gRPC server that will:
    1. Create a server instance with thread pool
    2. Add the sentiment analysis service
    3. Bind to the specified port
    4. Start listening for requests
    5. Keep running until interrupted
    
    The server will be accessible on the specified port (default: 50051)
    and ready to accept sentiment analysis requests from clients.
    """
    # Create gRPC server with thread pool for handling concurrent requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # TODO: Add the sentiment analysis service to the server
    # In a real implementation, you would need to:
    # 1. Generate gRPC code from proto files
    # 2. Import the generated modules
    # 3. Add the service to the server
    # 
    # Example:
    # from sentiment_analysis_pb2_grpc import add_SentimentAnalysisServiceServicer_to_server
    # add_SentimentAnalysisServiceServicer_to_server(SentimentAnalysisService(), server)
    
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 50051))
    
    # Bind server to the specified port
    server.add_insecure_port(f'[::]:{port}')
    
    # Start the server
    server.start()
    
    logger.info(f"Sentiment Analysis Agent server started on port {port}")
    logger.info("Server is ready to accept sentiment analysis requests")
    
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
    Main entry point for the sentiment analysis agent
    
    When this script is run directly, it will:
    1. Initialize the sentiment analysis agent
    2. Start the gRPC server
    3. Begin accepting requests
    
    The agent can then be called by other services or applications
    that need sentiment analysis capabilities.
    """
    serve() 