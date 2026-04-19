import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name="AI_SYSTEM", log_file="logs/system.log", level=logging.INFO):
    """Function to setup as many loggers as you want"""

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize default logger
logger = setup_logger()
