# zohencel_ai/chatbot/chat_manager.py

class SimpleChatbot:
    """A simple chatbot that responds with 'hi' to any user input."""

    def __init__(self):
        self.greeting = "hi"
    
    def respond(self, user_input: str) -> str:
        """
        Returns a generic greeting response to any input.

        Parameters:
            user_input (str): The user's input message.

        Returns:
            str: A greeting response.
        """
        return self.greeting
