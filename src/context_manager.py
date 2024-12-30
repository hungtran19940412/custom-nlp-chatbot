import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class ContextManager:
    def __init__(self, context_ttl: int = 3600):
        """Initialize the context manager with a TTL for contexts."""
        self.contexts = {}
        self.context_ttl = context_ttl  # Time to live in seconds
        self.max_context_length = 10  # Maximum number of messages to keep in context

    def get_context(self, context_id: Optional[str] = None) -> Dict:
        """Retrieve context for a given context_id."""
        if not context_id or context_id not in self.contexts:
            return {}

        context = self.contexts[context_id]
        
        # Check if context has expired
        if self._is_context_expired(context):
            self._cleanup_context(context_id)
            return {}
            
        return context["data"]

    def update_context(
        self,
        context_id: Optional[str],
        user_message: str,
        bot_response: str
    ) -> str:
        """Update context with new message and response."""
        try:
            # Create new context if none exists
            if not context_id or context_id not in self.contexts:
                context_id = str(uuid.uuid4())
                self.contexts[context_id] = {
                    "created_at": datetime.now(),
                    "last_updated": datetime.now(),
                    "data": {
                        "messages": [],
                        "topic": None,
                        "user_intent": None
                    }
                }
            
            context = self.contexts[context_id]
            
            # Update context data
            messages = context["data"]["messages"]
            messages.append({
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only the last N messages
            if len(messages) > self.max_context_length:
                messages.pop(0)
            
            # Update context metadata
            context["last_updated"] = datetime.now()
            
            # Attempt to identify topic and user intent
            self._update_topic_and_intent(context["data"], user_message)
            
            return context_id
            
        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")
            raise

    def _is_context_expired(self, context: Dict) -> bool:
        """Check if context has expired based on TTL."""
        last_updated = context["last_updated"]
        time_elapsed = (datetime.now() - last_updated).total_seconds()
        return time_elapsed > self.context_ttl

    def _cleanup_context(self, context_id: str):
        """Remove expired context."""
        try:
            del self.contexts[context_id]
        except KeyError:
            pass

    def _update_topic_and_intent(self, context_data: Dict, user_message: str):
        """Update topic and user intent based on the message content."""
        # This is a simple implementation that could be enhanced with
        # more sophisticated NLP techniques
        
        # Example topic detection based on keywords
        topics = {
            "financial": ["stock", "price", "market", "invest", "trading"],
            "support": ["help", "issue", "problem", "error", "how to"]
        }
        
        message_lower = user_message.lower()
        
        # Simple topic detection
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                context_data["topic"] = topic
                break
        
        # Simple intent detection
        intents = {
            "question": ["what", "how", "why", "when", "where", "?"],
            "request": ["can you", "please", "could you"],
            "complaint": ["not working", "broken", "error", "issue"]
        }
        
        for intent, patterns in intents.items():
            if any(pattern in message_lower for pattern in patterns):
                context_data["user_intent"] = intent
                break

    def save_contexts(self, file_path: str):
        """Save all contexts to a file."""
        try:
            # Convert datetime objects to ISO format strings
            serializable_contexts = {}
            for context_id, context in self.contexts.items():
                serializable_contexts[context_id] = {
                    "created_at": context["created_at"].isoformat(),
                    "last_updated": context["last_updated"].isoformat(),
                    "data": context["data"]
                }
            
            with open(file_path, 'w') as f:
                json.dump(serializable_contexts, f)
                
            logger.info(f"Contexts saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving contexts: {str(e)}")
            raise

    def load_contexts(self, file_path: str):
        """Load contexts from a file."""
        try:
            with open(file_path, 'r') as f:
                saved_contexts = json.load(f)
            
            # Convert ISO format strings back to datetime objects
            for context_id, context in saved_contexts.items():
                self.contexts[context_id] = {
                    "created_at": datetime.fromisoformat(context["created_at"]),
                    "last_updated": datetime.fromisoformat(context["last_updated"]),
                    "data": context["data"]
                }
                
            logger.info(f"Contexts loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading contexts: {str(e)}")
            raise

    def cleanup_expired_contexts(self):
        """Remove all expired contexts."""
        expired_contexts = [
            context_id
            for context_id, context in self.contexts.items()
            if self._is_context_expired(context)
        ]
        
        for context_id in expired_contexts:
            self._cleanup_context(context_id)
            
        return len(expired_contexts)
