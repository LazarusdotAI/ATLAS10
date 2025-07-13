"""
A.T.L.A.S. Startup Initialization Module
This module MUST be imported first by all A.T.L.A.S. components to ensure
Windows-compatible logging is set up before any component creates loggers.
"""

import os
import sys
import logging

# Set environment variables for Windows Unicode support
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Ensure the helper tools path is available
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and initialize Windows-compatible logging IMMEDIATELY
try:
    from atlas_logging_config import (
        ensure_windows_compatible_logging,
        force_reinitialize_logging,
        force_windows_compatible_formatters,
        patch_logging_module,
        get_atlas_logger
    )

    # Force initialization of Windows-compatible logging
    ensure_windows_compatible_logging()

    # Apply monkey-patch to ensure all future loggers are Windows-compatible
    patch_logging_module()

    # Force existing loggers to use Windows-compatible formatters
    force_windows_compatible_formatters()

    # Create a startup logger to confirm initialization
    startup_logger = get_atlas_logger('atlas_startup_init')
    startup_logger.info("A.T.L.A.S. startup initialization completed - Windows-compatible logging active")
    startup_logger.info("Unicode encoding issues should now be resolved")
    
except ImportError as e:
    # Fallback logging setup if atlas_logging_config is not available
    print(f"Warning: Could not import atlas_logging_config: {e}")
    print("Setting up basic Windows-compatible logging...")
    
    # Basic Windows-compatible logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('atlas_fallback.log', encoding='utf-8')
        ]
    )
    
    # Create fallback logger
    startup_logger = logging.getLogger('atlas_startup_init')
    startup_logger.info("A.T.L.A.S. fallback logging initialized")

def get_atlas_logger(name: str) -> logging.Logger:
    """
    Get a properly configured A.T.L.A.S. logger.
    This ensures Windows-compatible logging is always used.
    """
    # Ensure logging is initialized
    try:
        from atlas_logging_config import get_atlas_logger as _get_atlas_logger
        return _get_atlas_logger(name)
    except ImportError:
        # Fallback if atlas_logging_config is not available
        try:
            ensure_windows_compatible_logging()
        except NameError:
            pass
        return logging.getLogger(name)

def initialize_component_logging(component_name: str) -> logging.Logger:
    """
    Initialize logging for an A.T.L.A.S. component.
    This should be called at the start of each component's __init__ method.
    """
    logger = get_atlas_logger(component_name)
    logger.info(f"[INIT] {component_name} component logging initialized")
    return logger

# Export key functions for easy import
__all__ = [
    'get_atlas_logger',
    'initialize_component_logging',
    'ensure_windows_compatible_logging',
    'force_reinitialize_logging'
]

# Verification that this module was imported successfully
_ATLAS_STARTUP_INIT_LOADED = True
