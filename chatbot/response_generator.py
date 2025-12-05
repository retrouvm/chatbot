"""
Response generation module.
"""

import random
from logger import logger


class ResponseGenerator:
    """Handles response generation based on intents and entities."""
    
    def __init__(self, intents_data):
        """
        Initialize ResponseGenerator.
        
        Args:
            intents_data: Dictionary containing intents and responses
        """
        self.intents_data = intents_data
    
    def generate(self, intents_list, entities):
        """
        Generate response based on predicted intent and extracted entities.
        
        Args:
            intents_list: List of predicted intents with probabilities
            entities: Dictionary of extracted entities
        
        Returns:
            Generated response string
        """
        # Handle empty intent list with fallback
        if not intents_list or len(intents_list) == 0:
            return "I'm sorry, I didn't understand that. Could you please rephrase your question?"
        
        tag = intents_list[0]['intent']
        list_of_intents = self.intents_data.get('intents', [])
        
        # Find matching intent
        matched_intent = None
        for i in list_of_intents:
            if i.get('tag') == tag:
                matched_intent = i
                break
        
        # Fallback if intent not found
        if not matched_intent:
            return "I'm sorry, I didn't understand that. Could you please rephrase your question?"
        
        try:
            # Select random response
            responses = matched_intent.get('responses', [])
            if not responses:
                return "I'm sorry, I don't have a response for that."
            
            response = random.choice(responses).get('text', '')
            if not response:
                return "I'm sorry, I don't have a response for that."
            
            # Handle entity replacement
            missing_entities = []
            if 'inputs' in matched_intent:
                for entity in matched_intent['inputs']:
                    entity_type = entity.get('type', '')
                    if entity_type in entities:
                        response = response.replace(
                            f'{{{entity_type}}}',
                            str(entities[entity_type])
                        )
                    else:
                        missing_entities.append(entity)
            
            # Prompt for missing entities
            if len(missing_entities) > 0:
                for entity in missing_entities:
                    prompt = entity.get(
                        'prompt',
                        f'Please provide {entity.get("type", "information")}'
                    )
                    response += '\n' + prompt
                    try:
                        user_input = input(prompt + '\n> ').strip()
                        if user_input:
                            entities[entity.get('type', '')] = user_input
                            response = response.replace(
                                f'{{{entity.get("type", "")}}}',
                                user_input
                            )
                    except (EOFError, KeyboardInterrupt):
                        return "Input cancelled. Please try again."
            
            return response
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(error_msg)
            logger.error(error_msg)
            return "I'm sorry, I encountered an error processing your request. Please try again."

