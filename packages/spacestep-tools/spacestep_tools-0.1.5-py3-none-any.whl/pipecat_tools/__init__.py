"""
Pipecat Tools - A flexible toolkit for managing Pipecat function tools.

This library provides utilities for managing OpenAI-style function metadata
and handlers for Pipecat AI applications, with support for dynamic tool loading.
"""

from .core import (
    ToolManager,
    get_functions_meta,
    get_supported_function_names,
    get_function_handlers,
    register_custom_tools,
    get_required_constants,
    get_all_set_constants,
    set_constants
)
from .tools import (
    call_management,
    scheduling,
)

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    # Core functionality
    "ToolManager",
    "get_functions_meta",
    "get_supported_function_names", 
    "get_function_handlers",
    "register_custom_tools",
    "get_required_constants",
    "get_all_set_constants",
    "set_constants",
    # Built-in tools modules
    "call_management",
    "scheduling",
    # Version
    "__version__",
]