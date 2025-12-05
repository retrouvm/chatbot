"""
Backward-compatible entry point for RemindMe! Chatbot.
This file maintains compatibility with the old structure while using the new modular architecture.
"""

from chatbot.main import main

if __name__ == "__main__":
    main()
