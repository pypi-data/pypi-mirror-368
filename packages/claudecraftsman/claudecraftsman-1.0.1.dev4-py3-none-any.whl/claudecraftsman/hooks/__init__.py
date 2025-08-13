"""
ClaudeCraftsman hooks package for Claude Code integration.

Provides hook handlers and configuration for seamless integration
with Claude Code's hook system.
"""

from claudecraftsman.hooks.config import HookConfig, generate_hooks_json
from claudecraftsman.hooks.handlers import HookHandler

__all__ = [
    "HookConfig",
    "HookHandler",
    "generate_hooks_json",
]
