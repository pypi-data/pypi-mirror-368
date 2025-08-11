#!/usr/bin/env python3
"""
LLM Provider Manager
====================

Defines the provider interface and factory to obtain concrete providers.
Includes adapters for OpenAI, Anthropic, and Google (Gemini) with minimal
capability listing and chat support suitable for CLI usage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .config_manager import LLMConfigManager


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    def __init__(self, name: str, config: LLMConfigManager):
        self.name = name
        self.config = config

    @abstractmethod
    def list_models(self, capabilities: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return a list of models with metadata.

        capabilities: optional comma-separated filter like 'chat,tools,vision'.
        """

    @abstractmethod
    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        """Minimal chat API returning provider-normalized content."""


class OpenAIProvider(LLMProvider):
    """OpenAI provider adapter (uses openai>=0.28 client)."""

    def list_models(self, capabilities: Optional[str] = None) -> List[Dict[str, Any]]:
        # Static curated list for beta to keep fast and deterministic
        models = [
            {"name": "gpt-4o-mini", "capabilities": ["chat", "tools", "vision"], "context_window": 128000},
            {"name": "gpt-4o", "capabilities": ["chat", "tools", "vision"], "context_window": 128000},
            {"name": "o3-mini", "capabilities": ["chat", "tools", "reasoning"], "context_window": 200000},
        ]
        if capabilities:
            required = {cap.strip() for cap in capabilities.split(',') if cap.strip()}
            models = [m for m in models if required.issubset(set(m.get("capabilities", [])))]
        return models

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        import os
        import openai
        api_key = self.config.get_api_key("openai") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "missing_api_key", "message": "OpenAI API key not configured. Use 'agent llm configure set-key --provider openai --api-key ...'"}
        try:
            client = openai.OpenAI(api_key=api_key)
            result = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            choice = result.choices[0]
            text = choice.message.get("content") if hasattr(choice, "message") else choice.get("message", {}).get("content")
            return {"provider": "openai", "model": model, "text": text}
        except Exception as e:
            return {"error": "request_failed", "message": str(e)}


class AnthropicProvider(LLMProvider):
    """Anthropic provider adapter (minimal stub, requires anthropic package if expanded)."""

    def list_models(self, capabilities: Optional[str] = None) -> List[Dict[str, Any]]:
        models = [
            {"name": "claude-3-5-sonnet", "capabilities": ["chat", "tools"], "context_window": 200000},
            {"name": "claude-3-5-haiku", "capabilities": ["chat", "tools"], "context_window": 200000},
        ]
        if capabilities:
            required = {cap.strip() for cap in capabilities.split(',') if cap.strip()}
            models = [m for m in models if required.issubset(set(m.get("capabilities", [])))]
        return models

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        import os
        from anthropic import Anthropic

        api_key = self.config.get_api_key("anthropic") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {"error": "missing_api_key", "message": "Anthropic API key not configured. Use 'agent llm configure set-key --provider anthropic --api-key ...'"}
        try:
            client = Anthropic(api_key=api_key)
            system_texts = [m["content"] for m in messages if m.get("role") == "system"]
            system = "\n".join(system_texts) if system_texts else None
            content_messages = [m for m in messages if m.get("role") != "system"]
            result = client.messages.create(
                model=model,
                system=system,
                messages=content_messages,
                temperature=temperature,
                max_tokens=1024,
            )
            text = "".join([b.text for b in result.content if getattr(b, "type", "text") == "text"]) if hasattr(result, "content") else ""
            return {"provider": "anthropic", "model": model, "text": text}
        except Exception as e:
            return {"error": "request_failed", "message": str(e)}


class GoogleProvider(LLMProvider):
    """Google Gemini provider adapter (minimal, via google-generativeai)."""

    def list_models(self, capabilities: Optional[str] = None) -> List[Dict[str, Any]]:
        models = [
            {"name": "gemini-1.5-pro", "capabilities": ["chat", "tools", "vision"], "context_window": 1000000},
            {"name": "gemini-1.5-flash", "capabilities": ["chat", "tools", "vision"], "context_window": 1000000},
        ]
        if capabilities:
            required = {cap.strip() for cap in capabilities.split(',') if cap.strip()}
            models = [m for m in models if required.issubset(set(m.get("capabilities", [])))]
        return models

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
        import os
        import google.generativeai as genai

        api_key = self.config.get_api_key("google") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "missing_api_key", "message": "Google API key not configured. Use 'agent llm configure set-key --provider google --api-key ...'"}
        try:
            genai.configure(api_key=api_key)
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            model_obj = genai.GenerativeModel(model)
            resp = model_obj.generate_content(prompt, generation_config={"temperature": temperature})
            text = getattr(resp, "text", None) or (resp.candidates[0].content.parts[0].text if getattr(resp, "candidates", None) else "")
            return {"provider": "google", "model": model, "text": text}
        except Exception as e:
            return {"error": "request_failed", "message": str(e)}


class LLMProviderFactory:
    """Factory to create provider instances and list supported providers."""

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
    }

    @classmethod
    def list_providers(cls) -> List[str]:
        return sorted(list(cls._providers.keys()))

    @classmethod
    def get_provider(cls, name: str, config: LLMConfigManager) -> Optional[LLMProvider]:
        prov_cls = cls._providers.get((name or "").lower())
        return prov_cls(name=name, config=config) if prov_cls else None


