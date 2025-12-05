import os
import sys
import random
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
import spacy
from spacy.training.example import Example
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from logger import setup_logger, log_training_event

# Setup logger
logger = setup_logger('ner_training')

def preprocess_data(json_file):
    """
    Preprocess the JSON entities file into spaCy format.
    
    Args:
        json_file: Path to entities JSON file
    
    Returns:
        List of training examples in spaCy format
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded entities file: {json_file}")
    except FileNotFoundError:
        logger.error(f"Entities file not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        sys.exit(1)
    
    train_data = []
    for annotation in data.get("annotations", []):
        text = annotation.get("text", "")
        if not text:
            continue
        
        entities = []
        for entity in annotation.get("entities", []):
            start = entity.get("start", 0)
            end = entity.get("end", 0)
            label = entity.get("label", "")
            
            # Validate entity boundaries
            if start < 0 or end > len(text) or start >= end:
                logger.warning(f"Invalid entity boundaries: start={start}, end={end}, text_len={len(text)}")
                continue
            
            if not label:
                logger.warning("Empty label found, skipping")
                continue
            
            entities.append((start, end, label))
        
        if entities:  # Only add if we have valid entities
            train_data.append((text, {"entities": entities}))
    
    logger.info(f"Preprocessed {len(train_data)} training examples")
    return train_data

def train_ner_model(train_data, val_data, model_path="ner_model"):
    """
    Train the NER model using modern spaCy API with validation.
    
    Args:
        train_data: Training examples
        val_data: Validation examples
        model_path: Path to save the model
    
    Returns:
        Trained spaCy model
    """
    # Create blank spaCy model
    nlp = spacy.blank("en")
    
    # Add NER component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
    
    # Add labels from training data
    all_labels = set()
    for _, annotations in train_data:
        for ent in annotations.get("entities", []):
            all_labels.add(ent[2])
    
    for label in sorted(all_labels):
        ner.add_label(label)
    
    logger.info(f"Added {len(all_labels)} entity labels: {sorted(all_labels)}")
    
    # Convert to spaCy Examples
    train_examples = []
    for text, annotations in train_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)
    
    val_examples = []
    for text, annotations in val_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        val_examples.append(example)
    
    logger.info(f"Training with {len(train_examples)} examples, validating with {len(val_examples)} examples")
    
    # Training loop with early stopping
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    nlp.begin_training()
    
    best_val_loss = float('inf')
    patience_counter = 0
    patience = config.NER_TRAINING['early_stopping_patience']
    min_delta = config.NER_TRAINING['early_stopping_min_delta']
    
    iterations = config.NER_TRAINING['iterations']
    drop_rate = config.NER_TRAINING['drop_rate']
    
    log_training_event('START', f"Training NER model with {len(train_examples)} samples")
    
    for iteration in range(iterations):
        # Shuffle training data
        random.shuffle(train_examples)
        
        # Training
        losses = {}
        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.resume_training()
            for example in train_examples:
                nlp.update([example], drop=drop_rate, sgd=optimizer, losses=losses)
        
        # Validation
        val_losses = {}
        with nlp.disable_pipes(*other_pipes):
            for example in val_examples:
                nlp.update([example], drop=0.0, losses=val_losses)
        
        train_loss = losses.get('ner', 0.0)
        val_loss = val_losses.get('ner', 0.0)
        
        # Log progress
        if (iteration + 1) % 10 == 0 or iteration == 0:
            logger.info(f"Iteration {iteration + 1}/{iterations} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            log_training_event('PROGRESS', 
                f"Iteration {iteration + 1} - Train: {train_loss:.4f}, Val: {val_loss:.4f}")
        
        # Early stopping check
        if val_loss < best_val_loss - min_delta:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best model
            os.makedirs(model_path, exist_ok=True)
            nlp.to_disk(model_path)
            logger.debug(f"Saved best model at iteration {iteration + 1} (val_loss: {val_loss:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping at iteration {iteration + 1} (patience: {patience})")
                log_training_event('EARLY_STOP', 
                    f"Stopped at iteration {iteration + 1}, best val_loss: {best_val_loss:.4f}")
                break
    
    # Final save
    os.makedirs(model_path, exist_ok=True)
    nlp.to_disk(model_path)
    
    log_training_event('COMPLETE', 
        f"NER training completed - Final train loss: {train_loss:.4f}, Final val loss: {val_loss:.4f}, Best val loss: {best_val_loss:.4f}")
    
    logger.info("NER training has been completed.")
    return nlp

def main():
    """Main training function."""
    entities_file = config.MODEL_PATHS['entities_json']
    model_path = config.MODEL_PATHS['ner_model']
    
    logger.info("=" * 60)
    logger.info("Starting NER Model Training")
    logger.info("=" * 60)
    
    # Preprocess the data
    all_data = preprocess_data(entities_file)
    
    if len(all_data) < 2:
        logger.error("Not enough training data. Need at least 2 examples.")
        sys.exit(1)
    
    # Split into training and validation sets
    validation_split = config.NER_TRAINING['validation_split']
    train_data, val_data = train_test_split(
        all_data,
        test_size=validation_split,
        random_state=42
    )
    
    logger.info(f"Training set: {len(train_data)} examples")
    logger.info(f"Validation set: {len(val_data)} examples")
    logger.info(f"Validation split: {validation_split * 100}%")
    
    # Train the NER model
    model = train_ner_model(train_data, val_data, model_path=model_path)
    
    logger.info("=" * 60)
    logger.info("Training completed successfully!")
    logger.info("=" * 60)
    print('\n✓ NER training has been completed successfully!')
    print(f'✓ Model saved to: {model_path}')

if __name__ == "__main__":
    main()






