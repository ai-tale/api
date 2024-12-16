import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Configure and return a logger for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("aitale_api")
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    
    # Add filter to add request_id to log records
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'request_id'):
                record.request_id = 'no-request-id'
            return True
    
    # Create file handler
    file_handler = RotatingFileHandler(
        logs_dir / "aitale_api.log",
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(RequestIdFilter())
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 