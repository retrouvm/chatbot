import random
import json
import pickle
import numpy as np
import spacy

import nltk
from nltk.stem import WordNetLemmatizer

import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
from spacy.training.example import Example


#function to preprocess the JSON entities file into spaCy format
def preprocess_data(json_file):
    data = json.loads(open(json_file).read())
    train_data = []
    for annotation in data["annotations"]:
        text = annotation["text"]
        entities = []
        for entity in annotation["entities"]:
            start = entity["start"]
            end = entity["end"]
            label = entity["label"]
            entities.append((start, end, label))
        train_data.append((text, {"entities": entities}))
    return train_data



#function to train the NER model
def train_ner_model(train_data, model_path):
    nlp = spacy.load("en_core_web_sm")
    ner = nlp.get_pipe("ner")

    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for iteration in range(100):
            random.shuffle(train_data)
            losses = {}
            for text, annotations in train_data:
                example = Example.from_dict(nlp.make_doc(text), annotations)
                nlp.update([example], drop=0.5, sgd=optimizer, losses=losses)

    nlp.to_disk(model_path)
# Preprocess the data
train_data = preprocess_data("entities.json")

# Train the NER model
train_ner_model(train_data, "ner_model")


lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']


for intent in intents['intents']:
    for pattern in intent['patterns']:
        if isinstance(pattern, str):
            word_list = nltk.tokenize.word_tokenize(pattern)
            entities = []
        elif isinstance(pattern, dict):
            word_list = nltk.tokenize.word_tokenize(pattern.get('text', ''))
            entities = pattern.get('entities', [])
        words.extend(word_list)
        documents.append((word_list, intent['tag'], entities))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
    
        # Extract plain text from each response and reminder
        if 'responses' in intent:
            for response in intent['responses']:
                response_text = response['text']
                print(response_text)

        if 'patterns' in intent:
            for pattern in intent['patterns']:
                if isinstance(pattern, dict) and 'text' in pattern:
                    reminder_text = pattern['text']
                    for entity in pattern.get('entities', []):
                        reminder_text = reminder_text.replace(f'{{{entity}}}', 'some_value')
                    print(reminder_text)



words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
outputEmpty = [0] * len(classes)

for document in documents:
    bag = []
    wordPatterns = document[0]
    wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    outputRow = list(outputEmpty)
    outputRow[classes.index(document[1])] = 1
    training.append(bag + outputRow)

random.shuffle(training)
training = np.array(training)

trainX = training[:, :len(words)]
trainY = training[:, len(words):]

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(trainX, trainY, epochs=200, batch_size=5, verbose=1)
model.save('remindme.h5', hist)
print('Done')