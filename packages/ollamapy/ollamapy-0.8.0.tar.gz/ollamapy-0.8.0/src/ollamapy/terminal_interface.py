"""Terminal-based chat interface for Ollama."""

import sys
from typing import List, Tuple, Dict, Any
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .chat_session import ChatSession
from .actions import get_available_actions, execute_action, get_action_logs, clear_action_logs


class TerminalInterface:
    """Terminal-based chat interface with AI meta-reasoning."""
    
    def __init__(self, model_manager: ModelManager, analysis_engine: AnalysisEngine, 
                 chat_session: ChatSession):
        """Initialize the terminal interface.
        
        Args:
            model_manager: The ModelManager instance
            analysis_engine: The AnalysisEngine instance
            chat_session: The ChatSession instance
        """
        self.model_manager = model_manager
        self.analysis_engine = analysis_engine
        self.chat_session = chat_session
        self.actions = get_available_actions()
        
    def setup(self) -> bool:
        """Setup the chat environment and ensure models are available."""
        print("🤖 OllamaPy Multi-Action Chat Interface")
        print("=" * 50)
        
        # Check if Ollama is running and ensure models are available
        success, main_status, analysis_status = self.model_manager.ensure_models_available(
            self.chat_session.model, 
            self.analysis_engine.analysis_model
        )
        
        if not success:
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        # Display model status
        self.model_manager.display_model_status(
            self.chat_session.model, 
            self.analysis_engine.analysis_model
        )
        
        print(f"\n🧠 Multi-action system: AI evaluates ALL {len(self.actions)} actions for every query")
        for action_name, action_info in self.actions.items():
            params = action_info.get('parameters', {})
            if params:
                param_list = ', '.join([f"{p}: {info['type']}" for p, info in params.items()])
                print(f"   • {action_name} ({param_list})")
            else:
                print(f"   • {action_name}")
        print("\n💬 Chat started! Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("   Type 'clear' to clear conversation history.")
        print("   Type 'help' for more commands.\n")
        
        return True
    
    def print_help(self):
        """Print help information."""
        print("\n📖 Available commands:")
        print("  quit, exit, bye  - End the conversation")
        print("  clear           - Clear conversation history")
        print("  help            - Show this help message")
        print("  model           - Show current models")
        print("  models          - List available models")
        print("  actions         - Show available actions the AI can choose")
        print(f"\n🧠 Multi-action: The AI evaluates ALL actions and can run multiple per query.")
        print()
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled and should exit."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Thanks for chatting!")
            return True
        
        elif command == 'clear':
            self.chat_session.clear_conversation()
            print("🧹 Conversation history cleared!")
            return False
        
        elif command == 'help':
            self.print_help()
            return False
        
        elif command == 'model':
            print(f"🎯 Chat model: {self.chat_session.model}")
            if self.analysis_engine.analysis_model != self.chat_session.model:
                print(f"🔍 Analysis model: {self.analysis_engine.analysis_model}")
            else:
                print("🔍 Using same model for analysis and chat")
            return False
        
        elif command == 'models':
            models = self.model_manager.list_available_models()
            if models:
                print(f"📚 Available models: {', '.join(models)}")
            else:
                print("❌ No models found")
            return False
        
        elif command == 'actions':
            print(f"🔧 Available actions ({len(self.actions)}):")
            for name, info in self.actions.items():
                params = info.get('parameters', {})
                if params:
                    param_list = ', '.join([f"{p}: {spec['type']}" for p, spec in params.items()])
                    print(f"   • {name}({param_list}): {info['description']}")
                else:
                    print(f"   • {name}: {info['description']}")
            return False
        
        return False
    
    def get_user_input(self) -> str:
        """Get user input with a nice prompt."""
        try:
            return input("👤 You: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            sys.exit(0)
    
    def execute_multiple_actions(self, actions_with_params: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Execute multiple actions and collect their log outputs.
        
        Args:
            actions_with_params: List of (action_name, parameters) tuples
            
        Returns:
            Combined log output from all actions
        """
        if not actions_with_params:
            return ""
        
        # Clear any previous logs
        # clear_action_logs()
        
        print(f"🚀 Executing {len(actions_with_params)} action(s)...")
        
        for action_name, parameters in actions_with_params:
            print(f"   Running {action_name}", end="")
            if parameters:
                print(f" with {parameters}", end="")
            print("...")
            
            # Execute the action (it will log internally)
            execute_action(action_name, parameters)
        
        # Get all the logs that were generated
        combined_logs = get_action_logs()
        
        if combined_logs:
            print(f"📝 Actions generated {len(combined_logs)} log entries")
        
        return "\n".join(combined_logs)
    
    def generate_ai_response_with_context(self, user_input: str, action_logs: str):
        """Generate AI response with action context from logs.
        
        Args:
            user_input: The original user input
            action_logs: The combined log output from all executed actions
        """
        # Show which model is being used for chat response
        chat_model_display = self.chat_session.model
        if self.analysis_engine.analysis_model != self.chat_session.model:
            print(f"🤖 Chat model ({chat_model_display}): ", end="", flush=True)
        else:
            print("🤖 AI: ", end="", flush=True)
        
        try:
            for chunk in self.chat_session.stream_response_with_context(user_input, action_logs):
                print(chunk, end="", flush=True)
            
            print()  # New line after response
            
        except Exception as e:
            print(f"\n❌ Error generating response: {e}")
    
    def chat_loop(self):
        """Main chat loop with multi-action execution."""
        while True:
            user_input = self.get_user_input()
            
            if not user_input:
                continue
            
            # Handle commands
            if self.handle_command(user_input):
                break
            
            # Select ALL applicable actions and extract their parameters
            selected_actions = self.analysis_engine.select_all_applicable_actions(user_input)
            
            # Execute all selected actions and collect logs
            action_logs = self.execute_multiple_actions(selected_actions)
            
            # Generate AI response with action context from logs
            self.generate_ai_response_with_context(user_input, action_logs)
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()