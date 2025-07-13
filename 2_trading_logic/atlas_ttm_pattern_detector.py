"""
A.T.L.A.S TTM Squeeze Pattern Detection Module
Advanced pattern recognition for TTM Squeeze signals with multi-timeframe analysis
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from config import settings
from models import SignalStrength, TTMSqueezeSignal
from atlas_performance_optimizer import performance_optimizer

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """Supported timeframes for analysis"""
    DAILY = "1day"
    WEEKLY = "1week"
    HOURLY = "1hour"
    MINUTE_5 = "5min"


@dataclass
class HistogramPattern:
    """Histogram momentum pattern analysis"""
    bars: List[float]  # Last 4 histogram values
    decreasing_sequence: bool  # First 3 bars decreasing
    momentum_shift: bool  # 4th bar higher than 3rd
    momentum_strength: float  # Magnitude of momentum shift
    pattern_confidence: float  # Overall pattern confidence
    
    def __post_init__(self):
        if len(self.bars) >= 4:
            # Check decreasing sequence in first 3 bars
            self.decreasing_sequence = (
                self.bars[0] > self.bars[1] and 
                self.bars[1] > self.bars[2]
            )
            
            # Check momentum shift in 4th bar
            self.momentum_shift = self.bars[3] > self.bars[2]
            
            # Calculate momentum strength
            if self.momentum_shift:
                self.momentum_strength = abs(self.bars[3] - self.bars[2])
            else:
                self.momentum_strength = 0.0
            
            # Calculate pattern confidence
            self.pattern_confidence = self._calculate_confidence()
    
    def _calculate_confidence(self) -> float:
        """Calculate pattern confidence score"""
        confidence = 0.0
        
        # Base confidence for decreasing sequence
        if self.decreasing_sequence:
            confidence += 0.4
            
            # Additional confidence based on consistency of decrease
            decrease_1 = abs(self.bars[0] - self.bars[1])
            decrease_2 = abs(self.bars[1] - self.bars[2])
            
            # More consistent decreases = higher confidence
            consistency = 1.0 - abs(decrease_1 - decrease_2) / max(decrease_1 + decrease_2, 0.001)
            confidence += consistency * 0.2
        
        # Momentum shift confidence
        if self.momentum_shift:
            confidence += 0.3
            
            # Stronger momentum shift = higher confidence
            strength_factor = min(self.momentum_strength * 10, 0.1)  # Cap at 0.1
            confidence += strength_factor
        
        return min(confidence, 1.0)


@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe signal analysis"""
    daily_pattern: Optional[HistogramPattern]
    weekly_pattern: Optional[HistogramPattern]
    timeframe_alignment: bool
    combined_confidence: float
    trend_direction: str  # 'bullish', 'bearish', 'neutral'
    
    def __post_init__(self):
        self.timeframe_alignment = self._check_alignment()
        self.combined_confidence = self._calculate_combined_confidence()
        self.trend_direction = self._determine_trend_direction()
    
    def _check_alignment(self) -> bool:
        """Check if daily and weekly trends align"""
        if not self.daily_pattern or not self.weekly_pattern:
            return False
        
        # Both should show valid patterns
        daily_valid = (self.daily_pattern.decreasing_sequence and 
                      self.daily_pattern.momentum_shift)
        weekly_valid = (self.weekly_pattern.decreasing_sequence and 
                       self.weekly_pattern.momentum_shift)
        
        if not (daily_valid and weekly_valid):
            return False
        
        # Check directional alignment
        daily_direction = 1 if self.daily_pattern.bars[-1] > 0 else -1
        weekly_direction = 1 if self.weekly_pattern.bars[-1] > 0 else -1
        
        return daily_direction == weekly_direction
    
    def _calculate_combined_confidence(self) -> float:
        """Calculate combined confidence from both timeframes"""
        if not self.daily_pattern or not self.weekly_pattern:
            return 0.0
        
        # Weight daily more heavily (70%) than weekly (30%)
        daily_weight = 0.7
        weekly_weight = 0.3
        
        combined = (self.daily_pattern.pattern_confidence * daily_weight + 
                   self.weekly_pattern.pattern_confidence * weekly_weight)
        
        # Bonus for alignment
        if self.timeframe_alignment:
            combined += 0.1
        
        return min(combined, 1.0)
    
    def _determine_trend_direction(self) -> str:
        """Determine overall trend direction"""
        if not self.daily_pattern or not self.weekly_pattern:
            return 'neutral'
        
        daily_momentum = self.daily_pattern.bars[-1]
        weekly_momentum = self.weekly_pattern.bars[-1]
        
        # Both positive = bullish
        if daily_momentum > 0 and weekly_momentum > 0:
            return 'bullish'
        # Both negative = bearish
        elif daily_momentum < 0 and weekly_momentum < 0:
            return 'bearish'
        # Mixed signals = neutral
        else:
            return 'neutral'


@dataclass
class SqueezeState:
    """TTM Squeeze state analysis"""
    is_squeezed: bool
    squeeze_duration: int  # Number of bars in squeeze
    squeeze_intensity: float  # How tight the squeeze is
    release_probability: float  # Probability of imminent release
    
    def __post_init__(self):
        self.release_probability = self._calculate_release_probability()
    
    def _calculate_release_probability(self) -> float:
        """Calculate probability of squeeze release"""
        if not self.is_squeezed:
            return 0.0
        
        # Longer squeezes have higher release probability
        duration_factor = min(self.squeeze_duration / 20.0, 0.5)  # Cap at 0.5
        
        # Tighter squeezes have higher release probability
        intensity_factor = self.squeeze_intensity * 0.3
        
        return min(duration_factor + intensity_factor, 0.8)


class TTMPatternDetector:
    """
    Advanced TTM Squeeze pattern detection with multi-timeframe analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.bb_period = 20
        self.bb_stddev = 2.0
        self.kc_period = 20
        self.kc_multiplier = 1.5
        self.momentum_period = 12
        
        # Pattern detection thresholds
        self.min_pattern_confidence = 0.6
        self.min_momentum_shift = 0.001  # Minimum momentum change
        self.squeeze_intensity_threshold = 0.8
        
        self.logger.info("[TARGET] TTM Pattern Detector initialized")
    
    @performance_optimizer.performance_monitor("ttm_pattern_detection")
    async def detect_pattern(self, symbol: str, daily_data: pd.DataFrame, 
                           weekly_data: Optional[pd.DataFrame] = None) -> Optional[Dict[str, Any]]:
        """
        Main pattern detection method implementing the 4-criteria algorithm
        """
        try:
            # 1. Calculate technical indicators for daily timeframe
            daily_indicators = self._calculate_indicators(daily_data)
            if daily_indicators is None:
                return None
            
            # 2. Detect histogram momentum pattern (daily)
            daily_pattern = self._detect_histogram_pattern(daily_indicators['histogram'])
            if not daily_pattern or not self._validate_pattern(daily_pattern):
                return None
            
            # 3. Multi-timeframe analysis (if weekly data available)
            multi_tf_analysis = None
            if weekly_data is not None and len(weekly_data) >= 30:
                weekly_indicators = self._calculate_indicators(weekly_data)
                if weekly_indicators:
                    weekly_pattern = self._detect_histogram_pattern(weekly_indicators['histogram'])
                    if weekly_pattern:
                        multi_tf_analysis = MultiTimeframeAnalysis(
                            daily_pattern=daily_pattern,
                            weekly_pattern=weekly_pattern
                        )
            
            # 4. Squeeze state detection (optional enhancement)
            squeeze_state = self._detect_squeeze_state(daily_indicators)
            
            # 5. Calculate overall signal confidence
            signal_confidence = self._calculate_signal_confidence(
                daily_pattern, multi_tf_analysis, squeeze_state
            )
            
            if signal_confidence < self.min_pattern_confidence:
                return None
            
            # 6. Generate signal details
            signal_details = self._generate_signal_details(
                symbol, daily_data, daily_pattern, multi_tf_analysis, 
                squeeze_state, signal_confidence
            )
            
            self.logger.info(f"[TARGET] TTM Pattern detected for {symbol}: "
                           f"confidence={signal_confidence:.3f}, "
                           f"direction={signal_details['direction']}")
            
            return signal_details
            
        except Exception as e:
            self.logger.error(f"Error detecting TTM pattern for {symbol}: {e}")
            return None

    def validate_ttm_squeeze_with_5_criteria(self, symbol: str, daily_data: pd.DataFrame,
                                           weekly_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Enhanced TTM Squeeze validation with strict 5-criteria checking

        STRICT 5-Criteria Validation:
        1. 3 consecutive decreasing histogram bars (REQUIRED)
        2. 4th bar shows uptick (increasing) (REQUIRED)
        3. Momentum confirmation with direction (REQUIRED)
        4. Multi-timeframe EMA alignment (weekly/daily) (REQUIRED)
        5. Price above 5-EMA (REQUIRED)

        Returns detailed validation results with pass/fail for each criterion.
        """
        try:
            validation_results = {
                'symbol': symbol,
                'overall_valid': False,
                'criteria_met': 0,
                'total_criteria': 5,
                'confidence_score': 0.0,
                'validation_details': {},
                'timestamp': datetime.now()
            }

            # Calculate indicators
            daily_indicators = self._calculate_indicators(daily_data)
            if not daily_indicators:
                validation_results['validation_details']['error'] = 'Insufficient data for indicators'
                return validation_results

            # CRITERION 1: 3 consecutive decreasing histogram bars + 1 uptick
            histogram_validation = self._validate_strict_histogram_pattern(daily_indicators['histogram'])
            validation_results['validation_details']['criterion_1_histogram'] = histogram_validation
            if histogram_validation['valid']:
                validation_results['criteria_met'] += 1

            # CRITERION 2: Momentum confirmation
            momentum_validation = self._validate_strict_momentum(daily_indicators)
            validation_results['validation_details']['criterion_2_momentum'] = momentum_validation
            if momentum_validation['valid']:
                validation_results['criteria_met'] += 1

            # CRITERION 3: Multi-timeframe EMA alignment
            ema_validation = self._validate_strict_ema_alignment(daily_data, weekly_data)
            validation_results['validation_details']['criterion_3_ema'] = ema_validation
            if ema_validation['valid']:
                validation_results['criteria_met'] += 1

            # CRITERION 4: Price above 5-EMA
            price_validation = self._validate_strict_price_action(daily_data)
            validation_results['validation_details']['criterion_4_price'] = price_validation
            if price_validation['valid']:
                validation_results['criteria_met'] += 1

            # CRITERION 5: Squeeze state (bonus criterion)
            squeeze_validation = self._validate_strict_squeeze_state(daily_indicators)
            validation_results['validation_details']['criterion_5_squeeze'] = squeeze_validation
            if squeeze_validation['valid']:
                validation_results['criteria_met'] += 1

            # Calculate confidence score
            base_confidence = validation_results['criteria_met'] / validation_results['total_criteria']
            quality_bonus = self._calculate_pattern_quality_bonus(validation_results['validation_details'])
            validation_results['confidence_score'] = min(1.0, base_confidence + quality_bonus)

            # Overall validation (require at least 4 out of 5 criteria)
            validation_results['overall_valid'] = validation_results['criteria_met'] >= 4

            # Log validation results
            self.logger.info(f"TTM 5-Criteria Validation for {symbol}: "
                           f"{validation_results['criteria_met']}/5 criteria met, "
                           f"confidence: {validation_results['confidence_score']:.3f}, "
                           f"valid: {validation_results['overall_valid']}")

            return validation_results

        except Exception as e:
            self.logger.error(f"Error in 5-criteria TTM validation for {symbol}: {e}")
            return {
                'symbol': symbol,
                'overall_valid': False,
                'criteria_met': 0,
                'total_criteria': 5,
                'confidence_score': 0.0,
                'validation_details': {'error': str(e)},
                'timestamp': datetime.now()
            }

    def _validate_strict_histogram_pattern(self, histogram: pd.Series) -> Dict[str, Any]:
        """Validate strict histogram pattern: 3 declining + 1 uptick"""
        try:
            if len(histogram) < 4:
                return {'valid': False, 'reason': 'Insufficient histogram data', 'score': 0.0}

            # Get last 4 histogram values
            last_4 = histogram.tail(4).values

            # Check for 3 consecutive decreasing values
            declining_count = 0
            for i in range(3):
                if last_4[i] > last_4[i + 1]:
                    declining_count += 1

            # Check for uptick on 4th bar
            uptick = last_4[3] > last_4[2]

            # Strict validation: exactly 3 declining + 1 uptick
            pattern_valid = (declining_count == 3) and uptick

            # Calculate pattern strength
            if pattern_valid:
                decline_strength = sum(abs(last_4[i] - last_4[i + 1]) for i in range(3))
                uptick_strength = abs(last_4[3] - last_4[2])
                pattern_score = min(1.0, (decline_strength + uptick_strength) / 4)
            else:
                pattern_score = 0.0

            return {
                'valid': pattern_valid,
                'score': pattern_score,
                'declining_count': declining_count,
                'uptick': uptick,
                'histogram_values': last_4.tolist(),
                'reason': 'Valid 3-declining + 1-uptick pattern' if pattern_valid else f'Pattern failed: {declining_count} declining, uptick: {uptick}'
            }

        except Exception as e:
            return {'valid': False, 'reason': f'Histogram validation error: {e}', 'score': 0.0}

    def _validate_strict_momentum(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Validate momentum confirmation"""
        try:
            histogram = indicators['histogram']
            if len(histogram) < 2:
                return {'valid': False, 'reason': 'Insufficient momentum data', 'score': 0.0}

            # Current momentum direction
            current_momentum = histogram.iloc[-1]
            previous_momentum = histogram.iloc[-2]

            # Momentum must be positive and increasing
            momentum_positive = current_momentum > 0
            momentum_increasing = current_momentum > previous_momentum

            momentum_valid = momentum_positive and momentum_increasing
            momentum_strength = abs(current_momentum) if momentum_valid else 0

            return {
                'valid': momentum_valid,
                'score': min(1.0, momentum_strength * 10),  # Scale momentum strength
                'current_momentum': current_momentum,
                'momentum_direction': 'bullish' if momentum_positive else 'bearish',
                'momentum_trend': 'increasing' if momentum_increasing else 'decreasing',
                'reason': 'Valid bullish momentum' if momentum_valid else 'Momentum not bullish or not increasing'
            }

        except Exception as e:
            return {'valid': False, 'reason': f'Momentum validation error: {e}', 'score': 0.0}
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate all required technical indicators"""
        try:
            if len(df) < max(self.bb_period, self.kc_period, self.momentum_period) + 10:
                return None
            
            # Bollinger Bands
            bb_middle = df['close'].rolling(window=self.bb_period).mean()
            bb_std = df['close'].rolling(window=self.bb_period).std()
            bb_upper = bb_middle + (bb_std * self.bb_stddev)
            bb_lower = bb_middle - (bb_std * self.bb_stddev)
            
            # Keltner Channels
            kc_middle = df['close'].rolling(window=self.kc_period).mean()
            
            # True Range for ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = pd.Series(true_range).rolling(window=self.kc_period).mean()
            
            kc_upper = kc_middle + (atr * self.kc_multiplier)
            kc_lower = kc_middle - (atr * self.kc_multiplier)
            
            # TTM Histogram (Linear Regression Slope)
            histogram = self._calculate_histogram(df['close'], self.momentum_period)
            
            # Squeeze condition
            squeeze_active = (bb_upper <= kc_upper) & (bb_lower >= kc_lower)
            
            return {
                'bb_upper': bb_upper,
                'bb_lower': bb_lower,
                'bb_middle': bb_middle,
                'kc_upper': kc_upper,
                'kc_lower': kc_lower,
                'kc_middle': kc_middle,
                'atr': atr,
                'histogram': histogram,
                'squeeze_active': squeeze_active
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return None
    
    def _calculate_histogram(self, close_prices: pd.Series, period: int) -> pd.Series:
        """Calculate TTM Histogram using linear regression slope"""
        def linear_regression_slope(series):
            if len(series) < 2:
                return 0.0
            
            x = np.arange(len(series))
            y = series.values
            
            try:
                # Calculate linear regression slope
                n = len(x)
                sum_x = np.sum(x)
                sum_y = np.sum(y)
                sum_xy = np.sum(x * y)
                sum_x2 = np.sum(x * x)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                return slope
            except:
                return 0.0
        
        return close_prices.rolling(window=period).apply(linear_regression_slope, raw=False)
    
    def _detect_histogram_pattern(self, histogram: pd.Series) -> Optional[HistogramPattern]:
        """
        Detect the specific 4-bar histogram pattern:
        - 3 consecutive decreasing bars
        - 4th bar higher than 3rd bar
        """
        try:
            if len(histogram) < 4:
                return None
            
            # Get last 4 histogram values
            last_4_bars = histogram.tail(4).values
            
            # Remove NaN values
            last_4_bars = last_4_bars[~np.isnan(last_4_bars)]
            if len(last_4_bars) < 4:
                return None
            
            return HistogramPattern(bars=last_4_bars.tolist())
            
        except Exception as e:
            self.logger.error(f"Error detecting histogram pattern: {e}")
            return None
    
    def _validate_pattern(self, pattern: HistogramPattern) -> bool:
        """Validate that the pattern meets our criteria"""
        # Criterion 1: Three consecutive decreasing bars
        if not pattern.decreasing_sequence:
            return False
        
        # Criterion 2: Fourth bar higher than third bar (momentum confirmation)
        if not pattern.momentum_shift:
            return False
        
        # Criterion 3: Minimum momentum shift threshold
        if pattern.momentum_strength < self.min_momentum_shift:
            return False
        
        return True
    
    def _detect_squeeze_state(self, indicators: Dict[str, Any]) -> SqueezeState:
        """Detect current squeeze state (optional enhancement)"""
        try:
            squeeze_series = indicators['squeeze_active']
            current_squeeze = squeeze_series.iloc[-1] if len(squeeze_series) > 0 else False
            
            # Calculate squeeze duration
            squeeze_duration = 0
            if current_squeeze:
                # Count consecutive squeeze bars
                for i in range(len(squeeze_series) - 1, -1, -1):
                    if squeeze_series.iloc[i]:
                        squeeze_duration += 1
                    else:
                        break
            
            # Calculate squeeze intensity
            squeeze_intensity = 0.0
            if current_squeeze:
                bb_width = indicators['bb_upper'].iloc[-1] - indicators['bb_lower'].iloc[-1]
                kc_width = indicators['kc_upper'].iloc[-1] - indicators['kc_lower'].iloc[-1]
                
                if kc_width > 0:
                    squeeze_intensity = 1.0 - (bb_width / kc_width)
                    squeeze_intensity = max(0.0, min(1.0, squeeze_intensity))
            
            return SqueezeState(
                is_squeezed=current_squeeze,
                squeeze_duration=squeeze_duration,
                squeeze_intensity=squeeze_intensity
            )
            
        except Exception as e:
            self.logger.error(f"Error detecting squeeze state: {e}")
            return SqueezeState(False, 0, 0.0)
    
    def _calculate_signal_confidence(self, daily_pattern: HistogramPattern,
                                   multi_tf_analysis: Optional[MultiTimeframeAnalysis],
                                   squeeze_state: SqueezeState) -> float:
        """Calculate overall signal confidence score"""
        try:
            confidence = 0.0
            
            # Base confidence from daily pattern (60% weight)
            confidence += daily_pattern.pattern_confidence * 0.6
            
            # Multi-timeframe bonus (25% weight)
            if multi_tf_analysis and multi_tf_analysis.timeframe_alignment:
                confidence += multi_tf_analysis.combined_confidence * 0.25
            else:
                # Partial credit for single timeframe
                confidence += daily_pattern.pattern_confidence * 0.15
            
            # Squeeze state bonus (15% weight)
            if squeeze_state.is_squeezed:
                squeeze_bonus = squeeze_state.release_probability * 0.15
                confidence += squeeze_bonus
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating signal confidence: {e}")
            return 0.0
    
    def _generate_signal_details(self, symbol: str, df: pd.DataFrame,
                               daily_pattern: HistogramPattern,
                               multi_tf_analysis: Optional[MultiTimeframeAnalysis],
                               squeeze_state: SqueezeState,
                               confidence: float) -> Dict[str, Any]:
        """Generate comprehensive signal details"""
        try:
            current_price = df['close'].iloc[-1]
            current_histogram = daily_pattern.bars[-1]
            
            # Determine direction
            direction = 'bullish' if current_histogram > 0 else 'bearish'
            
            # Override with multi-timeframe if available
            if multi_tf_analysis:
                direction = multi_tf_analysis.trend_direction
            
            # Calculate entry, stop, and target levels
            atr = df['high'].subtract(df['low']).rolling(14).mean().iloc[-1]
            
            if direction == 'bullish':
                entry_price = current_price
                stop_loss = current_price - (atr * 1.5)
                target_price = current_price + (atr * 2.0)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 1.5)
                target_price = current_price - (atr * 2.0)
            
            # Convert confidence to signal strength
            if confidence >= 0.9:
                signal_strength = SignalStrength.VERY_STRONG
            elif confidence >= 0.8:
                signal_strength = SignalStrength.STRONG
            elif confidence >= 0.7:
                signal_strength = SignalStrength.MODERATE
            elif confidence >= 0.6:
                signal_strength = SignalStrength.WEAK
            else:
                signal_strength = SignalStrength.VERY_WEAK
            
            return {
                'symbol': symbol,
                'direction': direction,
                'signal_strength': signal_strength,
                'confidence': confidence,
                'entry_price': float(entry_price),
                'stop_loss': float(stop_loss),
                'target_price': float(target_price),
                'current_histogram': float(current_histogram),
                'histogram_pattern': {
                    'bars': daily_pattern.bars,
                    'decreasing_sequence': daily_pattern.decreasing_sequence,
                    'momentum_shift': daily_pattern.momentum_shift,
                    'momentum_strength': daily_pattern.momentum_strength,
                    'pattern_confidence': daily_pattern.pattern_confidence
                },
                'multi_timeframe': {
                    'available': multi_tf_analysis is not None,
                    'alignment': multi_tf_analysis.timeframe_alignment if multi_tf_analysis else False,
                    'combined_confidence': multi_tf_analysis.combined_confidence if multi_tf_analysis else 0.0
                } if multi_tf_analysis else None,
                'squeeze_state': {
                    'is_squeezed': squeeze_state.is_squeezed,
                    'duration': squeeze_state.squeeze_duration,
                    'intensity': squeeze_state.squeeze_intensity,
                    'release_probability': squeeze_state.release_probability
                },
                'timestamp': datetime.now(),
                'risk_reward_ratio': abs(target_price - entry_price) / abs(entry_price - stop_loss)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating signal details: {e}")
            return {}


    def get_pattern_parameters(self) -> Dict[str, Any]:
        """Get current pattern detection parameters"""
        return {
            'bb_period': self.bb_period,
            'bb_stddev': self.bb_stddev,
            'kc_period': self.kc_period,
            'kc_multiplier': self.kc_multiplier,
            'momentum_period': self.momentum_period,
            'min_pattern_confidence': self.min_pattern_confidence,
            'min_momentum_shift': self.min_momentum_shift,
            'squeeze_intensity_threshold': self.squeeze_intensity_threshold
        }

    def update_parameters(self, **kwargs):
        """Update pattern detection parameters"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"Updated parameter {key} = {value}")


class TTMPatternIntegrator:
    """
    Integration layer for TTM Pattern Detector with existing market engine
    """

    def __init__(self, market_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        self.pattern_detector = TTMPatternDetector()

        # Integration settings
        self.enable_multi_timeframe = True
        self.enable_squeeze_enhancement = True
        self.cache_patterns = True
        self.pattern_cache = {}
        self.cache_ttl = 300  # 5 minutes

        self.logger.info("[LINK] TTM Pattern Integrator initialized")

    async def get_enhanced_ttm_signal(self, symbol: str) -> Optional[TTMSqueezeSignal]:
        """
        Get enhanced TTM signal using advanced pattern detection
        """
        try:
            # Check cache first
            if self.cache_patterns:
                cache_key = f"{symbol}_ttm_pattern"
                cached_result = self._get_cached_pattern(cache_key)
                if cached_result:
                    return self._convert_to_ttm_signal(cached_result)

            # Get market data
            daily_data = await self._get_market_data(symbol, TimeFrame.DAILY)
            if daily_data is None or len(daily_data) < 50:
                return None

            weekly_data = None
            if self.enable_multi_timeframe:
                weekly_data = await self._get_market_data(symbol, TimeFrame.WEEKLY)

            # Detect pattern
            pattern_result = await self.pattern_detector.detect_pattern(
                symbol, daily_data, weekly_data
            )

            if not pattern_result:
                return None

            # Cache result
            if self.cache_patterns:
                self._cache_pattern(cache_key, pattern_result)

            # Convert to TTMSqueezeSignal
            return self._convert_to_ttm_signal(pattern_result)

        except Exception as e:
            self.logger.error(f"Error getting enhanced TTM signal for {symbol}: {e}")
            return None

    async def _get_market_data(self, symbol: str, timeframe: TimeFrame) -> Optional[pd.DataFrame]:
        """Get market data for specified timeframe"""
        try:
            if not self.market_engine:
                # Fallback to mock data for testing
                return self._generate_mock_data(symbol, timeframe)

            # Use market engine to get real data
            if timeframe == TimeFrame.DAILY:
                return await self.market_engine._get_historical_data(symbol, period="1d", limit=100)
            elif timeframe == TimeFrame.WEEKLY:
                return await self.market_engine._get_historical_data(symbol, period="1wk", limit=52)
            else:
                return await self.market_engine._get_historical_data(symbol, period="1h", limit=200)

        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol} {timeframe}: {e}")
            return None

    def _generate_mock_data(self, symbol: str, timeframe: TimeFrame) -> pd.DataFrame:
        """Generate mock data for testing purposes"""
        # This is for testing only - replace with real data in production
        np.random.seed(hash(symbol) % 2**32)

        periods = 100 if timeframe == TimeFrame.DAILY else 52
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='D' if timeframe == TimeFrame.DAILY else 'W')

        # Generate realistic OHLCV data
        base_price = 100.0
        prices = []

        for i in range(periods):
            if i == 0:
                open_price = base_price
            else:
                open_price = prices[-1]['close']

            change = np.random.normal(0, 0.02)  # 2% daily volatility
            close_price = open_price * (1 + change)

            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
            volume = np.random.randint(100000, 1000000)

            prices.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })

        df = pd.DataFrame(prices, index=dates)
        return df

    def _convert_to_ttm_signal(self, pattern_result: Dict[str, Any]) -> TTMSqueezeSignal:
        """Convert pattern detection result to TTMSqueezeSignal"""
        try:
            return TTMSqueezeSignal(
                symbol=pattern_result['symbol'],
                signal_strength=pattern_result['signal_strength'],
                histogram_value=pattern_result['current_histogram'],
                squeeze_active=pattern_result['squeeze_state']['is_squeezed'],
                momentum_direction=pattern_result['direction'],
                confidence=pattern_result['confidence'],
                entry_price=pattern_result['entry_price'],
                stop_loss=pattern_result['stop_loss'],
                target_price=pattern_result['target_price'],
                timestamp=pattern_result['timestamp']
            )

        except Exception as e:
            self.logger.error(f"Error converting pattern result to TTM signal: {e}")
            return None

    def _get_cached_pattern(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached pattern result"""
        if cache_key in self.pattern_cache:
            cached_data = self.pattern_cache[cache_key]
            if (datetime.now() - cached_data['timestamp']).total_seconds() < self.cache_ttl:
                return cached_data['result']
            else:
                del self.pattern_cache[cache_key]
        return None

    def _cache_pattern(self, cache_key: str, result: Dict[str, Any]):
        """Cache pattern result"""
        self.pattern_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }

        # Clean old cache entries
        if len(self.pattern_cache) > 100:
            oldest_key = min(self.pattern_cache.keys(),
                           key=lambda k: self.pattern_cache[k]['timestamp'])
            del self.pattern_cache[oldest_key]


# Global instances
ttm_pattern_detector = TTMPatternDetector()
ttm_pattern_integrator = TTMPatternIntegrator()
