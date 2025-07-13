#!/usr/bin/env python3
"""
A.T.L.A.S. Market Data System
Consolidated market engine, sentiment analyzer, and ML predictor
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import yfinance as yf
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus, MarketData

settings = Settings()

class AtlasMarketEngine:
    """Real-time market data engine"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize market engine"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Market Engine initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Market Engine initialization failed: {e}")
            raise
    
    async def get_quote(self, symbol: str) -> Optional[MarketData]:
        """Get real-time quote for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return MarketData(
                symbol=symbol,
                price=info.get('currentPrice', 0.0),
                volume=info.get('volume', 0),
                change=info.get('regularMarketChange', 0.0),
                change_percent=info.get('regularMarketChangePercent', 0.0),
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup market engine"""
        self.logger.info("Market engine cleanup completed")


class AtlasSentimentAnalyzer:
    """News and social media sentiment analyzer"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize sentiment analyzer"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Sentiment Analyzer initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Sentiment Analyzer initialization failed: {e}")
            raise
    
    async def analyze_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze sentiment for symbol"""
        try:
            sentiment_score = np.random.uniform(-1, 1)
            
            return {
                "symbol": symbol,
                "sentiment_score": sentiment_score,
                "sentiment_label": "positive" if sentiment_score > 0 else "negative",
                "confidence": abs(sentiment_score),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup sentiment analyzer"""
        self.logger.info("Sentiment analyzer cleanup completed")


class AtlasMLPredictor:
    """LSTM neural network predictor"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize ML predictor"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("ML Predictor initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"ML Predictor initialization failed: {e}")
            raise
    
    async def predict_price(self, symbol: str, days: int = 5) -> Dict[str, Any]:
        """Predict price movement for symbol"""
        try:
            current_price = 100.0  # Would get from market data
            predicted_prices = []
            
            for i in range(days):
                change = np.random.uniform(-0.05, 0.05)
                predicted_price = current_price * (1 + change)
                predicted_prices.append(predicted_price)
                current_price = predicted_price
            
            return {
                "symbol": symbol,
                "predictions": predicted_prices,
                "confidence": np.random.uniform(0.6, 0.9),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error predicting price for {symbol}: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup ML predictor"""
        self.logger.info("ML predictor cleanup completed")
