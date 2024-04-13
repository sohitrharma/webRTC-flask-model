import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    """Configure and return a logger."""
    log_directory = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_directory, exist_ok=True)
    
    log_file_path = os.path.join(log_directory, 'app.log')
    handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=3, mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # Get logging level from environment variable
    level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')

    logger.setLevel(numeric_level)
    logger.addHandler(handler)

    return logger
