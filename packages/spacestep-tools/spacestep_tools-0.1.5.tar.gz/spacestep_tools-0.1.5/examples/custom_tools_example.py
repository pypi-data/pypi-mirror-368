"""
Custom tools example for Pipecat Tools.

This example demonstrates how to create and register custom tools.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from pipecat_tools import ToolManager


# Create example custom tool files
CUSTOM_TOOL_CODE = '''
"""
Example custom tools for demonstration.
"""

from pipecat.services.llm_service import FunctionCallParams
from pipecat.frames.frames import FunctionCallResultProperties
import random


async def generate_random_number(params: FunctionCallParams):
    """
    Generate a random number within a specified range.
    
    Args:
        params: Pipecat function call parameters containing:
            - min_value (int): Minimum value (default: 1)
            - max_value (int): Maximum value (default: 100)
    """
    min_value = params.arguments.get("min_value", 1)
    max_value = params.arguments.get("max_value", 100)
    
    if min_value > max_value:
        result = f"Error: min_value ({min_value}) cannot be greater than max_value ({max_value})"
    else:
        random_num = random.randint(min_value, max_value)
        result = f"Generated random number: {random_num} (range: {min_value}-{max_value})"
    
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)


async def calculate_factorial(params: FunctionCallParams):
    """
    Calculate the factorial of a number.
    
    Args:
        params: Pipecat function call parameters containing:
            - number (int): Number to calculate factorial for
    """
    try:
        number = int(params.arguments["number"])
        
        if number < 0:
            result = "Error: Cannot calculate factorial of negative numbers"
        elif number > 20:
            result = "Error: Number too large (maximum: 20)"
        else:
            factorial = 1
            for i in range(1, number + 1):
                factorial *= i
            result = f"Factorial of {number} is {factorial}"
    except (ValueError, KeyError):
        result = "Error: Invalid number provided"
    
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)
'''

CUSTOM_TOOL_CONFIG = '''
generate_random_number:
  description: "Generate a random number within a specified range"
  parameters:
    type: object
    properties:
      min_value:
        type: integer
        description: "Minimum value for the random number"
        default: 1
      max_value:
        type: integer
        description: "Maximum value for the random number"
        default: 100
    required: []

calculate_factorial:
  description: "Calculate the factorial of a number"
  parameters:
    type: object
    properties:
      number:
        type: integer
        description: "Number to calculate factorial for (0-20)"
        minimum: 0
        maximum: 20
    required:
      - number
'''


async def main():
    print("=== Pipecat Tools Custom Tools Example ===\n")
    
    # Create temporary directory for custom tools
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write custom tool files
        tools_dir = Path(temp_dir) / "custom_tools"
        tools_dir.mkdir()
        
        # Create Python file with custom tools
        (tools_dir / "math_tools.py").write_text(CUSTOM_TOOL_CODE)
        
        # Create YAML config file
        config_file = Path(temp_dir) / "tools_config.yaml"
        config_file.write_text(CUSTOM_TOOL_CONFIG)
        
        print(f"Created custom tools in: {temp_dir}")
        print(f"  - Tools directory: {tools_dir}")
        print(f"  - Config file: {config_file}")
        print()
        
        # Initialize tool manager
        manager = ToolManager()
        
        # Show built-in tools first
        print("1. Built-in tools before registration:")
        builtin_tools = manager.get_supported_function_names()
        print(f"   Available: {len(builtin_tools)} tools")
        for tool in builtin_tools[:3]:  # Show first 3
            print(f"   • {tool}")
        print("   ...")
        print()
        
        # Register custom tools
        print("2. Registering custom tools...")
        try:
            manager.register_tools_from_directory(
                handlers_dir=str(tools_dir),
                config_file=str(config_file)
            )
            print("   ✓ Custom tools registered successfully!")
        except Exception as e:
            print(f"   ✗ Error registering custom tools: {e}")
            return
        print()
        
        # Show all tools after registration
        print("3. All tools after registration:")
        all_tools = manager.get_supported_function_names()
        print(f"   Available: {len(all_tools)} tools")
        for tool in all_tools:
            is_custom = tool in ["generate_random_number", "calculate_factorial"]
            marker = "🆕" if is_custom else "📦"
            print(f"   {marker} {tool}")
        print()
        
        # Get detailed info about custom tools
        print("4. Custom tool information:")
        for tool_name in ["generate_random_number", "calculate_factorial"]:
            tool_info = manager.get_tool_info(tool_name)
            if tool_info:
                print(f"   Tool: {tool_info['name']}")
                print(f"   Description: {tool_info['description']}")
                print(f"   Required params: {tool_info['parameters']['required']}")
                print()
        
        # Generate schema for custom tools
        print("5. Schema generation for custom tools:")
        custom_tools = ["generate_random_number", "calculate_factorial"]
        schema = manager.get_tools_schema(custom_tools)
        print(f"   Generated schema with {len(schema.standard_tools)} custom tools")
        for tool_schema in schema.standard_tools:
            print(f"   • {tool_schema.name}")
            print(f"     Description: {tool_schema.description}")
            print(f"     Parameters: {list(tool_schema.properties.keys())}")
        print()
        
        # Get handlers for custom tools
        print("6. Function handlers:")
        handlers = manager.get_handlers(custom_tools)
        print(f"   Got {len(handlers)} custom handlers:")
        for name, handler in handlers.items():
            print(f"   • {name}: {handler.__name__}")
        print()
        
        # Validate all tools
        print("7. Tool validation:")
        validation_results = manager.validate_tools(custom_tools + ["transfer_call"])
        for name, is_valid in validation_results.items():
            status = "✓ Valid" if is_valid else "✗ Invalid"
            tool_type = "Custom" if name in custom_tools else "Built-in"
            print(f"   {name} ({tool_type}): {status}")
        print()
        
        print("=== Custom tools example completed successfully! ===")
        print("Note: Custom tools are available only during this session.")
        print("In a real application, you'd store the tools in permanent directories.")


if __name__ == "__main__":
    asyncio.run(main()) 