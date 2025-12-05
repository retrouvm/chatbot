"""
Model loading utilities for the chatbot.
"""

import json
import pickle
import os
import sys
from pathlib import Path
from keras.models import load_model
import spacy
import config
from logger import logger, log_model_loading, log_error


class ModelLoader:
    """Handles loading of all models and data files."""
    
    def __init__(self):
        """Initialize ModelLoader."""
        self.nlp = None
        self.intent_model = None
        self.intents_data = None
        self.words = None
        self.classes = None
        self.model_paths = config.MODEL_PATHS
    
    def load_all(self):
        """
        Load all required models and data files.
        
        Returns:
            tuple: (nlp, intent_model, intents_data, words, classes)
        """
        self.load_ner_model()
        self.load_intent_model()
        self.load_intents_data()
        self.load_words()
        self.load_classes()
        
        return (
            self.nlp,
            self.intent_model,
            self.intents_data,
            self.words,
            self.classes
        )
    
    def load_ner_model(self):
        """Load the NER model."""
        try:
            if not os.path.exists(self.model_paths['ner_model']):
                raise FileNotFoundError(f"NER model not found at {self.model_paths['ner_model']}")
            
            self.nlp = spacy.load(self.model_paths['ner_model'])
            print("✓ NER model loaded successfully")
            log_model_loading('NER Model', success=True)
        except Exception as e:
            error_msg = f"Error loading NER model: {e}"
            print(f"✗ {error_msg}")
            log_model_loading('NER Model', success=False, error=str(e))
            sys.exit(1)
    
    def load_intent_model(self):
        """Load the intent classification model."""
        try:
            if not os.path.exists(self.model_paths['intents_model']):
                raise FileNotFoundError(f"Intents model not found at {self.model_paths['intents_model']}")
            
            self.intent_model = load_model(self.model_paths['intents_model'])
            print("✓ Intents model loaded successfully")
            log_model_loading('Intents Model', success=True)
        except Exception as e:
            error_msg = f"Error loading intents model: {e}"
            print(f"✗ {error_msg}")
            log_model_loading('Intents Model', success=False, error=str(e))
            sys.exit(1)
    
    def load_intents_data(self):
        """Load intents JSON data."""
        try:
            with open(self.model_paths['intents_json'], 'r', encoding='utf-8') as f:
                self.intents_data = json.load(f)
            print("✓ Intents data loaded successfully")
            logger.info(f"Loaded {len(self.intents_data.get('intents', []))} intents from JSON")
        except FileNotFoundError as e:
            error_msg = f"Intents file not found at {self.model_paths['intents_json']}"
            print(f"✗ {error_msg}")
            log_error('FileNotFound', error_msg, e)
            sys.exit(1)
        except json.JSONDecodeError as e:
            error_msg = f"Error parsing intents JSON: {e}"
            print(f"✗ {error_msg}")
            log_error('JSONDecodeError', error_msg, e)
            sys.exit(1)
        except Exception as e:
            error_msg = f"Error loading intents: {e}"
            print(f"✗ {error_msg}")
            log_error('Exception', error_msg, e)
            sys.exit(1)
    
    def load_words(self):
        """Load words vocabulary."""
        try:
            with open(self.model_paths['words_pkl'], 'rb') as f:
                self.words = pickle.load(f)
            print("✓ Words vocabulary loaded successfully")
        except FileNotFoundError:
            error_msg = f"Words file not found at {self.model_paths['words_pkl']}"
            print(f"✗ {error_msg}")
            sys.exit(1)
        except Exception as e:
            error_msg = f"Error loading words: {e}"
            print(f"✗ {error_msg}")
            sys.exit(1)
    
    def load_classes(self):
        """Load classes list."""
        try:
            with open(self.model_paths['classes_pkl'], 'rb') as f:
                self.classes = pickle.load(f)
            print("✓ Classes loaded successfully")
        except FileNotFoundError:
            error_msg = f"Classes file not found at {self.model_paths['classes_pkl']}"
            print(f"✗ {error_msg}")
            sys.exit(1)
        except Exception as e:
            error_msg = f"Error loading classes: {e}"
            print(f"✗ {error_msg}")
            sys.exit(1)

