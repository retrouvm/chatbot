"""
Main Chatbot class that orchestrates all components.
"""

import time
import config
from logger import logger, log_request, log_error
from chatbot.model_loader import ModelLoader
from chatbot.intent_classifier import IntentClassifier
from chatbot.entity_extractor import EntityExtractor
from chatbot.response_generator import ResponseGenerator


class Chatbot:
    """Main chatbot class that coordinates all components."""
    
    def __init__(self):
        """Initialize Chatbot and load all models."""
        print("Loading models...")
        loader = ModelLoader()
        nlp, intent_model, intents_data, words, classes = loader.load_all()
        
        self.intent_classifier = IntentClassifier(intent_model, words, classes)
        self.entity_extractor = EntityExtractor(nlp)
        self.response_generator = ResponseGenerator(intents_data)
        self.goodbye_statements = config.CHATBOT_CONFIG['goodbye_statements']
        self.welcome_message = config.CHATBOT_CONFIG['welcome_message']
    
    def process_message(self, message):
        """
        Process a user message and return a response.
        
        Args:
            message: User input message
        
        Returns:
            Response string
        """
        if not message or not message.strip():
            return "Please enter a message."
        
        start_time = time.time()
        
        # Extract entities and predict intent
        entities = self.entity_extractor.extract(message)
        intents = self.intent_classifier.predict(message)
        response = self.response_generator.generate(intents, entities)
        
        processing_time = time.time() - start_time
        
        # Log request and response
        log_request(message, response, processing_time)
        
        return response
    
    def is_goodbye(self, message):
        """
        Check if message contains goodbye statements.
        
        Args:
            message: User input message
        
        Returns:
            Boolean indicating if message is a goodbye
        """
        message_lower = message.lower()
        return any(word in message_lower for word in self.goodbye_statements)
    
    def run(self):
        """Run the interactive chatbot loop."""
        print("=" * 50)
        print(self.welcome_message)
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("=" * 50)
        
        while True:
            try:
                message = input("\nYou: ").strip()
                
                # Handle empty input
                if not message:
                    print("RemindMe!: Please enter a message.")
                    continue
                
                # Process message
                response = self.process_message(message)
                print("RemindMe!: ", response)
                
                # Check for goodbye statements
                if self.is_goodbye(message):
                    print('\nAre you sure you want to end this chat? Type "yes" or "no"')
                    try:
                        next_input = input('> ').lower().strip()
                        if next_input == 'yes':
                            print('Goodbye! Have a great day!')
                            break
                        elif next_input == 'no':
                            continue
                        else:
                            print('Invalid input. Please type "yes" or "no"')
                            continue
                    except (EOFError, KeyboardInterrupt):
                        print('\nGoodbye!')
                        break
            
            except KeyboardInterrupt:
                print('\n\nGoodbye!')
                break
            except EOFError:
                print('\n\nGoodbye!')
                break
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                print(f"RemindMe!: {error_msg}")
                print("Please try again or type 'quit' to exit.")
                log_error('UnexpectedError', error_msg, e)

