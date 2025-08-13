"""
ClaudeCraftsman: Artisanal development framework for Claude Code.

A Python-based framework that brings craftsman-quality standards to AI-assisted development.
"""

try:
    from claudecraftsman._version import __version__
except ImportError:
    # Fallback for development installs
    __version__ = "0.0.0+dev"
__author__ = "ClaudeCraftsman Team"

from claudecraftsman.core.config import Config, get_config
from claudecraftsman.core.registry import RegistryManager
from claudecraftsman.core.state import StateManager
from claudecraftsman.core.validation import QualityGates, run_quality_gates

__all__ = [
    "Config",
    "QualityGates",
    "RegistryManager",
    "StateManager",
    "__version__",
    "get_config",
    "run_quality_gates",
]
