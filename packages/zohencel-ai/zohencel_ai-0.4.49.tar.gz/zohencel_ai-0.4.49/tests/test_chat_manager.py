# tests/test_chat_manager.py

import unittest
from zohencel_ai.chatbot import SimpleChatbot

class TestSimpleChatbot(unittest.TestCase):
    def setUp(self):
        """Set up a SimpleChatbot instance for testing."""
        self.chatbot = SimpleChatbot()

    def test_respond(self):
        """Test if the chatbot responds with 'hi' to any input."""
        response = self.chatbot.respond("Hello there!")
        self.assertEqual(response, "hi", "The chatbot should respond with 'hi'.")

if __name__ == "__main__":
    unittest.main()
