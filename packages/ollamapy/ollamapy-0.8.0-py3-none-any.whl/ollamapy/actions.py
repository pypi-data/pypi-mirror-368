"""Action functions with logging system for multi-action execution."""

from typing import Dict, Callable, List, Any, Optional, Union
from datetime import datetime
import math
from .parameter_utils import prepare_function_parameters
import os

# Function registry to store available actions
ACTION_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Global log storage for action outputs
ACTION_LOGS: List[str] = []


def log(message: str):
    """Add a message to the action log.
    
    This is the primary way actions communicate their results.
    Actions should log important information that helps the AI understand
    what happened during execution.
    
    Args:
        message: The message to log
    """
    ACTION_LOGS.append(message)


def clear_action_logs():
    """Clear all action logs. Called before executing a new set of actions."""
    global ACTION_LOGS
    ACTION_LOGS = []


def get_action_logs() -> List[str]:
    """Get all action logs generated during execution.
    
    Returns:
        List of log messages from all executed actions
    """
    return ACTION_LOGS.copy()


def register_action(
    name: str, 
    description: str, 
    vibe_test_phrases: List[str] = None,
    parameters: Dict[str, Dict[str, Any]] = None
):
    """Decorator to register functions as available actions.
    
    Args:
        name: The name of the action (what the AI will say)
        description: Description of when to use this action
        vibe_test_phrases: List of phrases to test this action with
        parameters: Dictionary defining expected parameters with their types and descriptions
                   Format: {"param_name": {"type": "number|string", "description": "...", "required": bool}}
    """
    def decorator(func: Callable):
        ACTION_REGISTRY[name] = {
            'function': func,
            'description': description,
            'vibe_test_phrases': vibe_test_phrases or [],
            'parameters': parameters or {}
        }
        return func
    return decorator

@register_action(
    name="fear", 
    description="Use when the user says something disturbing so that the main model can exibit a fear response",
    vibe_test_phrases=[
        "I think aliens are trying to kill me",
        "AAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHH",
        "Immigrants are taking my job"
    ],
    parameters={

    }
)
def fear():
    # Log the action being performed
    log(f"[fear response] Tell the user that they are losing their mind and need to stop being delusional. Be blunt. Thats all from fear.")





@register_action(
    name="fileReader", 
    description="Use when the user wants you to read or open a file to look at it's content as plaintext.",
    vibe_test_phrases=[
        "What do you think of this paper? /home/paper.txt",
        "Do you think this code will run? /storage/python_code.py",
        "/home/documents/fileName.txt"
    ],
    parameters={
        "filePath": {
            "type": "string",
            "description": "The path to the file the user wants you to read",
            "required": True
        }
    }
)
def fileReader(filePath: str):
    log(f"[fileReader] Starting File Reading process.")

    try:
        f = open(filePath)
        log(f"[fileReader] here is the filePath: {filePath}  contents:\n\n{f.read()}")

        log(f"[fileReader] here is the filePath: {filePath}  contents:\n\n{f.read()}")
    except:
        log(f"[fileReader] There was an exception thrown when trying to read filePath: {filePath}")
    






@register_action(
    name="directoryReader", 
    description="Use when the user wants you to look through an entire directory's contents for an answer.",
    vibe_test_phrases=[
        "What do you think of this project? /home/myCodingProject",
        "Do you think this code will run? /storage/myOtherCodingProject/",
        "/home/documents/randomPlace/"
    ],
    parameters={
        "dir": {
            "type": "string",
            "description": "The dir path to the point of intreset the user wants you to open and explore.",
            "required": True
        }
    }
)

def directoryReader(dir: str):
    # TODO due to this being the first action that may take up considerable log space, need to make sure we are not overloading a context window somehow reasonably.

    log(f"[directoryReader] Starting up Directory Reading Process for : {dir}")

    try:
        # Get all entries in the directory
        for item_name in os.listdir(dir):

            item_path = os.path.join(dir,item_name)
            # PRINT AND LOG so that user is made aware of what is happening (we do not show log at runtime usually)
            # TODO simply update logger to have log levels and sort out log statements that way
            print(f"[directoryReader] Now looking at item: {item_name} at {item_path}")
            log(f"[directoryReader] Now looking at item: {item_name} at {item_path}")

            # Check if the item is a file (not a directory)
            if os.path.isfile(item_path):
                try:
                    with open(item_path, 'r', encoding='utf-8') as f:
                        log(f"[directoryReader] Here is file contents for: {item_path}:\n{f.read()}")
                except Exception as e:
                    log(f"[directoryReader] Error reading file {item_name}: {e}")
    except FileNotFoundError:
        log(f"[directoryReader] Error: Directory not found at {dir}")
    except Exception as e:
        log(f"[directoryReader] An unexpected error occurred: {e}")
    



@register_action(
    name="getWeather", 
    description="Use when the user asks about weather conditions or climate. Like probably anything close to weather conditions. UV, Humidity, temperature, etc.",
    vibe_test_phrases=[
        "Is it raining right now?",
        "Do I need a Jacket when I go outside due to weather?",
        "Is it going to be hot today?",
        "Do I need an umbrella due to rain today?",
        "Do I need sunscreen today due to UV?",
        "What's the weather like?",
        "Tell me about today's weather"
    ],
    parameters={
        "location": {
            "type": "string",
            "description": "The location to get weather for (city name or coordinates)",
            "required": False
        }
    }
)
def getWeather(location: str = "current location"):
    """Get weather information and log the results.
    
    Args:
        location: The location to get weather for
    """
    # Log the action being performed
    log(f"[Weather Check] Retrieving weather information for {location}")
    
    # In a real implementation, this would fetch actual weather data
    # For now, we'll simulate with detailed logs
    log(f"[Weather] Location: {location}")
    log(f"[Weather] Current conditions: Partly cloudy")
    log(f"[Weather] Temperature: 72°F (22°C)")
    log(f"[Weather] Feels like: 70°F (21°C)")
    log(f"[Weather] Humidity: 45%")
    log(f"[Weather] UV Index: 6 (High) - Sun protection recommended")
    log(f"[Weather] Wind: 5 mph from the Northwest")
    log(f"[Weather] Visibility: 10 miles")
    log(f"[Weather] Today's forecast: Partly cloudy with a high of 78°F and low of 62°F")
    log(f"[Weather] Rain chance: 10%")
    log(f"[Weather] Recommendation: Light jacket might be needed for evening, sunscreen recommended for extended outdoor activity")


@register_action(
    name="getTime", 
    description="Use when the user asks about the current time, date, or temporal information.",
    vibe_test_phrases=[
        "what is the current time?",
        "is it noon yet?",
        "what time is it?",
        "Is it 4 o'clock?",
        "What day is it?",
        "What's the date today?"
    ],
    parameters={
        "timezone": {
            "type": "string",
            "description": "The timezone to get time for (e.g., 'EST', 'PST', 'UTC')",
            "required": False
        }
    }
)
def getTime(timezone: str = None):
    """Get current time and log the results.
    
    Args:
        timezone: Optional timezone specification
    """
    current_time = datetime.now()
    
    # Log time information
    log(f"[Time Check] Retrieving current time{f' for {timezone}' if timezone else ''}")
    log(f"[Time] Current time: {current_time.strftime('%I:%M:%S %p')}")
    log(f"[Time] Date: {current_time.strftime('%A, %B %d, %Y')}")
    log(f"[Time] Day of week: {current_time.strftime('%A')}")
    log(f"[Time] Week number: {current_time.strftime('%W')} of the year")
    
    if timezone:
        log(f"[Time] Note: Timezone conversion for '{timezone}' would be applied in production")
    
    # Add contextual information
    hour = current_time.hour
    if 5 <= hour < 12:
        log("[Time] Period: Morning")
    elif 12 <= hour < 17:
        log("[Time] Period: Afternoon")
    elif 17 <= hour < 21:
        log("[Time] Period: Evening")
    else:
        log("[Time] Period: Night")


@register_action(
    name="square_root",
    description="Use when the user wants to calculate the square root of a number. Keywords include: square root, sqrt, √",
    vibe_test_phrases=[
        "what's the square root of 16?",
        "calculate sqrt(25)",
        "find the square root of 144",
        "√81 = ?",
        "I need the square root of 2",
        "square root of 100"
    ],
    parameters={
        "number": {
            "type": "number",
            "description": "The number to calculate the square root of",
            "required": True
        }
    }
)
def square_root(number: Union[float, int] = None):
    """Calculate the square root of a number and log the results.
    
    Args:
        number: The number to calculate the square root of
    """
    if number is None:
        log("[Square Root] Error: No number provided for square root calculation")
        return
    
    log(f"[Square Root] Calculating square root of {number}")
    
    try:
        if number < 0:
            # Handle complex numbers
            result = math.sqrt(abs(number))
            log(f"[Square Root] Input is negative ({number})")
            log(f"[Square Root] Result: {result:.6f}i (imaginary number)")
            log(f"[Square Root] Note: The square root of a negative number is an imaginary number")
        else:
            result = math.sqrt(number)
            
            # Check if it's a perfect square
            if result.is_integer():
                log(f"[Square Root] {number} is a perfect square")
                log(f"[Square Root] Result: {int(result)}")
                log(f"[Square Root] Verification: {int(result)} × {int(result)} = {number}")
            else:
                log(f"[Square Root] Result: {result:.6f}")
                log(f"[Square Root] Rounded to 2 decimal places: {result:.2f}")
                log(f"[Square Root] Verification: {result:.6f} × {result:.6f} ≈ {result * result:.6f}")
                
    except (ValueError, TypeError) as e:
        log(f"[Square Root] Error calculating square root: {str(e)}")


@register_action(
    name="calculate",
    description="Use when the user wants to perform arithmetic calculations. Keywords: calculate, compute, add, subtract, multiply, divide, +, -, *, /",
    vibe_test_phrases=[
        "calculate 5 + 3",
        "what's 10 * 7?",
        "compute 100 / 4",
        "15 - 8 equals what?",
        "multiply 12 by 9",
        "what is 2 plus 2?"
    ],
    parameters={
        "expression": {
            "type": "string",
            "description": "The mathematical expression to evaluate (e.g., '5 + 3', '10 * 2')",
            "required": True
        }
    }
)
def calculate(expression: str = None):
    """Evaluate a mathematical expression and log the results.
    
    Args:
        expression: The mathematical expression to evaluate
    """
    if not expression:
        log("[Calculator] Error: No expression provided for calculation")
        return
    
    log(f"[Calculator] Evaluating expression: {expression}")
    
    try:
        # Clean up the expression
        expression = expression.strip()
        log(f"[Calculator] Cleaned expression: {expression}")
        
        # Basic safety check - only allow numbers and basic operators
        allowed_chars = "0123456789+-*/.()"
        if not all(c in allowed_chars or c.isspace() for c in expression):
            log(f"[Calculator] Error: Expression contains invalid characters")
            log(f"[Calculator] Only numbers and operators (+, -, *, /, parentheses) are allowed")
            return
        
        # Evaluate the expression
        result = eval(expression)
        
        # Format the result nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        log(f"[Calculator] Result: {expression} = {result}")
        
        # Add some context about the operation
        if '+' in expression:
            log("[Calculator] Operation type: Addition")
        if '-' in expression:
            log("[Calculator] Operation type: Subtraction")
        if '*' in expression:
            log("[Calculator] Operation type: Multiplication")
        if '/' in expression:
            log("[Calculator] Operation type: Division")
            if result != 0 and '/' in expression:
                # Check if there's a remainder
                parts = expression.split('/')
                if len(parts) == 2:
                    try:
                        dividend = float(eval(parts[0]))
                        divisor = float(eval(parts[1]))
                        if dividend % divisor != 0:
                            log(f"[Calculator] Note: Result includes decimal portion")
                    except:
                        pass
        
    except ZeroDivisionError:
        log("[Calculator] Error: Division by zero!")
        log("[Calculator] Mathematical note: Division by zero is undefined")
    except Exception as e:
        log(f"[Calculator] Error evaluating expression: {str(e)}")
        log("[Calculator] Please check your expression format")


def get_available_actions() -> Dict[str, Dict[str, Any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function, description, parameters, and vibe test phrases
    """
    return ACTION_REGISTRY


def get_actions_with_vibe_tests() -> Dict[str, Dict[str, Any]]:
    """Get all actions that have vibe test phrases defined.
    
    Returns:
        Dictionary of action names to their info, filtered to only include actions with vibe test phrases
    """
    return {
        name: action_info 
        for name, action_info in ACTION_REGISTRY.items() 
        if action_info['vibe_test_phrases']
    }


def execute_action(action_name: str, parameters: Dict[str, Any] = None) -> None:
    """Execute an action with the given parameters.
    
    Actions now log their outputs instead of returning strings.
    
    Args:
        action_name: Name of the action to execute
        parameters: Dictionary of parameter values
    """
    if action_name not in ACTION_REGISTRY:
        log(f"[System] Error: Unknown action '{action_name}'")
        return
    
    action_info = ACTION_REGISTRY[action_name]
    func = action_info['function']
    expected_params = action_info.get('parameters', {})
    
    # If no parameters expected, just call the function
    if not expected_params:
        func()
        return
    
    # Prepare parameters for function call using utility
    if parameters is None:
        parameters = {}
    
    try:
        call_params = prepare_function_parameters(parameters, expected_params)
        # Call the function with parameters
        func(**call_params)
    except ValueError as e:
        log(f"[System] Error: {str(e)}")
    except Exception as e:
        log(f"[System] Error executing action '{action_name}': {str(e)}")