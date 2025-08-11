#!/usr/bin/env python3
"""
LLM Config Manager
==================

Stores LLM credentials and defaults in ~/.agent/llm.json, similar to
ProfileManager but scoped to model providers. Avoids saving secrets in
Agentfile; prefers env vars.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class LLMConfigManager:
    """Manage provider API keys and default model selection."""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".agent"
        self.config_file = self.config_dir / "llm.json"
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"providers": {}, "default": {}}
        return {"providers": {}, "default": {}}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def set_api_key(self, provider: str, api_key: str) -> None:
        data = self._load()
        providers = data.setdefault("providers", {})
        prov = providers.setdefault(provider, {})
        prov["api_key"] = api_key
        self._save(data)

    def get_api_key(self, provider: str) -> Optional[str]:
        data = self._load()
        return data.get("providers", {}).get(provider, {}).get("api_key")

    def set_default_model(self, provider: str, model: str) -> None:
        data = self._load()
        data["default"] = {"provider": provider, "model": model}
        self._save(data)

    def get_default(self) -> Dict[str, str]:
        data = self._load()
        return data.get("default", {})

    def auto_configure_from_env(self) -> Dict[str, Any]:
        """Populate keys and sensible defaults from environment variables.

        Returns a summary of what was configured.
        """
        data = self._load()
        providers = data.setdefault("providers", {})

        changed = {"keys": [], "default": None}

        if os.getenv("OPENAI_API_KEY"):
            providers.setdefault("openai", {})["api_key"] = os.getenv("OPENAI_API_KEY")
            changed["keys"].append("openai")
            if not data.get("default"):
                data["default"] = {"provider": "openai", "model": "gpt-4o-mini"}
                changed["default"] = data["default"]

        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if gemini_key:
            providers.setdefault("google", {})["api_key"] = gemini_key
            changed["keys"].append("google")
            if not data.get("default"):
                data["default"] = {"provider": "google", "model": "gemini-1.5-flash"}
                changed["default"] = data["default"]

        if os.getenv("ANTHROPIC_API_KEY"):
            providers.setdefault("anthropic", {})["api_key"] = os.getenv("ANTHROPIC_API_KEY")
            changed["keys"].append("anthropic")
            if not data.get("default"):
                data["default"] = {"provider": "anthropic", "model": "claude-3-5-haiku"}
                changed["default"] = data["default"]

        self._save(data)
        return changed


