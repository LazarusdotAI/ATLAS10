#!/usr/bin/env python3
"""
Lee Method Scanner for A.T.L.A.S.
Implements the Lee Method pattern detection algorithm replacing TTM Squeeze patterns
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import requests
import json

# Configure logging with ASCII-safe format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('lee_method_scanner.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LeeMethodSignal:
    """Lee Method signal detection result"""
    symbol: str
    signal_type: str  # 'bullish_momentum', 'bearish_momentum', 'neutral'
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    timeframe: str
    timestamp: datetime
    
    # Lee Method specific data
    histogram_sequence: List[float]  # The decreasing + increasing sequence
    momentum_bars: List[float]  # Momentum values for confirmation
    momentum_confirmation: bool
    
    # Multi-timeframe analysis
    weekly_trend: str  # 'bullish', 'bearish', 'neutral'
    daily_trend: str
    trend_alignment: bool  # Weekly and daily trend confirmation
    
    # Risk metrics
    risk_reward_ratio: float
    position_size_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for JSON serialization"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'confidence': self.confidence,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat(),
            'histogram_sequence': self.histogram_sequence,
            'momentum_bars': self.momentum_bars,
            'momentum_confirmation': self.momentum_confirmation,
            'weekly_trend': self.weekly_trend,
            'daily_trend': self.daily_trend,
            'trend_alignment': self.trend_alignment,
            'risk_reward_ratio': self.risk_reward_ratio,
            'position_size_percent': self.position_size_percent
        }

class LeeMethodScanner:
    """Lee Method pattern scanner implementing the 3-criteria algorithm"""
    
    def __init__(self, fmp_api_key: str = None):
        self.logger = logger
        self.fmp_api_key = fmp_api_key or "demo"
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
        # Lee Method parameters
        self.momentum_period = 12
        self.min_decreasing_bars = 3  # Minimum 3 decreasing bars
        self.max_lookback_bars = 10   # Maximum bars to look back for pattern
        
        # Multi-timeframe parameters
        self.ema_periods = [5, 8, 21, 50]
        
        # Risk management
        self.default_risk_percent = 2.0  # 2% risk per trade
        self.default_reward_ratio = 2.0  # 2:1 reward:risk ratio
        
    async def fetch_historical_data(self, symbol: str, timeframe: str = "1day", 
                                  limit: int = 100) -> pd.DataFrame:
        """Fetch historical price data"""
        try:
            url = f"{self.base_url}/historical-price-full/{symbol}"
            params = {
                'apikey': self.fmp_api_key,
                'timeseries': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'historical' not in data:
                self.logger.warning(f"No historical data for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['historical'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Ensure required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    self.logger.error(f"Missing required column: {col}")
                    return pd.DataFrame()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_momentum_histogram(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum histogram (similar to TTM but optimized for Lee Method)"""
        try:
            # Calculate momentum oscillator
            highest_high = df['high'].rolling(window=self.momentum_period).max()
            lowest_low = df['low'].rolling(window=self.momentum_period).min()
            
            # Momentum calculation
            df['momentum'] = df['close'] - ((highest_high + lowest_low) / 2)
            
            # Smooth the momentum (histogram bars)
            df['histogram'] = df['momentum'].rolling(window=3).mean()
            
            # Calculate EMAs for trend analysis
            for period in self.ema_periods:
                df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum histogram: {e}")
            return df
    
    def detect_lee_method_pattern(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Detect Lee Method pattern based on the 3 criteria:
        1. Three (or more) histogram bars that decrease, followed by an increase
        2. Momentum should be greater than the prior momentum bar
        3. Multi-timeframe trend confirmation (weekly/daily)
        """
        try:
            if len(df) < self.max_lookback_bars:
                return None
            
            # Get recent data for pattern analysis
            recent_data = df.tail(self.max_lookback_bars)
            histogram_values = recent_data['histogram'].values
            momentum_values = recent_data['momentum'].values
            
            # Criterion 1: Find decreasing sequence followed by increase
            pattern_result = self._find_decreasing_increasing_pattern(histogram_values)
            if not pattern_result:
                return None
            
            # Criterion 2: Momentum confirmation
            momentum_confirmed = self._check_momentum_confirmation(
                momentum_values, pattern_result['increase_index']
            )
            if not momentum_confirmed:
                return None
            
            # Criterion 3: Multi-timeframe trend analysis
            trend_analysis = self._analyze_multi_timeframe_trends(df)
            
            # Determine signal direction and strength
            signal_direction = self._determine_signal_direction(
                pattern_result, momentum_values, trend_analysis
            )
            
            return {
                'pattern_found': True,
                'histogram_sequence': pattern_result['sequence'],
                'momentum_confirmation': momentum_confirmed,
                'trend_analysis': trend_analysis,
                'signal_direction': signal_direction,
                'confidence': self._calculate_confidence(pattern_result, trend_analysis),
                'entry_index': len(recent_data) - 1  # Current bar
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting Lee Method pattern: {e}")
            return None
    
    def _find_decreasing_increasing_pattern(self, histogram_values: np.ndarray) -> Optional[Dict[str, Any]]:
        """Find the decreasing-increasing histogram pattern"""
        try:
            # Look for pattern in recent bars
            for start_idx in range(len(histogram_values) - self.min_decreasing_bars - 1):
                # Check for decreasing sequence
                decreasing_count = 0
                current_idx = start_idx
                
                # Count consecutive decreasing bars
                while (current_idx < len(histogram_values) - 1 and 
                       histogram_values[current_idx + 1] < histogram_values[current_idx]):
                    decreasing_count += 1
                    current_idx += 1
                
                # Check if we have minimum decreasing bars followed by increase
                if (decreasing_count >= self.min_decreasing_bars and 
                    current_idx < len(histogram_values) - 1 and
                    histogram_values[current_idx + 1] > histogram_values[current_idx]):
                    
                    # Found valid pattern
                    sequence = histogram_values[start_idx:current_idx + 2].tolist()
                    return {
                        'start_index': start_idx,
                        'decrease_count': decreasing_count,
                        'increase_index': current_idx + 1,
                        'sequence': sequence
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding decreasing-increasing pattern: {e}")
            return None
    
    def _check_momentum_confirmation(self, momentum_values: np.ndarray, 
                                   increase_index: int) -> bool:
        """Check if momentum is greater than prior momentum bar"""
        try:
            if increase_index < 1 or increase_index >= len(momentum_values):
                return False
            
            current_momentum = momentum_values[increase_index]
            prior_momentum = momentum_values[increase_index - 1]
            
            return current_momentum > prior_momentum
            
        except Exception as e:
            self.logger.error(f"Error checking momentum confirmation: {e}")
            return False
    
    def _analyze_multi_timeframe_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends across multiple timeframes using EMAs"""
        try:
            current = df.iloc[-1]
            
            # Daily trend analysis (using EMAs)
            daily_trend = 'neutral'
            if current['close'] > current['ema_21'] and current['ema_5'] > current['ema_8']:
                daily_trend = 'bullish'
            elif current['close'] < current['ema_21'] and current['ema_5'] < current['ema_8']:
                daily_trend = 'bearish'
            
            # Weekly trend simulation (using longer EMAs)
            weekly_trend = 'neutral'
            if current['ema_21'] > current['ema_50']:
                weekly_trend = 'bullish'
            elif current['ema_21'] < current['ema_50']:
                weekly_trend = 'bearish'
            
            # Trend alignment
            trend_alignment = (
                (daily_trend == 'bullish' and weekly_trend == 'bullish') or
                (daily_trend == 'bearish' and weekly_trend == 'bearish')
            )
            
            return {
                'daily_trend': daily_trend,
                'weekly_trend': weekly_trend,
                'trend_alignment': trend_alignment,
                'ema_alignment': current['ema_5'] > current['ema_8'] > current['ema_21']
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing multi-timeframe trends: {e}")
            return {
                'daily_trend': 'neutral',
                'weekly_trend': 'neutral',
                'trend_alignment': False,
                'ema_alignment': False
            }
    
    def _determine_signal_direction(self, pattern_result: Dict[str, Any], 
                                  momentum_values: np.ndarray,
                                  trend_analysis: Dict[str, Any]) -> str:
        """Determine the signal direction based on pattern and trends"""
        try:
            # Check if the increase is above or below zero line
            increase_value = pattern_result['sequence'][-1]
            
            # Combine pattern direction with trend analysis
            if (increase_value > 0 and 
                trend_analysis['daily_trend'] == 'bullish' and
                trend_analysis['trend_alignment']):
                return 'bullish_momentum'
            elif (increase_value < 0 and 
                  trend_analysis['daily_trend'] == 'bearish' and
                  trend_analysis['trend_alignment']):
                return 'bearish_momentum'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.error(f"Error determining signal direction: {e}")
            return 'neutral'
    
    def _calculate_confidence(self, pattern_result: Dict[str, Any], 
                            trend_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the signal"""
        try:
            confidence = 0.5  # Base confidence
            
            # Add confidence for pattern strength
            if pattern_result['decrease_count'] >= 4:
                confidence += 0.2
            
            # Add confidence for trend alignment
            if trend_analysis['trend_alignment']:
                confidence += 0.2
            
            # Add confidence for EMA alignment
            if trend_analysis['ema_alignment']:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5

    async def generate_lee_method_signal(self, symbol: str, df: pd.DataFrame) -> Optional[LeeMethodSignal]:
        """Generate a complete Lee Method signal"""
        try:
            # Calculate momentum histogram
            df_with_indicators = self.calculate_momentum_histogram(df)

            # Detect Lee Method pattern
            pattern_result = self.detect_lee_method_pattern(df_with_indicators)
            if not pattern_result or not pattern_result['pattern_found']:
                return None

            # Get current price data
            current = df_with_indicators.iloc[-1]
            entry_price = float(current['close'])

            # Calculate risk management levels
            risk_amount = entry_price * (self.default_risk_percent / 100)

            if pattern_result['signal_direction'] == 'bullish_momentum':
                target_price = entry_price + (risk_amount * self.default_reward_ratio)
                stop_loss = entry_price - risk_amount
            elif pattern_result['signal_direction'] == 'bearish_momentum':
                target_price = entry_price - (risk_amount * self.default_reward_ratio)
                stop_loss = entry_price + risk_amount
            else:
                return None  # No clear direction

            # Calculate risk-reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0

            # Create Lee Method signal
            signal = LeeMethodSignal(
                symbol=symbol,
                signal_type=pattern_result['signal_direction'],
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=pattern_result['confidence'],
                timeframe='daily',
                timestamp=datetime.now(),
                histogram_sequence=pattern_result['histogram_sequence'],
                momentum_bars=df_with_indicators['momentum'].tail(5).tolist(),
                momentum_confirmation=pattern_result['momentum_confirmation'],
                weekly_trend=pattern_result['trend_analysis']['weekly_trend'],
                daily_trend=pattern_result['trend_analysis']['daily_trend'],
                trend_alignment=pattern_result['trend_analysis']['trend_alignment'],
                risk_reward_ratio=risk_reward_ratio,
                position_size_percent=self.default_risk_percent
            )

            return signal

        except Exception as e:
            self.logger.error(f"Error generating Lee Method signal for {symbol}: {e}")
            return None

    async def scan_symbol(self, symbol: str) -> Optional[LeeMethodSignal]:
        """Scan a single symbol for Lee Method patterns"""
        try:
            # Fetch historical data
            df = await self.fetch_historical_data(symbol, "1day", 100)
            if df.empty:
                return None

            # Generate signal
            signal = await self.generate_lee_method_signal(symbol, df)
            return signal

        except Exception as e:
            self.logger.error(f"Error scanning {symbol}: {e}")
            return None

    async def scan_multiple_symbols(self, symbols: List[str]) -> List[LeeMethodSignal]:
        """Scan multiple symbols for Lee Method patterns"""
        signals = []

        try:
            # Process symbols in batches to avoid overwhelming APIs
            batch_size = 5
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]

                # Create tasks for concurrent processing
                tasks = [self.scan_symbol(symbol) for symbol in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in batch_results:
                    if isinstance(result, LeeMethodSignal):
                        signals.append(result)
                    elif isinstance(result, Exception):
                        self.logger.error(f"Error in batch processing: {result}")

                # Small delay between batches
                await asyncio.sleep(0.5)

            return signals

        except Exception as e:
            self.logger.error(f"Error scanning multiple symbols: {e}")
            return signals

    def get_latest_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the latest Lee Method signals (placeholder for real-time integration)"""
        # This would be connected to a real-time data feed in production
        return []

# Test function
async def test_lee_method_scanner():
    """Test the Lee Method scanner"""
    print("[SEARCH] Testing Lee Method Scanner")
    print("=" * 50)

    scanner = LeeMethodScanner()

    # Test symbols
    test_symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"]

    for symbol in test_symbols:
        print(f"\n[DATA] Analyzing {symbol} with Lee Method...")

        signal = await scanner.scan_symbol(symbol)

        if signal:
            print(f"   [TARGET] Lee Method Signal Detected!")
            print(f"   [UP] Type: {signal.signal_type}")
            print(f"   [MONEY] Entry: ${signal.entry_price:.2f}")
            print(f"   [TARGET] Target: ${signal.target_price:.2f}")
            print(f"   [SHIELD] Stop: ${signal.stop_loss:.2f}")
            print(f"   [STAR] Confidence: {signal.confidence:.1%}")
            print(f"   [DATA] R/R Ratio: {signal.risk_reward_ratio:.2f}")
            print(f"   [UP] Trends: Weekly={signal.weekly_trend}, Daily={signal.daily_trend}")
            print(f"   [OK] Momentum Confirmed: {signal.momentum_confirmation}")
            print(f"   [OK] Trend Alignment: {signal.trend_alignment}")
        else:
            print(f"   [CLOCK] No Lee Method signals detected")

if __name__ == "__main__":
    asyncio.run(test_lee_method_scanner())
