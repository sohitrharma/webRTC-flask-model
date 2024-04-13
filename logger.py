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
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
