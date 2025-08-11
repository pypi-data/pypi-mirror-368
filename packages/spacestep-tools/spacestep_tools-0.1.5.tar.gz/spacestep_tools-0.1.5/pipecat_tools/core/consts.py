"""Utility helpers for registering and retrieving per‑function constants.

This module acts as a tiny in‑memory registry that lets other parts of the
codebase declare constants required by tool functions (e.g. web‑hook URLs)
and then populate them from JSON files at runtime.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Any


# top level: agent_id → (func_name → { const_name: value })
_AGENT_CONSTANTS: dict[str, dict[str, dict[str, Any]]] = {}

def get_required_constants(agent_id: str, function_names: Iterable[str]):
    """Return unresolved constants for the supplied functions.

    Args:
        agent_id:
        function_names: Iterable of function names to inspect.

    Returns:
        Dict[str, List[str]]: A mapping where each key is a function name
        and the value is a sorted list of constant names that are still
        unset (``None``).
    """
    result: Dict[str, List[str]] = {}
    agent_map = _AGENT_CONSTANTS.get(agent_id, {})
    for fn in function_names:
        consts = agent_map.get(fn)
        if consts is None:
            logging.warning("Unknown function name %s", fn)
            continue
        missing = [name for name, value in consts.items() if value is None]
        if missing:
            result[fn] = sorted(missing)
    return result

def get_all_set_constants(agent_id: str):
    """Return every constant that already has a value.

    Returns:
        Dict[str, Dict[str, object]]: Mapping of function names to a
        sub‑mapping of constant names and their current values.
    """
    result: Dict[str, Dict[str, object]] = {}
    agent_map = _AGENT_CONSTANTS.get(agent_id, {})
    for fn, consts in agent_map.items():
        set_consts = {k: v for k, v in consts.items() if v is not None}
        if set_consts:
            result[fn] = set_consts
    return result


def get_constant(agent_id: str, function_name: str, constant_name: str):
    """Fetch a single constant.

    Args:
        agent_id:
        function_name: Name of the function whose constant is requested.
        constant_name: The specific constant name to retrieve.

    Returns:
        object: The constant's value.

    Raises:
        KeyError: If the function or constant is not registered.
    """
    try:
        return _AGENT_CONSTANTS[agent_id][function_name][constant_name]
    except KeyError as exc:
        raise KeyError(
            f"Constant '{constant_name}' for function '{function_name}' is not registered."
        ) from exc

def set_constants(
        agent_id: str,
        tools: dict[str, dict[str, Any] | None],
) -> None:
    """
    Merge a `tools` dict into the constants for a specific agent.
    """
    if not isinstance(tools, dict):
        raise ValueError(f"Expected a dict for tools, got {type(tools).__name__}")

    # get or create this agent’s map
    agent_map = _AGENT_CONSTANTS.setdefault(agent_id, {})

    for func_name, consts in tools.items():
        # coerce `foo:` (None) → {} so empty sections still create keys
        if consts is None:
            consts = {}
        elif not isinstance(consts, dict):
            logging.warning(
                "Skipping %r for agent %r: expected dict or None, got %s",
                func_name, agent_id, type(consts).__name__
            )
            continue

        fn_map = agent_map.setdefault(func_name, {})
        for key, val in consts.items():
            if key in fn_map and fn_map[key] is not None:
                logging.warning(
                    "Overwriting constant %r for %r (agent %r)",
                    key, func_name, agent_id
                )
            fn_map[key] = val