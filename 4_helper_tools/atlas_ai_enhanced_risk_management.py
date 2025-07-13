"""
A.T.L.A.S AI-Enhanced Risk Management System
Dynamic stop-loss calculations, adaptive position sizing, and real-time risk monitoring
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from config import settings
from models import EngineStatus

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class VolatilityRegime(Enum):
    """Market volatility regimes"""
    LOW_VOL = "low_volatility"
    NORMAL_VOL = "normal_volatility"
    HIGH_VOL = "high_volatility"
    EXTREME_VOL = "extreme_volatility"


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for a position or portfolio"""
    symbol: str
    current_price: float
    position_size: float
    entry_price: float
    unrealized_pnl: float
    risk_percentage: float
    volatility: float
    beta: float
    var_1day: float  # Value at Risk (1 day)
    var_5day: float  # Value at Risk (5 day)
    max_drawdown: float
    sharpe_ratio: float
    risk_level: RiskLevel


@dataclass
class DynamicStopLoss:
    """AI-calculated dynamic stop-loss recommendation"""
    symbol: str
    current_price: float
    recommended_stop: float
    stop_percentage: float
    confidence: float
    reasoning: str
    volatility_adjusted: bool
    trend_adjusted: bool
    support_level: Optional[float]
    time_decay_factor: float


@dataclass
class PositionSizeRecommendation:
    """AI-enhanced position sizing recommendation"""
    symbol: str
    recommended_size: float
    max_size: float
    risk_adjusted_size: float
    volatility_factor: float
    correlation_factor: float
    portfolio_impact: float
    reasoning: str


@dataclass
class RiskAlert:
    """Real-time risk monitoring alert"""
    alert_type: str
    severity: str
    symbol: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    action_required: str


class AIEnhancedRiskManager:
    """
    AI-powered risk management system with dynamic calculations and real-time monitoring
    """
    
    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        self.market_engine = None
        self.ml_predictor = None
        self.sentiment_analyzer = None
        
        # Risk parameters
        self.max_portfolio_risk = 0.02  # 2% max daily portfolio risk
        self.max_position_risk = 0.01   # 1% max risk per position
        self.correlation_threshold = 0.7  # Maximum correlation between positions
        
        # Volatility thresholds
        self.volatility_thresholds = {
            VolatilityRegime.LOW_VOL: 0.15,
            VolatilityRegime.NORMAL_VOL: 0.25,
            VolatilityRegime.HIGH_VOL: 0.40,
            VolatilityRegime.EXTREME_VOL: 0.60
        }
        
        # Active risk alerts
        self.active_alerts = []
        
        # Historical data cache
        self.price_history = {}
        self.volatility_cache = {}
        
    async def initialize(self, market_engine=None, ml_predictor=None, sentiment_analyzer=None):
        """Initialize with engine references"""
        try:
            self.market_engine = market_engine
            self.ml_predictor = ml_predictor
            self.sentiment_analyzer = sentiment_analyzer
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] AI-Enhanced Risk Manager initialized")
            
        except Exception as e:
            logger.error(f"[ERROR] AI-Enhanced Risk Manager initialization failed: {e}")
            self.status = EngineStatus.FAILED
            raise
    
    async def calculate_dynamic_stop_loss(self, symbol: str, entry_price: float, 
                                        position_size: float, timeframe: str = "1day") -> DynamicStopLoss:
        """Calculate AI-enhanced dynamic stop-loss"""
        try:
            current_price = await self._get_current_price(symbol)
            
            # Get historical volatility
            volatility = await self._calculate_volatility(symbol, timeframe)
            
            # Get support/resistance levels
            support_level = await self._find_support_level(symbol)
            
            # Base stop-loss calculation (ATR-based)
            atr_stop = await self._calculate_atr_stop(symbol, entry_price, volatility)
            
            # Volatility adjustment
            volatility_regime = self._classify_volatility_regime(volatility)
            volatility_multiplier = self._get_volatility_multiplier(volatility_regime)
            
            # Trend adjustment
            trend_direction = await self._determine_trend(symbol)
            trend_multiplier = 1.2 if trend_direction == "bullish" else 0.8
            
            # ML-enhanced stop calculation
            ml_stop = await self._ml_enhanced_stop_calculation(symbol, entry_price, current_price)
            
            # Combine all factors
            base_stop_distance = abs(current_price - entry_price) * 0.02  # 2% base
            atr_distance = atr_stop * volatility_multiplier * trend_multiplier
            
            # Use the more conservative (wider) stop
            final_stop_distance = max(base_stop_distance, atr_distance)
            
            # Apply ML adjustment if available
            if ml_stop:
                ml_distance = abs(current_price - ml_stop)
                final_stop_distance = (final_stop_distance + ml_distance) / 2
            
            # Calculate final stop price
            if position_size > 0:  # Long position
                recommended_stop = current_price - final_stop_distance
            else:  # Short position
                recommended_stop = current_price + final_stop_distance
            
            # Adjust for support/resistance
            if support_level and position_size > 0:
                recommended_stop = min(recommended_stop, support_level * 0.98)
            
            stop_percentage = abs(recommended_stop - current_price) / current_price
            
            # Calculate confidence based on data quality
            confidence = self._calculate_stop_confidence(volatility, support_level, ml_stop)
            
            # Generate reasoning
            reasoning = self._generate_stop_reasoning(volatility_regime, trend_direction, 
                                                    support_level, ml_stop)
            
            return DynamicStopLoss(
                symbol=symbol,
                current_price=current_price,
                recommended_stop=recommended_stop,
                stop_percentage=stop_percentage,
                confidence=confidence,
                reasoning=reasoning,
                volatility_adjusted=True,
                trend_adjusted=True,
                support_level=support_level,
                time_decay_factor=1.0
            )
            
        except Exception as e:
            logger.error(f"Error calculating dynamic stop-loss for {symbol}: {e}")
            # Fallback to simple percentage stop
            current_price = await self._get_current_price(symbol)
            fallback_stop = current_price * 0.98 if position_size > 0 else current_price * 1.02
            
            return DynamicStopLoss(
                symbol=symbol,
                current_price=current_price,
                recommended_stop=fallback_stop,
                stop_percentage=0.02,
                confidence=0.5,
                reasoning="Fallback 2% stop due to calculation error",
                volatility_adjusted=False,
                trend_adjusted=False,
                support_level=None,
                time_decay_factor=1.0
            )
    
    async def calculate_adaptive_position_size(self, symbol: str, account_value: float,
                                             risk_tolerance: float = 0.02) -> PositionSizeRecommendation:
        """Calculate adaptive position size based on market conditions"""
        try:
            # Get current market data
            current_price = await self._get_current_price(symbol)
            volatility = await self._calculate_volatility(symbol)
            
            # Base position size calculation
            base_risk_amount = account_value * risk_tolerance
            
            # Volatility adjustment
            volatility_regime = self._classify_volatility_regime(volatility)
            volatility_factor = self._get_position_size_multiplier(volatility_regime)
            
            # Correlation adjustment (if portfolio exists)
            correlation_factor = await self._calculate_correlation_adjustment(symbol)
            
            # Market regime adjustment
            market_regime = await self._assess_market_regime()
            regime_factor = self._get_regime_multiplier(market_regime)
            
            # Calculate adjusted position size
            risk_adjusted_amount = base_risk_amount * volatility_factor * correlation_factor * regime_factor
            
            # Convert to share quantity
            stop_loss_distance = current_price * 0.02  # Assume 2% stop
            recommended_shares = risk_adjusted_amount / stop_loss_distance
            recommended_size = recommended_shares * current_price
            
            # Maximum position size (never more than 20% of account)
            max_size = account_value * 0.20
            final_size = min(recommended_size, max_size)
            
            # Portfolio impact assessment
            portfolio_impact = final_size / account_value
            
            reasoning = f"""Position sizing based on:
• Volatility regime: {volatility_regime.value} (factor: {volatility_factor:.2f})
• Correlation factor: {correlation_factor:.2f}
• Market regime factor: {regime_factor:.2f}
• Portfolio impact: {portfolio_impact*100:.1f}%"""
            
            return PositionSizeRecommendation(
                symbol=symbol,
                recommended_size=final_size,
                max_size=max_size,
                risk_adjusted_size=risk_adjusted_amount,
                volatility_factor=volatility_factor,
                correlation_factor=correlation_factor,
                portfolio_impact=portfolio_impact,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            # Fallback calculation
            fallback_size = account_value * 0.05  # 5% of account
            return PositionSizeRecommendation(
                symbol=symbol,
                recommended_size=fallback_size,
                max_size=account_value * 0.20,
                risk_adjusted_size=fallback_size,
                volatility_factor=1.0,
                correlation_factor=1.0,
                portfolio_impact=0.05,
                reasoning="Fallback 5% position size due to calculation error"
            )


    async def monitor_real_time_risk(self, portfolio: Dict[str, Any]) -> List[RiskAlert]:
        """Real-time risk monitoring with automatic alerts"""
        alerts = []

        try:
            total_portfolio_value = portfolio.get("total_value", 0)
            positions = portfolio.get("positions", [])

            # Portfolio-level risk checks
            portfolio_risk = await self._calculate_portfolio_risk(positions)
            if portfolio_risk > self.max_portfolio_risk:
                alerts.append(RiskAlert(
                    alert_type="portfolio_risk",
                    severity="high",
                    symbol="PORTFOLIO",
                    message=f"Portfolio risk ({portfolio_risk*100:.1f}%) exceeds maximum ({self.max_portfolio_risk*100:.1f}%)",
                    current_value=portfolio_risk,
                    threshold_value=self.max_portfolio_risk,
                    timestamp=datetime.now(),
                    action_required="Reduce position sizes or close some positions"
                ))

            # Position-level risk checks
            for position in positions:
                symbol = position.get("symbol", "")
                position_value = position.get("market_value", 0)
                unrealized_pnl = position.get("unrealized_pnl", 0)

                # Position size check
                position_risk = abs(position_value) / total_portfolio_value
                if position_risk > 0.25:  # 25% max per position
                    alerts.append(RiskAlert(
                        alert_type="position_size",
                        severity="medium",
                        symbol=symbol,
                        message=f"Position size ({position_risk*100:.1f}%) is large",
                        current_value=position_risk,
                        threshold_value=0.25,
                        timestamp=datetime.now(),
                        action_required="Consider reducing position size"
                    ))

                # Drawdown check
                if unrealized_pnl < 0:
                    drawdown = abs(unrealized_pnl) / abs(position_value)
                    if drawdown > 0.10:  # 10% drawdown alert
                        alerts.append(RiskAlert(
                            alert_type="drawdown",
                            severity="high" if drawdown > 0.15 else "medium",
                            symbol=symbol,
                            message=f"Position down {drawdown*100:.1f}%",
                            current_value=drawdown,
                            threshold_value=0.10,
                            timestamp=datetime.now(),
                            action_required="Review stop-loss and consider exit"
                        ))

            # Correlation risk check
            correlation_risk = await self._check_correlation_risk(positions)
            if correlation_risk > self.correlation_threshold:
                alerts.append(RiskAlert(
                    alert_type="correlation",
                    severity="medium",
                    symbol="PORTFOLIO",
                    message=f"High correlation between positions ({correlation_risk:.2f})",
                    current_value=correlation_risk,
                    threshold_value=self.correlation_threshold,
                    timestamp=datetime.now(),
                    action_required="Diversify holdings to reduce correlation"
                ))

            # Update active alerts
            self.active_alerts = alerts

            return alerts

        except Exception as e:
            logger.error(f"Error in real-time risk monitoring: {e}")
            return []

    # Helper methods
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            if self.market_engine:
                quote = await self.market_engine.get_quote(symbol)
                return quote.get("price", 100.0)
            else:
                # Fallback prices for testing
                fallback_prices = {
                    "AAPL": 175.0, "MSFT": 340.0, "GOOGL": 125.0,
                    "TSLA": 250.0, "NVDA": 450.0, "SPY": 450.0
                }
                return fallback_prices.get(symbol, 100.0)
        except:
            return 100.0

    async def _calculate_volatility(self, symbol: str, timeframe: str = "1day") -> float:
        """Calculate historical volatility"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.volatility_cache:
                cached_time, cached_vol = self.volatility_cache[cache_key]
                if datetime.now() - cached_time < timedelta(hours=1):
                    return cached_vol

            # Calculate volatility (simplified for demo)
            if self.market_engine:
                # Would get historical data and calculate actual volatility
                volatility = 0.25  # Placeholder
            else:
                # Default volatilities by symbol
                default_vols = {
                    "SPY": 0.15, "QQQ": 0.20, "AAPL": 0.25,
                    "TSLA": 0.45, "NVDA": 0.35, "MSFT": 0.22
                }
                volatility = default_vols.get(symbol, 0.25)

            # Cache result
            self.volatility_cache[cache_key] = (datetime.now(), volatility)
            return volatility

        except Exception as e:
            logger.error(f"Error calculating volatility for {symbol}: {e}")
            return 0.25  # Default volatility

    def _classify_volatility_regime(self, volatility: float) -> VolatilityRegime:
        """Classify volatility regime"""
        if volatility <= self.volatility_thresholds[VolatilityRegime.LOW_VOL]:
            return VolatilityRegime.LOW_VOL
        elif volatility <= self.volatility_thresholds[VolatilityRegime.NORMAL_VOL]:
            return VolatilityRegime.NORMAL_VOL
        elif volatility <= self.volatility_thresholds[VolatilityRegime.HIGH_VOL]:
            return VolatilityRegime.HIGH_VOL
        else:
            return VolatilityRegime.EXTREME_VOL

    def _get_volatility_multiplier(self, regime: VolatilityRegime) -> float:
        """Get volatility multiplier for stop-loss calculation"""
        multipliers = {
            VolatilityRegime.LOW_VOL: 0.8,
            VolatilityRegime.NORMAL_VOL: 1.0,
            VolatilityRegime.HIGH_VOL: 1.3,
            VolatilityRegime.EXTREME_VOL: 1.6
        }
        return multipliers.get(regime, 1.0)

    def _get_position_size_multiplier(self, regime: VolatilityRegime) -> float:
        """Get position size multiplier based on volatility"""
        multipliers = {
            VolatilityRegime.LOW_VOL: 1.2,    # Larger positions in low vol
            VolatilityRegime.NORMAL_VOL: 1.0,
            VolatilityRegime.HIGH_VOL: 0.7,   # Smaller positions in high vol
            VolatilityRegime.EXTREME_VOL: 0.5
        }
        return multipliers.get(regime, 1.0)

    async def _find_support_level(self, symbol: str) -> Optional[float]:
        """Find nearest support level"""
        try:
            current_price = await self._get_current_price(symbol)
            # Simplified support calculation (would use actual technical analysis)
            support_level = current_price * 0.95  # 5% below current price
            return support_level
        except:
            return None

    async def _calculate_atr_stop(self, symbol: str, entry_price: float, volatility: float) -> float:
        """Calculate ATR-based stop distance"""
        try:
            # Simplified ATR calculation
            atr = entry_price * volatility * 0.1  # 10% of volatility as ATR proxy
            return atr * 2  # 2x ATR for stop distance
        except:
            return entry_price * 0.02  # 2% fallback

    async def _determine_trend(self, symbol: str) -> str:
        """Determine trend direction"""
        try:
            # Simplified trend determination
            # Would use actual technical indicators
            return "bullish"  # Placeholder
        except:
            return "neutral"

    async def _ml_enhanced_stop_calculation(self, symbol: str, entry_price: float, current_price: float) -> Optional[float]:
        """ML-enhanced stop-loss calculation"""
        try:
            if self.ml_predictor:
                # Would use ML model to predict optimal stop
                # For now, return None to indicate ML not available
                return None
            return None
        except:
            return None

    def _calculate_stop_confidence(self, volatility: float, support_level: Optional[float], ml_stop: Optional[float]) -> float:
        """Calculate confidence in stop-loss recommendation"""
        confidence = 0.5  # Base confidence

        # Higher confidence with lower volatility
        if volatility < 0.2:
            confidence += 0.2
        elif volatility > 0.4:
            confidence -= 0.1

        # Higher confidence with support level
        if support_level:
            confidence += 0.2

        # Higher confidence with ML confirmation
        if ml_stop:
            confidence += 0.1

        return min(max(confidence, 0.3), 0.9)

    def _generate_stop_reasoning(self, volatility_regime: VolatilityRegime, trend_direction: str,
                                support_level: Optional[float], ml_stop: Optional[float]) -> str:
        """Generate human-readable reasoning for stop-loss"""
        reasoning = f"Stop-loss calculated based on {volatility_regime.value} market conditions"

        if trend_direction == "bullish":
            reasoning += " with bullish trend adjustment"
        elif trend_direction == "bearish":
            reasoning += " with bearish trend adjustment"

        if support_level:
            reasoning += " and nearby support level"

        if ml_stop:
            reasoning += " with ML model confirmation"

        return reasoning

    async def _calculate_portfolio_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate overall portfolio risk"""
        try:
            total_risk = 0.0
            for position in positions:
                position_value = abs(position.get("market_value", 0))
                unrealized_pnl = position.get("unrealized_pnl", 0)
                if position_value > 0:
                    position_risk = abs(unrealized_pnl) / position_value
                    total_risk += position_risk

            return total_risk / len(positions) if positions else 0.0
        except:
            return 0.0

    async def _check_correlation_risk(self, positions: List[Dict[str, Any]]) -> float:
        """Check correlation risk between positions"""
        try:
            if len(positions) < 2:
                return 0.0

            # Simplified correlation check
            # In reality, would calculate actual correlations
            symbols = [pos.get("symbol", "") for pos in positions]

            # Check for sector concentration
            tech_stocks = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
            tech_count = sum(1 for symbol in symbols if symbol in tech_stocks)

            if tech_count > len(symbols) * 0.6:  # More than 60% in tech
                return 0.8  # High correlation

            return 0.3  # Default moderate correlation
        except:
            return 0.0

    async def _calculate_correlation_adjustment(self, symbol: str) -> float:
        """Calculate correlation adjustment factor for position sizing"""
        try:
            # Simplified correlation adjustment
            # Would check actual portfolio correlations
            return 1.0  # No adjustment for now
        except:
            return 1.0

    async def _assess_market_regime(self) -> str:
        """Assess current market regime"""
        try:
            # Simplified market regime assessment
            # Would use VIX, market breadth, etc.
            return "normal"  # Placeholder
        except:
            return "normal"

    def _get_regime_multiplier(self, regime: str) -> float:
        """Get position size multiplier based on market regime"""
        multipliers = {
            "bull": 1.2,
            "normal": 1.0,
            "bear": 0.7,
            "crisis": 0.5
        }
        return multipliers.get(regime, 1.0)

    async def calculate_portfolio_metrics(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            positions = portfolio.get("positions", [])
            total_value = portfolio.get("total_value", 0)

            if not positions or total_value <= 0:
                return {"error": "Invalid portfolio data"}

            # Calculate individual position metrics
            position_metrics = []
            for position in positions:
                symbol = position.get("symbol", "")
                current_price = await self._get_current_price(symbol)
                position_size = position.get("quantity", 0)
                entry_price = position.get("avg_cost", current_price)
                market_value = position.get("market_value", 0)
                unrealized_pnl = position.get("unrealized_pnl", 0)

                volatility = await self._calculate_volatility(symbol)

                # Calculate risk metrics
                risk_percentage = abs(market_value) / total_value
                var_1day = abs(market_value) * volatility * 1.65  # 95% confidence
                var_5day = var_1day * np.sqrt(5)

                # Determine risk level
                if risk_percentage > 0.25:
                    risk_level = RiskLevel.EXTREME
                elif risk_percentage > 0.15:
                    risk_level = RiskLevel.HIGH
                elif risk_percentage > 0.10:
                    risk_level = RiskLevel.MODERATE
                else:
                    risk_level = RiskLevel.LOW

                position_metrics.append(RiskMetrics(
                    symbol=symbol,
                    current_price=current_price,
                    position_size=position_size,
                    entry_price=entry_price,
                    unrealized_pnl=unrealized_pnl,
                    risk_percentage=risk_percentage,
                    volatility=volatility,
                    beta=1.0,  # Placeholder
                    var_1day=var_1day,
                    var_5day=var_5day,
                    max_drawdown=abs(unrealized_pnl) / abs(market_value) if market_value != 0 else 0,
                    sharpe_ratio=0.0,  # Would calculate with returns
                    risk_level=risk_level
                ))

            # Portfolio-level metrics
            total_var_1day = sum(pos.var_1day for pos in position_metrics)
            portfolio_risk = total_var_1day / total_value

            return {
                "portfolio_value": total_value,
                "portfolio_risk": portfolio_risk,
                "total_var_1day": total_var_1day,
                "position_count": len(positions),
                "position_metrics": position_metrics,
                "risk_alerts": await self.monitor_real_time_risk(portfolio)
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {"error": str(e)}

    async def generate_risk_report(self, portfolio: Dict[str, Any]) -> str:
        """Generate comprehensive risk assessment report"""
        try:
            metrics = await self.calculate_portfolio_metrics(portfolio)

            if "error" in metrics:
                return f"[ERROR] Error generating risk report: {metrics['error']}"

            report = f"""[SHIELD] **COMPREHENSIVE RISK ASSESSMENT**
**A.T.L.A.S powered by Predicto**

[DATA] **PORTFOLIO OVERVIEW**
• Total Value: ${metrics['portfolio_value']:,.2f}
• Portfolio Risk: {metrics['portfolio_risk']*100:.2f}%
• Daily VaR (95%): ${metrics['total_var_1day']:,.2f}
• Position Count: {metrics['position_count']}

[TARGET] **POSITION RISK ANALYSIS**"""

            for pos in metrics['position_metrics']:
                risk_emoji = {
                    RiskLevel.LOW: "🟢",
                    RiskLevel.MODERATE: "🟡",
                    RiskLevel.HIGH: "🟠",
                    RiskLevel.EXTREME: "🔴"
                }[pos.risk_level]

                report += f"""
{risk_emoji} **{pos.symbol}**
   • Position Size: {pos.risk_percentage*100:.1f}% of portfolio
   • Current P&L: ${pos.unrealized_pnl:,.2f}
   • Volatility: {pos.volatility*100:.1f}%
   • Daily VaR: ${pos.var_1day:,.2f}
   • Risk Level: {pos.risk_level.value.upper()}"""

            # Risk alerts
            alerts = metrics.get('risk_alerts', [])
            if alerts:
                report += f"""

[WARN] **ACTIVE RISK ALERTS** ({len(alerts)} alerts)"""
                for alert in alerts[:5]:  # Show top 5 alerts
                    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert.severity, "⚪")
                    report += f"""
{severity_emoji} {alert.alert_type.upper()}: {alert.message}
   Action: {alert.action_required}"""

            # Recommendations
            report += f"""

[IDEA] **RISK MANAGEMENT RECOMMENDATIONS**
• Maintain stop-losses on all positions
• Consider reducing position sizes if portfolio risk > 3%
• Diversify across sectors and asset classes
• Monitor correlation between positions
• Review and adjust risk parameters weekly

🎓 **EDUCATIONAL NOTE**
Risk management is the foundation of successful trading. Never risk more than you can afford to lose, and always have a plan for both profits and losses."""

            return report

        except Exception as e:
            logger.error(f"Error generating risk report: {e}")
            return "[ERROR] Error generating risk assessment report. Please try again."


# Global instance
ai_enhanced_risk_manager = AIEnhancedRiskManager()
