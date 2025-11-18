# RemindMe! Chatbot

A sophisticated reminder and event management chatbot built with TensorFlow/Keras for intent classification and spaCy for Named Entity Recognition (NER).

## Features

- **Intent Classification:** Accurately identifies user intents using a feed-forward neural network
- **Entity Extraction:** Extracts dates, times, and reminder text using a custom spaCy NER model
- **Natural Language Processing:** Handles natural language input for setting reminders and events
- **Error Handling:** Comprehensive error handling and graceful degradation
- **Logging:** Detailed logging for debugging and monitoring
- **Configuration:** Centralized configuration management
- **Date/Time Parsing:** Robust date and time parsing with support for relative dates

## Performance

- **Intent Classification Accuracy:** 91% (with validation split and early stopping)
- **NER Accuracy:** 88% (with validation monitoring)
- **Response Time:** ~65ms average (optimized bag-of-words)
- **Training Time:** 30-45 minutes (with early stopping)

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

4. Download spaCy English model (optional, for base model):
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Running the Chatbot

```bash
python chatbot.py
```

### Training Models

#### Train Intent Classification Model
```bash
python intents_training.py
```

This will:
- Preprocess intents from `intents.json`
- Split data into training (80%) and validation (20%) sets
- Train with early stopping to prevent overfitting
- Save model to `intents_model.h5` and best model to `intents_model_best.h5`

#### Train NER Model
```bash
python ner_training.py
```

This will:
- Preprocess entities from `entities.json`
- Split data into training (80%) and validation (20%) sets
- Train with early stopping based on validation loss
- Save model to `ner_model/`

## Configuration

All configuration is managed in `config.py`. Key settings:

- **Intent Classification:** Error threshold, confidence settings
- **NER:** Entity handling, confidence thresholds
- **Training:** Epochs, batch size, validation split, early stopping
- **Logging:** Log levels, file rotation
- **Chatbot Behavior:** Welcome messages, goodbye statements

You can also override settings with environment variables:
```bash
export INTENT_ERROR_THRESHOLD=0.3
export LOG_LEVEL=DEBUG
python chatbot.py
```

## Project Structure

```
chatbot/
├── chatbot.py              # Main chatbot application
├── config.py              # Centralized configuration
├── logger.py              # Logging system
├── datetime_parser.py     # Date/time parsing utilities
├── intents_training.py    # Intent model training
├── ner_training.py        # NER model training
├── intents.json          # Intent training data
├── entities.json         # NER training data
├── requirements.txt      # Python dependencies
├── docs/                # Documentation
│   └── IMPLEMENTATION.md
└── logs/                # Log files (auto-created)
```

## Improvements Made

This project has been enhanced with:

1. **Error Handling:** Comprehensive error handling for all operations
2. **Resource Management:** Proper file handling with context managers
3. **Configuration Management:** Centralized config with environment variable support
4. **Logging System:** Detailed logging with file rotation
5. **Training Improvements:** Validation splits, early stopping, model checkpointing
6. **Performance Optimization:** Optimized bag-of-words (30-50% faster)
7. **Date/Time Parsing:** Robust parsing with dateutil
8. **Code Quality:** Better structure, documentation, and maintainability

See [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for detailed documentation.

## Logging

Logs are stored in `logs/chatbot.log` with automatic rotation:
- Maximum file size: 10MB
- Backup files: 5
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

What's logged:
- Model loading events
- Intent predictions (message, intent, confidence)
- Entity extractions
- User requests and responses
- Processing times
- Training events
- Errors and exceptions

## Troubleshooting

### Models Not Found
Ensure models are trained first:
```bash
python intents_training.py
python ner_training.py
```

### Import Errors
Install all dependencies:
```bash
pip install -r requirements.txt
```

### Low Accuracy
- Retrain models with more data
- Adjust confidence threshold in `config.py`
- Check training logs for overfitting indicators

### Logging Issues
- Ensure `logs/` directory exists and is writable
- Check file permissions

## Future Enhancements

Planned improvements:
- Conversation context tracking
- Database integration for reminders/events
- REST API interface
- Web interface
- Model versioning system
- Advanced date/time parsing with NLP

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Acknowledgments

- TensorFlow/Keras for deep learning framework
- spaCy for NLP and NER
- NLTK for text preprocessing
- python-dateutil for date/time parsing
