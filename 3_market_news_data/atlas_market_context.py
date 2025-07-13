"""
A.T.L.A.S Market Context Engine
Real-time market intelligence and context analysis for informed trading decisions
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from config import settings
from models import Quote, MarketContext, SignalStrength
from atlas_performance_optimizer import performance_optimizer

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime classifications"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING = "trending"
    RANGING = "ranging"


class MarketPhase(Enum):
    """Market phases during trading day"""
    PRE_MARKET = "pre_market"
    OPENING = "opening"
    MORNING_SESSION = "morning_session"
    MIDDAY = "midday"
    AFTERNOON_SESSION = "afternoon_session"
    CLOSING = "closing"
    AFTER_HOURS = "after_hours"


@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence data"""
    regime: MarketRegime
    phase: MarketPhase
    sentiment_score: float  # -1 to 1
    volatility_percentile: float  # 0 to 100
    trend_strength: float  # 0 to 1
    momentum_score: float  # -1 to 1
    risk_level: str  # 'low', 'medium', 'high'
    key_levels: Dict[str, float]  # support/resistance
    market_breadth: Dict[str, float]
    sector_rotation: Dict[str, float]
    institutional_flow: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'regime': self.regime.value,
            'phase': self.phase.value,
            'sentiment_score': self.sentiment_score,
            'volatility_percentile': self.volatility_percentile,
            'trend_strength': self.trend_strength,
            'momentum_score': self.momentum_score,
            'risk_level': self.risk_level,
            'key_levels': self.key_levels,
            'market_breadth': self.market_breadth,
            'sector_rotation': self.sector_rotation,
            'institutional_flow': self.institutional_flow,
            'timestamp': self.timestamp.isoformat()
        }


class MarketContextEngine:
    """
    Real-time market context analysis engine providing comprehensive market intelligence
    """
    
    def __init__(self, market_engine=None, sentiment_analyzer=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        self.sentiment_analyzer = sentiment_analyzer
        
        # Configuration
        self.enabled = settings.PERFORMANCE_MONITORING_ENABLED
        self.update_interval = 300  # 5 minutes
        
        # Market data tracking
        self.current_context: Optional[MarketIntelligence] = None
        self.context_history: List[MarketIntelligence] = []
        self.market_data_cache = {}
        
        # Analysis parameters
        self.volatility_lookback = 252  # 1 year for volatility percentile
        self.trend_lookback = 50  # 50 days for trend analysis
        self.momentum_lookback = 20  # 20 days for momentum
        
        # Key market symbols for analysis
        self.market_symbols = ['SPY', 'QQQ', 'IWM', 'DIA', 'VIX', 'TLT', 'GLD']
        self.sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Communication': 'XLC'
        }
        
        # State tracking
        self.is_running = False
        self.update_task = None
        
        self.logger.info(f"[WEB] Market Context Engine initialized - enabled: {self.enabled}")
    
    async def start_monitoring(self):
        """Start real-time market context monitoring"""
        if not self.enabled:
            self.logger.info("Market context engine disabled")
            return
        
        if self.is_running:
            self.logger.warning("Market context engine already running")
            return
        
        self.is_running = True
        self.logger.info("[LAUNCH] Starting market context monitoring...")
        
        try:
            self.update_task = asyncio.create_task(self._context_update_loop())
            await self.update_task
        except asyncio.CancelledError:
            self.logger.info("Market context monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error in market context monitoring: {e}")
        finally:
            self.is_running = False
    
    def stop_monitoring(self):
        """Stop market context monitoring"""
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
        self.is_running = False
        self.logger.info("🛑 Market context monitoring stopped")
    
    async def _context_update_loop(self):
        """Main context update loop"""
        while self.is_running:
            try:
                # Update market context
                await self._update_market_context()
                
                # Sleep until next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in context update loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    @performance_optimizer.performance_monitor("market_context_update")
    async def _update_market_context(self):
        """Update comprehensive market context"""
        try:
            self.logger.debug("🔄 Updating market context...")
            
            # Get current market data
            market_data = await self._gather_market_data()
            
            if not market_data:
                self.logger.warning("No market data available for context update")
                return
            
            # Analyze market regime
            regime = await self._analyze_market_regime(market_data)
            
            # Determine market phase
            phase = self._determine_market_phase()
            
            # Calculate sentiment score
            sentiment_score = await self._calculate_market_sentiment()
            
            # Calculate volatility percentile
            volatility_percentile = await self._calculate_volatility_percentile(market_data)
            
            # Analyze trend strength
            trend_strength = await self._analyze_trend_strength(market_data)
            
            # Calculate momentum score
            momentum_score = await self._calculate_momentum_score(market_data)
            
            # Assess risk level
            risk_level = self._assess_risk_level(volatility_percentile, sentiment_score, trend_strength)
            
            # Identify key levels
            key_levels = await self._identify_key_levels(market_data)
            
            # Analyze market breadth
            market_breadth = await self._analyze_market_breadth()
            
            # Analyze sector rotation
            sector_rotation = await self._analyze_sector_rotation()
            
            # Analyze institutional flow
            institutional_flow = await self._analyze_institutional_flow()
            
            # Create market intelligence object
            intelligence = MarketIntelligence(
                regime=regime,
                phase=phase,
                sentiment_score=sentiment_score,
                volatility_percentile=volatility_percentile,
                trend_strength=trend_strength,
                momentum_score=momentum_score,
                risk_level=risk_level,
                key_levels=key_levels,
                market_breadth=market_breadth,
                sector_rotation=sector_rotation,
                institutional_flow=institutional_flow,
                timestamp=datetime.now()
            )
            
            # Update current context
            self.current_context = intelligence
            self.context_history.append(intelligence)
            
            # Keep history manageable
            if len(self.context_history) > 1000:
                self.context_history = self.context_history[-1000:]
            
            self.logger.info(f"[DATA] Market context updated: {regime.value}, sentiment: {sentiment_score:.2f}, "
                           f"volatility: {volatility_percentile:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error updating market context: {e}")
    
    async def _gather_market_data(self) -> Dict[str, Any]:
        """Gather current market data for analysis"""
        try:
            market_data = {}
            
            for symbol in self.market_symbols:
                try:
                    if self.market_engine:
                        quote = await self.market_engine.get_quote(symbol)
                        if quote:
                            market_data[symbol] = {
                                'price': quote.price,
                                'change': quote.change,
                                'change_percent': quote.change_percent,
                                'volume': quote.volume
                            }
                    else:
                        # Mock data for testing
                        market_data[symbol] = {
                            'price': 100.0 + np.random.normal(0, 5),
                            'change': np.random.normal(0, 2),
                            'change_percent': np.random.normal(0, 2),
                            'volume': np.random.randint(1000000, 10000000)
                        }
                except Exception as e:
                    self.logger.debug(f"Error getting data for {symbol}: {e}")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error gathering market data: {e}")
            return {}
    
    async def _analyze_market_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """Analyze current market regime"""
        try:
            spy_data = market_data.get('SPY', {})
            vix_data = market_data.get('VIX', {})
            
            spy_change = spy_data.get('change_percent', 0)
            vix_level = vix_data.get('price', 20)
            
            # Simple regime classification
            if vix_level > 30:
                return MarketRegime.HIGH_VOLATILITY
            elif vix_level < 15:
                return MarketRegime.LOW_VOLATILITY
            elif spy_change > 1.0:
                return MarketRegime.BULL_MARKET
            elif spy_change < -1.0:
                return MarketRegime.BEAR_MARKET
            else:
                return MarketRegime.SIDEWAYS
                
        except Exception as e:
            self.logger.error(f"Error analyzing market regime: {e}")
            return MarketRegime.SIDEWAYS
    
    def _determine_market_phase(self) -> MarketPhase:
        """Determine current market phase based on time"""
        try:
            current_time = datetime.now().time()
            
            if current_time < datetime.strptime("09:30", "%H:%M").time():
                return MarketPhase.PRE_MARKET
            elif current_time < datetime.strptime("10:00", "%H:%M").time():
                return MarketPhase.OPENING
            elif current_time < datetime.strptime("12:00", "%H:%M").time():
                return MarketPhase.MORNING_SESSION
            elif current_time < datetime.strptime("14:00", "%H:%M").time():
                return MarketPhase.MIDDAY
            elif current_time < datetime.strptime("15:30", "%H:%M").time():
                return MarketPhase.AFTERNOON_SESSION
            elif current_time < datetime.strptime("16:00", "%H:%M").time():
                return MarketPhase.CLOSING
            else:
                return MarketPhase.AFTER_HOURS
                
        except Exception as e:
            self.logger.error(f"Error determining market phase: {e}")
            return MarketPhase.MIDDAY
    
    async def _calculate_market_sentiment(self) -> float:
        """Calculate overall market sentiment"""
        try:
            if self.sentiment_analyzer:
                # Get sentiment for major market symbols
                sentiments = []
                for symbol in ['SPY', 'QQQ', 'IWM']:
                    sentiment_result = await self.sentiment_analyzer.analyze_sentiment(symbol)
                    if sentiment_result:
                        sentiments.append(sentiment_result.overall_sentiment)
                
                if sentiments:
                    return np.mean(sentiments)
            
            # Fallback: use price action
            return 0.0  # Neutral
            
        except Exception as e:
            self.logger.error(f"Error calculating market sentiment: {e}")
            return 0.0
    
    async def _calculate_volatility_percentile(self, market_data: Dict[str, Any]) -> float:
        """Calculate volatility percentile"""
        try:
            # This would use historical volatility data
            # For now, use VIX as proxy
            vix_data = market_data.get('VIX', {})
            vix_level = vix_data.get('price', 20)
            
            # Simple percentile calculation (VIX 10-50 range)
            percentile = min(max((vix_level - 10) / 40 * 100, 0), 100)
            return percentile
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility percentile: {e}")
            return 50.0
    
    async def _analyze_trend_strength(self, market_data: Dict[str, Any]) -> float:
        """Analyze trend strength"""
        try:
            # This would use moving averages and trend indicators
            # For now, use simple price momentum
            spy_data = market_data.get('SPY', {})
            change_percent = abs(spy_data.get('change_percent', 0))
            
            # Normalize to 0-1 scale
            trend_strength = min(change_percent / 3.0, 1.0)  # 3% = max strength
            return trend_strength
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend strength: {e}")
            return 0.5
    
    async def _calculate_momentum_score(self, market_data: Dict[str, Any]) -> float:
        """Calculate momentum score"""
        try:
            # Average momentum across major indices
            momentum_scores = []
            
            for symbol in ['SPY', 'QQQ', 'IWM']:
                data = market_data.get(symbol, {})
                change_percent = data.get('change_percent', 0)
                # Normalize to -1 to 1 scale
                momentum = max(min(change_percent / 5.0, 1.0), -1.0)  # 5% = max momentum
                momentum_scores.append(momentum)
            
            if momentum_scores:
                return np.mean(momentum_scores)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum score: {e}")
            return 0.0
    
    def _assess_risk_level(self, volatility_percentile: float, sentiment_score: float, 
                          trend_strength: float) -> str:
        """Assess overall market risk level"""
        try:
            risk_score = 0.0
            
            # Volatility component
            if volatility_percentile > 80:
                risk_score += 0.4
            elif volatility_percentile > 60:
                risk_score += 0.2
            
            # Sentiment component
            if abs(sentiment_score) > 0.7:  # Extreme sentiment
                risk_score += 0.3
            
            # Trend component
            if trend_strength > 0.8:  # Strong trending
                risk_score += 0.3
            
            if risk_score > 0.7:
                return 'high'
            elif risk_score > 0.4:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            self.logger.error(f"Error assessing risk level: {e}")
            return 'medium'
    
    async def _identify_key_levels(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Identify key support and resistance levels"""
        try:
            spy_data = market_data.get('SPY', {})
            current_price = spy_data.get('price', 400)
            
            # Simple key levels calculation
            # In production, this would use technical analysis
            return {
                'support_1': current_price * 0.98,
                'support_2': current_price * 0.95,
                'resistance_1': current_price * 1.02,
                'resistance_2': current_price * 1.05
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying key levels: {e}")
            return {}
    
    async def _analyze_market_breadth(self) -> Dict[str, float]:
        """Analyze market breadth indicators"""
        try:
            # This would analyze advance/decline ratios, new highs/lows, etc.
            # For now, return mock data
            return {
                'advance_decline_ratio': 1.2,
                'new_highs_lows_ratio': 0.8,
                'up_volume_ratio': 0.6,
                'breadth_score': 0.65
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market breadth: {e}")
            return {}
    
    async def _analyze_sector_rotation(self) -> Dict[str, float]:
        """Analyze sector rotation patterns"""
        try:
            sector_performance = {}
            
            for sector, etf in self.sector_etfs.items():
                try:
                    if self.market_engine:
                        quote = await self.market_engine.get_quote(etf)
                        if quote:
                            sector_performance[sector] = quote.change_percent
                    else:
                        # Mock data
                        sector_performance[sector] = np.random.normal(0, 1.5)
                except:
                    sector_performance[sector] = 0.0
            
            return sector_performance
            
        except Exception as e:
            self.logger.error(f"Error analyzing sector rotation: {e}")
            return {}
    
    async def _analyze_institutional_flow(self) -> Dict[str, Any]:
        """Analyze institutional money flow"""
        try:
            # This would analyze institutional trading patterns
            # For now, return mock data
            return {
                'net_flow': 'positive',
                'flow_strength': 0.6,
                'smart_money_indicator': 0.7,
                'dark_pool_activity': 'elevated'
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing institutional flow: {e}")
            return {}
    
    async def get_current_context(self) -> Optional[MarketIntelligence]:
        """Get current market context"""
        if not self.current_context:
            await self._update_market_context()
        return self.current_context
    
    async def get_context_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Get specific context for a symbol"""
        try:
            current_context = await self.get_current_context()
            
            if not current_context:
                return {}
            
            # Get symbol-specific data
            symbol_context = {
                'market_regime': current_context.regime.value,
                'market_phase': current_context.phase.value,
                'overall_sentiment': current_context.sentiment_score,
                'volatility_environment': current_context.volatility_percentile,
                'trend_strength': current_context.trend_strength,
                'risk_level': current_context.risk_level
            }
            
            # Add sector-specific context if applicable
            for sector, etf in self.sector_etfs.items():
                if symbol == etf:
                    symbol_context['sector'] = sector
                    symbol_context['sector_performance'] = current_context.sector_rotation.get(sector, 0.0)
                    break
            
            return symbol_context
            
        except Exception as e:
            self.logger.error(f"Error getting context for {symbol}: {e}")
            return {}
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get market context engine status"""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'current_context_available': self.current_context is not None,
            'context_history_count': len(self.context_history),
            'last_update': self.current_context.timestamp.isoformat() if self.current_context else None,
            'update_interval_seconds': self.update_interval,
            'monitored_symbols': len(self.market_symbols),
            'monitored_sectors': len(self.sector_etfs)
        }


# Global market context engine instance
market_context_engine = MarketContextEngine()
