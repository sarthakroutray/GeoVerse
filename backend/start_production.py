#!/usr/bin/env python3
"""
Production server startup script for GeoVerse backend.
This script starts the FastAPI server with proper configuration.
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logging import setup_logging
from src.utils.config import settings

def main():
    """Start the production server"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting GeoVerse production server...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"Vector dimension: {settings.vector_dimension}")
    
    # Start the server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # No reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main()
