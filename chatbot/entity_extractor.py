"""
Entity extraction module using NER.
"""

import config
from logger import logger, log_error


class EntityExtractor:
    """Handles named entity extraction from user messages."""
    
    def __init__(self, nlp_model):
        """
        Initialize EntityExtractor.
        
        Args:
            nlp_model: Loaded spaCy NER model
        """
        self.nlp = nlp_model
        self.keep_first_only = config.NER_CONFIG['keep_first_entity_only']
    
    def extract(self, message):
        """
        Extract named entities from message using NER model.
        
        Args:
            message: Input message string
        
        Returns:
            Dictionary mapping entity labels to entity text
        """
        if not message or not message.strip():
            return {}
        
        try:
            doc = self.nlp(message)
            entities = {}
            
            for ent in doc.ents:
                # Handle multiple entities of same type based on config
                if self.keep_first_only:
                    if ent.label_ not in entities:
                        entities[ent.label_] = ent.text
                else:
                    # Keep all entities, store as list
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                    entities[ent.label_].append(ent.text)
            
            if entities:
                logger.debug(f"Extracted entities from '{message}': {entities}")
            
            return entities
        except Exception as e:
            error_msg = f"Error extracting entities: {e}"
            print(error_msg)
            log_error('EntityExtractionError', error_msg, e)
            return {}

