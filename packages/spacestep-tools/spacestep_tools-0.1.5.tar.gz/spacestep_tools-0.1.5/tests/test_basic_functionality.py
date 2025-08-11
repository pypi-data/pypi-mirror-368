"""
Basic functionality tests for Pipecat Tools.
"""

import pytest
from pipecat_tools import (
    ToolManager,
    get_functions_meta,
    get_supported_function_names,
    get_function_handlers,
)


class TestBasicFunctionality:
    """Test basic library functionality."""
    
    def test_get_supported_function_names(self):
        """Test getting supported function names."""
        names = get_supported_function_names()
        assert isinstance(names, list)
        assert len(names) > 0
        assert "transfer_call" in names
        assert "end_call" in names
        assert "get_weekday" in names
    
    def test_get_functions_meta(self):
        """Test getting function metadata."""
        schema = get_functions_meta(["transfer_call", "end_call"])
        assert schema is not None
        assert hasattr(schema, 'standard_tools')
        assert len(schema.standard_tools) == 2
        
        # Check that each tool has required attributes
        for tool in schema.standard_tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'properties')
            assert hasattr(tool, 'required')
    
    def test_get_function_handlers(self):
        """Test getting function handlers."""
        handlers = get_function_handlers(["transfer_call", "end_call"])
        assert isinstance(handlers, dict)
        assert len(handlers) == 2
        assert "transfer_call" in handlers
        assert "end_call" in handlers
        
        # Check that handlers are callable
        for handler in handlers.values():
            assert callable(handler)
    
    def test_unknown_function_ignored(self):
        """Test that unknown functions are ignored gracefully."""
        schema = get_functions_meta(["transfer_call", "unknown_function"])
        assert len(schema.standard_tools) == 1
        assert schema.standard_tools[0].name == "transfer_call"
        
        handlers = get_function_handlers(["transfer_call", "unknown_function"])
        assert len(handlers) == 1
        assert "transfer_call" in handlers
        assert "unknown_function" not in handlers


class TestToolManager:
    """Test ToolManager class functionality."""
    
    def test_tool_manager_initialization(self):
        """Test ToolManager initialization."""
        manager = ToolManager()
        assert manager is not None
    
    def test_get_supported_function_names(self):
        """Test ToolManager get_supported_function_names method."""
        manager = ToolManager()
        names = manager.get_supported_function_names()
        assert isinstance(names, list)
        assert len(names) > 0
        assert "transfer_call" in names
    
    def test_get_tools_schema(self):
        """Test ToolManager get_tools_schema method."""
        manager = ToolManager()
        schema = manager.get_tools_schema(["transfer_call"])
        assert schema is not None
        assert len(schema.standard_tools) == 1
        assert schema.standard_tools[0].name == "transfer_call"
    
    def test_get_handlers(self):
        """Test ToolManager get_handlers method."""
        manager = ToolManager()
        handlers = manager.get_handlers(["transfer_call"])
        assert isinstance(handlers, dict)
        assert len(handlers) == 1
        assert "transfer_call" in handlers
        assert callable(handlers["transfer_call"])
    
    def test_get_tool_info(self):
        """Test ToolManager get_tool_info method."""
        manager = ToolManager()
        info = manager.get_tool_info("transfer_call")
        assert info is not None
        assert info["name"] == "transfer_call"
        assert "description" in info
        assert "has_handler" in info
        assert "parameters" in info
        assert info["has_handler"] is True
    
    def test_get_tool_info_unknown(self):
        """Test ToolManager get_tool_info with unknown tool."""
        manager = ToolManager()
        info = manager.get_tool_info("unknown_tool")
        assert info is None
    
    def test_list_tools(self):
        """Test ToolManager list_tools method."""
        manager = ToolManager()
        tools = manager.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check structure of tool info
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "has_handler" in tool
            assert "parameters" in tool
    
    def test_validate_tools(self):
        """Test ToolManager validate_tools method."""
        manager = ToolManager()
        results = manager.validate_tools(["transfer_call", "unknown_tool"])
        assert isinstance(results, dict)
        assert len(results) == 2
        assert results["transfer_call"] is True
        assert results["unknown_tool"] is False


class TestBuiltInTools:
    """Test built-in tools are properly configured."""
    
    def test_call_management_tools(self):
        """Test call management tools are available."""
        names = get_supported_function_names()
        call_tools = ["transfer_call", "await_call_transfer", "end_call", "get_weekday"]
        
        for tool in call_tools:
            assert tool in names
    
    def test_scheduling_tools(self):
        """Test scheduling tools are available."""
        names = get_supported_function_names()
        scheduling_tools = ["get_available_time_slots", "book_appointment"]
        
        for tool in scheduling_tools:
            assert tool in names
    
    def test_all_tools_have_handlers(self):
        """Test that all supported tools have handlers."""
        names = get_supported_function_names()
        handlers = get_function_handlers(names)
        
        # All supported tools should have handlers
        assert len(handlers) == len(names)
        for name in names:
            assert name in handlers
            assert callable(handlers[name])


if __name__ == "__main__":
    pytest.main([__file__]) 