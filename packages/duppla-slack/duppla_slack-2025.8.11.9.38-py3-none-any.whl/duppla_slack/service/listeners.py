from typing import Callable
from duppla_slack.models import SlackResponse
from logging import getLogger

logger = getLogger(__name__)

class MessageListener:
    """A class to manage message listeners for the SlackService."""
    
    def __init__(self):
        self._listeners: list[Callable[[SlackResponse], None]] = []
    
    def add_listener(self, listener: Callable[[SlackResponse], None]) -> None:
        """Add a new listener function that will be called with the result of send_msg.
        
        Args:
            listener: A callable that takes a SlackResponse as argument
        """
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[SlackResponse], None]) -> None:
        """Remove a previously added listener.
        
        Args:
            listener: The listener function to remove
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def notify_listeners(self, response: SlackResponse) -> None:
        """Notify all registered listeners with the response.
        
        Args:
            response: The SlackResponse from send_msg
        """
        for listener in self._listeners:
            try:
                listener(response)
            except Exception as e:
                # Log error but don't stop other listeners
                logger.error(f"Error in message listener: {e}") 