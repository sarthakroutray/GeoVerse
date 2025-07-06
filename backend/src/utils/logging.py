# Logging configuration for GeoVerse
import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: str = "logs/backend.log"):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s.%(funcName)s (%(filename)s:%(lineno)d): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "level": log_level,
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO", 
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    return logging.getLogger(__name__)


# Create default logger
logger = setup_logging()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    app_name: str = "geoverse"
) -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if log file specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f"geoverse.{name}")

# Create default logger
logger = setup_logging()

# Log startup message    logger.info("GeoVerse Backend Logger Initialized")
logger.info(f"Log Level: {logger.level}")
logger.info(f"Handlers: {len(logger.handlers)}")

def log_request(endpoint: str, method: str, user_id: Optional[str] = None):
    """Log API request"""
    user_info = f" (User: {user_id})" if user_id else ""
    logger.info(f"API Request: {method} {endpoint}{user_info}")

def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    context_str = f" in {context}" if context else ""
    logger.error(f"Error{context_str}: {str(error)}", exc_info=True)

def log_performance(operation: str, duration: float, details: Optional[str] = None):
    """Log performance metrics"""
    details_str = f" - {details}" if details else ""
    logger.info(f"Performance: {operation} took {duration:.3f}s{details_str}")
