"""
Text preprocessing utilities for the chatbot.
"""

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer

class Preprocessor:
    """Handles text preprocessing for intent classification."""
    
    def __init__(self, words_vocabulary=None):
        """
        Initialize preprocessor.
        
        Args:
            words_vocabulary: List of words in vocabulary (for bag-of-words)
        """
        self.lemmatizer = WordNetLemmatizer()
        self.words = words_vocabulary
    
    def clean_up_sentence(self, sentence):
        """
        Tokenize and lemmatize a sentence.
        
        Args:
            sentence: Input sentence string
        
        Returns:
            List of lemmatized words
        """
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words
    
    def bag_of_words(self, sentence):
        """
        Convert sentence to bag of words representation (optimized).
        
        Args:
            sentence: Input sentence string
        
        Returns:
            numpy array representing bag of words
        """
        if self.words is None:
            raise ValueError("Words vocabulary not set. Initialize Preprocessor with words_vocabulary.")
        
        sentence_words = self.clean_up_sentence(sentence)
        bag = np.zeros(len(self.words), dtype=np.float32)
        word_set = set(sentence_words)  # Use set for O(1) lookup
        
        for i, word in enumerate(self.words):
            if word in word_set:
                bag[i] = 1
        
        return bag
    
    def set_vocabulary(self, words_vocabulary):
        """
        Set or update the words vocabulary.
        
        Args:
            words_vocabulary: List of words in vocabulary
        """
        self.words = words_vocabulary

