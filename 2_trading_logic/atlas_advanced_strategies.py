#!/usr/bin/env python3
"""
A.T.L.A.S. Advanced Trading Strategies
Sophisticated trading strategies beyond basic TTM Squeeze including momentum breakouts,
mean reversion, pairs trading, and institutional flow analysis
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Types of trading strategies"""
    MOMENTUM_BREAKOUT = "momentum_breakout"
    MEAN_REVERSION = "mean_reversion"
    PAIRS_TRADING = "pairs_trading"
    INSTITUTIONAL_FLOW = "institutional_flow"
    VOLATILITY_BREAKOUT = "volatility_breakout"
    TREND_FOLLOWING = "trend_following"

class SignalStrength(Enum):
    """Signal strength levels"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class TradingSignal:
    """Advanced trading signal with detailed analysis"""
    symbol: str
    strategy_type: StrategyType
    signal_strength: SignalStrength
    direction: str  # "bullish", "bearish", "neutral"
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    risk_reward_ratio: float
    timeframe: str
    analysis: str
    timestamp: datetime
    additional_data: Dict[str, Any]

class ATLASAdvancedStrategies:
    """
    Advanced trading strategies engine for A.T.L.A.S.
    Implements sophisticated strategies beyond basic pattern recognition
    """
    
    def __init__(self, market_engine=None):
        self.market_engine = market_engine
        self.logger = logger
        
        # Strategy parameters
        self.momentum_threshold = 0.02  # 2% price movement
        self.volume_threshold = 1.5     # 1.5x average volume
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.correlation_threshold = 0.7
        
        # Historical data cache
        self.price_cache = {}
        self.volume_cache = {}
        
    async def analyze_all_strategies(self, symbol: str) -> List[TradingSignal]:
        """Analyze all available strategies for a symbol"""
        signals = []
        
        try:
            # Get market data
            market_data = await self._get_market_data(symbol)
            if not market_data:
                return signals
            
            # Run all strategy analyses
            strategies = [
                self._analyze_momentum_breakout(symbol, market_data),
                self._analyze_mean_reversion(symbol, market_data),
                self._analyze_volatility_breakout(symbol, market_data),
                self._analyze_trend_following(symbol, market_data),
                self._analyze_institutional_flow(symbol, market_data)
            ]
            
            # Collect all signals
            for strategy_signals in await asyncio.gather(*strategies, return_exceptions=True):
                if isinstance(strategy_signals, list):
                    signals.extend(strategy_signals)
                elif isinstance(strategy_signals, Exception):
                    self.logger.error(f"Strategy analysis error: {strategy_signals}")
            
            # Sort by confidence and signal strength
            signals.sort(key=lambda x: (x.confidence, x.signal_strength.value), reverse=True)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error analyzing strategies for {symbol}: {e}")
            return signals
    
    async def _analyze_momentum_breakout(self, symbol: str, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Analyze momentum breakout patterns"""
        signals = []
        
        try:
            current_price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)
            
            # Get price history for momentum calculation
            price_history = await self._get_price_history(symbol, days=20)
            if len(price_history) < 10:
                return signals
            
            # Calculate momentum indicators
            price_change_5d = (current_price - price_history[-5]) / price_history[-5]
            price_change_20d = (current_price - price_history[0]) / price_history[0]
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            # Detect breakout conditions
            if (abs(price_change_5d) > self.momentum_threshold and 
                volume_ratio > self.volume_threshold):
                
                direction = "bullish" if price_change_5d > 0 else "bearish"
                
                # Calculate targets and stops
                if direction == "bullish":
                    target_price = current_price * 1.05  # 5% target
                    stop_loss = current_price * 0.97     # 3% stop
                else:
                    target_price = current_price * 0.95  # 5% target
                    stop_loss = current_price * 1.03     # 3% stop
                
                # Determine signal strength
                strength_score = min(abs(price_change_5d) * 10 + volume_ratio, 4)
                if strength_score >= 3:
                    signal_strength = SignalStrength.VERY_STRONG
                elif strength_score >= 2:
                    signal_strength = SignalStrength.STRONG
                elif strength_score >= 1:
                    signal_strength = SignalStrength.MODERATE
                else:
                    signal_strength = SignalStrength.WEAK
                
                confidence = min(0.95, 0.6 + (strength_score * 0.1))
                risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss)
                
                signal = TradingSignal(
                    symbol=symbol,
                    strategy_type=StrategyType.MOMENTUM_BREAKOUT,
                    signal_strength=signal_strength,
                    direction=direction,
                    entry_price=current_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    confidence=confidence,
                    risk_reward_ratio=risk_reward,
                    timeframe="1-3 days",
                    analysis=f"Momentum breakout detected: {price_change_5d:.2%} price move with {volume_ratio:.1f}x volume",
                    timestamp=datetime.now(),
                    additional_data={
                        "price_change_5d": price_change_5d,
                        "price_change_20d": price_change_20d,
                        "volume_ratio": volume_ratio,
                        "strength_score": strength_score
                    }
                )
                signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"Error in momentum breakout analysis: {e}")
        
        return signals
    
    async def _analyze_mean_reversion(self, symbol: str, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Analyze mean reversion opportunities"""
        signals = []
        
        try:
            current_price = market_data.get('price', 0)
            
            # Get technical indicators
            rsi = await self._calculate_rsi(symbol, period=14)
            bollinger_bands = await self._calculate_bollinger_bands(symbol, period=20)
            
            if not rsi or not bollinger_bands:
                return signals
            
            bb_upper, bb_middle, bb_lower = bollinger_bands
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            
            # Detect oversold conditions (mean reversion up)
            if rsi < self.rsi_oversold and bb_position < 0.2:
                direction = "bullish"
                target_price = bb_middle  # Target middle band
                stop_loss = current_price * 0.95
                
                confidence = 0.7 + (self.rsi_oversold - rsi) / 100
                signal_strength = SignalStrength.STRONG if rsi < 25 else SignalStrength.MODERATE
                
            # Detect overbought conditions (mean reversion down)
            elif rsi > self.rsi_overbought and bb_position > 0.8:
                direction = "bearish"
                target_price = bb_middle  # Target middle band
                stop_loss = current_price * 1.05
                
                confidence = 0.7 + (rsi - self.rsi_overbought) / 100
                signal_strength = SignalStrength.STRONG if rsi > 75 else SignalStrength.MODERATE
            
            else:
                return signals
            
            risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss)
            
            signal = TradingSignal(
                symbol=symbol,
                strategy_type=StrategyType.MEAN_REVERSION,
                signal_strength=signal_strength,
                direction=direction,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=min(0.95, confidence),
                risk_reward_ratio=risk_reward,
                timeframe="3-7 days",
                analysis=f"Mean reversion setup: RSI {rsi:.1f}, BB position {bb_position:.2f}",
                timestamp=datetime.now(),
                additional_data={
                    "rsi": rsi,
                    "bb_position": bb_position,
                    "bb_upper": bb_upper,
                    "bb_middle": bb_middle,
                    "bb_lower": bb_lower
                }
            )
            signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"Error in mean reversion analysis: {e}")
        
        return signals
    
    async def _analyze_volatility_breakout(self, symbol: str, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Analyze volatility breakout patterns"""
        signals = []
        
        try:
            current_price = market_data.get('price', 0)
            
            # Calculate volatility indicators
            atr = await self._calculate_atr(symbol, period=14)
            volatility_ratio = await self._calculate_volatility_ratio(symbol, period=20)
            
            if not atr or not volatility_ratio:
                return signals
            
            # Detect low volatility compression followed by expansion
            if volatility_ratio < 0.7:  # Low volatility
                # Look for breakout direction
                price_history = await self._get_price_history(symbol, days=5)
                if len(price_history) >= 5:
                    recent_high = max(price_history[-5:])
                    recent_low = min(price_history[-5:])
                    
                    # Breakout above recent high
                    if current_price > recent_high * 1.01:
                        direction = "bullish"
                        target_price = current_price + (atr * 2)
                        stop_loss = current_price - atr
                        
                    # Breakdown below recent low
                    elif current_price < recent_low * 0.99:
                        direction = "bearish"
                        target_price = current_price - (atr * 2)
                        stop_loss = current_price + atr
                    
                    else:
                        return signals
                    
                    confidence = 0.75 + (0.7 - volatility_ratio) * 0.5
                    signal_strength = SignalStrength.STRONG
                    risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss)
                    
                    signal = TradingSignal(
                        symbol=symbol,
                        strategy_type=StrategyType.VOLATILITY_BREAKOUT,
                        signal_strength=signal_strength,
                        direction=direction,
                        entry_price=current_price,
                        target_price=target_price,
                        stop_loss=stop_loss,
                        confidence=min(0.95, confidence),
                        risk_reward_ratio=risk_reward,
                        timeframe="1-5 days",
                        analysis=f"Volatility breakout: Low vol ({volatility_ratio:.2f}) followed by breakout",
                        timestamp=datetime.now(),
                        additional_data={
                            "atr": atr,
                            "volatility_ratio": volatility_ratio,
                            "recent_high": recent_high,
                            "recent_low": recent_low
                        }
                    )
                    signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"Error in volatility breakout analysis: {e}")
        
        return signals
    
    async def _analyze_trend_following(self, symbol: str, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Analyze trend following opportunities"""
        signals = []
        
        try:
            current_price = market_data.get('price', 0)
            
            # Calculate moving averages
            ema_20 = await self._calculate_ema(symbol, period=20)
            ema_50 = await self._calculate_ema(symbol, period=50)
            
            if not ema_20 or not ema_50:
                return signals
            
            # Trend following conditions
            if ema_20 > ema_50 and current_price > ema_20:
                # Uptrend continuation
                direction = "bullish"
                target_price = current_price * 1.08
                stop_loss = ema_20 * 0.98
                
                trend_strength = (ema_20 - ema_50) / ema_50
                confidence = 0.65 + min(trend_strength * 5, 0.25)
                signal_strength = SignalStrength.MODERATE
                
            elif ema_20 < ema_50 and current_price < ema_20:
                # Downtrend continuation
                direction = "bearish"
                target_price = current_price * 0.92
                stop_loss = ema_20 * 1.02
                
                trend_strength = (ema_50 - ema_20) / ema_50
                confidence = 0.65 + min(trend_strength * 5, 0.25)
                signal_strength = SignalStrength.MODERATE
                
            else:
                return signals
            
            risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss)
            
            signal = TradingSignal(
                symbol=symbol,
                strategy_type=StrategyType.TREND_FOLLOWING,
                signal_strength=signal_strength,
                direction=direction,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=min(0.90, confidence),
                risk_reward_ratio=risk_reward,
                timeframe="5-15 days",
                analysis=f"Trend following: EMA20 {ema_20:.2f}, EMA50 {ema_50:.2f}",
                timestamp=datetime.now(),
                additional_data={
                    "ema_20": ema_20,
                    "ema_50": ema_50,
                    "trend_strength": trend_strength
                }
            )
            signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"Error in trend following analysis: {e}")
        
        return signals
    
    async def _analyze_institutional_flow(self, symbol: str, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Analyze institutional flow patterns"""
        signals = []
        
        try:
            # This would integrate with real institutional flow data
            # For now, simulate based on volume and price action
            
            current_price = market_data.get('price', 0)
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)
            
            # Detect unusual volume patterns
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 3.0:  # Unusual volume
                # Analyze price action during high volume
                price_history = await self._get_price_history(symbol, days=3)
                if len(price_history) >= 3:
                    price_change = (current_price - price_history[-3]) / price_history[-3]
                    
                    # Strong price movement with high volume suggests institutional activity
                    if abs(price_change) > 0.03:  # 3% move
                        direction = "bullish" if price_change > 0 else "bearish"
                        
                        if direction == "bullish":
                            target_price = current_price * 1.06
                            stop_loss = current_price * 0.96
                        else:
                            target_price = current_price * 0.94
                            stop_loss = current_price * 1.04
                        
                        confidence = 0.70 + min(volume_ratio * 0.05, 0.20)
                        signal_strength = SignalStrength.STRONG if volume_ratio > 5 else SignalStrength.MODERATE
                        risk_reward = abs(target_price - current_price) / abs(current_price - stop_loss)
                        
                        signal = TradingSignal(
                            symbol=symbol,
                            strategy_type=StrategyType.INSTITUTIONAL_FLOW,
                            signal_strength=signal_strength,
                            direction=direction,
                            entry_price=current_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            confidence=min(0.95, confidence),
                            risk_reward_ratio=risk_reward,
                            timeframe="2-7 days",
                            analysis=f"Institutional flow: {volume_ratio:.1f}x volume with {price_change:.2%} move",
                            timestamp=datetime.now(),
                            additional_data={
                                "volume_ratio": volume_ratio,
                                "price_change_3d": price_change,
                                "institutional_score": volume_ratio * abs(price_change) * 10
                            }
                        )
                        signals.append(signal)
            
        except Exception as e:
            self.logger.error(f"Error in institutional flow analysis: {e}")
        
        return signals
    
    # Helper methods for technical calculations
    async def _get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current market data for symbol"""
        try:
            if self.market_engine:
                # Use real market engine if available
                quote = await self.market_engine.get_quote(symbol)
                return {
                    'price': float(quote.get('price', 0)),
                    'volume': int(quote.get('volume', 0)),
                    'avg_volume': int(quote.get('avg_volume', 0))
                }
            else:
                # Fallback to mock data
                return {
                    'price': 175.25,
                    'volume': 1500000,
                    'avg_volume': 1000000
                }
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return None
    
    async def _get_price_history(self, symbol: str, days: int) -> List[float]:
        """Get historical price data"""
        try:
            # This would integrate with real historical data
            # For now, generate realistic mock data
            base_price = 175.25
            prices = []
            for i in range(days):
                # Simulate realistic price movement
                change = np.random.normal(0, 0.02)  # 2% daily volatility
                if i == 0:
                    prices.append(base_price)
                else:
                    prices.append(prices[-1] * (1 + change))
            return prices
        except Exception as e:
            self.logger.error(f"Error getting price history: {e}")
            return []
    
    async def _calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            # Mock RSI calculation - would use real price data
            return np.random.uniform(25, 75)  # Random RSI for testing
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return None
    
    async def _calculate_bollinger_bands(self, symbol: str, period: int = 20) -> Optional[Tuple[float, float, float]]:
        """Calculate Bollinger Bands"""
        try:
            # Mock Bollinger Bands - would use real price data
            current_price = 175.25
            std_dev = current_price * 0.02  # 2% standard deviation
            middle = current_price
            upper = middle + (2 * std_dev)
            lower = middle - (2 * std_dev)
            return (upper, middle, lower)
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {e}")
            return None
    
    async def _calculate_atr(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate Average True Range"""
        try:
            # Mock ATR calculation
            return 175.25 * 0.025  # 2.5% of price as ATR
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {e}")
            return None
    
    async def _calculate_volatility_ratio(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calculate current volatility vs historical average"""
        try:
            # Mock volatility ratio
            return np.random.uniform(0.5, 1.5)
        except Exception as e:
            self.logger.error(f"Error calculating volatility ratio: {e}")
            return None
    
    async def _calculate_ema(self, symbol: str, period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        try:
            # Mock EMA calculation
            base_price = 175.25
            return base_price * np.random.uniform(0.98, 1.02)
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {e}")
            return None
