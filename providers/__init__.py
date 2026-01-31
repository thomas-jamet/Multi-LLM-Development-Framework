#!/usr/bin/env python3
"""
LLM Provider Registry

Central registry for all supported LLM providers.
"""

from typing import Dict, Optional

from providers.base import LLMProvider
from providers.gemini import GeminiProvider
from providers.claude import ClaudeProvider
from providers.codex import CodexProvider


# Supported providers list
SUPPORTED_PROVIDERS = ["gemini", "claude", "codex"]

# Default provider for backward compatibility
DEFAULT_PROVIDER = "gemini"

# Provider instances (lazy initialization)
_provider_instances: Dict[str, LLMProvider] = {}


def get_provider(name: Optional[str] = None) -> LLMProvider:
    """Get a provider instance by name.
    
    Args:
        name: Provider name (gemini, claude, codex). Defaults to DEFAULT_PROVIDER.
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider name is not supported
    """
    provider_name = name or DEFAULT_PROVIDER
    
    if provider_name not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider: {provider_name}. "
            f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}"
        )
    
    # Lazy initialization
    if provider_name not in _provider_instances:
        if provider_name == "gemini":
            _provider_instances[provider_name] = GeminiProvider()
        elif provider_name == "claude":
            _provider_instances[provider_name] = ClaudeProvider()
        elif provider_name == "codex":
            _provider_instances[provider_name] = CodexProvider()
    
    return _provider_instances[provider_name]


def get_all_providers() -> Dict[str, LLMProvider]:
    """Get all provider instances.
    
    Returns:
        Dictionary mapping provider names to instances
    """
    return {name: get_provider(name) for name in SUPPORTED_PROVIDERS}


__all__ = [
    "LLMProvider",
    "GeminiProvider", 
    "ClaudeProvider",
    "CodexProvider",
    "get_provider",
    "get_all_providers",
    "SUPPORTED_PROVIDERS",
    "DEFAULT_PROVIDER",
]
