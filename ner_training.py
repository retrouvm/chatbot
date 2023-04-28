import os

import random
import json

import spacy
from spacy.training.example import Example




#code for training the NER model

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
def train_ner_model(train_data, model_path="ner_model"):
    nlp = spacy.blank("en")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for iteration in range(1000):
            random.shuffle(train_data)
            losses = {}
            for text, annotations in train_data:
                example = Example.from_dict(nlp.make_doc(text), annotations)
                nlp.update([example], drop=0.5, sgd=optimizer, losses=losses)
            print("Iteration {} Losses: {}".format(iteration, losses))
    os.makedirs(model_path, exist_ok=True)
    print("NER training has been completed.")
    nlp.to_disk(model_path)

# Preprocess the data
train_data = preprocess_data("entities.json")

# Train the NER model
train_ner_model(train_data, model_path="ner_model")






