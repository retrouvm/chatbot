import random
import json
import pickle
import numpy as np
import nltk
import sys
import os
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import spacy
import config

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Global variables for models and data
nlp = None
model = None
intents = None
words = None
classes = None

# Import configuration
MODEL_PATHS = config.MODEL_PATHS
ERROR_THRESHOLD = config.INTENT_CONFIG['error_threshold']
FALLBACK_INTENT = config.INTENT_CONFIG['fallback_intent']

def load_models():
    """Load all required models and data files with error handling."""
    global nlp, model, intents, words, classes
    
    try:
        # Load NER model
        if not os.path.exists(MODEL_PATHS['ner_model']):
            raise FileNotFoundError(f"NER model not found at {MODEL_PATHS['ner_model']}")
        nlp = spacy.load(MODEL_PATHS['ner_model'])
        print("✓ NER model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading NER model: {e}")
        sys.exit(1)
    
    try:
        # Load intents model
        if not os.path.exists(MODEL_PATHS['intents_model']):
            raise FileNotFoundError(f"Intents model not found at {MODEL_PATHS['intents_model']}")
        model = load_model(MODEL_PATHS['intents_model'])
        print("✓ Intents model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading intents model: {e}")
        sys.exit(1)
    
    try:
        # Load intents JSON
        with open(MODEL_PATHS['intents_json'], 'r', encoding='utf-8') as f:
            intents = json.load(f)
        print("✓ Intents data loaded successfully")
    except FileNotFoundError:
        print(f"✗ Intents file not found at {MODEL_PATHS['intents_json']}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing intents JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading intents: {e}")
        sys.exit(1)
    
    try:
        # Load words pickle
        with open(MODEL_PATHS['words_pkl'], 'rb') as f:
            words = pickle.load(f)
        print("✓ Words vocabulary loaded successfully")
    except FileNotFoundError:
        print(f"✗ Words file not found at {MODEL_PATHS['words_pkl']}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading words: {e}")
        sys.exit(1)
    
    try:
        # Load classes pickle
        with open(MODEL_PATHS['classes_pkl'], 'rb') as f:
            classes = pickle.load(f)
        print("✓ Classes loaded successfully")
    except FileNotFoundError:
        print(f"✗ Classes file not found at {MODEL_PATHS['classes_pkl']}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading classes: {e}")
        sys.exit(1)

# Load all models on startup
load_models()

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
    
def bag_of_words(sentence):
    """Convert sentence to bag of words representation (optimized)."""
    sentence_words = clean_up_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    word_set = set(sentence_words)  # Use set for O(1) lookup
    for i, word in enumerate(words):
        if word in word_set:
            bag[i] = 1
    return bag

def predict_class(sentence):
    """Predict intent class for a given sentence."""
    if not sentence or not sentence.strip():
        return []
    
    try:
        sentence = sentence.lower().strip()
        bow = bag_of_words(sentence)
        verbose = 1 if config.INTENT_CONFIG['use_verbose'] else 0
        res = model.predict(np.array([bow]), verbose=verbose)[0]
        
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return_list = []
        for r in results:
            return_list.append({'intent': classes[r[0]], 'probability': float(r[1])})
        
        return return_list
    except Exception as e:
        print(f"Error in predict_class: {e}")
        return []

def get_response(intents_list, intents_json, entities):
    """Generate response based on predicted intent and extracted entities."""
    # Handle empty intent list with fallback
    if not intents_list or len(intents_list) == 0:
        return "I'm sorry, I didn't understand that. Could you please rephrase your question?"
    
    tag = intents_list[0]['intent']
    list_of_intents = intents_json.get('intents', [])
    
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
                    response = response.replace(f'{{{entity_type}}}', str(entities[entity_type]))
                else:
                    missing_entities.append(entity)
        
        # Prompt for missing entities
        if len(missing_entities) > 0:
            for entity in missing_entities:
                prompt = entity.get('prompt', f'Please provide {entity.get("type", "information")}')
                response += '\n' + prompt
                try:
                    user_input = input(prompt + '\n> ').strip()
                    if user_input:
                        entities[entity.get('type', '')] = user_input
                        response = response.replace(f'{{{entity.get("type", "")}}}', user_input)
                except (EOFError, KeyboardInterrupt):
                    return "Input cancelled. Please try again."
        
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try again."


goodbye_statements = ['bye', 'goodbye', 'see you', 'later', 'quit', 'exit', 'leave', 'end']

def extract_entities(message):
    """Extract named entities from message using NER model."""
    if not message or not message.strip():
        return {}
    
    try:
        doc = nlp(message)
        entities = {}
        for ent in doc.ents:
            # Handle multiple entities of same type based on config
            if config.NER_CONFIG['keep_first_entity_only']:
                if ent.label_ not in entities:
                    entities[ent.label_] = ent.text
            else:
                # Keep all entities, store as list
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
        return entities
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return {}

def main():
    """Main chatbot loop."""
    print("=" * 50)
    print(config.CHATBOT_CONFIG['welcome_message'])
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("=" * 50)
    
    goodbye_statements = config.CHATBOT_CONFIG['goodbye_statements']
    
    while True:
        try:
            message = input("\nYou: ").strip()
            
            # Handle empty input
            if not message:
                print("RemindMe!: Please enter a message.")
                continue
            
            # Extract entities and predict intent
            entities = extract_entities(message)
            ints = predict_class(message)
            res = get_response(ints, intents, entities)
            print("RemindMe!: ", res)
            
            # Check for goodbye statements
            message_lower = message.lower()
            if any(word in message_lower for word in goodbye_statements):
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
            print(f"RemindMe!: An unexpected error occurred: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
