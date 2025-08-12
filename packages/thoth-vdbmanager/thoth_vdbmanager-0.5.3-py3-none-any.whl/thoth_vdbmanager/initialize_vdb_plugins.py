# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""
Plugin initialization utilities for vector database backends.
"""

import logging
from typing import Dict

from .vdb_discovery import get_available_vectordbs

logger = logging.getLogger(__name__)


def initialize_vectordb_plugins() -> Dict[str, bool]:
    """
    Initialize available vector database plugins by checking 
    which backends have their dependencies installed.
    
    Returns:
        Dict[str, bool]: Dictionary mapping backend names to availability status
    """
    try:
        logger.info("Initializing vector database plugins...")
        
        # Get available vector databases based on installed dependencies
        available_backends = get_available_vectordbs()
        
        # Log available plugins
        available_list = [backend for backend, available in available_backends.items() if available]
        unavailable_list = [backend for backend, available in available_backends.items() if not available]
        
        if available_list:
            logger.info(f"Available vector database backends: {', '.join(available_list)}")
        if unavailable_list:
            logger.info(f"Unavailable vector database backends (missing dependencies): {', '.join(unavailable_list)}")
            
        return available_backends
        
    except Exception as e:
        logger.error(f"Error initializing vector database plugins: {str(e)}")
        return {}