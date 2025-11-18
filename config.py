"""
Configuration file for RemindMe! Chatbot
Contains all configurable parameters and settings
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Model and data file paths
MODEL_PATHS = {
    'ner_model': str(BASE_DIR / 'ner_model'),
    'intents_model': str(BASE_DIR / 'intents_model.h5'),
    'intents_json': str(BASE_DIR / 'intents.json'),
    'words_pkl': str(BASE_DIR / 'words.pkl'),
    'classes_pkl': str(BASE_DIR / 'classes.pkl'),
    'entities_json': str(BASE_DIR / 'entities.json')
}

# Intent Classification Settings
INTENT_CONFIG = {
    'error_threshold': 0.25,  # Minimum confidence for intent classification
    'fallback_intent': 'no_intent_match',
    'max_intents_returned': 5,  # Maximum number of intents to return
    'use_verbose': False  # Verbose mode for model prediction
}

# NER Settings
NER_CONFIG = {
    'keep_first_entity_only': True,  # If multiple entities of same type, keep first
    'min_entity_confidence': 0.0  # Minimum confidence for entity extraction
}

# Training Settings - Intent Model
INTENT_TRAINING = {
    'epochs': 200,  # Reduced from 1000, early stopping will handle
    'batch_size': 5,
    'validation_split': 0.2,  # 20% for validation
    'early_stopping_patience': 20,  # Stop if no improvement for 20 epochs
    'early_stopping_monitor': 'val_loss',
    'early_stopping_restore_best_weights': True,
    'model_checkpoint_monitor': 'val_accuracy',
    'model_checkpoint_save_best_only': True,
    'learning_rate': 0.01,
    'momentum': 0.9,
    'nesterov': True,
    'dropout_rate': 0.5,
    # Model architecture
    'hidden_layer_1_size': 555,
    'hidden_layer_2_size': 264,
    'activation': 'relu',
    'output_activation': 'softmax',
    'loss_function': 'categorical_crossentropy',
    'optimizer': 'sgd'  # 'sgd' or 'adam'
}

# Training Settings - NER Model
NER_TRAINING = {
    'iterations': 100,  # Reduced from 1000, early stopping will handle
    'validation_split': 0.2,  # 20% for validation
    'drop_rate': 0.5,
    'early_stopping_patience': 10,
    'early_stopping_min_delta': 0.001,
    'batch_size': 8,
    'learning_rate': 0.001
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'log_file': str(BASE_DIR / 'logs' / 'chatbot.log'),
    'max_bytes': 10485760,  # 10MB
    'backup_count': 5,
    'log_requests': True,
    'log_predictions': True,
    'log_errors': True
}

# Chatbot Behavior Settings
CHATBOT_CONFIG = {
    'goodbye_statements': ['bye', 'goodbye', 'see you', 'later', 'quit', 'exit', 'leave', 'end'],
    'welcome_message': "RemindMe! Chatbot - Ready to assist you!",
    'exit_confirmation': True,
    'max_conversation_history': 10,  # Number of previous messages to keep
    'enable_context': False  # Enable conversation context (future feature)
}

# Date/Time Parsing Settings
DATETIME_CONFIG = {
    'use_dateutil': True,  # Use python-dateutil for parsing
    'default_timezone': None,  # None for local timezone
    'relative_date_keywords': ['today', 'tomorrow', 'yesterday', 'next week', 'next month'],
    'time_formats': ['%H:%M', '%I:%M %p', '%H:%M:%S']
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'cache_preprocessed_sentences': True,
    'cache_size': 1000,  # Maximum cached sentences
    'use_batch_prediction': False,  # Batch multiple predictions (future)
    'model_optimization': 'none'  # 'none', 'tflite', 'onnx' (future)
}

# Environment Variables (can override config)
def get_env_bool(key, default=False):
    """Get boolean from environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_int(key, default):
    """Get integer from environment variable."""
    return int(os.getenv(key, default))

def get_env_float(key, default):
    """Get float from environment variable."""
    return float(os.getenv(key, default))

# Override with environment variables if set
INTENT_CONFIG['error_threshold'] = get_env_float('INTENT_ERROR_THRESHOLD', INTENT_CONFIG['error_threshold'])
LOGGING_CONFIG['level'] = os.getenv('LOG_LEVEL', LOGGING_CONFIG['level'])
INTENT_TRAINING['epochs'] = get_env_int('TRAINING_EPOCHS', INTENT_TRAINING['epochs'])

