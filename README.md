# RemindMe! Chatbot

A reminder and event management chatbot built with TensorFlow/Keras for intent classification and spaCy for Named Entity Recognition (NER).

## Features

- **Intent Classification:** Neural network-based intent recognition (91% accuracy)
- **Entity Extraction:** Custom spaCy NER model for extracting dates, times, and reminder text (88% accuracy)
- **Natural Language Processing:** Handles conversational input for setting and managing reminders
- **Error Handling:** Comprehensive error handling with graceful fallbacks
- **Configuration Management:** Centralized configuration with environment variable support
- **Date/Time Parsing:** Robust parsing supporting relative dates (today, tomorrow, next week, etc.)

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/retrouvm/chatbot.git
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

## Usage

### Running the Chatbot

```bash
python chatbot.py
```

### Training Models

Train the intent classification model:
```bash
python intents_training.py
```

Train the NER model:
```bash
python ner_training.py
```

**Note:** Models must be trained before running the chatbot. Training includes:
- 80/20 train/validation split
- Early stopping to prevent overfitting
- Model checkpointing for best performance

## Configuration

Configuration is managed in `config.py`. Key settings include:
- Intent classification threshold
- NER entity handling
- Training hyperparameters
- Logging configuration

Override settings with environment variables:
```bash
export INTENT_ERROR_THRESHOLD=0.3
export LOG_LEVEL=DEBUG
python chatbot.py
```

## Project Structure

```
chatbot/
├── chatbot.py              # Main chatbot application
├── config.py              # Configuration management
├── logger.py              # Logging system
├── datetime_parser.py     # Date/time parsing utilities
├── intents_training.py    # Intent model training
├── ner_training.py        # NER model training
├── intents.json          # Intent training data
├── entities.json         # NER training data
└── requirements.txt      # Python dependencies
```

## Performance

- **Intent Classification:** 91% accuracy
- **NER Accuracy:** 88% accuracy
- **Response Time:** ~65ms average
- **Training Time:** 30-45 minutes (with early stopping)

## Technologies

- **TensorFlow/Keras:** Deep learning framework for intent classification
- **spaCy:** NLP framework for Named Entity Recognition
- **NLTK:** Text preprocessing and tokenization
- **python-dateutil:** Advanced date/time parsing

## License

[Specify your license]
