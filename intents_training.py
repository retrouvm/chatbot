import random
import json
import pickle
import numpy as np
import os
import sys
from sklearn.model_selection import train_test_split
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
import config
from logger import setup_logger, log_training_event

# Setup logger
logger = setup_logger('intent_training')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def preprocess_intents(intents_file):
    """
    Preprocess intents file and return training data.
    
    Args:
        intents_file: Path to intents JSON file
    
    Returns:
        tuple: (trainX, trainY, classes, words)
    """
    words = []
    classes = []
    documents = []
    ignore_letters = ['?', '!', '.', ',']

    try:
        with open(intents_file, 'r', encoding='utf-8') as f:
            intents = json.load(f)
        logger.info(f"Loaded intents file: {intents_file}")
    except FileNotFoundError:
        logger.error(f"Intents file not found: {intents_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        sys.exit(1)

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
    
    logger.info(f"Vocabulary size: {len(words)}")
    logger.info(f"Number of classes: {len(classes)}")
    logger.info(f"Classes: {classes}")

    # Save words and classes with proper file handling
    try:
        with open(config.MODEL_PATHS['words_pkl'], 'wb') as f:
            pickle.dump(words, f)
        with open(config.MODEL_PATHS['classes_pkl'], 'wb') as f:
            pickle.dump(classes, f)
        logger.info("Saved words.pkl and classes.pkl")
    except Exception as e:
        logger.error(f"Error saving pickle files: {e}")
        sys.exit(1)


    training = []
    outputEmpty = [0] * len(classes)

    # Optimize bag of words creation
    for document in documents:
        bag = np.zeros(len(words), dtype=np.float32)
        wordPatterns = document[0]
        wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]
        wordPatterns_set = set(wordPatterns)  # Use set for O(1) lookup
        
        for i, word in enumerate(words):
            if word in wordPatterns_set:
                bag[i] = 1

        outputRow = list(outputEmpty)
        outputRow[classes.index(document[1])] = 1
        training.append(list(bag) + outputRow)

    random.shuffle(training)
    training = np.array(training)

    trainX = training[:, :len(words)]
    trainY = training[:, len(words):]
    
    logger.info(f"Training data shape: X={trainX.shape}, Y={trainY.shape}")
    return trainX, trainY, classes

def train_intents_model(trainX, trainY, valX, valY, classes, model_path):
    """
    Train the intent classification model with validation and early stopping.
    
    Args:
        trainX: Training features
        trainY: Training labels
        valX: Validation features
        valY: Validation labels
        classes: List of class names
        model_path: Path to save the model
    
    Returns:
        Trained model and training history
    """
    # Build model architecture from config
    model = tf.keras.Sequential()
    
    # Input layer
    model.add(tf.keras.layers.Dense(
        config.INTENT_TRAINING['hidden_layer_1_size'],
        input_shape=(len(trainX[0]),),
        activation=config.INTENT_TRAINING['activation']
    ))
    model.add(tf.keras.layers.Dropout(config.INTENT_TRAINING['dropout_rate']))
    
    # Hidden layer
    model.add(tf.keras.layers.Dense(
        config.INTENT_TRAINING['hidden_layer_2_size'],
        activation=config.INTENT_TRAINING['activation']
    ))
    model.add(tf.keras.layers.Dropout(config.INTENT_TRAINING['dropout_rate']))
    
    # Output layer
    model.add(tf.keras.layers.Dense(
        len(trainY[0]),
        activation=config.INTENT_TRAINING['output_activation']
    ))

    # Configure optimizer
    if config.INTENT_TRAINING['optimizer'] == 'sgd':
        optimizer = tf.keras.optimizers.SGD(
            learning_rate=config.INTENT_TRAINING['learning_rate'],
            momentum=config.INTENT_TRAINING['momentum'],
            nesterov=config.INTENT_TRAINING['nesterov']
        )
    else:
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=config.INTENT_TRAINING['learning_rate']
        )
    
    model.compile(
        loss=config.INTENT_TRAINING['loss_function'],
        optimizer=optimizer,
        metrics=['accuracy']
    )
    
    logger.info("Model architecture created")
    model.summary(print_fn=logger.info)

    # Setup callbacks
    callbacks = []
    
    # Early stopping
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor=config.INTENT_TRAINING['early_stopping_monitor'],
        patience=config.INTENT_TRAINING['early_stopping_patience'],
        restore_best_weights=config.INTENT_TRAINING['early_stopping_restore_best_weights'],
        verbose=1
    )
    callbacks.append(early_stopping)
    
    # Model checkpointing
    checkpoint_path = model_path.replace('.h5', '_best.h5')
    model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
        checkpoint_path,
        monitor=config.INTENT_TRAINING['model_checkpoint_monitor'],
        save_best_only=config.INTENT_TRAINING['model_checkpoint_save_best_only'],
        verbose=1
    )
    callbacks.append(model_checkpoint)
    
    log_training_event('START', f"Training model with {len(trainX)} samples, {len(valX)} validation samples")
    
    # Train model
    history = model.fit(
        trainX, trainY,
        validation_data=(valX, valY),
        epochs=config.INTENT_TRAINING['epochs'],
        batch_size=config.INTENT_TRAINING['batch_size'],
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    model.save(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Log training results
    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    final_train_loss = history.history['loss'][-1]
    final_val_loss = history.history['val_loss'][-1]
    
    log_training_event('COMPLETE', 
        f"Training completed - Train Acc: {final_train_acc:.4f}, Val Acc: {final_val_acc:.4f}, "
        f"Train Loss: {final_train_loss:.4f}, Val Loss: {final_val_loss:.4f}")
    
    return model, history

def main():
    """Main training function."""
    intents_file = config.MODEL_PATHS['intents_json']
    model_path = config.MODEL_PATHS['intents_model']
    
    logger.info("=" * 60)
    logger.info("Starting Intent Model Training")
    logger.info("=" * 60)
    
    # Preprocess the intents data
    trainX, trainY, classes = preprocess_intents(intents_file)
    
    # Split into training and validation sets
    validation_split = config.INTENT_TRAINING['validation_split']
    trainX, valX, trainY, valY = train_test_split(
        trainX, trainY,
        test_size=validation_split,
        random_state=42,
        stratify=trainY  # Maintain class distribution
    )
    
    logger.info(f"Training set: {len(trainX)} samples")
    logger.info(f"Validation set: {len(valX)} samples")
    logger.info(f"Validation split: {validation_split * 100}%")
    
    # Train the intents model
    model, history = train_intents_model(
        trainX, trainY, valX, valY, classes, model_path
    )
    
    logger.info("=" * 60)
    logger.info("Training completed successfully!")
    logger.info("=" * 60)
    print('\n✓ Training has been completed successfully!')
    print(f'✓ Model saved to: {model_path}')
    print(f'✓ Best model saved to: {model_path.replace(".h5", "_best.h5")}')

if __name__ == "__main__":
    main()