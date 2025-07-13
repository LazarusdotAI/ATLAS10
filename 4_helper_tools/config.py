"""
A.T.L.A.S AI Trading System - Configuration Management
Production-ready configuration with environment validation and fallbacks
"""

import os
import logging
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Production-ready application settings with validation"""
    
    # Application Settings
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    PORT: int = Field(default=8080, env="PORT")
    
    # Validation Mode - allows system to run without API keys for testing
    VALIDATION_MODE: bool = Field(default=False, env="VALIDATION_MODE")

    # API Keys - Required for production, optional in validation mode
    ALPACA_API_KEY: Optional[str] = Field(default=None, env="ALPACA_API_KEY")
    ALPACA_SECRET_KEY: Optional[str] = Field(default=None, env="ALPACA_SECRET_KEY")
    ALPACA_BASE_URL: str = Field(default="https://paper-api.alpaca.markets", env="ALPACA_BASE_URL")

    FMP_API_KEY: Optional[str] = Field(default=None, env="FMP_API_KEY")
    FMP_BASE_URL: str = Field(default="https://financialmodelingprep.com/api", env="FMP_BASE_URL")

    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(default=0.2, env="OPENAI_TEMPERATURE")
    
    # Optional APIs with fallbacks
    PREDICTO_API_KEY: Optional[str] = Field(default=None, env="PREDICTO_API_KEY")
    PREDICTO_BASE_URL: str = Field(default="https://api.predic.to", env="PREDICTO_BASE_URL")

    # Web Search APIs (for sentiment analysis and news)
    GOOGLE_SEARCH_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = Field(default=None, env="GOOGLE_SEARCH_ENGINE_ID")
    BING_SEARCH_API_KEY: Optional[str] = Field(default=None, env="BING_SEARCH_API_KEY")

    # Social Media APIs (for sentiment analysis)
    TWITTER_BEARER_TOKEN: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    REDDIT_CLIENT_ID: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")

    # ML Model Configuration
    ML_MODELS_ENABLED: bool = Field(default=True, env="ML_MODELS_ENABLED")
    SENTIMENT_MODEL_PATH: str = Field(default="distilbert-base-uncased-finetuned-sst-2-english", env="SENTIMENT_MODEL_PATH")
    LSTM_MODEL_PATH: str = Field(default="models/lstm_predictor.h5", env="LSTM_MODEL_PATH")
    ML_PREDICTION_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="ML_PREDICTION_CONFIDENCE_THRESHOLD")

    # Options Trading Configuration
    OPTIONS_TRADING_ENABLED: bool = Field(default=True, env="OPTIONS_TRADING_ENABLED")
    OPTIONS_MAX_EXPIRY_DAYS: int = Field(default=45, env="OPTIONS_MAX_EXPIRY_DAYS")
    OPTIONS_MIN_VOLUME: int = Field(default=100, env="OPTIONS_MIN_VOLUME")
    OPTIONS_MAX_SPREAD_PERCENT: float = Field(default=5.0, env="OPTIONS_MAX_SPREAD_PERCENT")

    # Proactive Assistant Configuration
    PROACTIVE_ASSISTANT_ENABLED: bool = Field(default=True, env="PROACTIVE_ASSISTANT_ENABLED")
    MORNING_BRIEFING_TIME: str = Field(default="09:00", env="MORNING_BRIEFING_TIME")
    ALERT_COOLDOWN_MINUTES: int = Field(default=15, env="ALERT_COOLDOWN_MINUTES")
    MIN_SIGNAL_STRENGTH: int = Field(default=4, env="MIN_SIGNAL_STRENGTH")

    # Performance Optimization
    PERFORMANCE_MONITORING_ENABLED: bool = Field(default=True, env="PERFORMANCE_MONITORING_ENABLED")
    MEMORY_USAGE_THRESHOLD: float = Field(default=80.0, env="MEMORY_USAGE_THRESHOLD")
    CPU_USAGE_THRESHOLD: float = Field(default=80.0, env="CPU_USAGE_THRESHOLD")

    # Enhanced Memory System
    ENHANCED_MEMORY_ENABLED: bool = Field(default=True, env="ENHANCED_MEMORY_ENABLED")
    CONVERSATION_MEMORY_LIMIT: int = Field(default=1000, env="CONVERSATION_MEMORY_LIMIT")
    MEMORY_IMPORTANCE_THRESHOLD: float = Field(default=0.5, env="MEMORY_IMPORTANCE_THRESHOLD")
    
    # Trading Configuration
    PAPER_TRADING: bool = Field(default=True, env="PAPER_TRADING")
    DEFAULT_RISK_PERCENT: float = Field(default=2.0, env="DEFAULT_RISK_PERCENT")
    MAX_POSITIONS: int = Field(default=10, env="MAX_POSITIONS")
    
    # Performance Settings
    API_TIMEOUT: int = Field(default=30, env="API_TIMEOUT")
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")
    MAX_SCAN_RESULTS: int = Field(default=50, env="MAX_SCAN_RESULTS")
    
    # Database Settings
    DATABASE_URL: str = Field(default="sqlite:///atlas.db", env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=5, env="DATABASE_POOL_SIZE")

    # Multiple Database Configuration (Enhanced Memory System)
    MEMORY_DB_PATH: str = Field(default="atlas_memory.db", env="MEMORY_DB_PATH")
    RAG_DB_PATH: str = Field(default="atlas_rag.db", env="RAG_DB_PATH")
    COMPLIANCE_DB_PATH: str = Field(default="atlas_compliance.db", env="COMPLIANCE_DB_PATH")
    FEEDBACK_DB_PATH: str = Field(default="atlas_feedback.db", env="FEEDBACK_DB_PATH")
    ENHANCED_MEMORY_DB_PATH: str = Field(default="atlas_enhanced_memory.db", env="ENHANCED_MEMORY_DB_PATH")
    
    # Initialization Settings
    STARTUP_TIMEOUT: int = Field(default=60, env="STARTUP_TIMEOUT")
    BACKGROUND_INIT: bool = Field(default=True, env="BACKGROUND_INIT")
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {valid_levels}')
        return v.upper()

    @field_validator('PORT')
    @classmethod
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError('PORT must be between 1024 and 65535')
        return v

    @field_validator('DEFAULT_RISK_PERCENT')
    @classmethod
    def validate_risk_percent(cls, v):
        if not 0.1 <= v <= 10.0:
            raise ValueError('DEFAULT_RISK_PERCENT must be between 0.1 and 10.0')
        return v

    def __init__(self, **kwargs):
        """Initialize settings with validation mode support"""
        super().__init__(**kwargs)

        # In production mode, ensure critical API keys are present
        if not self.VALIDATION_MODE:
            missing_keys = []

            if not self.ALPACA_API_KEY:
                missing_keys.append("ALPACA_API_KEY")
            if not self.ALPACA_SECRET_KEY:
                missing_keys.append("ALPACA_SECRET_KEY")
            if not self.FMP_API_KEY:
                missing_keys.append("FMP_API_KEY")
            if not self.OPENAI_API_KEY:
                missing_keys.append("OPENAI_API_KEY")

            if missing_keys:
                raise ValueError(
                    f"Missing required API keys for production mode: {', '.join(missing_keys)}. "
                    f"Set VALIDATION_MODE=true to run without API keys for testing."
                )

    def is_api_available(self, api_name: str) -> bool:
        """Check if a specific API is available (has valid key)"""
        api_keys = {
            "alpaca": self.ALPACA_API_KEY and self.ALPACA_SECRET_KEY,
            "fmp": self.FMP_API_KEY,
            "openai": self.OPENAI_API_KEY,
            "predicto": self.PREDICTO_API_KEY
        }
        return bool(api_keys.get(api_name.lower(), False))

    def get_available_apis(self) -> list[str]:
        """Get list of available APIs based on configured keys"""
        available = []
        if self.is_api_available("alpaca"):
            available.append("alpaca")
        if self.is_api_available("fmp"):
            available.append("fmp")
        if self.is_api_available("openai"):
            available.append("openai")
        if self.is_api_available("predicto"):
            available.append("predicto")
        return available
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables


# Global settings instance
settings = Settings()


# Logging configuration - Windows compatible format without Unicode characters
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "atlas.log",
            "mode": "a"
        }
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        }
    }
}


def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration and return status"""
    status = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "api_keys": {},
        "validation_mode": settings.VALIDATION_MODE
    }

    # In validation mode, missing API keys are warnings, not errors
    if settings.VALIDATION_MODE:
        status["warnings"].append("Running in VALIDATION_MODE - some features may be limited")

    # Check required API keys
    required_keys = {
        "ALPACA_API_KEY": settings.ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": settings.ALPACA_SECRET_KEY,
        "FMP_API_KEY": settings.FMP_API_KEY,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY
    }

    for key_name, key_value in required_keys.items():
        if not key_value or key_value.startswith("your_") or key_value == "placeholder":
            if settings.VALIDATION_MODE:
                status["warnings"].append(f"Missing {key_name} (validation mode)")
                status["api_keys"][key_name] = "missing_validation_mode"
            else:
                status["errors"].append(f"Missing or invalid {key_name}")
                status["valid"] = False
                status["api_keys"][key_name] = "invalid"
        else:
            status["api_keys"][key_name] = "valid"

    # Check optional keys
    optional_keys = {
        "PREDICTO_API_KEY": settings.PREDICTO_API_KEY
    }

    for key_name, key_value in optional_keys.items():
        if not key_value:
            status["warnings"].append(f"Optional {key_name} not configured")
            status["api_keys"][key_name] = "missing"
        else:
            status["api_keys"][key_name] = "valid"

    return status


def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "timeout": settings.API_TIMEOUT
    }


def get_api_config(service: str) -> Dict[str, Any]:
    """Get API configuration for specific service with validation mode support"""
    configs = {
        "alpaca": {
            "api_key": settings.ALPACA_API_KEY,
            "secret_key": settings.ALPACA_SECRET_KEY,
            "base_url": settings.ALPACA_BASE_URL,
            "paper_trading": settings.PAPER_TRADING,
            "available": settings.is_api_available("alpaca"),
            "validation_mode": settings.VALIDATION_MODE
        },
        "fmp": {
            "api_key": settings.FMP_API_KEY,
            "base_url": settings.FMP_BASE_URL,
            "available": settings.is_api_available("fmp"),
            "validation_mode": settings.VALIDATION_MODE
        },
        "openai": {
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "temperature": settings.OPENAI_TEMPERATURE,
            "available": settings.is_api_available("openai"),
            "validation_mode": settings.VALIDATION_MODE
        },
        "predicto": {
            "api_key": settings.PREDICTO_API_KEY,
            "base_url": settings.PREDICTO_BASE_URL,
            "enabled": bool(settings.PREDICTO_API_KEY),
            "available": settings.is_api_available("predicto"),
            "validation_mode": settings.VALIDATION_MODE
        }
    }

    config = configs.get(service, {})

    # Add global validation mode flag to all configs
    if config:
        config["validation_mode"] = settings.VALIDATION_MODE
        config["available"] = config.get("available", False)

    return config


# Export commonly used settings
__all__ = [
    "settings",
    "LOGGING_CONFIG", 
    "validate_environment",
    "get_database_config",
    "get_api_config"
]
