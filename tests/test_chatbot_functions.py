"""
Unit tests for chatbot core functions
Note: These tests require models to be trained first
"""

import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock imports for testing without full model loading
try:
    import chatbot
    MODELS_AVAILABLE = True
except Exception:
    MODELS_AVAILABLE = False

class TestChatbotFunctions(unittest.TestCase):
    """Test cases for chatbot core functions."""
    
    @unittest.skipUnless(MODELS_AVAILABLE, "Models not available")
    def test_clean_up_sentence(self):
        """Test sentence cleaning."""
        result = chatbot.clean_up_sentence("Hello, world!")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
    
    @unittest.skipUnless(MODELS_AVAILABLE, "Models not available")
    def test_bag_of_words(self):
        """Test bag of words conversion."""
        if chatbot.words is None:
            self.skipTest("Words vocabulary not loaded")
        
        result = chatbot.bag_of_words("hello world")
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), len(chatbot.words))
    
    @unittest.skipUnless(MODELS_AVAILABLE, "Models not available")
    def test_predict_class_empty(self):
        """Test prediction with empty input."""
        result = chatbot.predict_class("")
        self.assertEqual(result, [])
    
    @unittest.skipUnless(MODELS_AVAILABLE, "Models not available")
    def test_extract_entities_empty(self):
        """Test entity extraction with empty input."""
        result = chatbot.extract_entities("")
        self.assertEqual(result, {})
    
    def test_get_response_fallback(self):
        """Test response generation with empty intent list."""
        # This should work even without models
        result = chatbot.get_response([], {'intents': []}, {})
        self.assertIn("didn't understand", result.lower())

if __name__ == '__main__':
    unittest.main()

