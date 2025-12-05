"""
Entry point for the RemindMe! Chatbot application.
"""

from chatbot.chatbot import Chatbot


def main():
    """Main entry point."""
    chatbot = Chatbot()
    chatbot.run()


if __name__ == "__main__":
    main()

