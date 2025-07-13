"""
A.T.L.A.S. Standardized Logging Configuration
Windows-compatible logging setup without Unicode characters
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any

class WindowsCompatibleFormatter(logging.Formatter):
    """Custom formatter that ensures Windows compatibility"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def format(self, record):
        # Get the original formatted message
        formatted = super().format(record)
        
        # Remove any Unicode characters that might cause issues
        # Replace common problematic characters found in A.T.L.A.S. logs
        replacements = {
            # Core system emojis
            '[AI]': '[AI]',
            '[OK]': '[OK]',
            '[ERROR]': '[ERROR]',
            '[WARN]': '[WARN]',
            '[DATA]': '[DATA]',
            '[LAUNCH]': '[LAUNCH]',
            '[TRADE]': '[TRADE]',
            '[TARGET]': '[TARGET]',
            '[SEARCH]': '[SEARCH]',
            '[UP]': '[UP]',
            '[DOWN]': '[DOWN]',
            '[MONEY]': '[MONEY]',
            '[SHIELD]': '[SHIELD]',
            '[STAR]': '[STAR]',
            '[TOOL]': '[TOOL]',
            '[WEB]': '[WEB]',
            '[NOTE]': '[NOTE]',
            '[FINISH]': '[FINISH]',
            '[SUCCESS]': '[SUCCESS]',
            '[LINK]': '[LINK]',
            '[BRAIN]': '[BRAIN]',
            '[BOOK]': '[BOOK]',
            '[LIBRARY]': '[LIBRARY]',
            '[DOC]': '[DOC]',
            '[IDEA]': '[IDEA]',
            '[FAST]': '[FAST]',

            # Additional emojis found in codebase
            '[TALK]': '[TALK]',
            '[DELETE]': '[DELETE]',
            '[INFO]': '[INFO]',
            '[BOT]': '[BOT]',

            # Entertainment emojis (keeping for completeness)
            '🎮': '[GAME]',
            '🎪': '[CIRCUS]',
            '🎭': '[THEATER]',
            '🎨': '[ART]',
            '🎲': '[DICE]',
            '🎳': '[BOWLING]',
            '🎸': '[GUITAR]',
            '🎹': '[PIANO]',
            '🎺': '[TRUMPET]',
            '🎻': '[VIOLIN]',
            '🥁': '[DRUMS]',
            '🎤': '[MIC]',
            '🎧': '[HEADPHONES]',
            '📻': '[RADIO]',
            '🎬': '[MOVIE]',
            '🎞️': '[FILM]',
            '📹': '[VIDEO]',
            '📷': '[CAMERA]',
            '📸': '[PHOTO]',

            # Technology emojis
            '[LAPTOP]': '[LAPTOP]',
            '[DESKTOP]': '[DESKTOP]',
            '[PRINTER]': '[PRINTER]',
            '[KEYBOARD]': '[KEYBOARD]',
            '[MOUSE]': '[MOUSE]',
            '[TRACKBALL]': '[TRACKBALL]',
            '[DISK]': '[DISK]',
            '[FLOPPY]': '[FLOPPY]',
            '[CD]': '[CD]',
            '[DVD]': '[DVD]',
            '[PHONE]': '[PHONE]',
            '[TELEPHONE]': '[TELEPHONE]',
            '[RECEIVER]': '[RECEIVER]',
            '[PAGER]': '[PAGER]',
            '[FAX]': '[FAX]',
            '[BATTERY]': '[BATTERY]',
            '[PLUG]': '[PLUG]'
        }
        
        for emoji, replacement in replacements.items():
            formatted = formatted.replace(emoji, replacement)
        
        # Ensure ASCII encoding with multiple fallback strategies
        try:
            # First attempt: encode with replacement
            formatted = formatted.encode('ascii', 'replace').decode('ascii')
        except UnicodeError:
            try:
                # Second attempt: encode with ignore
                formatted = formatted.encode('ascii', 'ignore').decode('ascii')
            except UnicodeError:
                # Final fallback: remove all non-ASCII characters manually
                formatted = ''.join(char for char in formatted if ord(char) < 128)

        # Additional safety check: ensure no problematic characters remain
        if any(ord(char) > 127 for char in formatted):
            formatted = ''.join(char if ord(char) < 128 else '?' for char in formatted)

        return formatted

def get_atlas_logging_config() -> Dict[str, Any]:
    """Get standardized A.T.L.A.S. logging configuration"""
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                '()': WindowsCompatibleFormatter,
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                '()': WindowsCompatibleFormatter,
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                '()': WindowsCompatibleFormatter,
                'format': '[%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'atlas_system.log',
                'mode': 'a',
                'encoding': 'utf-8'
            },
            'error_file': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'atlas_errors.log',
                'mode': 'a',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'atlas_ai_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_predicto_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_trading_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_risk_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_options_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_market_engine': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'atlas_server': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'error_file']
        }
    }

def setup_atlas_logging(log_level: str = 'INFO') -> None:
    """Setup standardized A.T.L.A.S. logging"""
    
    # Get configuration
    config = get_atlas_logging_config()
    
    # Adjust log level if specified
    if log_level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        config['root']['level'] = log_level.upper()
        for logger_config in config['loggers'].values():
            logger_config['level'] = log_level.upper()
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger('atlas_logging')
    logger.info("A.T.L.A.S. logging system initialized - Windows compatible format")
    logger.info(f"Log level: {log_level.upper()}")
    logger.info("Unicode characters will be automatically converted to ASCII")

def get_atlas_logger(name: str) -> logging.Logger:
    """Get a properly configured A.T.L.A.S. logger"""
    
    # Ensure logging is configured
    if not logging.getLogger().handlers:
        setup_atlas_logging()
    
    return logging.getLogger(name)

class AtlasLoggerMixin:
    """Mixin class to add standardized logging to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = get_atlas_logger(self.__class__.__name__)
        return self._logger

# Convenience functions for common log patterns
def log_system_startup(component_name: str) -> None:
    """Log system component startup"""
    logger = get_atlas_logger(component_name)
    logger.info(f"{component_name} starting up...")

def log_system_ready(component_name: str) -> None:
    """Log system component ready"""
    logger = get_atlas_logger(component_name)
    logger.info(f"{component_name} ready and operational")

def log_api_request(endpoint: str, method: str = "GET") -> None:
    """Log API request"""
    logger = get_atlas_logger('atlas_api')
    logger.info(f"API {method} {endpoint}")

def log_trading_action(action: str, symbol: str, details: str = "") -> None:
    """Log trading action"""
    logger = get_atlas_logger('atlas_trading')
    logger.info(f"Trading action: {action} {symbol} {details}")

def log_error_with_context(error: Exception, context: str = "") -> None:
    """Log error with context"""
    logger = get_atlas_logger('atlas_error')
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def log_performance_metric(metric_name: str, value: float, unit: str = "") -> None:
    """Log performance metric"""
    logger = get_atlas_logger('atlas_performance')
    logger.info(f"Performance metric - {metric_name}: {value} {unit}")

# Global flag to track if logging has been initialized
_logging_initialized = False

def ensure_windows_compatible_logging():
    """
    Ensure Windows-compatible logging is initialized before any component creates loggers.
    This function is idempotent and can be called multiple times safely.
    """
    global _logging_initialized

    if not _logging_initialized:
        # Force Windows-safe mode for all logging
        setup_atlas_logging('INFO')
        _logging_initialized = True

        # Get a test logger to verify setup
        test_logger = logging.getLogger('atlas_startup_test')
        test_logger.info("Windows-compatible logging initialized successfully")

def force_reinitialize_logging():
    """
    Force reinitialize logging system (useful for testing or recovery)
    """
    global _logging_initialized

    # Clear all existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Reset flag and reinitialize
    _logging_initialized = False
    ensure_windows_compatible_logging()

def force_windows_compatible_formatters():
    """
    Force all existing loggers to use Windows-compatible formatters
    This is a nuclear option to fix Unicode issues in already-created loggers
    """
    try:
        # Get all existing loggers
        loggers = [logging.getLogger(name) for name in logging.Logger.manager.loggerDict]
        loggers.append(logging.getLogger())  # Add root logger

        # Create Windows-compatible formatter
        formatter = WindowsCompatibleFormatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Apply to all handlers of all loggers
        for logger in loggers:
            for handler in logger.handlers:
                handler.setFormatter(formatter)

        print("Windows-compatible formatters applied to all existing loggers")

    except Exception as e:
        print(f"Error applying Windows-compatible formatters: {e}")

def patch_logging_module():
    """
    Monkey-patch the logging module to always use Windows-compatible loggers
    """
    original_getLogger = logging.getLogger

    def windows_compatible_getLogger(name=None):
        logger = original_getLogger(name)

        # Ensure this logger uses Windows-compatible formatting
        if not any(isinstance(handler.formatter, WindowsCompatibleFormatter)
                  for handler in logger.handlers):
            # If no Windows-compatible formatter found, ensure logging is set up
            ensure_windows_compatible_logging()

        return logger

    # Replace the original getLogger function
    logging.getLogger = windows_compatible_getLogger

# Initialize default logging with Windows compatibility immediately
ensure_windows_compatible_logging()

# Apply monkey-patch to ensure all future loggers are Windows-compatible
patch_logging_module()

# Force existing loggers to use Windows-compatible formatters
force_windows_compatible_formatters()

# Create a default logger that can be imported by other modules
logger = get_atlas_logger('atlas_system')

# Example usage patterns
if __name__ == "__main__":
    # Setup logging
    setup_atlas_logging('INFO')

    # Test different log types
    log_system_startup("TestComponent")
    log_api_request("/api/v1/test", "POST")
    log_trading_action("BUY", "AAPL", "100 shares at $150.00")
    log_performance_metric("response_time", 0.25, "seconds")
    log_system_ready("TestComponent")

    print("Logging test complete - check atlas_system.log file")
