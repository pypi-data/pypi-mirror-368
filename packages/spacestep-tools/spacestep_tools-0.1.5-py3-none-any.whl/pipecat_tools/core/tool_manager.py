"""
Object-oriented tool management interface for Pipecat Tools.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional, Any, Callable
from pathlib import Path

from .management import (
    get_functions_meta as _get_functions_meta,
    get_supported_function_names as _get_supported_function_names,
    get_function_handlers as _get_function_handlers,
    register_custom_tools as _register_custom_tools,
)

from .consts import (
    get_required_constants as _get_required_constants,
    get_all_set_constants as _get_all_set_constants,
    set_constants as _set_constants
)

class ToolManager:
    """
    Object-oriented interface for managing Pipecat function tools.
    
    This class provides a convenient way to manage tools, their metadata,
    and handlers in a single interface. It supports both built-in tools
    and custom tools loaded from external sources.
    
    Example:
        >>> manager = ToolManager()
        >>> manager.register_tools_from_directory("./custom_tools")
        >>> tools_schema = manager.get_tools_schema(["transfer_call", "my_custom_tool"])
        >>> handlers = manager.get_handlers(["transfer_call", "my_custom_tool"])
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the ToolManager.
        
        Args:
            logger: Optional logger instance. If not provided, creates a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self._custom_tools_registered = False
    
    def get_supported_function_names(self) -> List[str]:
        """
        Get a list of all supported function names.
        
        Returns:
            List of function names that have registered metadata and handlers.
        """
        return _get_supported_function_names()
    
    def get_tools_schema(self, function_names: Iterable[str]):
        """
        Build a Pipecat ToolsSchema for the given function names.
        
        Args:
            function_names: Iterable of function name strings to include.
            
        Returns:
            A ToolsSchema containing FunctionSchema objects for each valid name.
        """
        return _get_functions_meta(function_names)
    
    def get_handlers(self, function_names: Iterable[str]) -> Dict[str, Callable]:
        """
        Get function handlers for the specified function names.
        
        Args:
            function_names: Iterable of function name strings.
            
        Returns:
            Dictionary mapping function names to their callable handlers.
        """
        return _get_function_handlers(function_names)
    
    def register_tools_from_directory(
        self,
        handlers_dir: str | Path,
        config_file: Optional[str | Path] = None
    ) -> None:
        """
        Register custom tools from a directory and optional configuration file.
        
        Args:
            handlers_dir: Path to directory containing Python files with tool handlers.
            config_file: Optional path to YAML file with tool metadata configurations.
        """
        handlers_path = str(handlers_dir) if handlers_dir else None
        config_path = str(config_file) if config_file else None
        
        try:
            _register_custom_tools(handlers_path, config_path)
            self._custom_tools_registered = True
            self.logger.info(f"Successfully registered custom tools from {handlers_dir}")
        except Exception as e:
            self.logger.error(f"Failed to register custom tools: {e}")
            raise
    
    def register_tools_from_config(self, config_file: str | Path) -> None:
        """
        Register custom tools from a YAML configuration file only.
        
        Args:
            config_file: Path to YAML file with tool metadata configurations.
        """
        self.register_tools_from_directory(None, config_file)
    
    def get_tool_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.
        
        Args:
            function_name: Name of the function to get info for.
            
        Returns:
            Dictionary with tool information including metadata and whether
            it has a handler, or None if the tool is not found.
        """
        supported_names = self.get_supported_function_names()
        handlers = self.get_handlers([function_name])
        
        if function_name not in supported_names:
            return None
        
        # Get the schema to extract metadata
        schema = self.get_tools_schema([function_name])
        tool_schema = None
        if schema.standard_tools:
            tool_schema = schema.standard_tools[0]
        
        return {
            "name": function_name,
            "has_handler": function_name in handlers,
            "description": tool_schema.description if tool_schema else None,
            "parameters": {
                "properties": tool_schema.properties if tool_schema else {},
                "required": tool_schema.required if tool_schema else [],
            },
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Get information about all available tools.
        
        Returns:
            List of dictionaries containing information about each tool.
        """
        supported_names = self.get_supported_function_names()
        return [
            self.get_tool_info(name) 
            for name in supported_names
            if self.get_tool_info(name) is not None
        ]
    
    def validate_tools(self, function_names: Iterable[str]) -> Dict[str, bool]:
        """
        Validate that the specified function names are supported and have handlers.
        
        Args:
            function_names: Function names to validate.
            
        Returns:
            Dictionary mapping function names to their validation status.
        """
        supported_names = set(self.get_supported_function_names())
        handlers = self.get_handlers(function_names)
        
        return {
            name: name in supported_names and name in handlers
            for name in function_names
        }

    def get_required_constants(self, agent_id: str, function_names: Iterable[str]):
        """Return unresolved constants for the supplied functions.

        Args:
            agent_id:
            function_names: Iterable of function names to inspect.

        Returns:
            Dict[str, List[str]]: A mapping where each key is a function name
            and the value is a sorted list of constant names that are still
            unset (``None``).
        """
        return _get_required_constants(agent_id, function_names)

    def get_all_set_constants(self, aget_id:str):
        """Return every constant that already has a value.

        Returns:
            Dict[str, Dict[str, object]]: Mapping of function names to a
            sub‑mapping of constant names and their current values.
        """
        return _get_all_set_constants(aget_id)


    def set_constants(self, agent_id: str, tools: dict[str, dict[str, Any]]) -> None:
        """
        Merge constants from an in-memory `tools` dict of the form:

            {
              "end_call": {},
              "book_appointment": { "webhook_url": "…" },
            }

        into the shared _FUNCTION_CONSTANTS.
        """
        return _set_constants(agent_id, tools)