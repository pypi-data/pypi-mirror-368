"""
Utilities for producing OpenAI-style function-calling tool metadata.

The public helper `get_functions_meta()` takes an iterable of function
names and returns a list that can be fed directly to the OpenAI
`tools=` parameter.

Example:
    tools = get_functions_meta(["transfer_call", "end_call"])
"""
from __future__ import annotations

from typing import Iterable, List, Dict, Final, Callable
import importlib.util
import logging
import os
import sys
import yaml  # requires PyYAML
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

# Import built-in tools
from ..tools.call_management import (
    transfer_call,
    end_call,
    get_weekday,
    await_call_transfer,
)
from ..tools.scheduling import (
    get_available_time_slots,
    book_appointment,
)

# Global registry for function handlers
_FUNCTION_HANDLERS: Final[Dict[str, Callable]] = {
    "transfer_call": transfer_call,
    "await_call_transfer": await_call_transfer,
    "end_call": end_call,
    "get_weekday": get_weekday,
    "get_available_time_slots": get_available_time_slots,
    "book_appointment": book_appointment,
}

# Preset metadata for each callable tool
_FUNCTION_PRESETS: Final[Dict[str, Dict[str, str | dict]]] = {
    "transfer_call": {
        "description": (
            "Use this function to transfer client to the licensed agent "
            "when they agreed to."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    "end_call": {
        "description": (
            "End the phone call when:\n"
            "- if the human user and the assistant have clearly finished speaking "
            "to each other;\n"
            '- if the user said goodbye (e.g., "bye", "goodbye", "farewell", '
            '"see you", "adios");\n'
            "- after assistant has already left the voicemail message."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    "get_weekday": {
        "description": (
            "Use this to determine what day of the week a given date falls on "
            "(e.g., Monday, Tuesday). This helps decide if a requested call "
            "can be scheduled."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "The date to check, in YYYY-MM-DD format",
                }
            },
            "required": ["date"],
        },
    },
    "get_available_time_slots": {
        "description": (
            "Get the available time slots in a calendar for specified dates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dates": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "date",
                        "description": "A date in the format yyyy-mm-dd."
                    },
                    "description": (
                        "A list of dates to check for available slots. "
                        "Each date must have the format yyyy-mm-dd."
                    ),
                }
            },
            "required": ["dates"],
        },
    },
    "await_call_transfer": {
        "description": "Call this function when a call transfer is happening.",
        "parameters": {"type": "object", "properties": {}},
    },
    "book_appointment": {
        "description": "Book an appointment for a client.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Client's full name.",
                },
                "email": {
                    "type": "string",
                    "description": "Client's email address.",
                },
                "phone_number": {
                    "type": "string",
                    "description": "Client's phone number.",
                },
                "selected_time_slot": {
                    "type": "string",
                    "description": (
                        'Appointment slot in the format "YYYY-MM-DD, HH:MM - HH:MM".'
                    ),
                },
            },
            "required": ["name", "email", "phone_number", "selected_time_slot"],
        },
    },
}


def get_functions_meta(function_names: Iterable[str]):
    """
    Build a Pipecat ToolsSchema for the given function names.

    Args:
        function_names: Iterable of function name strings to expose.

    Returns:
        A ToolsSchema containing FunctionSchema objects for each valid name.
    """
    seen: set[str] = set()
    schemas: list[FunctionSchema] = []

    for name in function_names:
        if name in seen:
            continue
        preset = _FUNCTION_PRESETS.get(name)
        if not preset:
            continue  # ignore unknown names
        params = preset.get("parameters", {})
        properties = params.get("properties", {})
        required = params.get("required", [])
        schema = FunctionSchema(
            name=name,
            description=preset["description"],
            properties=properties,
            required=required,
        )
        schemas.append(schema)
        seen.add(name)

    return ToolsSchema(standard_tools=schemas)


def get_supported_function_names() -> List[str]:
    """
    Return a list of all function names that have preset metadata.

    Example:
        >>> get_supported_function_names()
        ['transfer_call', 'end_call', 'get_weekday', ...]
    """
    return list(_FUNCTION_PRESETS.keys())


def get_function_handlers(function_names: Iterable[str]) -> Dict[str, Callable]:
    """
    Return a mapping of function name → callable handler for every supported
    name in *function_names*. Unknown names are skipped.

    Example:
        >>> get_function_handlers(["transfer_call", "foo"])
        {'transfer_call': <coroutine function transfer_call at 0x...>}
    """
    return {
        name: _FUNCTION_HANDLERS[name]
        for name in function_names
        if name in _FUNCTION_HANDLERS
    }


def register_custom_tools(
    handlers: str | None = None,
    function_configurations: str | None = None,
) -> None:
    """
    Dynamically extend ``_FUNCTION_HANDLERS`` and ``_FUNCTION_PRESETS``
    with user-provided code and YAML metadata.

    Args:
        handlers: Absolute (or project-relative) path to a folder whose *.py
            files expose additional tool callables at module top-level.
            Every top-level callable whose name does **not** start with "_"
            is added to ``_FUNCTION_HANDLERS``. Collisions overwrite the
            built-in entry after logging a warning.

        function_configurations: Path to a YAML file that maps function
            names to the same ``{description, parameters}`` shape used by
            ``_FUNCTION_PRESETS``. Unknown keys are simply added; existing
            keys are overridden with a warning.
    """
    logger = logging.getLogger(__name__)

    # Load handlers from directory
    if handlers and os.path.isdir(handlers):
        for filename in os.listdir(handlers):
            if filename.startswith("_") or not filename.endswith(".py"):
                continue

            module_name = filename[:-3]
            file_path = os.path.join(handlers, filename)

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)  # type: ignore[arg-type]

            for name, attr in module.__dict__.items():
                if name.startswith("_") or not callable(attr):
                    continue
                if getattr(attr, "__module__", None) != module.__name__:
                    continue  # skip re-exports

                if name in _FUNCTION_HANDLERS:
                    logger.warning(
                        "Custom tool handler '%s' overrides existing definition.", name
                    )
                _FUNCTION_HANDLERS[name] = attr

    # Load configurations from YAML file
    if function_configurations and os.path.isfile(function_configurations):
        try:
            with open(function_configurations, "r", encoding="utf-8") as fh:
                presets: dict = yaml.safe_load(fh) or {}
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to parse YAML at %s: %s", function_configurations, exc)
            presets = {}

        if not isinstance(presets, dict):
            logger.error(
                "Function configuration YAML must be a mapping (got %s).", type(presets)
            )
            presets = {}

        for name, meta in presets.items():
            if not isinstance(meta, dict) or "description" not in meta or "parameters" not in meta:
                logger.warning("Skipping malformed preset for '%s' in YAML file.", name)
                continue

            if name in _FUNCTION_PRESETS:
                logger.warning(
                    "Custom function preset '%s' overrides existing metadata.", name
                )
            _FUNCTION_PRESETS[name] = meta

    # Validation: every preset needs an implementation
    missing = [name for name in _FUNCTION_PRESETS if name not in _FUNCTION_HANDLERS]
    if missing:
        raise ValueError(
            "Missing implementation(s) for function preset(s): "
            + ", ".join(sorted(missing))
        ) 