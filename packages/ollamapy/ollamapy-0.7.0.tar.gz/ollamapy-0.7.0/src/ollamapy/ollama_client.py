"""Ollama API client for terminal chat interface."""

import json
import requests
from typing import Dict, List, Optional, Generator


class OllamaClient:
    """Client for interacting with local Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.
        
        Args:
            base_url: The base URL for the Ollama API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException:
            return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model if it's not available locally."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        print(f"\r{data['status']}", end='', flush=True)
                    if data.get('status') == 'success':
                        print()  # New line after completion
                        return True
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error pulling model: {e}")
            return False
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]], 
                   system: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat responses from Ollama.
        
        Args:
            model: The model to use for chat
            messages: List of message dicts with 'role' and 'content'
            system: Optional system message
            
        Yields:
            Response chunks as strings
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
                    if data.get('done', False):
                        break
                        
        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"