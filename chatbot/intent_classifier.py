"""
Intent classification module.
"""

import numpy as np
import config
from logger import logger, log_prediction, log_error
from chatbot.utils.preprocessor import Preprocessor


class IntentClassifier:
    """Handles intent classification for user messages."""
    
    def __init__(self, model, words, classes):
        """
        Initialize IntentClassifier.
        
        Args:
            model: Trained Keras model for intent classification
            words: List of words in vocabulary
            classes: List of intent classes
        """
        self.model = model
        self.preprocessor = Preprocessor(words_vocabulary=words)
        self.classes = classes
        self.error_threshold = config.INTENT_CONFIG['error_threshold']
        self.use_verbose = config.INTENT_CONFIG['use_verbose']
    
    def predict(self, sentence):
        """
        Predict intent class for a given sentence.
        
        Args:
            sentence: Input sentence string
        
        Returns:
            List of dictionaries with 'intent' and 'probability' keys
        """
        if not sentence or not sentence.strip():
            return []
        
        try:
            sentence = sentence.lower().strip()
            bow = self.preprocessor.bag_of_words(sentence)
            verbose = 1 if self.use_verbose else 0
            res = self.model.predict(np.array([bow]), verbose=verbose)[0]
            
            results = [[i, r] for i, r in enumerate(res) if r > self.error_threshold]
            results.sort(key=lambda x: x[1], reverse=True)
            
            return_list = []
            for r in results:
                return_list.append({
                    'intent': self.classes[r[0]],
                    'probability': float(r[1])
                })
            
            # Log prediction
            if return_list:
                log_prediction(
                    sentence,
                    return_list[0]['intent'],
                    return_list[0]['probability']
                )
            else:
                logger.warning(
                    f"No intent matched for sentence: '{sentence}' "
                    f"(threshold: {self.error_threshold})"
                )
            
            return return_list
        except Exception as e:
            error_msg = f"Error in predict_class: {e}"
            print(error_msg)
            log_error('PredictionError', error_msg, e)
            return []

