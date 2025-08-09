"""Model management utilities for Ollama operations."""

from typing import List, Tuple
from .ollama_client import OllamaClient


class ModelManager:
    """Handles model availability checking, pulling, and validation."""
    
    def __init__(self, client: OllamaClient):
        """Initialize the model manager.
        
        Args:
            client: The OllamaClient instance to use
        """
        self.client = client
    
    def is_server_available(self) -> bool:
        """Check if Ollama server is running and accessible."""
        return self.client.is_available()
    
    def list_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.client.list_models()
    
    def pull_model_if_needed(self, model: str) -> bool:
        """Pull a model if it's not available locally.
        
        Args:
            model: The model name to pull
            
        Returns:
            True if model is available or was successfully pulled, False otherwise
        """
        available_models = self.list_available_models()
        model_available = any(model in available_model for available_model in available_models)
        
        if not model_available:
            print(f"📥 Model '{model}' not found locally. Pulling...")
            if not self.client.pull_model(model):
                print(f"❌ Failed to pull model '{model}'")
                return False
        
        return True
    
    def ensure_models_available(self, main_model: str, analysis_model: str = None) -> Tuple[bool, str, str]:
        """Ensure required models are available, pulling them if necessary.
        
        Args:
            main_model: The main chat model to ensure is available
            analysis_model: Optional separate analysis model (defaults to main_model)
            
        Returns:
            Tuple of (success, main_model_status, analysis_model_status)
        """
        # Use main model for analysis if no separate model specified
        if analysis_model is None:
            analysis_model = main_model
        
        # Check if Ollama is running
        if not self.is_server_available():
            return False, "Server not available", "Server not available"
        
        print("✅ Connected to Ollama server")
        
        # Check main model
        if not self.pull_model_if_needed(main_model):
            return False, "Failed to pull", "Not checked"
        
        # Check analysis model (if different from main model)
        if analysis_model != main_model:
            if not self.pull_model_if_needed(analysis_model):
                return False, "Available", "Failed to pull"
        
        return True, "Available", "Available"
    
    def display_model_status(self, main_model: str, analysis_model: str = None):
        """Display current model configuration.
        
        Args:
            main_model: The main chat model
            analysis_model: Optional separate analysis model
        """
        print(f"🎯 Using chat model: {main_model}")
        if analysis_model and analysis_model != main_model:
            print(f"🔍 Using analysis model: {analysis_model}")
        else:
            print(f"🔍 Using same model for analysis and chat")
        
        available_models = self.list_available_models()
        if available_models:
            print(f"📚 Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")