# SpaceStep Tools

A flexible toolkit for managing Pipecat function tools with OpenAI-style metadata. This library provides utilities for managing function tools and handlers for Pipecat AI applications, with support for dynamic tool loading and custom tool registration.

## Features

- **Built-in Tools**: Comes with pre-configured tools for call management and scheduling
- **Dynamic Tool Loading**: Register custom tools from Python files and YAML configurations
- **OpenAI-Compatible**: Generate OpenAI-style function metadata automatically
- **Type Safety**: Full type hints and validation
- **CLI Interface**: Command-line tools for managing and validating tools
- **Extensible Architecture**: Easy to add new tools and modify existing ones

## Installation

```bash
pip install spacestep-tools
```

For development:
```bash
pip install spacestep-tools[dev]
```

## Quick Start

### Basic Usage

```python
from pipecat_tools import ToolManager

# Initialize the tool manager
manager = ToolManager()

# Get available tools
available_tools = manager.get_supported_function_names()
print(f"Available tools: {available_tools}")

# Get OpenAI-compatible schema for specific tools
tools_schema = manager.get_tools_schema(["transfer_call", "end_call"])

# Get function handlers
handlers = manager.get_handlers(["transfer_call", "end_call"])
```

### Using Built-in Tools

The library comes with several built-in tools:

#### Call Management Tools
- `transfer_call`: Transfer the call to a licensed agent
- `await_call_transfer`: Handle call transfer states
- `end_call`: End the current call
- `get_weekday`: Get the day of the week for a given date

#### Scheduling Tools
- `get_available_time_slots`: Get available appointment slots for dates
- `book_appointment`: Book an appointment for a client

```python
from pipecat_tools import get_functions_meta, get_function_handlers

# Get schema for scheduling tools
schema = get_functions_meta(["get_available_time_slots", "book_appointment"])

# Get handlers
handlers = get_function_handlers(["get_available_time_slots", "book_appointment"])
```

## Adding Custom Tools

### Method 1: Directory-based Registration

Create a directory with Python files containing your custom tool functions:

**File: `my_tools/weather.py`**
```python
from pipecat.services.llm_service import FunctionCallParams
from pipecat.frames.frames import FunctionCallResultProperties
import httpx

async def get_weather(params: FunctionCallParams):
    """
    Get current weather for a city.
    
    Args:
        params: Pipecat function call parameters containing:
            - city (str): Name of the city
    """
    city = params.arguments["city"]
    
    # Your weather API integration here
    try:
        # Example API call
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.weather.com/current?city={city}")
            weather_data = response.json()
        
        result = f"Current weather in {city}: {weather_data['description']}, {weather_data['temp']}°C"
    except Exception as e:
        result = f"Failed to get weather for {city}: {str(e)}"
    
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)


async def get_forecast(params: FunctionCallParams):
    """
    Get weather forecast for a city.
    
    Args:
        params: Pipecat function call parameters containing:
            - city (str): Name of the city
            - days (int): Number of days to forecast (default: 3)
    """
    city = params.arguments["city"]
    days = params.arguments.get("days", 3)
    
    # Your forecast API integration here
    result = f"Weather forecast for {city} for the next {days} days: [forecast data]"
    
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)
```

**File: `my_tools_config.yaml`**
```yaml
get_weather:
  description: "Get current weather information for a specified city"
  parameters:
    type: object
    properties:
      city:
        type: string
        description: "Name of the city to get weather for"
    required:
      - city

get_forecast:
  description: "Get weather forecast for a specified city"
  parameters:
    type: object
    properties:
      city:
        type: string
        description: "Name of the city to get forecast for"
      days:
        type: integer
        description: "Number of days to forecast (1-7)"
        minimum: 1
        maximum: 7
    required:
      - city
```

**Registration:**
```python
from pipecat_tools import ToolManager

manager = ToolManager()

# Register custom tools
manager.register_tools_from_directory(
    handlers_dir="./my_tools",
    config_file="./my_tools_config.yaml"
)

# Now you can use your custom tools
schema = manager.get_tools_schema(["get_weather", "get_forecast"])
handlers = manager.get_handlers(["get_weather", "get_forecast"])
```

### Method 2: YAML-only Configuration

If you only need to modify metadata for existing tools:

```python
manager = ToolManager()
manager.register_tools_from_config("./custom_config.yaml")
```

### Method 3: Using the Functional API

```python
from pipecat_tools import register_custom_tools

# Register tools globally
register_custom_tools(
    handlers="./my_tools",
    function_configurations="./my_tools_config.yaml"
)

# Now use the global functions
from pipecat_tools import get_functions_meta, get_function_handlers

schema = get_functions_meta(["get_weather"])
handlers = get_function_handlers(["get_weather"])
```

## Tool Function Requirements

When creating custom tools, follow these requirements:

### 1. Function Signature
```python
async def your_tool_name(params: FunctionCallParams):
    """
    Your tool description.
    
    Args:
        params: Pipecat function call parameters containing:
            - param1 (type): Description
            - param2 (type): Description
    """
    # Extract parameters
    param1 = params.arguments["param1"]
    param2 = params.arguments.get("param2", "default_value")
    
    # Your logic here
    result = "Your result"
    
    # Send result back
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)
```

### 2. YAML Configuration Schema
```yaml
your_tool_name:
  description: "Clear description of what the tool does"
  parameters:
    type: object
    properties:
      param1:
        type: string  # or number, integer, boolean, array, object
        description: "Description of parameter"
      param2:
        type: integer
        description: "Description of optional parameter"
        minimum: 1
        maximum: 100
    required:
      - param1
```

### 3. Parameter Types
Supported parameter types:
- `string`: Text values
- `number`: Floating-point numbers
- `integer`: Whole numbers
- `boolean`: True/false values
- `array`: Lists of values
- `object`: Complex nested objects

### 4. Parameter Validation
Add validation constraints:
```yaml
parameters:
  type: object
  properties:
    email:
      type: string
      format: email
    age:
      type: integer
      minimum: 0
      maximum: 120
    options:
      type: array
      items:
        type: string
      minItems: 1
      maxItems: 5
```

## Environment Variables


## Managing Per‑Function Constants

Some tools (such as `get_available_time_slots` and
`book_appointment`) need non‑public configuration values—typically webhook
URLs. Rather than hard‑coding those strings or passing them as user‑visible
parameters, SpaceStep Tools ships a lightweight helper module
`spacestep_tools.consts` that keeps an in‑memory registry keyed by  
*function → constant → value*.

### Loading constants at startup

```python
from pipecat_tools import (
    set_constants,
    get_required_constants,
)

#  Merge from an in-memory `tools` dict
tools = {
    "end_call": {},
    "book_appointment": {
        "webhook_url": "https://api.example.com/appointments"
    },
}
set_constants(agent_id, tools)

# Optionally verify that every constant has been provided
missing = get_required_constants(
    ["get_available_time_slots", "book_appointment"]
)
if missing:
    raise RuntimeError(f"Unset constants: {missing}")
```

### Accessing constants inside your tool

```python
import inspect
from pipecat_tools import get_constant
from pipecat.services.llm_service import FunctionCallParams

async def book_appointment(params: FunctionCallParams):
    # Retrieve the constant for this function
    func_name = inspect.currentframe().f_code.co_name
    agent_id = params.arguments["agent_id"]
    webhook_url = get_constant(agent_id, func_name, "webhook_url")
    # ... use webhook_url to call downstream service ...
```

Additional helper functions:

* `get_all_set_constants(aget_id)` – returns every constant that already has a value.
* `get_constant(agent_id, fn, name)` – fetch a single constant value or raise
  `KeyError` if the pair is not registered.

> **Note**  
> These constants are strictly internal implementation details; they never
> appear in the tool's public parameter schema nor can end‑users override
> them at runtime.

## CLI Usage

The library includes a command-line interface:

```bash
# List all available tools
pipecat-tools list

# Get detailed info about a specific tool
pipecat-tools info transfer_call

# Validate tools
pipecat-tools validate transfer_call end_call

# Register custom tools
pipecat-tools register --handlers-dir ./my_tools --config-file ./config.yaml
```

## Advanced Usage

### Custom Tool Manager

```python
import logging
from pipecat_tools import ToolManager

# Custom logger
logger = logging.getLogger("my_app")
manager = ToolManager(logger=logger)

# Get tool information
tool_info = manager.get_tool_info("transfer_call")
print(f"Tool: {tool_info['name']}")
print(f"Description: {tool_info['description']}")

# List all tools with details
all_tools = manager.list_tools()
for tool in all_tools:
    print(f"{tool['name']}: {tool['description']}")

# Validate multiple tools
validation_results = manager.validate_tools(["tool1", "tool2", "nonexistent"])
for name, is_valid in validation_results.items():
    print(f"{name}: {'✓' if is_valid else '✗'}")
```

### Error Handling

```python
from pipecat_tools import ToolManager

manager = ToolManager()

try:
    manager.register_tools_from_directory("./nonexistent_dir")
except ValueError as e:
    print(f"Registration failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration with Pipecat

```python
from pipecat.pipeline.pipeline import Pipeline
from pipecat.services.llm_service import LLMService
from pipecat_tools import ToolManager

# Initialize tool manager
tool_manager = ToolManager()
tool_manager.register_tools_from_directory("./my_tools", "./tools_config.yaml")

# Get tools for your pipeline
available_tools = ["transfer_call", "get_weather", "book_appointment"]
schema = tool_manager.get_tools_schema(available_tools)
handlers = tool_manager.get_handlers(available_tools)

# Configure your LLM service with tools
llm_service = LLMService(
    model="gpt-4",
    tools=schema,
    tool_handlers=handlers
)

# Add to your pipeline
pipeline = Pipeline([
    # ... other services
    llm_service,
    # ... other services
])
```

## Best Practices

### 1. Tool Naming
- Use descriptive, action-oriented names: `get_weather`, `book_appointment`, `send_email`
- Use snake_case for function names
- Avoid generic names like `process` or `handle`

### 2. Documentation
- Always provide clear docstrings
- Document all parameters and their types
- Include usage examples in docstrings

### 3. Error Handling
- Handle errors gracefully in your tool functions
- Return meaningful error messages
- Log errors for debugging

### 4. Configuration
- Use environment variables for API keys and URLs
- Provide sensible defaults
- Validate configuration at startup

### 5. Testing
- Write unit tests for your custom tools
- Test both success and error scenarios
- Mock external API calls

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### v0.1.0
- Initial release
- Built-in call management and scheduling tools
- Dynamic tool loading support
- CLI interface
- Comprehensive documentation 