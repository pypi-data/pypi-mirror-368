"""Shared utilities for parameter handling and conversion."""

import re
from typing import Any, Dict, Union


def convert_parameter_value(value: Any, param_type: str) -> Any:
    """Convert a parameter value to the expected type.
    
    Args:
        value: The value to convert
        param_type: The expected type ('number' or 'string')
        
    Returns:
        The converted value, or the original value if conversion fails
    """
    if param_type == 'number' and value is not None:
        try:
            # Try to convert to number
            if isinstance(value, str):
                # Remove any whitespace
                value = value.strip()
                # Handle both int and float
                value = float(value)
                # Convert to int if it's a whole number
                if value.is_integer():
                    value = int(value)
        except (ValueError, AttributeError):
            # Return None to indicate conversion failure
            return None
    
    return value


def validate_required_parameters(parameters: Dict[str, Any], expected_params: Dict[str, Dict[str, Any]]) -> bool:
    """Validate that all required parameters are present.
    
    Args:
        parameters: The actual parameters provided
        expected_params: The expected parameter specifications
        
    Returns:
        True if all required parameters are present, False otherwise
    """
    for param_name, param_spec in expected_params.items():
        if param_spec.get('required', False) and param_name not in parameters:
            return False
    return True


def extract_numbers_from_text(text: str) -> list:
    """Extract numbers from text using regex.
    
    Args:
        text: The text to extract numbers from
        
    Returns:
        List of numbers found in the text
    """
    numbers = re.findall(r'-?\d+\.?\d*', text)
    result = []
    for num_str in numbers:
        try:
            value = float(num_str)
            result.append(int(value) if value.is_integer() else value)
        except ValueError:
            continue
    return result


def extract_expressions_from_text(text: str) -> list:
    """Extract mathematical expressions from text.
    
    Args:
        text: The text to extract expressions from
        
    Returns:
        List of mathematical expressions found
    """
    # Simple pattern for basic arithmetic
    expressions = re.findall(r'(\d+\s*[+\-*/]\s*\d+)', text)
    return [expr.replace(' ', '') for expr in expressions]


def prepare_function_parameters(parameters: Dict[str, Any], expected_params: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Prepare parameters for function call by converting types and validating.
    
    Args:
        parameters: The raw parameters
        expected_params: The expected parameter specifications
        
    Returns:
        Dictionary of prepared parameters ready for function call
    """
    call_params = {}
    
    for param_name, param_spec in expected_params.items():
        if param_name in parameters:
            value = parameters[param_name]
            
            # Type conversion
            converted_value = convert_parameter_value(value, param_spec['type'])
            if converted_value is None and param_spec['type'] == 'number':
                # Conversion failed for required number
                raise ValueError(f"Parameter '{param_name}' must be a number, got '{value}'")
            
            call_params[param_name] = converted_value
        elif param_spec.get('required', False):
            raise ValueError(f"Required parameter '{param_name}' not provided")
    
    return call_params


def extract_parameter_from_response(response_content: str, param_type: str) -> Any:
    """Extract parameter value from AI response content.
    
    Args:
        response_content: The cleaned response from AI
        param_type: The expected parameter type
        
    Returns:
        The extracted parameter value, or None if not found
    """
    # Check if not found
    if 'NOT_FOUND' in response_content.upper() or not response_content:
        return None
    
    # Process based on type
    if param_type == 'number':
        # Try to extract a number from the response
        # First try to convert the whole response
        try:
            value = float(response_content)
            return int(value) if value.is_integer() else value
        except:
            # Try to find a number in the response
            numbers = extract_numbers_from_text(response_content)
            if numbers:
                return numbers[0]
            return None
    else:
        # For string type, return the cleaned response
        return response_content