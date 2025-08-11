"""
Basic usage example for Pipecat Tools.

This example demonstrates how to use the library's built-in tools
and register custom tools.
"""

import asyncio
from pipecat_tools import ToolManager, get_functions_meta, get_function_handlers


async def main():
    print("=== Pipecat Tools Basic Usage Example ===\n")
    
    # Initialize tool manager
    manager = ToolManager()
    
    # List available built-in tools
    print("1. Available built-in tools:")
    available_tools = manager.get_supported_function_names()
    for tool in available_tools:
        print(f"   • {tool}")
    print()
    
    # Get detailed information about a specific tool
    print("2. Tool information:")
    tool_info = manager.get_tool_info("get_weekday")
    if tool_info:
        print(f"   Name: {tool_info['name']}")
        print(f"   Description: {tool_info['description']}")
        print(f"   Has handler: {tool_info['has_handler']}")
        if tool_info['parameters']['required']:
            print(f"   Required parameters: {', '.join(tool_info['parameters']['required'])}")
    print()
    
    # Get OpenAI-compatible schema for specific tools
    print("3. Getting schema for call management tools:")
    call_tools = ["transfer_call", "end_call", "get_weekday"]
    schema = manager.get_tools_schema(call_tools)
    print(f"   Generated schema with {len(schema.standard_tools)} tools")
    for tool_schema in schema.standard_tools:
        print(f"   • {tool_schema.name}: {tool_schema.description}")
    print()
    
    # Get function handlers
    print("4. Getting function handlers:")
    handlers = manager.get_handlers(call_tools)
    print(f"   Got {len(handlers)} handlers:")
    for name, handler in handlers.items():
        print(f"   • {name}: {handler.__name__}")
    print()
    
    # Validate tools
    print("5. Tool validation:")
    validation_results = manager.validate_tools(["transfer_call", "invalid_tool", "get_weekday"])
    for name, is_valid in validation_results.items():
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"   {name}: {status}")
    print()
    
    # Alternative: Use functional API
    print("6. Using functional API:")
    schema_func = get_functions_meta(["book_appointment"])
    handlers_func = get_function_handlers(["book_appointment"])
    print(f"   Schema: {len(schema_func.standard_tools)} tools")
    print(f"   Handlers: {len(handlers_func)} handlers")
    print()
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(main()) 