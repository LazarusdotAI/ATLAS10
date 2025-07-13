#!/usr/bin/env python3
"""
A.T.L.A.S. Pattern Detection System
Consolidated TTM detector, Lee method scanner, and enhanced scanners
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json
import requests

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus

settings = Settings()

class AtlasTTMPatternDetector:
    """TTM Squeeze pattern detection"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize TTM pattern detector"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("TTM Pattern Detector initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"TTM Pattern Detector initialization failed: {e}")
            raise
    
    def calculate_ttm_squeeze(self, data):
        """Calculate TTM Squeeze indicators"""
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        bb_middle = data['Close'].rolling(window=bb_period).mean()
        bb_upper = bb_middle + (data['Close'].rolling(window=bb_period).std() * bb_std)
        bb_lower = bb_middle - (data['Close'].rolling(window=bb_period).std() * bb_std)
        
        # Keltner Channels
        kc_period = 20
        kc_atr_period = 10
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=kc_atr_period).mean()
        
        kc_middle = data['Close'].rolling(window=kc_period).mean()
        kc_upper = kc_middle + (atr * 1.5)
        kc_lower = kc_middle - (atr * 1.5)
        
        # Squeeze condition
        squeeze = (bb_lower > kc_lower) & (bb_upper < kc_upper)
        
        momentum = data['Close'] - ((bb_upper + bb_lower) / 2)
        
        return {
            'squeeze': squeeze,
            'momentum': momentum,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'kc_upper': kc_upper,
            'kc_lower': kc_lower
        }
    
    async def cleanup(self):
        """Cleanup TTM pattern detector"""
        self.logger.info("TTM pattern detector cleanup completed")


class AtlasLeeMethodScanner:
    """Lee Method pattern scanner with specific criteria"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize Lee Method scanner"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Lee Method Scanner initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Lee Method Scanner initialization failed: {e}")
            raise
    
    def detect_lee_method_pattern(self, data):
        """
        Detect Lee Method pattern with three specific criteria:
        1. Histogram Pattern Detection (3+ decreasing bars followed by uptick)
        2. Momentum Confirmation (current momentum > previous momentum)
        3. Multi-timeframe Analysis (weekly/daily trend alignment)
        """
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        histogram_pattern = self._detect_histogram_pattern(histogram)
        
        momentum_confirmation = self._detect_momentum_confirmation(histogram)
        
        trend_alignment = self._detect_trend_alignment(data)
        
        lee_signal = histogram_pattern & momentum_confirmation & trend_alignment
        
        return {
            'lee_signal': lee_signal,
            'histogram_pattern': histogram_pattern,
            'momentum_confirmation': momentum_confirmation,
            'trend_alignment': trend_alignment,
            'histogram': histogram,
            'macd': macd,
            'signal': signal
        }
    
    def _detect_histogram_pattern(self, histogram):
        """Detect 3+ decreasing histogram bars followed by uptick"""
        decreasing_count = 0
        pattern_detected = pd.Series(False, index=histogram.index)
        
        for i in range(3, len(histogram)):
            if (histogram.iloc[i-3] > histogram.iloc[i-2] > histogram.iloc[i-1] and
                histogram.iloc[i] > histogram.iloc[i-1]):
                pattern_detected.iloc[i] = True
        
        return pattern_detected
    
    def _detect_momentum_confirmation(self, histogram):
        """Detect current momentum > previous momentum"""
        momentum_conf = histogram > histogram.shift(1)
        return momentum_conf
    
    def _detect_trend_alignment(self, data):
        """Simplified trend alignment check"""
        short_ma = data['Close'].rolling(window=10).mean()
        short_trend = data['Close'] > short_ma
        
        long_ma = data['Close'].rolling(window=50).mean()
        long_trend = data['Close'] > long_ma
        
        alignment = short_trend & long_trend
        return alignment
    
    async def scan_symbols(self, symbols: List[str]) -> Dict[str, Any]:
        """Scan multiple symbols for Lee Method patterns"""
        results = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="6mo")
                
                if len(data) > 50:  # Ensure enough data
                    pattern_data = self.detect_lee_method_pattern(data)
                    
                    current_signal = pattern_data['lee_signal'].iloc[-1] if len(pattern_data['lee_signal']) > 0 else False
                    
                    results[symbol] = {
                        'has_pattern': bool(current_signal),
                        'histogram_value': float(pattern_data['histogram'].iloc[-1]) if len(pattern_data['histogram']) > 0 else 0.0,
                        'macd_value': float(pattern_data['macd'].iloc[-1]) if len(pattern_data['macd']) > 0 else 0.0,
                        'signal_strength': self._calculate_signal_strength(pattern_data),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    results[symbol] = {
                        'has_pattern': False,
                        'error': 'Insufficient data'
                    }
                    
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {e}")
                results[symbol] = {
                    'has_pattern': False,
                    'error': str(e)
                }
        
        return results
    
    def _calculate_signal_strength(self, pattern_data):
        """Calculate signal strength based on pattern criteria"""
        strength = 0.0
        
        if pattern_data['histogram_pattern'].iloc[-1]:
            strength += 0.4
        if pattern_data['momentum_confirmation'].iloc[-1]:
            strength += 0.3
        if pattern_data['trend_alignment'].iloc[-1]:
            strength += 0.3
        
        return strength
    
    async def cleanup(self):
        """Cleanup Lee Method scanner"""
        self.logger.info("Lee Method scanner cleanup completed")


class AtlasEnhancedScanner:
    """Enhanced pattern scanner with multiple detection methods"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.ttm_detector = AtlasTTMPatternDetector()
        self.lee_scanner = AtlasLeeMethodScanner()
        
    async def initialize(self):
        """Initialize enhanced scanner"""
        try:
            await self.ttm_detector.initialize()
            await self.lee_scanner.initialize()
            self.status = EngineStatus.ACTIVE
            self.logger.info("Enhanced Scanner initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Enhanced Scanner initialization failed: {e}")
            raise
    
    async def comprehensive_scan(self, symbols: List[str]) -> Dict[str, Any]:
        """Perform comprehensive pattern scan"""
        lee_results = await self.lee_scanner.scan_symbols(symbols)
        
        comprehensive_results = {
            'lee_method': lee_results,
            'scan_timestamp': datetime.now().isoformat(),
            'symbols_scanned': len(symbols),
            'patterns_found': sum(1 for result in lee_results.values() if result.get('has_pattern', False))
        }
        
        return comprehensive_results
    
    async def cleanup(self):
        """Cleanup enhanced scanner"""
        await self.ttm_detector.cleanup()
        await self.lee_scanner.cleanup()
        self.logger.info("Enhanced scanner cleanup completed")
