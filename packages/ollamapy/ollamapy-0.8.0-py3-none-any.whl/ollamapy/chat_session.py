"""Chat session management for conversation state and response generation."""

from typing import List, Dict
from .ollama_client import OllamaClient


class ChatSession:
    """Manages conversation state and AI response generation."""
    
    def __init__(self, model: str, client: OllamaClient, system_message: str):
        """Initialize the chat session.
        
        Args:
            model: The model to use for chat responses
            client: The OllamaClient instance
            system_message: The system message to set context
        """
        self.model = model
        self.client = client
        self.system_message = system_message if system_message else "You are a straight forward and powerful assistant. You are basically a Janet from the Good Place but just a tad sassy to stay engaging. Make sure the user"
        self.conversation: List[Dict[str, str]] = []
    
    def add_user_message(self, message: str):
        """Add a user message to the conversation history.
        
        Args:
            message: The user's message
        """
        self.conversation.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str):
        """Add an assistant message to the conversation history.
        
        Args:
            message: The assistant's message
        """
        self.conversation.append({"role": "assistant", "content": message})
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation.clear_conversation()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation.copy()
    
    def generate_response_with_context(self, user_input: str, action_logs: str = None) -> str:
        """Generate AI response with optional action context from logs.
        
        Args:
            user_input: The original user input
            action_logs: Optional combined log output from executed actions
            
        Returns:
            The generated response content
        """
        # Add user message to conversation
        self.add_user_message(user_input)
        
        # Build the AI's context message
        if action_logs:
            # Actions produced logs - include them as context
            context_message = f"""<context>
The following information was gathered from various tools and actions:

{action_logs}

Use this information to provide a comprehensive and accurate response to the user.
</context>"""
        else:
            # No actions executed - just normal chat
            context_message = None
        
        # Prepare messages for the AI
        messages_for_ai = self.conversation.copy()
        
        # If we have action context, add it as a system-like message
        if context_message:
            messages_for_ai.append({"role": "system", "content": context_message})
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,
                messages=messages_for_ai,
                system=self.system_message
            ):
                response_content += chunk
            
            # Add AI response to conversation (without the action context)
            self.add_assistant_message(response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"\n❌ {error_msg}")
            return error_msg
    
    def stream_response_with_context(self, user_input: str, action_logs: str = None):
        """Stream AI response with optional action context, yielding chunks.
        
        Args:
            user_input: The original user input
            action_logs: Optional combined log output from executed actions
            
        Yields:
            Response chunks as they arrive
        """
        # Add user message to conversation
        self.add_user_message(user_input)
        
        # Build the AI's context message
        if action_logs:
            # Actions produced logs - include them as context
            context_message = f"""<context>
Snap judgements made by a reasoning model has led to multiple responses to get triggered automatically. The logs to all of the actions that were executed are below. Please keep in mind the user's intent and understand that some of these responses that get triggered may in fact not be helpful to crafting the response to the user. Here are the complete logs of the last snap judgement's response logs:
\n
{action_logs}
\n
If this information is useful to the user's request then use this information to help you. If there is information that is not helpful to the user's request then ignore it completely and do not remark on it. This is only possibly helpful context.\nThis is likely the last thing before responding to the user you will get. Respond to the user now, and apologies for repeat instructions. Do not respond to this context, respond to the oringinal user input: {user_input}.
</context>"""
        else:
            # No actions executed - just normal chat
            context_message = None
        
        # Prepare messages for the AI
        messages_for_ai = self.conversation.copy()
        
        # If we have action context, add it as a system-like message
        if context_message:
            messages_for_ai.append({"role": "system", "content": context_message})
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,
                messages=messages_for_ai,
                system=self.system_message
            ):
                response_content += chunk
                yield chunk
            
            # Add AI response to conversation (without the action context)
            self.add_assistant_message(response_content)
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"\n❌ {error_msg}")
            yield error_msg