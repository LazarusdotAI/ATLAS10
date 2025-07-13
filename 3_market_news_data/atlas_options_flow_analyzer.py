"""
A.T.L.A.S Options Flow Analysis Module
Advanced options flow analysis with unusual activity detection and automated trading signals
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
from collections import defaultdict

from config import settings
from models import OptionType, OptionContract
from atlas_performance_optimizer import performance_optimizer

# Optional ML imports with graceful fallback
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class OptionsFlowData:
    """Options flow data point"""
    symbol: str
    option_type: str  # 'call' or 'put'
    strike: float
    expiration: str
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    premium: float
    unusual_activity_score: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'option_type': self.option_type,
            'strike': self.strike,
            'expiration': self.expiration,
            'volume': self.volume,
            'open_interest': self.open_interest,
            'implied_volatility': self.implied_volatility,
            'delta': self.delta,
            'premium': self.premium,
            'unusual_activity_score': self.unusual_activity_score,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class OptionsSignal:
    """Options flow trading signal"""
    symbol: str
    signal_type: str  # 'bullish', 'bearish', 'neutral'
    confidence: float
    recommended_strategy: str  # 'bull_call_spread', 'bear_put_spread', etc.
    entry_strikes: List[float]
    expiration: str
    max_risk: float
    max_reward: float
    probability_profit: float
    unusual_flow_indicators: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'recommended_strategy': self.recommended_strategy,
            'entry_strikes': self.entry_strikes,
            'expiration': self.expiration,
            'max_risk': self.max_risk,
            'max_reward': self.max_reward,
            'probability_profit': self.probability_profit,
            'unusual_flow_indicators': self.unusual_flow_indicators,
            'timestamp': self.timestamp.isoformat()
        }


class UnusualActivityDetector:
    """Detects unusual options activity patterns"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Thresholds for unusual activity
        self.volume_threshold_multiplier = 3.0  # 3x average volume
        self.oi_ratio_threshold = 0.5  # Volume > 50% of open interest
        self.iv_spike_threshold = 0.2  # 20% IV increase
        self.premium_threshold = 100000  # $100k+ premium
        
        # Historical data for comparison
        self.historical_data = defaultdict(list)
        self.lookback_days = 30
    
    def detect_unusual_activity(self, flow_data: List[OptionsFlowData]) -> List[OptionsFlowData]:
        """Detect unusual activity in options flow data"""
        try:
            unusual_flows = []
            
            for data in flow_data:
                score = self._calculate_unusual_score(data)
                
                if score > 0.6:  # Threshold for unusual activity
                    data.unusual_activity_score = score
                    unusual_flows.append(data)
            
            # Sort by unusual activity score
            unusual_flows.sort(key=lambda x: x.unusual_activity_score, reverse=True)
            
            return unusual_flows
            
        except Exception as e:
            self.logger.error(f"Error detecting unusual activity: {e}")
            return []
    
    def _calculate_unusual_score(self, data: OptionsFlowData) -> float:
        """Calculate unusual activity score for options flow"""
        try:
            score = 0.0
            
            # Volume analysis
            avg_volume = self._get_average_volume(data.symbol, data.strike, data.option_type)
            if avg_volume > 0 and data.volume > avg_volume * self.volume_threshold_multiplier:
                score += 0.3
            
            # Open interest ratio
            if data.open_interest > 0:
                oi_ratio = data.volume / data.open_interest
                if oi_ratio > self.oi_ratio_threshold:
                    score += 0.2
            
            # Premium size
            total_premium = data.volume * data.premium * 100  # Convert to dollars
            if total_premium > self.premium_threshold:
                score += 0.2
            
            # Implied volatility spike
            avg_iv = self._get_average_iv(data.symbol, data.strike, data.option_type)
            if avg_iv > 0 and data.implied_volatility > avg_iv * (1 + self.iv_spike_threshold):
                score += 0.2
            
            # Delta concentration (unusual strikes)
            if abs(data.delta) < 0.2 or abs(data.delta) > 0.8:  # Very OTM or ITM
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating unusual score: {e}")
            return 0.0
    
    def _get_average_volume(self, symbol: str, strike: float, option_type: str) -> float:
        """Get average volume for comparison"""
        # This would query historical data
        # For now, return a mock average
        return 100.0
    
    def _get_average_iv(self, symbol: str, strike: float, option_type: str) -> float:
        """Get average implied volatility for comparison"""
        # This would query historical data
        # For now, return a mock average
        return 0.25


class OptionsFlowAnalyzer:
    """
    Options flow analysis with unusual activity detection and automated trading signals
    """
    
    def __init__(self, market_engine=None, options_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        self.options_engine = options_engine
        
        # Components
        self.unusual_detector = UnusualActivityDetector()
        
        # Configuration
        self.enabled = settings.OPTIONS_TRADING_ENABLED
        self.scan_symbols = self._get_scan_universe()
        self.min_confidence = 0.7
        
        # ML model (if available)
        self.ml_model = None
        self.scaler = None
        self.ml_enabled = ML_AVAILABLE and settings.ML_MODELS_ENABLED
        
        # Flow tracking
        self.flow_history = []
        self.signals_generated = []
        
        self.logger.info(f"[DATA] Options Flow Analyzer initialized - enabled: {self.enabled}, ML: {self.ml_enabled}")
    
    async def initialize(self):
        """Initialize ML models if available"""
        if self.ml_enabled:
            try:
                self.logger.info("[TOOL] Initializing options flow ML model...")
                self.ml_model = self._create_ml_model()
                self.scaler = StandardScaler()
                self.logger.info("[OK] Options flow ML model initialized")
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to initialize ML model: {e}")
                self.ml_enabled = False
    
    @performance_optimizer.performance_monitor("options_flow_analysis")
    async def analyze_options_flow(self, symbols: Optional[List[str]] = None) -> List[OptionsSignal]:
        """Analyze options flow for unusual activity and generate signals"""
        try:
            if not self.enabled:
                return []
            
            symbols = symbols or self.scan_symbols
            all_signals = []
            
            for symbol in symbols:
                try:
                    # Get options flow data
                    flow_data = await self._get_options_flow_data(symbol)
                    
                    if not flow_data:
                        continue
                    
                    # Detect unusual activity
                    unusual_flows = self.unusual_detector.detect_unusual_activity(flow_data)
                    
                    if not unusual_flows:
                        continue
                    
                    # Generate trading signals
                    signals = await self._generate_trading_signals(symbol, unusual_flows)
                    all_signals.extend(signals)
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing flow for {symbol}: {e}")
                    continue
            
            # Filter and rank signals
            filtered_signals = self._filter_signals(all_signals)
            
            self.logger.info(f"[DATA] Options flow analysis complete: {len(filtered_signals)} signals generated")
            
            return filtered_signals
            
        except Exception as e:
            self.logger.error(f"Error in options flow analysis: {e}")
            return []
    
    async def _get_options_flow_data(self, symbol: str) -> List[OptionsFlowData]:
        """Get options flow data for symbol"""
        try:
            # This would integrate with options data provider
            # For now, generate mock data
            return self._generate_mock_flow_data(symbol)
            
        except Exception as e:
            self.logger.error(f"Error getting options flow data for {symbol}: {e}")
            return []
    
    def _generate_mock_flow_data(self, symbol: str) -> List[OptionsFlowData]:
        """Generate enhanced mock options flow data with realistic patterns"""
        flow_data = []
        base_price = 175.25  # Realistic price for major stocks

        # Generate multiple expiration dates
        expirations = [
            (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),   # Weekly
            (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),  # Monthly
        ]

        # Generate realistic flow patterns with varying unusual activity
        for exp_idx, expiration in enumerate(expirations):
            # Generate call flows
            for i in range(4):
                strike = base_price + (i + 1) * 5  # OTM calls

                # Simulate unusual activity (30% chance)
                is_unusual = np.random.random() > 0.7
                volume_multiplier = np.random.uniform(3, 8) if is_unusual else 1
                base_volume = int(np.random.randint(200, 800) * volume_multiplier)

                # Calculate realistic Greeks based on moneyness
                moneyness = (base_price - strike) / base_price
                delta = max(0.05, min(0.95, 0.5 + moneyness * 2))

                call_flow = OptionsFlowData(
                    symbol=symbol,
                    option_type='call',
                    strike=strike,
                    expiration=expiration,
                    volume=base_volume,
                    open_interest=base_volume * np.random.randint(3, 8),
                    implied_volatility=np.random.uniform(0.18, 0.45),
                    delta=delta,
                    premium=max(0.10, np.random.uniform(0.5, 8.0)),
                    unusual_activity_score=np.random.uniform(0.7, 0.95) if is_unusual else np.random.uniform(0.1, 0.4),
                    timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 60))
                )
                flow_data.append(call_flow)

            # Generate put flows
            for i in range(4):
                strike = base_price - (i + 1) * 5  # OTM puts

                # Simulate unusual activity (25% chance for puts)
                is_unusual = np.random.random() > 0.75
                volume_multiplier = np.random.uniform(2.5, 6) if is_unusual else 1
                base_volume = int(np.random.randint(150, 600) * volume_multiplier)

                # Calculate realistic Greeks
                moneyness = (strike - base_price) / base_price
                delta = max(-0.95, min(-0.05, -0.5 + moneyness * 2))

                put_flow = OptionsFlowData(
                    symbol=symbol,
                    option_type='put',
                    strike=strike,
                    expiration=expiration,
                    volume=base_volume,
                    open_interest=base_volume * np.random.randint(2, 6),
                    implied_volatility=np.random.uniform(0.20, 0.50),
                    delta=delta,
                    premium=max(0.10, np.random.uniform(0.5, 8.0)),
                    unusual_activity_score=np.random.uniform(0.6, 0.9) if is_unusual else np.random.uniform(0.1, 0.3),
                    timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 60))
                )
                flow_data.append(put_flow)

        # Add some ATM straddle activity (volatility plays)
        if np.random.random() > 0.5:  # 50% chance of straddle activity
            atm_strike = base_price
            straddle_volume = np.random.randint(1000, 3000)

            # ATM call for straddle
            straddle_call = OptionsFlowData(
                symbol=symbol,
                option_type='call',
                strike=atm_strike,
                expiration=expirations[0],  # Near-term
                volume=straddle_volume,
                open_interest=straddle_volume * 4,
                implied_volatility=np.random.uniform(0.30, 0.50),
                delta=0.5,
                premium=np.random.uniform(4.0, 10.0),
                unusual_activity_score=np.random.uniform(0.8, 0.95),
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 30))
            )
            flow_data.append(straddle_call)

            # ATM put for straddle
            straddle_put = OptionsFlowData(
                symbol=symbol,
                option_type='put',
                strike=atm_strike,
                expiration=expirations[0],
                volume=straddle_volume,
                open_interest=straddle_volume * 4,
                implied_volatility=np.random.uniform(0.30, 0.50),
                delta=-0.5,
                premium=np.random.uniform(4.0, 10.0),
                unusual_activity_score=np.random.uniform(0.8, 0.95),
                timestamp=datetime.now() - timedelta(minutes=np.random.randint(1, 30))
            )
            flow_data.append(straddle_put)

        return flow_data
    
    async def _generate_trading_signals(self, symbol: str, unusual_flows: List[OptionsFlowData]) -> List[OptionsSignal]:
        """Generate trading signals from unusual options flow"""
        try:
            signals = []
            
            # Group flows by type and analyze patterns
            call_flows = [f for f in unusual_flows if f.option_type == 'call']
            put_flows = [f for f in unusual_flows if f.option_type == 'put']
            
            # Analyze call flow patterns
            if call_flows:
                call_signal = self._analyze_call_flow_pattern(symbol, call_flows)
                if call_signal:
                    signals.append(call_signal)
            
            # Analyze put flow patterns
            if put_flows:
                put_signal = self._analyze_put_flow_pattern(symbol, put_flows)
                if put_signal:
                    signals.append(put_signal)
            
            # Look for spread opportunities
            if call_flows and put_flows:
                spread_signal = self._analyze_spread_opportunities(symbol, call_flows, put_flows)
                if spread_signal:
                    signals.append(spread_signal)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generating trading signals: {e}")
            return []
    
    def _analyze_call_flow_pattern(self, symbol: str, call_flows: List[OptionsFlowData]) -> Optional[OptionsSignal]:
        """Analyze call flow patterns for bullish signals"""
        try:
            if not call_flows:
                return None
            
            # Calculate aggregate metrics
            total_volume = sum(f.volume for f in call_flows)
            avg_delta = np.mean([f.delta for f in call_flows])
            avg_iv = np.mean([f.implied_volatility for f in call_flows])
            
            # Determine signal strength
            confidence = 0.0
            indicators = []
            
            if total_volume > 1000:
                confidence += 0.3
                indicators.append("High call volume")
            
            if avg_delta > 0.5:
                confidence += 0.2
                indicators.append("ITM call buying")
            
            if avg_iv > 0.4:
                confidence += 0.2
                indicators.append("IV spike in calls")
            
            if confidence < self.min_confidence:
                return None
            
            # Find optimal strikes for bull call spread
            sorted_flows = sorted(call_flows, key=lambda x: x.volume, reverse=True)
            entry_strikes = [sorted_flows[0].strike]
            if len(sorted_flows) > 1:
                entry_strikes.append(sorted_flows[1].strike)
            
            return OptionsSignal(
                symbol=symbol,
                signal_type='bullish',
                confidence=confidence,
                recommended_strategy='bull_call_spread',
                entry_strikes=entry_strikes,
                expiration=call_flows[0].expiration,
                max_risk=500.0,  # Would calculate based on spread
                max_reward=1500.0,  # Would calculate based on spread
                probability_profit=0.65,  # Would calculate based on analysis
                unusual_flow_indicators=indicators,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing call flow pattern: {e}")
            return None
    
    def _analyze_put_flow_pattern(self, symbol: str, put_flows: List[OptionsFlowData]) -> Optional[OptionsSignal]:
        """Analyze put flow patterns for bearish signals"""
        try:
            if not put_flows:
                return None
            
            # Calculate aggregate metrics
            total_volume = sum(f.volume for f in put_flows)
            avg_delta = np.mean([abs(f.delta) for f in put_flows])
            avg_iv = np.mean([f.implied_volatility for f in put_flows])
            
            # Determine signal strength
            confidence = 0.0
            indicators = []
            
            if total_volume > 1000:
                confidence += 0.3
                indicators.append("High put volume")
            
            if avg_delta > 0.5:
                confidence += 0.2
                indicators.append("ITM put buying")
            
            if avg_iv > 0.4:
                confidence += 0.2
                indicators.append("IV spike in puts")
            
            if confidence < self.min_confidence:
                return None
            
            # Find optimal strikes for bear put spread
            sorted_flows = sorted(put_flows, key=lambda x: x.volume, reverse=True)
            entry_strikes = [sorted_flows[0].strike]
            if len(sorted_flows) > 1:
                entry_strikes.append(sorted_flows[1].strike)
            
            return OptionsSignal(
                symbol=symbol,
                signal_type='bearish',
                confidence=confidence,
                recommended_strategy='bear_put_spread',
                entry_strikes=entry_strikes,
                expiration=put_flows[0].expiration,
                max_risk=500.0,  # Would calculate based on spread
                max_reward=1500.0,  # Would calculate based on spread
                probability_profit=0.65,  # Would calculate based on analysis
                unusual_flow_indicators=indicators,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing put flow pattern: {e}")
            return None
    
    def _analyze_spread_opportunities(self, symbol: str, call_flows: List[OptionsFlowData], 
                                    put_flows: List[OptionsFlowData]) -> Optional[OptionsSignal]:
        """Analyze opportunities for complex spread strategies"""
        try:
            # Look for straddle/strangle opportunities
            call_volume = sum(f.volume for f in call_flows)
            put_volume = sum(f.volume for f in put_flows)
            
            # If both call and put volume are high, might indicate straddle
            if call_volume > 500 and put_volume > 500:
                confidence = min((call_volume + put_volume) / 5000, 0.9)
                
                if confidence > self.min_confidence:
                    return OptionsSignal(
                        symbol=symbol,
                        signal_type='neutral',
                        confidence=confidence,
                        recommended_strategy='long_straddle',
                        entry_strikes=[call_flows[0].strike, put_flows[0].strike],
                        expiration=call_flows[0].expiration,
                        max_risk=1000.0,
                        max_reward=None,  # Unlimited
                        probability_profit=0.55,
                        unusual_flow_indicators=["High call and put volume", "Volatility play"],
                        timestamp=datetime.now()
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing spread opportunities: {e}")
            return None
    
    def _filter_signals(self, signals: List[OptionsSignal]) -> List[OptionsSignal]:
        """Filter and rank signals by quality"""
        try:
            # Filter by minimum confidence
            filtered = [s for s in signals if s.confidence >= self.min_confidence]
            
            # Sort by confidence
            filtered.sort(key=lambda x: x.confidence, reverse=True)
            
            # Limit to top signals
            return filtered[:10]
            
        except Exception as e:
            self.logger.error(f"Error filtering signals: {e}")
            return signals
    
    def _get_scan_universe(self) -> List[str]:
        """Get list of symbols to scan for options flow"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'SPY', 'QQQ', 'IWM', 'DIA', 'AMD', 'INTC', 'CRM', 'ORCL'
        ]
    
    def _create_ml_model(self):
        """Create ML model for options flow analysis"""
        if not ML_AVAILABLE:
            return None
        
        model = Sequential([
            Dense(64, activation='relu', input_shape=(10,)),  # 10 features
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dense(3, activation='softmax')  # 3 classes: bullish, bearish, neutral
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get summary of options flow analysis"""
        return {
            'enabled': self.enabled,
            'ml_enabled': self.ml_enabled,
            'scan_symbols_count': len(self.scan_symbols),
            'signals_generated_today': len([s for s in self.signals_generated 
                                          if s.timestamp.date() == datetime.now().date()]),
            'flow_data_points': len(self.flow_history),
            'min_confidence': self.min_confidence
        }


# Global options flow analyzer instance
options_flow_analyzer = OptionsFlowAnalyzer()
