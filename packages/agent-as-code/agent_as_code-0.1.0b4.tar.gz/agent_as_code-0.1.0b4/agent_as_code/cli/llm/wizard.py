#!/usr/bin/env python3
"""
Interactive Wizard for LLM Configuration
---------------------------------------

A simple, guided setup to store API keys and choose a default model.
Designed to be short and helpful for first-time users.
"""

from __future__ import annotations

from typing import Optional

from .manager import LLMProviderFactory


def prompt(text: str) -> str:
    try:
        return input(text)
    except EOFError:
        return ""
    except KeyboardInterrupt:
        # Gracefully propagate cancellation to caller
        raise KeyboardInterrupt


def run_interactive_wizard(config_manager) -> None:
    try:
        print("LLM Configuration Wizard")
        print("-------------------------")
        print("We'll help you set API keys and pick a default model. Press Enter to skip any step.")

        providers = LLMProviderFactory.list_providers()
        print("\nSupported providers:")
        for p in providers:
            print(f"  - {p}")

        for p in providers:
            key = prompt(f"Enter API key for {p} (or leave blank to skip): ")
            if key:
                config_manager.set_api_key(p, key)
                print(f"Saved API key for {p}.")

        default_provider = prompt("\nChoose default provider (openai/anthropic/google): ")
        if default_provider and default_provider not in providers:
            print("Unknown provider; skipping default selection.")
            return

        if default_provider:
            provider = LLMProviderFactory.get_provider(default_provider, config_manager)
            if not provider:
                print("Invalid provider; aborting.")
                return
            models = provider.list_models()
            if not models:
                print("No models available; aborting.")
                return
            print("Available models:")
            for idx, m in enumerate(models, 1):
                print(f"  {idx}. {m['name']} (caps={','.join(m.get('capabilities', []))})")
            choice = prompt("Pick a model number: ")
            try:
                idx = int(choice) - 1
                model = models[idx]["name"]
                config_manager.set_default_model(default_provider, model)
                print(f"Default set to {default_provider}:{model}")
            except Exception:
                print("Invalid choice; skipping.")
    except KeyboardInterrupt:
        print("\nWizard cancelled by user.")


