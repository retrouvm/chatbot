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
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
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
            if 'entities' in i:
                for entity in i['entities']:
                    if entity in entities:
                        response = response.replace(f'{{{entity}}}', entities[entity])
            return response

goodbye_statements = ['bye', 'goodbye', 'see you', 'later', 'quit', 'stop', 'stupid', 'exit', 'leave']

def extract_entities(message):
    doc = nlp(message)
    entities = {}
    for ent in doc.ents:
        print(ent.label_, ent.text)
        entities[ent.label_] = ent.text
    return entities
"""def extract_entities(message):
    doc = nlp(message)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities"""

while True:
    message = input("")
    entities = extract_entities(message)
    ints = predict_class(message)
    res = get_response(ints, intents, entities)
    print(res)
    
    if any(word in goodbye_statements for word in message.split()):
        print('Are you sure you want to end this chat? Type "yes" or "no"')
        next_input = input('> ').lower().strip()
        if next_input == 'yes':
            print('Goodbye!')
            break
        elif next_input == 'no':
            continue
        else:
            print('Invalid input. Please type "yes" or "no"')
            continue