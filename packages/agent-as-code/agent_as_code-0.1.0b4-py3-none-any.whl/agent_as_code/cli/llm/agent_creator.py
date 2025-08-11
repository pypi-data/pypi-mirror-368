#!/usr/bin/env python3
"""
LLM-Enhanced Agent Creator
==========================

This module integrates LLM capabilities with agent creation, allowing users to:
- Generate Agentfiles from natural language descriptions
- Get intelligent template recommendations
- Create agents with LLM-powered guidance
- Optimize existing agents using AI analysis
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from .manager import LLMProviderFactory
from .config_manager import LLMConfigManager


class LLMAgentCreator:
    """LLM-powered agent creation and optimization."""

    def __init__(self):
        """Initialize the LLM agent creator."""
        self.config = LLMConfigManager()
        self.default_provider = self.config.get_default().get("provider", "openai")
        self.default_model = self.config.get_default().get("model", "gpt-4o-mini")

    def generate_agentfile(self, description: str, output_path: str = "Agentfile") -> Dict[str, Any]:
        """
        Generate an Agentfile from natural language description using LLM.
        
        Args:
            description: Natural language description of the agent
            output_path: Path to save the generated Agentfile
            
        Returns:
            Dict containing generation results and metadata
        """
        try:
            # Get LLM provider
            provider = LLMProviderFactory.get_provider(self.default_provider, self.config)
            if not provider:
                return {"error": "no_provider", "message": f"No LLM provider available: {self.default_provider}"}
            
            # Create prompt for Agentfile generation
            system_prompt = """You are an expert in creating Agent as Code (AaC) configurations. 
            Generate a complete Agentfile based on the user's description.
            
            Rules:
            1. Use appropriate base image (agent/python:3.11-docker for Python agents)
            2. Define relevant capabilities based on the description
            3. Choose appropriate model and configuration
            4. Include necessary dependencies
            5. Set appropriate environment variables
            6. Expose relevant ports
            7. Include health checks
            8. Add meaningful metadata labels
            
            Return ONLY the Agentfile content, no explanations."""
            
            user_prompt = f"Create an Agentfile for: {description}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Generate Agentfile content
            result = provider.chat(self.default_model, messages)
            
            if "error" in result:
                return result
            
            agentfile_content = result.get("text", "")
            
            # Save to file
            with open(output_path, 'w') as f:
                f.write(agentfile_content)
            
            return {
                "success": True,
                "output_path": output_path,
                "content": agentfile_content,
                "provider": self.default_provider,
                "model": self.default_model
            }
            
        except Exception as e:
            return {"error": "generation_failed", "message": str(e)}

    def suggest_template(self, description: str) -> Dict[str, Any]:
        """
        Suggest the best template based on agent description.
        
        Args:
            description: Natural language description of the agent
            
        Returns:
            Dict containing template recommendation and reasoning
        """
        try:
            provider = LLMProviderFactory.get_provider(self.default_provider, self.config)
            if not provider:
                return {"error": "no_provider", "message": f"No LLM provider available: {self.default_provider}"}
            
            system_prompt = """You are an expert in AI agent development. 
            Analyze the user's agent description and recommend the best template.
            
            Available templates:
            - python-agent: General Python AI agents, good for most use cases
            - node-agent: JavaScript/Node.js agents, good for web services
            - java-agent: Java agents, good for enterprise applications
            
            Consider:
            1. Programming language requirements
            2. Performance needs
            3. Integration requirements
            4. Team expertise
            
            Return a JSON response with:
            {
                "template": "template-name",
                "reasoning": "explanation of choice",
                "capabilities": ["list", "of", "suggested", "capabilities"],
                "dependencies": ["list", "of", "key", "dependencies"]
            }"""
            
            user_prompt = f"Recommend template for: {description}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = provider.chat(self.default_model, messages)
            
            if "error" in result:
                return result
            
            try:
                # Try to parse JSON response
                response_text = result.get("text", "")
                # Extract JSON if it's wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                suggestion = json.loads(response_text)
                return {
                    "success": True,
                    "suggestion": suggestion,
                    "provider": self.default_provider,
                    "model": self.default_model
                }
            except json.JSONDecodeError:
                # Fallback to text parsing
                return {
                    "success": True,
                    "suggestion": {
                        "template": "python-agent",
                        "reasoning": "Default fallback template",
                        "capabilities": ["general-ai"],
                        "dependencies": ["openai"]
                    },
                    "raw_response": result.get("text", ""),
                    "provider": self.default_provider,
                    "model": self.default_model
                }
                
        except Exception as e:
            return {"error": "suggestion_failed", "message": str(e)}

    def generate_test_cases(self, agent_description: str, test_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate test cases for an agent using LLM.
        
        Args:
            agent_description: Description of the agent to test
            test_type: Type of tests to generate (comprehensive, edge-cases, performance)
            
        Returns:
            Dict containing generated test cases
        """
        try:
            provider = LLMProviderFactory.get_provider(self.default_provider, self.config)
            if not provider:
                return {"error": "no_provider", "message": f"No LLM provider available: {self.default_provider}"}
            
            system_prompt = f"""You are an expert in AI agent testing. 
            Generate {test_type} test cases for the described agent.
            
            Generate:
            1. Unit test cases with input/output expectations
            2. Integration test scenarios
            3. Edge case handling
            4. Error condition tests
            5. Performance test scenarios
            
            Return a JSON response with:
            {{
                "test_cases": [
                    {{
                        "name": "test_name",
                        "description": "what this test validates",
                        "input": {{"data": "test input"}},
                        "expected_output": {{"result": "expected result"}},
                        "test_type": "unit|integration|edge|error|performance"
                    }}
                ],
                "test_data": {{"sample_inputs": ["list", "of", "inputs"]}},
                "validation_logic": "description of how to validate results"
            }}"""
            
            user_prompt = f"Generate {test_type} tests for: {agent_description}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = provider.chat(self.default_model, messages)
            
            if "error" in result:
                return result
            
            try:
                response_text = result.get("text", "")
                # Extract JSON if wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                test_cases = json.loads(response_text)
                return {
                    "success": True,
                    "test_cases": test_cases,
                    "provider": self.default_provider,
                    "model": self.default_model
                }
            except json.JSONDecodeError:
                return {
                    "error": "json_parse_failed",
                    "message": "Could not parse test cases as JSON",
                    "raw_response": response_text
                }
                
        except Exception as e:
            return {"error": "test_generation_failed", "message": str(e)}

    def optimize_agent(self, agent_path: str, optimization_goal: str) -> Dict[str, Any]:
        """
        Analyze and optimize an existing agent using LLM.
        
        Args:
            agent_path: Path to the agent project
            optimization_goal: Goal for optimization (performance, cost, accuracy)
            
        Returns:
            Dict containing optimization recommendations
        """
        try:
            provider = LLMProviderFactory.get_provider(self.default_provider, self.config)
            if not provider:
                return {"error": "no_provider", "message": f"No LLM provider available: {self.default_provider}"}
            
            # Read Agentfile
            agentfile_path = Path(agent_path) / "Agentfile"
            if not agentfile_path.exists():
                return {"error": "no_agentfile", "message": f"Agentfile not found at {agentfile_path}"}
            
            with open(agentfile_path, 'r') as f:
                agentfile_content = f.read()
            
            system_prompt = f"""You are an expert in AI agent optimization. 
            Analyze the provided Agentfile and suggest optimizations for: {optimization_goal}
            
            Consider:
            1. Model selection and configuration
            2. Capability optimization
            3. Resource allocation
            4. Cost optimization
            5. Performance improvements
            6. Security enhancements
            
            Return a JSON response with:
            {{
                "current_analysis": {{
                    "strengths": ["list", "of", "current", "strengths"],
                    "weaknesses": ["list", "of", "areas", "for", "improvement"]
                }},
                "optimization_recommendations": [
                    {{
                        "category": "model|capability|resource|security",
                        "current": "current setting",
                        "recommended": "recommended setting",
                        "reasoning": "why this change helps",
                        "impact": "high|medium|low",
                        "effort": "high|medium|low"
                    }}
                ],
                "optimized_agentfile": "complete optimized Agentfile content"
            }}"""
            
            user_prompt = f"Analyze and optimize this Agentfile for {optimization_goal}:\n\n{agentfile_content}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            result = provider.chat(self.default_model, messages)
            
            if "error" in result:
                return result
            
            try:
                response_text = result.get("text", "")
                # Extract JSON if wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                optimization = json.loads(response_text)
                return {
                    "success": True,
                    "optimization": optimization,
                    "provider": self.default_provider,
                    "model": self.default_model
                }
            except json.JSONDecodeError:
                return {
                    "error": "json_parse_failed",
                    "message": "Could not parse optimization as JSON",
                    "raw_response": response_text
                }
                
        except Exception as e:
            return {"error": "optimization_failed", "message": str(e)}
