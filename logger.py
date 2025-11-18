"""
Logging module for RemindMe! Chatbot
Provides centralized logging functionality
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import config

def setup_logger(name='chatbot', log_file=None, level=None):
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        log_file: Path to log file (uses config if None)
        level: Logging level (uses config if None)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set logging level
    log_level = level or getattr(logging, config.LOGGING_CONFIG['level'], logging.INFO)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_file = config.LOGGING_CONFIG['log_file']
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        config.LOGGING_CONFIG['format'],
        datefmt=config.LOGGING_CONFIG['date_format']
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.LOGGING_CONFIG['max_bytes'],
        backupCount=config.LOGGING_CONFIG['backup_count']
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger instance
logger = setup_logger()

def log_prediction(message, intent, confidence, entities=None):
    """Log intent prediction for analysis."""
    if config.LOGGING_CONFIG['log_predictions']:
        log_msg = f"Prediction - Message: '{message}', Intent: {intent}, Confidence: {confidence:.4f}"
        if entities:
            log_msg += f", Entities: {entities}"
        logger.info(log_msg)

def log_error(error_type, message, exception=None):
    """Log errors with context."""
    if config.LOGGING_CONFIG['log_errors']:
        log_msg = f"Error [{error_type}]: {message}"
        if exception:
            log_msg += f" - Exception: {str(exception)}"
        logger.error(log_msg, exc_info=exception is not None)

def log_request(user_input, response, processing_time=None):
    """Log user requests and responses."""
    if config.LOGGING_CONFIG['log_requests']:
        log_msg = f"Request - Input: '{user_input}', Response: '{response[:100]}...'"
        if processing_time:
            log_msg += f", Processing time: {processing_time:.4f}s"
        logger.info(log_msg)

def log_model_loading(model_name, success=True, error=None):
    """Log model loading events."""
    if success:
        logger.info(f"Model loaded successfully: {model_name}")
    else:
        logger.error(f"Failed to load model: {model_name} - {error}")

def log_training_event(event_type, message, **kwargs):
    """Log training-related events."""
    log_msg = f"Training [{event_type}]: {message}"
    if kwargs:
        log_msg += f" - {kwargs}"
    logger.info(log_msg)

