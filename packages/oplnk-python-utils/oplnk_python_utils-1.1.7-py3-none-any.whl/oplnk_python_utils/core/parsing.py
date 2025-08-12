"""
Parsing utilities - Functions for parsing and type conversion
"""

import re
from typing import List, Dict, Any, Union
from datetime import datetime
from .data import merge_dicts


def infer_type(value: Union[str, List, Any]) -> Any:
    """
    Infer the correct Python type from a string value.
    
    Args:
        value: The value to convert (string, list, or other)
        
    Returns:
        Value converted to appropriate Python type
    """
    if isinstance(value, list):
        return [infer_type(v) for v in value]

    if not isinstance(value, str):
        return value  # Skip non-string non-list

    # Now it's safe to do .lower()
    value_lower = value.lower()
    if value_lower in {"true", "false"}:
        return value_lower == "true"

    # Try to convert to int
    try:
        return int(value)
    except ValueError:
        pass

    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass

    # Try to convert to datetime
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        pass

    # If nothing works, return the original string
    return value


def parse_key_string_to_list(s: str) -> List[str]:
    """
    Parse a string like 'filters[name][$containsi]' into ['filters', 'name', '$containsi'].
    
    Args:
        s: String with bracketed notation
        
    Returns:
        List of parsed key components
    """
    parts = re.findall(r"\[([^\]]+)\]", s)
    parts.insert(0, s.split("[")[0])
    return parts


def parse_list_to_dict(lst: List[str], value: str) -> Dict[str, Any]:
    """
    Convert a list of keys and a value into a nested dictionary.
    
    Args:
        lst: List of keys for nested structure
        value: Value to place at the deepest level
        
    Returns:
        Nested dictionary structure
    """
    result = None
    new_value = infer_type(value)

    for key in reversed(lst):
        if key.isdigit():
            result = [new_value] if result is None else [result]
        else:
            result = {key: new_value} if result is None else {key: result}

    return result


def parse_params_to_dict(params: Union[Dict[str, str], Any]) -> Dict[str, Any]:
    """
    Parse query parameters into a structured dictionary.
    Handles nested parameters like filters[name][$containsi]=john
    
    Args:
        params: Query parameters (FastAPI QueryParams or dict-like object)
        
    Returns:
        Structured dictionary with nested parameters
    """
    # Handle FastAPI QueryParams or similar objects
    if hasattr(params, 'items'):
        param_dict = dict(params.items()) if hasattr(params, 'items') else dict(params)
    else:
        param_dict = params

    result = {}
    for key, value in param_dict.items():
        args = parse_key_string_to_list(key)
        dictionary = parse_list_to_dict(args, value)
        result = merge_dicts(result, dictionary)
    return result 