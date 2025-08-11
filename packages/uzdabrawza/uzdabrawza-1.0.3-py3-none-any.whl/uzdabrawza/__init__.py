"""
🏴‍☠️ uzdabrawza - The Anal-Queen of AI Browser Automation 🏴‍☠️

A beautifully fucked-up browser automation script that gives zero shits about
anything while somehow still working perfectly. Smells like smegma but runs like a dream.

This package provides comprehensive browser automation capabilities with stealth features,
multi-LLM provider support, and organized anarchy throughout the codebase.
"""

__version__ = "1.0.0"
__author__ = "uzdabrawza"
__email__ = "uzdabrawza@example.com"
__description__ = "The Anal-Queen of AI Browser Automation - A beautifully fucked-up browser automation script that actually works"
__url__ = "https://github.com/yourusername/uzdabrawza"

# Package metadata
__title__ = "uzdabrawza"
__license__ = "MIT"
__copyright__ = "Copyright 2025 uzdabrawza"

# Export main functionality
from .core import main as run_automation
from .cli import main as cli_main

# Package-level constants
SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic", 
    "google",
    "ollama",
    "azure",
    "deepseek",
    "groq", 
    "openrouter",
    "aws"
]

DEFAULT_MODELS = {
    "openai": "gpt-5-mini",
    "anthropic": "claude-opus-4-1", 
    "google": "gemini-2.5-flash",
    "ollama": "llama3.1",
    "azure": "gpt-5",
    "deepseek": "deepseek-reasoner",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "meta-llama/llama-3.1-70b-instruct",
    "aws": "anthropic.claude-opus-4-1-20250805-v1:0",
}

# Import core dependencies
import patchright

def get_version() -> str:
    """Get the current version of uzdabrawza."""
    return __version__

def is_stealth_available() -> bool:
    """Check if stealth capabilities (patchright) are available."""
    return True  # Always available since patchright is a core dependency

def get_supported_providers() -> list[str]:
    """Get list of supported LLM providers."""
    return SUPPORTED_PROVIDERS.copy()

def get_default_model(provider: str) -> str:
    """Get the default model for a given provider."""
    return DEFAULT_MODELS.get(provider, "gpt-5-mini")

# Package level constants for configuration
CLUSTERFUCK_ENV_DEFAULTS = {
    # Browser-use core settings
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
    "GOOGLE_API_KEY": "",
    "DEEPSEEK_API_KEY": "",
    "GROK_API_KEY": "",
    "NOVITA_API_KEY": "",
    "OPENROUTER_API_KEY": "",
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "AWS_REGION": "",
    "AZURE_OPENAI_ENDPOINT": "",
    "AZURE_OPENAI_KEY": "",
    "ANONYMIZED_TELEMETRY": "true",
    "BROWSER_USE_CLOUD_SYNC": "",
    "BROWSER_USE_CLOUD_API_URL": "https://api.browser-use.com",
    "BROWSER_USE_CONFIG_DIR": "",
    # Web UI compatibility
    "OPENAI_ENDPOINT": "https://api.openai.com/v1",
    "ANTHROPIC_ENDPOINT": "https://api.anthropic.com",
    "DEEPSEEK_ENDPOINT": "https://api.deepseek.com",
    "OLLAMA_ENDPOINT": "http://localhost:11434",
    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
}

# Expose main functions for programmatic usage
__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "__url__",
    "run_automation",
    "cli_main",
    "get_version",
    "is_stealth_available", 
    "get_supported_providers",
    "get_default_model",
    "SUPPORTED_PROVIDERS",
    "DEFAULT_MODELS",
    "CLUSTERFUCK_ENV_DEFAULTS",
]