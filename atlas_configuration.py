#!/usr/bin/env python3
"""
A.T.L.A.S. Configuration System
Consolidated config, models, logging, and startup initialization
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import sys

class EngineStatus(Enum):
    """Engine status enumeration"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

ERROR_HANDLING_AVAILABLE = True

class Settings(BaseSettings):
    """Application settings"""
    
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    FMP_API_KEY: str = Field(default="", description="Financial Modeling Prep API key")
    ALPACA_API_KEY: str = Field(default="", description="Alpaca API key")
    ALPACA_SECRET_KEY: str = Field(default="", description="Alpaca secret key")
    PREDICTO_API_KEY: str = Field(default="", description="Predicto API key")
    
    DATABASE_URL: str = Field(default="sqlite:///atlas.db", description="Database URL")
    
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8080, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    PAPER_TRADING: bool = Field(default=True, description="Use paper trading")
    MAX_POSITION_SIZE: float = Field(default=10000.0, description="Maximum position size")
    RISK_TOLERANCE: float = Field(default=0.02, description="Risk tolerance")
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

class AIResponse(BaseModel):
    """AI response model"""
    response: str
    type: str
    confidence: float
    context: Dict[str, Any] = Field(default_factory=dict)

class TradingSignal(BaseModel):
    """Trading signal model"""
    symbol: str
    action: str
    price: float
    quantity: int
    confidence: float
    timestamp: str
    reasoning: str

class MarketData(BaseModel):
    """Market data model"""
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: str

class PortfolioPosition(BaseModel):
    """Portfolio position model"""
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float

class RiskMetrics(BaseModel):
    """Risk metrics model"""
    var_95: float
    var_99: float
    expected_shortfall: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('atlas_system.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('atlas')

logger = setup_logging()
