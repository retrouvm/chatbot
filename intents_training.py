import random
import json
import pickle
import numpy as np


import nltk
from nltk.stem import WordNetLemmatizer

import tensorflow as tf

#code for training the intents model
lemmatizer = WordNetLemmatizer()

#function that takes the path to the intents file as input and returns the preprocessed training data
def preprocess_intents(intents_file):
    words = []
    classes = []
    documents = []
    ignore_letters = ['?', '!', '.', ',']

    intents = json.loads(open(intents_file).read())

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
    return trainX, trainY, classes

def train_intents_model(trainX, trainY, classes, model_path):
    model = tf.keras.Sequential()
    #input layer
    model.add(tf.keras.layers.Dense(555, input_shape=(len(trainX[0]),), activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    #hidden layer
    model.add(tf.keras.layers.Dense(264, activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    #output layer
    model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))

    sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    hist = model.fit(trainX, trainY, epochs=1000, batch_size=5, verbose=1)
    model.save(model_path)

    return model

# Preprocess the intents data
trainX, trainY, classes = preprocess_intents('intents.json')

# Train the intents model
model = train_intents_model(trainX, trainY, classes, 'intents_model.h5')
print('Training has been completed')