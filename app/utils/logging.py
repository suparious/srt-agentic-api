import logging
from logging.handlers import RotatingFileHandler
import os
from app.config import settings

def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger with file and console handlers."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # File Handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)  # 10MB per file, keep 5 old versions
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create loggers
main_logger = setup_logger('main', settings.LOG_DIR + '/main.log')
agent_logger = setup_logger('agent', settings.LOG_DIR + '/agent.log')
memory_logger = setup_logger('memory', settings.LOG_DIR + '/memory.log')
llm_logger = setup_logger('llm', settings.LOG_DIR + '/llm.log')
function_logger = setup_logger('function', settings.LOG_DIR + '/function.log')  # New logger for function operations
