"""
RemindMe! Chatbot Package
A reminder and event management chatbot with intent classification and NER.
"""

__version__ = "1.0.0"

from chatbot.chatbot import Chatbot
from chatbot.model_loader import ModelLoader

__all__ = ['Chatbot', 'ModelLoader']

