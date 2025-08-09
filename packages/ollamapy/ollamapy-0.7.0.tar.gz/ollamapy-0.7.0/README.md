# OllamaPy

A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities. OllamaPy provides an intuitive way to interact with local AI models while featuring unique "vibe tests" that evaluate AI decision-making consistency.

## Features

- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 🧠 **Meta-Reasoning** - AI analyzes user input and selects appropriate actions
- 🛠️ **Extensible Actions** - Easy-to-extend action system with parameter support
- 🧪 **AI Vibe Tests** - Built-in tests to evaluate AI consistency and reliability
- 🔢 **Parameter Extraction** - AI intelligently extracts parameters from natural language
- 🏗️ **Modular Architecture** - Clean separation of concerns for easy testing and extension

## Prerequisites

You need to have [Ollama](https://ollama.ai/) installed and running on your system.

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start the Ollama server
ollama serve
```

## Installation

Install from PyPI:

```bash
pip install ollamapy
```

Or install from source:

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install .
```

## Quick Start

Simply run the chat interface:

```bash
ollamapy
```

This will start a chat session with the default model (gemma3:4b). If the model isn't available locally, OllamaPy will automatically pull it for you.

## Usage Examples

### Basic Chat
```bash
# Start chat with default model
ollamapy
```

### Custom Model
```bash
# Use a specific model
ollamapy --model gemma2:2b
ollamapy -m codellama:7b
```

### Dual Model Setup (Analysis + Chat)
```bash
# Use a small, fast model for analysis and a larger model for chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
ollamapy -a gemma2:2b -m mistral:7b

# This is great for performance - small model does action selection, large model handles conversation
```

### System Message
```bash
# Set context for the AI
ollamapy --system "You are a helpful coding assistant specializing in Python"
ollamapy -s "You are a creative writing partner"
```

### Combined Options
```bash
# Use custom models with system message
ollamapy --analysis-model gemma2:2b --model mistral:7b --system "You are a helpful assistant"
```

## Meta-Reasoning System

OllamaPy features a unique meta-reasoning system where the AI analyzes user input and dynamically selects from available actions. The AI examines the intent behind your message and chooses the most appropriate response action.

### Dual Model Architecture

For optimal performance, you can use two different models:
- **Analysis Model**: A smaller, faster model (like `gemma2:2b`) for quick action selection
- **Chat Model**: A larger, more capable model (like `llama3.2:7b`) for generating responses

This architecture provides the best of both worlds - fast decision-making and high-quality responses.

```bash
# Example: Fast analysis with powerful chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
```

### Currently Available Actions

- **null** - Default conversation mode. Used for normal chat when no special action is needed
- **getWeather** - Provides weather information (accepts optional location parameter)
- **getTime** - Returns the current date and time (accepts optional timezone parameter)
- **square_root** - Calculates the square root of a number (requires number parameter)
- **calculate** - Evaluates basic mathematical expressions (requires expression parameter)

### How Meta-Reasoning Works

When you send a message, the AI:
1. **Analyzes** your input to understand intent
2. **Selects** the most appropriate action(s) from all available actions
3. **Extracts** any required parameters from your input
4. **Executes** the chosen action(s) with parameters
5. **Responds** using the action's output as context

## Creating Custom Actions

The action system is designed to be easily extensible. Here's a comprehensive guide on creating your own actions:

### Basic Action Structure

```python
from ollamapy.actions import register_action

@register_action(
    name="action_name",
    description="When to use this action",
    vibe_test_phrases=["test phrase 1", "test phrase 2"],  # Optional
    parameters={  # Optional
        "param_name": {
            "type": "string|number",
            "description": "What this parameter is for",
            "required": True|False
        }
    }
)
def action_name(param_name=None):
    """Your action implementation."""
    from ollamapy.actions import log
    
    # Log results so the AI can use them as context
    log(f"[Action] Result: {some_result}")
    # Actions communicate via logging, not return values
```

### Example 1: Simple Action (No Parameters)

```python
from ollamapy.actions import register_action, log

@register_action(
    name="joke",
    description="Use when the user wants to hear a joke or needs cheering up",
    vibe_test_phrases=[
        "tell me a joke",
        "I need a laugh",
        "cheer me up",
        "make me smile"
    ]
)
def joke():
    """Tell a random joke."""
    import random
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!"
    ]
    selected_joke = random.choice(jokes)
    log(f"[Joke] {selected_joke}")
```

### Example 2: Action with Required Parameter

```python
@register_action(
    name="convert_temp",
    description="Convert temperature between Celsius and Fahrenheit",
    vibe_test_phrases=[
        "convert 32 fahrenheit to celsius",
        "what's 100C in fahrenheit?",
        "20 degrees celsius in F"
    ],
    parameters={
        "value": {
            "type": "number",
            "description": "The temperature value to convert",
            "required": True
        },
        "unit": {
            "type": "string",
            "description": "The unit to convert from (C or F)",
            "required": True
        }
    }
)
def convert_temp(value, unit):
    """Convert temperature between units."""
    unit = unit.upper()
    if unit == 'C':
        # Celsius to Fahrenheit
        result = (value * 9/5) + 32
        log(f"[Temperature] {value}°C = {result:.1f}°F")
    elif unit == 'F':
        # Fahrenheit to Celsius
        result = (value - 32) * 5/9
        log(f"[Temperature] {value}°F = {result:.1f}°C")
    else:
        log(f"[Temperature] Error: Unknown unit '{unit}'. Use 'C' or 'F'.")
```

### Adding Your Actions to OllamaPy

1. Create a new Python file for your actions (e.g., `my_actions.py`)
2. Import and implement your actions using the patterns above
3. Import your actions module before starting OllamaPy

```python
# my_script.py
from ollamapy import chat
import my_actions  # This registers your actions

# Now start chat with your custom actions available
chat()
```

## Vibe Tests

Vibe tests are a built-in feature that evaluates how consistently AI models interpret human intent and choose appropriate actions. These tests help you understand model behavior and compare performance across different models.

### Running Vibe Tests

```bash
# Run vibe tests with default settings
ollamapy --vibetest

# Run with multiple iterations for statistical confidence
ollamapy --vibetest -n 5

# Test a specific model
ollamapy --vibetest --model gemma2:2b -n 3

# Use dual models for testing (analysis + chat)
ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b -n 5
```

### Understanding Results

Vibe tests evaluate:
- **Action Selection**: How reliably the AI chooses the correct action
- **Parameter Extraction**: How accurately the AI extracts required parameters
- **Consistency**: How stable the AI's decisions are across multiple runs

Tests pass with a 60% or higher success rate, ensuring reasonable consistency in decision-making.

## Chat Commands

While chatting, you can use these built-in commands:

- `quit`, `exit`, `bye` - End the conversation
- `clear` - Clear conversation history
- `help` - Show available commands
- `model` - Display current models (both chat and analysis)
- `models` - List all available models
- `actions` - Show available actions the AI can choose from

## Python API

You can also use OllamaPy programmatically:

```python
from ollamapy import OllamaClient, ModelManager, AnalysisEngine, ChatSession, TerminalInterface

# Create components
client = OllamaClient()
model_manager = ModelManager(client)
analysis_engine = AnalysisEngine("gemma2:2b", client)  # Fast analysis model
chat_session = ChatSession("llama3.2:7b", client, "You are a helpful assistant")

# Start a terminal interface
terminal = TerminalInterface(model_manager, analysis_engine, chat_session)
terminal.run()

# Or use components directly
messages = [{"role": "user", "content": "Hello!"}]
for chunk in client.chat_stream("gemma3:4b", messages):
    print(chunk, end="", flush=True)

# Execute actions programmatically
from ollamapy import execute_action
execute_action("square_root", {"number": 16})

# Run vibe tests programmatically
from ollamapy import run_vibe_tests
success = run_vibe_tests(
    model="llama3.2:7b", 
    analysis_model="gemma2:2b", 
    iterations=5
)
```

### Available Classes and Functions

#### Core Components:
- **`OllamaClient`** - Low-level API client for Ollama
- **`ModelManager`** - Model availability, pulling, and validation
- **`AnalysisEngine`** - AI decision-making and action selection  
- **`ChatSession`** - Conversation state and response generation
- **`TerminalInterface`** - Terminal UI and user interaction

#### Action System:
- **`register_action()`** - Decorator for creating new actions
- **`execute_action()`** - Execute an action with parameters
- **`get_available_actions()`** - Get all registered actions
- **`log()`** - Log messages from within actions

#### Testing:
- **`VibeTestRunner`** - Advanced vibe test runner with configuration
- **`run_vibe_tests()`** - Simple function to run vibe tests

#### Utilities:
- **`convert_parameter_value()`** - Convert parameter types
- **`extract_numbers_from_text()`** - Extract numbers from text
- **`prepare_function_parameters()`** - Prepare parameters for function calls

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

- `gemma3:4b` (default) - Fast and capable general-purpose model
- `llama3.2:3b` - Efficient and responsive for most tasks
- `gemma2:2b` - Lightweight model, great for analysis tasks
- `gemma2:9b` - Larger Gemma model for complex tasks
- `codellama:7b` - Specialized for coding tasks
- `mistral:7b` - Strong general-purpose model

To see available models on your system: `ollama list`

## Development

Clone the repository and install in development mode:

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run vibe tests:

```bash
pytest -m vibetest
```

### Architecture Overview

OllamaPy uses a clean, modular architecture:

```
┌───────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ TerminalInterface │    │  AnalysisEngine │    │   ChatSession   │
│                   │    │                 │    │                 │
│ • User input      │    │ • Action select │    │ • Conversation  │
│ • Commands        │    │ • Parameter     │    │ • Response gen  │
│ • Display         │    │   extraction    │    │ • History       │
└───────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                       │                       │
         └─────────────────────────────┼───────────────────────────┘
                                 │
                    ┌───────────────────┐    ┌─────────────────┐
                    │  ModelManager  │    │ OllamaClient │
                    │                │    │              │
                    │ • Model pull   │    │ • HTTP API   │
                    │ • Availability │    │ • Streaming  │
                    │ • Validation   │    │ • Low-level  │
                    └───────────────────┘    └─────────────────┘
```

Each component has a single responsibility and can be tested independently.

## Troubleshooting

### "Ollama server is not running!"
Make sure Ollama is installed and running:
```bash
ollama serve
```

### Model not found
OllamaPy will automatically pull models, but you can also pull manually:
```bash
ollama pull gemma3:4b
```

### Parameter extraction issues
- Use a more capable analysis model: `ollamapy --analysis-model llama3.2:3b`
- Ensure your action descriptions clearly indicate what parameters are needed
- Check that your test phrases include the expected parameters

### Vibe test failures
- Try different models: `ollamapy --vibetest --model gemma2:9b`
- Use separate analysis model: `ollamapy --vibetest --analysis-model gemma2:2b`
- Increase iterations for better statistics: `ollamapy --vibetest -n 10`
- Check that your test phrases clearly indicate the intended action

### Performance issues
- Use a smaller model for analysis: `--analysis-model gemma2:2b`
- Ensure sufficient system resources for your chosen models
- Check Ollama server performance with `ollama ps`

## Project Information

- **Version**: 0.7.0
- **License**: GPL-3.0-or-later
- **Author**: The Lazy Artist
- **Python**: >=3.8
- **Dependencies**: requests>=2.25.0

## Links

- [PyPI Package](https://pypi.org/project/ollamapy/)
- [GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)
- [Issues](https://github.com/ScienceIsVeryCool/OllamaPy/issues)
- [Ollama Documentation](https://ollama.ai/)

## License

This project is licensed under the GPL-3.0-or-later license. See the LICENSE file for details.