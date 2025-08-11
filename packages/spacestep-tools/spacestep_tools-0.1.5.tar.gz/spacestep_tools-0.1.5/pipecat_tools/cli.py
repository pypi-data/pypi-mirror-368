"""
Command-line interface for Pipecat Tools.
"""

import argparse
from pathlib import Path
from typing import Optional

from .core import ToolManager


def list_tools(manager: ToolManager) -> None:
    """List all available tools."""
    tools = manager.list_tools()
    if not tools:
        print("No tools available.")
        return
    
    print("Available tools:")
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
        if tool['parameters']['required']:
            print(f"    Required parameters: {', '.join(tool['parameters']['required'])}")


def validate_tools(manager: ToolManager, tool_names: list[str]) -> None:
    """Validate that tools are properly configured."""
    validation_results = manager.validate_tools(tool_names)
    
    print("Tool validation results:")
    for name, is_valid in validation_results.items():
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {name}: {status}")


def get_tool_info(manager: ToolManager, tool_name: str) -> None:
    """Get detailed information about a specific tool."""
    info = manager.get_tool_info(tool_name)
    if not info:
        print(f"Tool '{tool_name}' not found.")
        return
    
    print(f"Tool: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Has handler: {'Yes' if info['has_handler'] else 'No'}")
    
    if info['parameters']['properties']:
        print("Parameters:")
        for param, details in info['parameters']['properties'].items():
            required = " (required)" if param in info['parameters']['required'] else ""
            print(f"  • {param}: {details.get('type', 'unknown')}{required}")
            if 'description' in details:
                print(f"    {details['description']}")
    else:
        print("Parameters: None")


def register_custom_tools(manager: ToolManager, handlers_dir: Optional[str], config_file: Optional[str]) -> None:
    """Register custom tools from directory and/or config file."""
    try:
        if handlers_dir:
            handlers_path = Path(handlers_dir)
            if not handlers_path.exists():
                print(f"Error: Handlers directory '{handlers_dir}' does not exist.")
                return
        
        if config_file:
            config_path = Path(config_file)
            if not config_path.exists():
                print(f"Error: Config file '{config_file}' does not exist.")
                return
        
        manager.register_tools_from_directory(handlers_dir, config_file)
        print("Custom tools registered successfully.")
        
    except Exception as e:
        print(f"Error registering custom tools: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Pipecat Tools - Manage function tools for Pipecat AI applications"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List tools command
    subparsers.add_parser("list", help="List all available tools")
    
    # Validate tools command
    validate_parser = subparsers.add_parser("validate", help="Validate tools")
    validate_parser.add_argument("tools", nargs="+", help="Tool names to validate")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get detailed information about a tool")
    info_parser.add_argument("tool_name", help="Name of the tool to get info for")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register custom tools")
    register_parser.add_argument("--handlers-dir", help="Directory containing tool handler Python files")
    register_parser.add_argument("--config-file", help="YAML configuration file with tool metadata")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize ToolManager
    manager = ToolManager()
    
    # Execute commands
    if args.command == "list":
        list_tools(manager)
    elif args.command == "validate":
        validate_tools(manager, args.tools)
    elif args.command == "info":
        get_tool_info(manager, args.tool_name)
    elif args.command == "register":
        if not args.handlers_dir and not args.config_file:
            print("Error: Must provide either --handlers-dir or --config-file (or both)")
            return
        register_custom_tools(manager, args.handlers_dir, args.config_file)


if __name__ == "__main__":
    main() 