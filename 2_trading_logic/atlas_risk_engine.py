"""
A.T.L.A.S Risk Engine - AI-Enhanced Risk Management
Safety guardrails and AI-enhanced stop-loss calculation
"""

# CRITICAL: Import startup initialization FIRST to ensure Windows-compatible logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '4_helper_tools'))

try:
    from atlas_startup_init import initialize_component_logging
    logger = initialize_component_logging('atlas_risk_engine')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

import asyncio
import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from config import settings
from models import (
    RiskAssessment, AnalysisRequest, EngineStatus, OrderSide
)


class AtlasRiskEngine:
    """
    Risk management engine with AI-enhanced analysis and safety guardrails
    """
    
    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        
        # Risk parameters
        self.max_position_size = settings.DEFAULT_RISK_PERCENT / 100.0  # 2% default
        self.max_daily_loss = 0.03  # 3% max daily loss
        self.max_portfolio_risk = 0.10  # 10% max portfolio risk
        
        # Risk monitoring
        self.daily_pnl = 0.0
        self.portfolio_risk = 0.0
        self.active_positions_risk = {}
        
        # Circuit breakers
        self.circuit_breakers = {
            "daily_loss": False,
            "portfolio_risk": False,
            "volatility": False
        }
        
        logger.info("[SHIELD] Risk Engine created - safety guardrails active")
    
    async def initialize(self):
        """Initialize risk engine"""
        try:
            # Load risk parameters from config
            self._load_risk_parameters()
            
            # Initialize risk monitoring
            await self._initialize_risk_monitoring()
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Risk Engine initialization completed")
            
        except Exception as e:
            logger.error(f"[ERROR] Risk Engine initialization failed: {e}")
            self.status = EngineStatus.DEGRADED
            # Continue with basic risk management
    
    def _load_risk_parameters(self):
        """Load risk parameters from configuration"""
        try:
            self.max_position_size = settings.DEFAULT_RISK_PERCENT / 100.0
            logger.info(f"[DATA] Risk parameters loaded - Max position size: {self.max_position_size:.1%}")
            
        except Exception as e:
            logger.error(f"Error loading risk parameters: {e}")
    
    async def _initialize_risk_monitoring(self):
        """Initialize risk monitoring systems"""
        try:
            # Reset daily tracking
            self.daily_pnl = 0.0
            self.portfolio_risk = 0.0
            
            # Reset circuit breakers
            for breaker in self.circuit_breakers:
                self.circuit_breakers[breaker] = False
            
            logger.info("[SEARCH] Risk monitoring systems initialized")
            
        except Exception as e:
            logger.error(f"Risk monitoring initialization error: {e}")
    
    async def assess_risk(self, request: AnalysisRequest) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        try:
            # Input validation
            if not request or not hasattr(request, 'symbol') or not request.symbol:
                raise ValueError("Invalid request: symbol is required")

            symbol = request.symbol

            # Get current market data (would integrate with market engine)
            current_price = 100.0  # Placeholder

            # Validate price data
            if current_price <= 0:
                raise ValueError(f"Invalid price data for {symbol}: {current_price}")

            # Calculate position sizing
            position_size = await self._calculate_position_size(symbol, current_price)

            # Validate position size
            if position_size <= 0:
                logger.warning(f"Invalid position size calculated for {symbol}: {position_size}")
                position_size = 1  # Default minimal position

            # Calculate stop loss
            stop_loss_price = await self._calculate_ai_stop_loss(symbol, current_price)

            # Validate stop loss
            if stop_loss_price <= 0 or stop_loss_price >= current_price:
                logger.warning(f"Invalid stop loss calculated for {symbol}: {stop_loss_price}")
                stop_loss_price = current_price * 0.95  # Default 5% stop loss

            # Calculate risk metrics with error handling
            risk_amount = abs(current_price - stop_loss_price) * position_size
            position_value = current_price * position_size
            risk_percentage = (risk_amount / position_value) * 100 if position_value > 0 else 0.0
            
            # Assess overall risk score
            risk_score = await self._calculate_risk_score(symbol, current_price, position_size)
            
            # Generate risk factors and recommendations
            risk_factors = await self._identify_risk_factors(symbol, current_price)
            recommendations = await self._generate_recommendations(symbol, risk_score, risk_factors)
            
            # Calculate confidence level
            confidence_level = await self._calculate_confidence(symbol, risk_score)
            
            return RiskAssessment(
                symbol=symbol,
                risk_score=risk_score,
                position_size=position_size,
                stop_loss_price=stop_loss_price,
                risk_amount=risk_amount,
                risk_percentage=risk_percentage,
                confidence_level=confidence_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except ValueError as e:
            logger.error(f"Risk assessment validation error for {request.symbol}: {e}")
            # Return conservative risk assessment for validation errors
            return RiskAssessment(
                symbol=request.symbol,
                risk_score=9.0,  # Very high risk due to validation error
                position_size=0,
                stop_loss_price=0,
                risk_amount=0,
                risk_percentage=0,
                confidence=0.0,
                risk_factors=[f"Validation error: {str(e)}"],
                recommendations=["Fix data issues before trading"],
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Risk assessment error for {request.symbol}: {e}")
            # Return conservative risk assessment for unexpected errors
            return RiskAssessment(
                symbol=request.symbol,
                risk_score=8.0,  # High risk due to error
                position_size=0,
                stop_loss_price=0,
                risk_amount=0,
                risk_percentage=0,
                confidence=0.1,
                risk_factors=["Risk assessment failed"],
                recommendations=["Manual review required"],
                timestamp=datetime.now()
            )
    
    async def _calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate optimal position size based on risk parameters"""
        try:
            # Get account value (would integrate with trading engine)
            account_value = 100000.0  # Placeholder
            
            # Calculate base position size
            max_risk_amount = account_value * self.max_position_size
            
            # Adjust for volatility (simplified)
            volatility_factor = await self._get_volatility_factor(symbol)
            adjusted_risk = max_risk_amount / volatility_factor if volatility_factor > 0 else max_risk_amount

            # Calculate position size
            position_size = adjusted_risk / price if price > 0 else 0

            # Apply maximum position limits
            max_position_value = account_value * 0.20  # Max 20% in single position
            max_shares = max_position_value / price if price > 0 else 0
            
            position_size = min(position_size, max_shares)
            
            # Input validation for calculated values
            if position_size <= 0:
                logger.warning(f"Calculated position size is zero or negative for {symbol}: {position_size}")
                return 1.0  # Minimum viable position

            logger.info(f"Position size calculated for {symbol}: {position_size:.2f} shares")
            return max(1.0, position_size)  # Ensure minimum 1 share

        except ValueError as e:
            logger.error(f"Position size validation error for {symbol}: {e}")
            return 1.0  # Conservative fallback
        except Exception as e:
            logger.error(f"Position size calculation error for {symbol}: {e}")
            return 1.0  # Conservative fallback
    
    async def _calculate_ai_stop_loss(self, symbol: str, current_price: float) -> float:
        """Calculate AI-enhanced stop loss price"""
        try:
            # Technical analysis based stop loss
            technical_stop = await self._calculate_technical_stop_loss(symbol, current_price)
            
            # Volatility based stop loss
            volatility_stop = await self._calculate_volatility_stop_loss(symbol, current_price)
            
            # Support/Resistance based stop loss
            support_stop = await self._calculate_support_stop_loss(symbol, current_price)
            
            # AI consensus (simplified)
            stop_prices = [technical_stop, volatility_stop, support_stop]
            stop_prices = [price for price in stop_prices if price > 0]
            
            if stop_prices:
                # Use the most conservative (closest to current price) stop
                ai_stop_loss = max(stop_prices)  # For long positions
            else:
                # Fallback to percentage-based stop
                ai_stop_loss = current_price * 0.98  # 2% stop loss
            
            logger.info(f"[TARGET] AI stop loss calculated for {symbol}: ${ai_stop_loss:.2f}")
            return ai_stop_loss
            
        except Exception as e:
            logger.error(f"AI stop loss calculation error: {e}")
            return current_price * 0.98  # Fallback
    
    async def _calculate_technical_stop_loss(self, symbol: str, price: float) -> float:
        """Calculate technical analysis based stop loss"""
        try:
            # Simplified technical stop loss
            # In production, this would use actual technical indicators
            
            # ATR-based stop (Average True Range)
            atr = price * 0.02  # Simplified 2% ATR
            technical_stop = price - (atr * 2)  # 2x ATR stop
            
            return max(technical_stop, price * 0.95)  # Max 5% stop
            
        except Exception as e:
            logger.error(f"Technical stop loss error: {e}")
            return price * 0.98
    
    async def _calculate_volatility_stop_loss(self, symbol: str, price: float) -> float:
        """Calculate volatility-based stop loss"""
        try:
            # Get volatility factor
            volatility = await self._get_volatility_factor(symbol)
            
            # Adjust stop based on volatility
            volatility_multiplier = min(volatility, 3.0)  # Cap at 3x
            stop_percentage = 0.02 * volatility_multiplier  # Base 2% * volatility
            
            volatility_stop = price * (1 - stop_percentage)
            
            return max(volatility_stop, price * 0.90)  # Max 10% stop
            
        except Exception as e:
            logger.error(f"Volatility stop loss error: {e}")
            return price * 0.98
    
    async def _calculate_support_stop_loss(self, symbol: str, price: float) -> float:
        """Calculate support/resistance based stop loss"""
        try:
            # Simplified support level calculation
            # In production, this would analyze actual price levels
            
            # Assume support is 3-5% below current price
            support_level = price * 0.96  # 4% below as support
            
            # Place stop slightly below support
            support_stop = support_level * 0.995  # 0.5% below support
            
            return support_stop
            
        except Exception as e:
            logger.error(f"Support stop loss error: {e}")
            return price * 0.98
    
    async def _get_volatility_factor(self, symbol: str) -> float:
        """Get volatility factor for symbol"""
        try:
            # Simplified volatility calculation
            # In production, this would calculate actual historical volatility
            
            volatility_map = {
                "SPY": 1.0,
                "QQQ": 1.2,
                "AAPL": 1.3,
                "TSLA": 2.5,
                "NVDA": 2.0,
                "AMZN": 1.8
            }
            
            return volatility_map.get(symbol, 1.5)  # Default moderate volatility
            
        except Exception as e:
            logger.error(f"Volatility factor error: {e}")
            return 1.5
    
    async def _calculate_risk_score(self, symbol: str, price: float, position_size: float) -> float:
        """Calculate overall risk score (0-10)"""
        try:
            # Base risk factors
            volatility_risk = min((await self._get_volatility_factor(symbol)) * 2, 10)
            position_value = position_size * price
            position_risk = min((position_value / 100000) * 50, 10) if position_value > 0 else 0  # Position as % of account
            market_risk = 3.0  # Placeholder market risk
            
            # Weighted risk score
            risk_score = (volatility_risk * 0.4 + position_risk * 0.3 + market_risk * 0.3)
            
            return min(max(risk_score, 0.0), 10.0)
            
        except Exception as e:
            logger.error(f"Risk score calculation error: {e}")
            return 5.0  # Moderate risk
    
    async def _identify_risk_factors(self, symbol: str, price: float) -> List[str]:
        """Identify specific risk factors"""
        try:
            risk_factors = []
            
            # Volatility risk
            volatility = await self._get_volatility_factor(symbol)
            if volatility > 2.0:
                risk_factors.append("High volatility stock")
            
            # Market conditions
            # This would integrate with market analysis
            risk_factors.append("General market uncertainty")
            
            # Sector risks
            if symbol in ["TSLA", "NVDA", "AMD"]:
                risk_factors.append("Technology sector concentration")
            
            # Liquidity risks
            if symbol not in ["SPY", "QQQ", "AAPL", "MSFT"]:
                risk_factors.append("Lower liquidity stock")
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Risk factors identification error: {e}")
            return ["Unable to assess specific risks"]
    
    async def _generate_recommendations(self, symbol: str, risk_score: float, risk_factors: List[str]) -> List[str]:
        """Generate risk management recommendations"""
        try:
            recommendations = []
            
            if risk_score > 7.0:
                recommendations.append("Consider reducing position size due to high risk")
                recommendations.append("Use tighter stop loss")
            elif risk_score > 5.0:
                recommendations.append("Monitor position closely")
                recommendations.append("Consider taking partial profits if available")
            else:
                recommendations.append("Risk level acceptable for current strategy")
            
            # Specific recommendations based on risk factors
            if "High volatility stock" in risk_factors:
                recommendations.append("Use wider stop loss to avoid whipsaws")
            
            if "Technology sector concentration" in risk_factors:
                recommendations.append("Consider diversifying across sectors")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation error: {e}")
            return ["Monitor position and market conditions"]
    
    async def _calculate_confidence(self, symbol: str, risk_score: float) -> float:
        """Calculate confidence level in risk assessment"""
        try:
            # Base confidence
            base_confidence = 0.8
            
            # Adjust based on data availability
            # In production, this would consider data quality and completeness
            
            # Adjust based on risk score extremes
            if risk_score < 2.0 or risk_score > 8.0:
                base_confidence *= 0.9  # Less confident in extreme scores
            
            return min(max(base_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.7
    
    async def check_circuit_breakers(self, portfolio_value: float, daily_pnl: float) -> Dict[str, bool]:
        """Check if any circuit breakers should be triggered"""
        try:
            # Daily loss circuit breaker
            daily_loss_pct = abs(daily_pnl) / portfolio_value if portfolio_value > 0 else 0
            if daily_loss_pct > self.max_daily_loss:
                self.circuit_breakers["daily_loss"] = True
                logger.warning(f"🚨 Daily loss circuit breaker triggered: {daily_loss_pct:.1%}")
            
            # Portfolio risk circuit breaker
            if self.portfolio_risk > self.max_portfolio_risk:
                self.circuit_breakers["portfolio_risk"] = True
                logger.warning(f"🚨 Portfolio risk circuit breaker triggered: {self.portfolio_risk:.1%}")
            
            return self.circuit_breakers.copy()
            
        except Exception as e:
            logger.error(f"Circuit breaker check error: {e}")
            return self.circuit_breakers
    
    async def cleanup(self):
        """Cleanup risk engine resources"""
        try:
            # Save risk metrics
            # Reset circuit breakers
            for breaker in self.circuit_breakers:
                self.circuit_breakers[breaker] = False
            
            logger.info("[OK] Risk Engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during risk engine cleanup: {e}")
