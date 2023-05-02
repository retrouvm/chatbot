import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import spacy

# Load the NER model
nlp = spacy.load("ner_model")

# Load the intents model
model = load_model('intents_model.h5')

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
    
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    sentence = sentence.lower()
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.50
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    
    results.sort(key = lambda x: x[1], reverse = True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json, entities):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            response = random.choice(i['responses'])['text']
            missing_entities = []
            if 'inputs' in i:
                for entity in i['inputs']:
                    if entity['type'] in entities:
                        response = response.replace(f'{{{entity["type"]}}}', entities[entity["type"]])
                    else:
                        # Prompt for missing entity
                        missing_entities.append(entity)
            if len(missing_entities) > 0:
                for entity in missing_entities:
                    response += '\n' + entity['prompt']
                    entities[entity['type']] = input(entity['prompt'] + '\n')
                    response = response.replace(f'{{{entity["type"]}}}', entities[entity["type"]])
            return response


goodbye_statements = ['bye', 'goodbye', 'see you', 'later', 'quit', 'exit', 'leave', 'end']

def extract_entities(message):
    doc = nlp(message)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

while True:
    message = input("You: ")
    entities = extract_entities(message)
    ints = predict_class(message)
    res = get_response(ints, intents, entities)
    print("RemindMe!: ", res)
    
    if any(word in goodbye_statements for word in message.split()):
        print('\nAre you sure you want to end this chat? Type "yes" or "no"')
        next_input = input('> ').lower().strip()
        if next_input == 'yes':
            print('Goodbye!')
            break
        elif next_input == 'no':
            continue
        else:
            print('Invalid input. Please type "yes" or "no"')
            continue
