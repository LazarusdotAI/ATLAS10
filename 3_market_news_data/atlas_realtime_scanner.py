"""
A.T.L.A.S Real-time TTM Squeeze Scanner
Enhanced real-time scanning with ML integration and proactive alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import json

from config import settings
from models import TTMSqueezeSignal, SignalStrength, TechnicalIndicators
from atlas_performance_optimizer import performance_optimizer

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Enhanced scan result with ML predictions"""
    symbol: str
    signal_strength: SignalStrength
    ttm_signal: TTMSqueezeSignal
    ml_prediction: Optional[float] = None
    sentiment_score: Optional[float] = None
    confidence_score: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'signal_strength': self.signal_strength.value,
            'ttm_signal': self.ttm_signal.dict() if self.ttm_signal else None,
            'ml_prediction': self.ml_prediction,
            'sentiment_score': self.sentiment_score,
            'confidence_score': self.confidence_score,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'risk_reward_ratio': self.risk_reward_ratio,
            'timestamp': self.timestamp.isoformat()
        }


class RealTimeTTMScanner:
    """
    Enhanced real-time TTM Squeeze scanner with ML integration
    """
    
    def __init__(self, market_engine=None, ai_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        self.ai_engine = ai_engine
        
        # Configuration
        self.scan_interval = 60  # seconds
        self.min_signal_strength = settings.MIN_SIGNAL_STRENGTH
        self.max_scan_results = settings.MAX_SCAN_RESULTS
        
        # State management
        self.is_running = False
        self.scan_task = None
        self.last_scan_time = None
        
        # Results tracking
        self.current_signals: Dict[str, ScanResult] = {}
        self.signal_history: List[ScanResult] = []
        self.scan_count = 0
        
        # Symbol universe
        self.scan_symbols = self._get_scan_universe()
        
        # Performance tracking
        self.scan_performance = {
            'total_scans': 0,
            'signals_found': 0,
            'avg_scan_time': 0.0,
            'last_scan_duration': 0.0
        }
        
        self.logger.info(f"[TARGET] Real-time TTM Scanner initialized - {len(self.scan_symbols)} symbols")
    
    def _get_scan_universe(self) -> List[str]:
        """Get list of symbols to scan"""
        # Default scan universe - in production this would be configurable
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'ARKK', 'XLF', 'XLE',
            'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'SQ', 'SHOP',
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA',
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'DHR', 'ABT',
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'OXY', 'MPC'
        ]
    
    async def start_scanning(self):
        """Start real-time scanning"""
        if self.is_running:
            self.logger.warning("Scanner already running")
            return
        
        self.is_running = True
        self.logger.info("[LAUNCH] Starting real-time TTM Squeeze scanner...")
        
        try:
            self.scan_task = asyncio.create_task(self._scan_loop())
            await self.scan_task
        except asyncio.CancelledError:
            self.logger.info("Scanner stopped")
        except Exception as e:
            self.logger.error(f"Scanner error: {e}")
        finally:
            self.is_running = False
    
    def stop_scanning(self):
        """Stop real-time scanning"""
        if self.scan_task and not self.scan_task.done():
            self.scan_task.cancel()
        self.is_running = False
        self.logger.info("🛑 Real-time scanner stopped")
    
    async def _scan_loop(self):
        """Main scanning loop"""
        while self.is_running:
            try:
                scan_start = datetime.now()
                
                # Perform scan
                await self._perform_scan()
                
                # Update performance metrics
                scan_duration = (datetime.now() - scan_start).total_seconds()
                self._update_performance_metrics(scan_duration)
                
                # Wait for next scan
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"Error in scan loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    @performance_optimizer.performance_monitor("ttm_scan")
    async def _perform_scan(self):
        """Perform TTM Squeeze scan on all symbols"""
        try:
            self.scan_count += 1
            self.last_scan_time = datetime.now()
            
            # Clear old signals
            self._cleanup_old_signals()
            
            # Scan symbols in batches to avoid overwhelming APIs
            batch_size = 10
            new_signals = []
            
            for i in range(0, len(self.scan_symbols), batch_size):
                batch = self.scan_symbols[i:i + batch_size]
                batch_results = await self._scan_batch(batch)
                new_signals.extend(batch_results)
                
                # Small delay between batches
                await asyncio.sleep(0.1)
            
            # Update current signals
            self._update_signals(new_signals)
            
            # Log scan results
            signal_count = len([s for s in new_signals if s.signal_strength != SignalStrength.VERY_WEAK])
            self.logger.info(f"[DATA] Scan completed: {len(new_signals)} symbols, {signal_count} signals")
            
        except Exception as e:
            self.logger.error(f"Error performing scan: {e}")
    
    async def _scan_batch(self, symbols: List[str]) -> List[ScanResult]:
        """Scan a batch of symbols"""
        results = []
        
        for symbol in symbols:
            try:
                result = await self._scan_symbol(symbol)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {e}")
        
        return results
    
    async def _scan_symbol(self, symbol: str) -> Optional[ScanResult]:
        """Scan individual symbol for TTM Squeeze signals"""
        try:
            if not self.market_engine:
                return None
            
            # Get TTM Squeeze signal
            ttm_signal = await self.market_engine.get_ttm_squeeze_signal(symbol)
            if not ttm_signal:
                return None
            
            # Determine base signal strength
            signal_strength = self._calculate_signal_strength(ttm_signal)
            
            # Get ML prediction if available
            ml_prediction = None
            if self.ai_engine and hasattr(self.ai_engine, 'ml_predictor'):
                try:
                    ml_result = await self.ai_engine.ml_predictor.predict_returns(symbol)
                    if ml_result:
                        ml_prediction = ml_result.predicted_return
                        # Enhance signal strength with ML confidence
                        signal_strength = self._enhance_with_ml(signal_strength, ml_result)
                except Exception as e:
                    self.logger.debug(f"ML prediction failed for {symbol}: {e}")
            
            # Get sentiment score if available
            sentiment_score = None
            if self.ai_engine and hasattr(self.ai_engine, 'sentiment_analyzer'):
                try:
                    sentiment_result = await self.ai_engine.sentiment_analyzer.analyze_sentiment(symbol)
                    if sentiment_result:
                        sentiment_score = sentiment_result.overall_sentiment
                        # Enhance signal strength with sentiment
                        signal_strength = self._enhance_with_sentiment(signal_strength, sentiment_result)
                except Exception as e:
                    self.logger.debug(f"Sentiment analysis failed for {symbol}: {e}")
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(ttm_signal, ml_prediction, sentiment_score)
            
            # Calculate entry, stop, and target prices
            entry_price, stop_loss, target_price = self._calculate_trade_levels(ttm_signal)
            
            # Calculate risk-reward ratio
            risk_reward_ratio = None
            if entry_price and stop_loss and target_price:
                risk = abs(entry_price - stop_loss)
                reward = abs(target_price - entry_price)
                if risk > 0:
                    risk_reward_ratio = reward / risk
            
            return ScanResult(
                symbol=symbol,
                signal_strength=signal_strength,
                ttm_signal=ttm_signal,
                ml_prediction=ml_prediction,
                sentiment_score=sentiment_score,
                confidence_score=confidence_score,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=target_price,
                risk_reward_ratio=risk_reward_ratio
            )
            
        except Exception as e:
            self.logger.error(f"Error scanning symbol {symbol}: {e}")
            return None
    
    def _calculate_signal_strength(self, ttm_signal: TTMSqueezeSignal) -> SignalStrength:
        """Calculate base signal strength from TTM Squeeze"""
        if not ttm_signal:
            return SignalStrength.VERY_WEAK
        
        # Base strength from TTM signal
        if ttm_signal.signal_strength == "very_strong":
            return SignalStrength.VERY_STRONG
        elif ttm_signal.signal_strength == "strong":
            return SignalStrength.STRONG
        elif ttm_signal.signal_strength == "moderate":
            return SignalStrength.MODERATE
        elif ttm_signal.signal_strength == "weak":
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _enhance_with_ml(self, base_strength: SignalStrength, ml_result) -> SignalStrength:
        """Enhance signal strength with ML prediction"""
        if not ml_result or ml_result.confidence < 0.6:
            return base_strength
        
        # If ML prediction aligns with TTM signal, enhance strength
        ml_strength_value = self._strength_to_value(ml_result.signal_strength)
        base_value = self._strength_to_value(base_strength)
        
        # Average the strengths with ML weight based on confidence
        ml_weight = ml_result.confidence
        enhanced_value = base_value * (1 - ml_weight) + ml_strength_value * ml_weight
        
        return self._value_to_strength(enhanced_value)
    
    def _enhance_with_sentiment(self, base_strength: SignalStrength, sentiment_result) -> SignalStrength:
        """Enhance signal strength with sentiment analysis"""
        if not sentiment_result or sentiment_result.confidence < 0.5:
            return base_strength
        
        # Sentiment enhancement based on alignment
        sentiment_strength_value = min(abs(sentiment_result.overall_sentiment) * 5, 4)  # Scale to 0-4
        base_value = self._strength_to_value(base_strength)
        
        # Enhance if sentiment is strong and confident
        if sentiment_result.confidence > 0.7 and abs(sentiment_result.overall_sentiment) > 0.3:
            enhanced_value = min(base_value + 1, 4)  # Boost by one level
            return self._value_to_strength(enhanced_value)
        
        return base_strength
    
    def _strength_to_value(self, strength: SignalStrength) -> int:
        """Convert signal strength to numeric value"""
        mapping = {
            SignalStrength.VERY_WEAK: 0,
            SignalStrength.WEAK: 1,
            SignalStrength.MODERATE: 2,
            SignalStrength.STRONG: 3,
            SignalStrength.VERY_STRONG: 4
        }
        return mapping.get(strength, 0)
    
    def _value_to_strength(self, value: float) -> SignalStrength:
        """Convert numeric value to signal strength"""
        value = max(0, min(4, round(value)))
        mapping = {
            0: SignalStrength.VERY_WEAK,
            1: SignalStrength.WEAK,
            2: SignalStrength.MODERATE,
            3: SignalStrength.STRONG,
            4: SignalStrength.VERY_STRONG
        }
        return mapping.get(value, SignalStrength.VERY_WEAK)
    
    def _calculate_confidence(self, ttm_signal: TTMSqueezeSignal, ml_prediction: Optional[float], 
                            sentiment_score: Optional[float]) -> float:
        """Calculate overall confidence score"""
        confidence_factors = []
        
        # TTM confidence
        if ttm_signal:
            confidence_factors.append(ttm_signal.confidence)
        
        # ML confidence (if available)
        if ml_prediction is not None:
            confidence_factors.append(0.7)  # Base ML confidence
        
        # Sentiment confidence (if available)
        if sentiment_score is not None:
            confidence_factors.append(0.6)  # Base sentiment confidence
        
        if not confidence_factors:
            return 0.0
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _calculate_trade_levels(self, ttm_signal: TTMSqueezeSignal) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate entry, stop loss, and target prices"""
        if not ttm_signal or not ttm_signal.entry_price:
            return None, None, None
        
        entry_price = ttm_signal.entry_price
        stop_loss = ttm_signal.stop_loss
        target_price = ttm_signal.target_price
        
        return entry_price, stop_loss, target_price
    
    def _update_signals(self, new_signals: List[ScanResult]):
        """Update current signals and history"""
        # Update current signals
        for signal in new_signals:
            if signal.signal_strength != SignalStrength.VERY_WEAK:
                self.current_signals[signal.symbol] = signal
        
        # Add to history
        self.signal_history.extend(new_signals)
        
        # Keep history manageable
        if len(self.signal_history) > 1000:
            self.signal_history = self.signal_history[-1000:]
        
        # Update performance
        self.scan_performance['signals_found'] = len(self.current_signals)
    
    def _cleanup_old_signals(self):
        """Remove old signals that are no longer valid"""
        cutoff_time = datetime.now() - timedelta(minutes=30)
        
        expired_symbols = [
            symbol for symbol, signal in self.current_signals.items()
            if signal.timestamp < cutoff_time
        ]
        
        for symbol in expired_symbols:
            del self.current_signals[symbol]
    
    def _update_performance_metrics(self, scan_duration: float):
        """Update performance tracking metrics"""
        self.scan_performance['total_scans'] += 1
        self.scan_performance['last_scan_duration'] = scan_duration
        
        # Update average scan time
        total_scans = self.scan_performance['total_scans']
        current_avg = self.scan_performance['avg_scan_time']
        self.scan_performance['avg_scan_time'] = (current_avg * (total_scans - 1) + scan_duration) / total_scans
    
    def get_live_signals(self, min_strength: int = 3) -> List[Dict[str, Any]]:
        """Get current live signals above minimum strength"""
        min_strength_enum = self._value_to_strength(min_strength)
        
        filtered_signals = [
            signal for signal in self.current_signals.values()
            if self._strength_to_value(signal.signal_strength) >= min_strength
        ]
        
        # Sort by signal strength and confidence
        filtered_signals.sort(
            key=lambda s: (self._strength_to_value(s.signal_strength), s.confidence_score),
            reverse=True
        )
        
        return [signal.to_dict() for signal in filtered_signals[:self.max_scan_results]]
    
    def get_scanner_status(self) -> Dict[str, Any]:
        """Get scanner status and performance metrics"""
        return {
            'is_running': self.is_running,
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'scan_count': self.scan_count,
            'current_signals_count': len(self.current_signals),
            'scan_symbols_count': len(self.scan_symbols),
            'performance': self.scan_performance,
            'scan_interval': self.scan_interval
        }


# Global scanner instance
realtime_scanner = RealTimeTTMScanner()
