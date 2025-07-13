"""
A.T.L.A.S Options Trading Engine
Advanced options trading with Greeks calculations, strategies, and risk management
"""

import logging
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import asyncio

from config import settings
from models import OptionType, StrategyType, OptionContract, OptionsStrategy, Quote, Position
from atlas_performance_optimizer import performance_optimizer

logger = logging.getLogger(__name__)


class BlackScholesCalculator:
    """
    Complete Black-Scholes options pricing and Greeks calculator

    Implements the full Black-Scholes-Merton model for European options
    with comprehensive Greeks calculation and advanced features.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_free_rate = 0.05  # 5% default risk-free rate
        self.dividend_yield = 0.0   # Default dividend yield

        # Calculation precision settings
        self.precision_digits = 6
        self.min_time_to_expiry = 1/365  # Minimum 1 day
        self.min_volatility = 0.001      # Minimum 0.1% volatility
        self.max_volatility = 5.0        # Maximum 500% volatility
    
    def calculate_option_price(self, S: float, K: float, T: float, r: float, 
                             sigma: float, option_type: OptionType) -> float:
        """Calculate Black-Scholes option price"""
        try:
            if T <= 0:
                # Option expired - intrinsic value only
                if option_type == OptionType.CALL:
                    return max(S - K, 0)
                else:
                    return max(K - S, 0)
            
            # Black-Scholes formula with zero division protection
            if K <= 0 or sigma <= 0 or T <= 0:
                return 0.01  # Minimal option value

            d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            
            if option_type == OptionType.CALL:
                price = S * self._norm_cdf(d1) - K * math.exp(-r * T) * self._norm_cdf(d2)
            else:
                price = K * math.exp(-r * T) * self._norm_cdf(-d2) - S * self._norm_cdf(-d1)
            
            return max(price, 0.01)  # Minimum price of $0.01
            
        except Exception as e:
            self.logger.error(f"Error calculating option price: {e}")
            return 0.01
    
    def calculate_greeks(self, S: float, K: float, T: float, r: float, 
                        sigma: float, option_type: OptionType) -> Dict[str, float]:
        """Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho)"""
        try:
            if T <= 0 or K <= 0 or S <= 0 or sigma <= 0:
                return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

            d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)

            # Delta
            if option_type == OptionType.CALL:
                delta = self._norm_cdf(d1)
            else:
                delta = self._norm_cdf(d1) - 1

            # Gamma (same for calls and puts)
            denominator = S * sigma * math.sqrt(T)
            gamma = self._norm_pdf(d1) / denominator if denominator > 0 else 0
            
            # Theta (time decay)
            if option_type == OptionType.CALL:
                theta = (-S * self._norm_pdf(d1) * sigma / (2 * math.sqrt(T)) 
                        - r * K * math.exp(-r * T) * self._norm_cdf(d2)) / 365
            else:
                theta = (-S * self._norm_pdf(d1) * sigma / (2 * math.sqrt(T)) 
                        + r * K * math.exp(-r * T) * self._norm_cdf(-d2)) / 365
            
            # Vega (volatility sensitivity)
            vega = S * self._norm_pdf(d1) * math.sqrt(T) / 100
            
            # Rho (interest rate sensitivity)
            if option_type == OptionType.CALL:
                rho = K * T * math.exp(-r * T) * self._norm_cdf(d2) / 100
            else:
                rho = -K * T * math.exp(-r * T) * self._norm_cdf(-d2) / 100
            
            return {
                "delta": round(delta, 4),
                "gamma": round(gamma, 4),
                "theta": round(theta, 4),
                "vega": round(vega, 4),
                "rho": round(rho, 4)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Greeks: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

    def calculate_implied_volatility(self, market_price: float, S: float, K: float,
                                   T: float, r: float, option_type: OptionType,
                                   max_iterations: int = 100, tolerance: float = 1e-6) -> float:
        """
        Calculate implied volatility using Newton-Raphson method

        Args:
            market_price: Observed market price of the option
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            option_type: Call or Put
            max_iterations: Maximum iterations for convergence
            tolerance: Convergence tolerance

        Returns:
            Implied volatility (annualized)
        """
        try:
            # Input validation
            if market_price <= 0 or S <= 0 or K <= 0 or T <= 0:
                return 0.2  # Default 20% volatility

            # Initial guess for volatility
            sigma = 0.2  # Start with 20%

            for i in range(max_iterations):
                # Calculate option price and vega with current volatility
                calculated_price = self.calculate_option_price(S, K, T, r, sigma, option_type)
                greeks = self.calculate_greeks(S, K, T, r, sigma, option_type)
                vega = greeks.get('vega', 0)

                # Price difference
                price_diff = calculated_price - market_price

                # Check convergence
                if abs(price_diff) < tolerance:
                    return round(sigma, 4)

                # Newton-Raphson update
                if vega > 0:
                    sigma = sigma - price_diff / vega
                    # Keep volatility within reasonable bounds
                    sigma = max(self.min_volatility, min(self.max_volatility, sigma))
                else:
                    break

            # Return best estimate if no convergence
            return round(max(self.min_volatility, min(self.max_volatility, sigma)), 4)

        except Exception as e:
            self.logger.error(f"Implied volatility calculation error: {e}")
            return 0.2  # Default fallback

    def calculate_probability_of_profit(self, S: float, K: float, T: float, r: float,
                                      sigma: float, option_type: OptionType,
                                      premium_paid: float) -> float:
        """
        Calculate probability of profit for an options trade

        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put
            premium_paid: Premium paid for the option

        Returns:
            Probability of profit (0-1)
        """
        try:
            if option_type == OptionType.CALL:
                # For calls, need stock price > strike + premium at expiration
                breakeven = K + premium_paid
                # Calculate probability that S_T > breakeven
                d = (math.log(S / breakeven) + (r - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
                prob_profit = 1 - self._norm_cdf(d)
            else:
                # For puts, need stock price < strike - premium at expiration
                breakeven = K - premium_paid
                # Calculate probability that S_T < breakeven
                d = (math.log(S / breakeven) + (r - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
                prob_profit = self._norm_cdf(d)

            return round(max(0, min(1, prob_profit)), 4)

        except Exception as e:
            self.logger.error(f"Probability of profit calculation error: {e}")
            return 0.5  # Default 50% probability

    def calculate_expected_move(self, S: float, T: float, sigma: float) -> Dict[str, float]:
        """
        Calculate expected price move based on implied volatility

        Args:
            S: Current stock price
            T: Time to expiration (years)
            sigma: Implied volatility

        Returns:
            Dictionary with expected moves (1 standard deviation)
        """
        try:
            # Expected move = Stock Price * Volatility * sqrt(Time)
            expected_move = S * sigma * math.sqrt(T)

            return {
                "expected_move_dollars": round(expected_move, 2),
                "expected_move_percent": round((expected_move / S) * 100, 2),
                "upper_range": round(S + expected_move, 2),
                "lower_range": round(S - expected_move, 2),
                "two_sigma_upper": round(S + (2 * expected_move), 2),
                "two_sigma_lower": round(S - (2 * expected_move), 2)
            }

        except Exception as e:
            self.logger.error(f"Expected move calculation error: {e}")
            return {
                "expected_move_dollars": 0,
                "expected_move_percent": 0,
                "upper_range": S,
                "lower_range": S,
                "two_sigma_upper": S,
                "two_sigma_lower": S
            }

    def calculate_time_decay(self, S: float, K: float, T: float, r: float,
                           sigma: float, option_type: OptionType) -> Dict[str, float]:
        """
        Calculate time decay (theta) over different time periods

        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put

        Returns:
            Dictionary with time decay analysis
        """
        try:
            current_price = self.calculate_option_price(S, K, T, r, sigma, option_type)

            # Calculate price after 1 day
            T_1day = max(0, T - 1/365)
            price_1day = self.calculate_option_price(S, K, T_1day, r, sigma, option_type)

            # Calculate price after 1 week
            T_1week = max(0, T - 7/365)
            price_1week = self.calculate_option_price(S, K, T_1week, r, sigma, option_type)

            # Calculate price after 1 month
            T_1month = max(0, T - 30/365)
            price_1month = self.calculate_option_price(S, K, T_1month, r, sigma, option_type)

            return {
                "current_price": round(current_price, 4),
                "price_after_1_day": round(price_1day, 4),
                "price_after_1_week": round(price_1week, 4),
                "price_after_1_month": round(price_1month, 4),
                "theta_1_day": round(price_1day - current_price, 4),
                "theta_1_week": round(price_1week - current_price, 4),
                "theta_1_month": round(price_1month - current_price, 4),
                "daily_decay_percent": round(((price_1day - current_price) / current_price) * 100, 4) if current_price > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Time decay calculation error: {e}")
            return {
                "current_price": 0,
                "price_after_1_day": 0,
                "price_after_1_week": 0,
                "price_after_1_month": 0,
                "theta_1_day": 0,
                "theta_1_week": 0,
                "theta_1_month": 0,
                "daily_decay_percent": 0
            }

class OptionsStrategyRecommendationEngine:
    """
    Comprehensive options strategy recommendation engine

    Implements major options strategies with risk/reward analysis:
    - Covered Calls
    - Protective Puts
    - Long/Short Straddles
    - Long/Short Strangles
    - Bull/Bear Call Spreads
    - Bull/Bear Put Spreads
    - Iron Condors
    - Butterfly Spreads
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bs_calculator = BlackScholesCalculator()

        # Strategy configuration
        self.min_probability_profit = 0.30  # 30% minimum
        self.max_risk_per_trade = 0.05      # 5% of portfolio
        self.min_risk_reward_ratio = 1.5    # 1.5:1 minimum

    def recommend_strategy(self, market_outlook: str, stock_price: float,
                          volatility: float, time_horizon: int,
                          risk_tolerance: str = "medium") -> Dict[str, Any]:
        """
        Recommend optimal options strategy based on market outlook and parameters

        Args:
            market_outlook: "bullish", "bearish", "neutral", "volatile"
            stock_price: Current stock price
            volatility: Implied volatility (annualized)
            time_horizon: Days to expiration
            risk_tolerance: "low", "medium", "high"

        Returns:
            Dictionary with recommended strategies and analysis
        """
        try:
            strategies = []

            # Generate strategy recommendations based on outlook
            if market_outlook.lower() == "bullish":
                strategies.extend(self._get_bullish_strategies(stock_price, volatility, time_horizon))
            elif market_outlook.lower() == "bearish":
                strategies.extend(self._get_bearish_strategies(stock_price, volatility, time_horizon))
            elif market_outlook.lower() == "neutral":
                strategies.extend(self._get_neutral_strategies(stock_price, volatility, time_horizon))
            elif market_outlook.lower() == "volatile":
                strategies.extend(self._get_volatility_strategies(stock_price, volatility, time_horizon))
            else:
                # Default to neutral strategies
                strategies.extend(self._get_neutral_strategies(stock_price, volatility, time_horizon))

            # Filter strategies by risk tolerance
            filtered_strategies = self._filter_by_risk_tolerance(strategies, risk_tolerance)

            # Rank strategies by expected return and probability of profit
            ranked_strategies = self._rank_strategies(filtered_strategies)

            return {
                "market_outlook": market_outlook,
                "recommended_strategies": ranked_strategies[:3],  # Top 3 strategies
                "all_strategies": ranked_strategies,
                "market_conditions": {
                    "stock_price": stock_price,
                    "volatility": volatility,
                    "time_horizon": time_horizon,
                    "risk_tolerance": risk_tolerance
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Strategy recommendation error: {e}")
            return {
                "error": str(e),
                "recommended_strategies": [],
                "market_outlook": market_outlook
            }

    def _get_bullish_strategies(self, stock_price: float, volatility: float,
                               time_horizon: int) -> List[Dict[str, Any]]:
        """Get bullish options strategies"""
        strategies = []

        # 1. Long Call
        call_strike = stock_price * 1.05  # 5% OTM
        long_call = self._analyze_long_call(stock_price, call_strike, time_horizon, volatility)
        strategies.append(long_call)

        # 2. Bull Call Spread
        lower_strike = stock_price * 1.02  # 2% OTM
        upper_strike = stock_price * 1.08  # 8% OTM
        bull_call_spread = self._analyze_bull_call_spread(
            stock_price, lower_strike, upper_strike, time_horizon, volatility
        )
        strategies.append(bull_call_spread)

        # 3. Covered Call (if holding stock)
        call_strike_cc = stock_price * 1.10  # 10% OTM
        covered_call = self._analyze_covered_call(stock_price, call_strike_cc, time_horizon, volatility)
        strategies.append(covered_call)

        return strategies

    def _get_bearish_strategies(self, stock_price: float, volatility: float,
                               time_horizon: int) -> List[Dict[str, Any]]:
        """Get bearish options strategies"""
        strategies = []

        # 1. Long Put
        put_strike = stock_price * 0.95  # 5% OTM
        long_put = self._analyze_long_put(stock_price, put_strike, time_horizon, volatility)
        strategies.append(long_put)

        # 2. Bear Put Spread
        upper_strike = stock_price * 0.98  # 2% OTM
        lower_strike = stock_price * 0.92  # 8% OTM
        bear_put_spread = self._analyze_bear_put_spread(
            stock_price, upper_strike, lower_strike, time_horizon, volatility
        )
        strategies.append(bear_put_spread)

        # 3. Protective Put (if holding stock)
        put_strike_pp = stock_price * 0.90  # 10% OTM
        protective_put = self._analyze_protective_put(stock_price, put_strike_pp, time_horizon, volatility)
        strategies.append(protective_put)

        return strategies

    def _get_neutral_strategies(self, stock_price: float, volatility: float,
                               time_horizon: int) -> List[Dict[str, Any]]:
        """Get neutral/sideways market strategies"""
        strategies = []

        # 1. Iron Condor
        iron_condor = self._analyze_iron_condor(stock_price, time_horizon, volatility)
        strategies.append(iron_condor)

        # 2. Short Straddle
        short_straddle = self._analyze_short_straddle(stock_price, time_horizon, volatility)
        strategies.append(short_straddle)

        # 3. Butterfly Spread
        butterfly = self._analyze_butterfly_spread(stock_price, time_horizon, volatility)
        strategies.append(butterfly)

        return strategies

    def _get_volatility_strategies(self, stock_price: float, volatility: float,
                                  time_horizon: int) -> List[Dict[str, Any]]:
        """Get high volatility strategies"""
        strategies = []

        # 1. Long Straddle
        long_straddle = self._analyze_long_straddle(stock_price, time_horizon, volatility)
        strategies.append(long_straddle)

        # 2. Long Strangle
        call_strike = stock_price * 1.05
        put_strike = stock_price * 0.95
        long_strangle = self._analyze_long_strangle(
            stock_price, call_strike, put_strike, time_horizon, volatility
        )
        strategies.append(long_strangle)

        return strategies

    def _analyze_long_call(self, stock_price: float, strike: float,
                          time_horizon: int, volatility: float) -> Dict[str, Any]:
        """Analyze long call strategy"""
        try:
            time_to_expiry = time_horizon / 365.0
            risk_free_rate = 0.05

            # Calculate option price
            option_price = self.bs_calculator.calculate_option_price(
                stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
            )

            # Calculate Greeks
            greeks = self.bs_calculator.calculate_greeks(
                stock_price, strike, time_to_expiry, risk_free_rate, volatility, OptionType.CALL
            )

            # Risk/Reward analysis
            max_loss = option_price  # Premium paid
            breakeven = strike + option_price

            # Probability of profit
            prob_profit = self.bs_calculator.calculate_probability_of_profit(
                stock_price, strike, time_to_expiry, risk_free_rate, volatility,
                OptionType.CALL, option_price
            )

            return {
                "strategy_name": "Long Call",
                "strategy_type": "bullish",
                "complexity": "beginner",
                "option_price": round(option_price, 2),
                "max_loss": round(max_loss, 2),
                "max_gain": "unlimited",
                "breakeven": round(breakeven, 2),
                "probability_profit": round(prob_profit * 100, 1),
                "greeks": greeks,
                "time_decay_risk": "high",
                "volatility_impact": "positive",
                "recommended_for": "Strong bullish outlook with limited risk",
                "execution_steps": [
                    f"Buy 1 call option with ${strike:.0f} strike",
                    f"Pay premium of ${option_price:.2f}",
                    f"Profit if stock rises above ${breakeven:.2f}",
                    f"Maximum loss: ${max_loss:.2f}"
                ]
            }

        except Exception as e:
            self.logger.error(f"Long call analysis error: {e}")
            return {"strategy_name": "Long Call", "error": str(e)}
    
    def calculate_implied_volatility(self, market_price: float, S: float, K: float, 
                                   T: float, r: float, option_type: OptionType) -> float:
        """Calculate implied volatility using Newton-Raphson method"""
        try:
            if T <= 0:
                return 0.0
            
            # Initial guess
            sigma = 0.3
            tolerance = 0.001
            max_iterations = 100
            
            for i in range(max_iterations):
                price = self.calculate_option_price(S, K, T, r, sigma, option_type)
                vega = self.calculate_greeks(S, K, T, r, sigma, option_type)["vega"] * 100
                
                price_diff = price - market_price
                
                if abs(price_diff) < tolerance or vega == 0:
                    break
                
                # Newton-Raphson update
                sigma = sigma - price_diff / vega
                sigma = max(0.01, min(sigma, 5.0))  # Keep sigma reasonable
            
            return round(sigma, 4)
            
        except Exception as e:
            self.logger.error(f"Error calculating implied volatility: {e}")
            return 0.3  # Default IV
    
    def _norm_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _norm_pdf(self, x: float) -> float:
        """Probability density function for standard normal distribution"""
        return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


class OptionsStrategyBuilder:
    """Builder for complex options strategies"""
    
    def __init__(self, bs_calculator: BlackScholesCalculator):
        self.logger = logging.getLogger(__name__)
        self.bs_calculator = bs_calculator
    
    def build_long_call(self, underlying: str, strike: float, expiration: datetime,
                       underlying_price: float, iv: float) -> OptionsStrategy:
        """Build a long call strategy"""
        try:
            T = (expiration - datetime.now()).days / 365.0
            r = self.bs_calculator.risk_free_rate
            
            option_price = self.bs_calculator.calculate_option_price(
                underlying_price, strike, T, r, iv, OptionType.CALL
            )
            
            # Strategy characteristics
            max_loss = option_price
            max_profit = None  # Unlimited
            breakeven = strike + option_price
            
            return OptionsStrategy(
                strategy_type=StrategyType.LONG_CALL,
                underlying_symbol=underlying,
                contracts=[],  # Would be populated with actual contracts
                max_profit=max_profit,
                max_loss=max_loss,
                breakeven_points=[breakeven],
                probability_of_profit=self._calculate_pop_long_call(underlying_price, strike, T, iv),
                risk_reward_ratio=None,  # Unlimited upside
                margin_requirement=max_loss
            )
            
        except Exception as e:
            self.logger.error(f"Error building long call strategy: {e}")
            return None
    
    def build_iron_condor(self, underlying: str, short_call_strike: float, 
                         long_call_strike: float, short_put_strike: float,
                         long_put_strike: float, expiration: datetime,
                         underlying_price: float, iv: float) -> OptionsStrategy:
        """Build an iron condor strategy"""
        try:
            T = (expiration - datetime.now()).days / 365.0
            r = self.bs_calculator.risk_free_rate
            
            # Calculate option prices
            short_call_price = self.bs_calculator.calculate_option_price(
                underlying_price, short_call_strike, T, r, iv, OptionType.CALL
            )
            long_call_price = self.bs_calculator.calculate_option_price(
                underlying_price, long_call_strike, T, r, iv, OptionType.CALL
            )
            short_put_price = self.bs_calculator.calculate_option_price(
                underlying_price, short_put_strike, T, r, iv, OptionType.PUT
            )
            long_put_price = self.bs_calculator.calculate_option_price(
                underlying_price, long_put_strike, T, r, iv, OptionType.PUT
            )
            
            # Net credit received
            net_credit = (short_call_price + short_put_price) - (long_call_price + long_put_price)
            
            # Strategy characteristics
            max_profit = net_credit
            max_loss = (long_call_strike - short_call_strike) - net_credit
            
            # Breakeven points
            upper_breakeven = short_call_strike + net_credit
            lower_breakeven = short_put_strike - net_credit
            
            return OptionsStrategy(
                strategy_type=StrategyType.IRON_CONDOR,
                underlying_symbol=underlying,
                contracts=[],  # Would be populated with actual contracts
                max_profit=max_profit,
                max_loss=max_loss,
                breakeven_points=[lower_breakeven, upper_breakeven],
                probability_of_profit=self._calculate_pop_iron_condor(
                    underlying_price, lower_breakeven, upper_breakeven, T, iv
                ),
                risk_reward_ratio=max_profit / max_loss if max_loss > 0 else float('inf'),
                margin_requirement=max_loss
            )
            
        except Exception as e:
            self.logger.error(f"Error building iron condor strategy: {e}")
            return None
    
    def build_straddle(self, underlying: str, strike: float, expiration: datetime,
                      underlying_price: float, iv: float, is_long: bool = True) -> OptionsStrategy:
        """Build a straddle strategy (long or short)"""
        try:
            T = (expiration - datetime.now()).days / 365.0
            r = self.bs_calculator.risk_free_rate
            
            call_price = self.bs_calculator.calculate_option_price(
                underlying_price, strike, T, r, iv, OptionType.CALL
            )
            put_price = self.bs_calculator.calculate_option_price(
                underlying_price, strike, T, r, iv, OptionType.PUT
            )
            
            total_premium = call_price + put_price
            
            if is_long:
                # Long straddle
                max_loss = total_premium
                max_profit = None  # Unlimited
                upper_breakeven = strike + total_premium
                lower_breakeven = strike - total_premium
                margin_requirement = max_loss
            else:
                # Short straddle
                max_profit = total_premium
                max_loss = None  # Unlimited
                upper_breakeven = strike + total_premium
                lower_breakeven = strike - total_premium
                margin_requirement = None  # Would need to calculate margin requirements
            
            return OptionsStrategy(
                strategy_type=StrategyType.STRADDLE,
                underlying_symbol=underlying,
                contracts=[],  # Would be populated with actual contracts
                max_profit=max_profit,
                max_loss=max_loss,
                breakeven_points=[lower_breakeven, upper_breakeven],
                probability_of_profit=self._calculate_pop_straddle(
                    underlying_price, lower_breakeven, upper_breakeven, T, iv
                ),
                risk_reward_ratio=None,  # Depends on direction
                margin_requirement=margin_requirement
            )
            
        except Exception as e:
            self.logger.error(f"Error building straddle strategy: {e}")
            return None
    
    def _calculate_pop_long_call(self, S: float, K: float, T: float, sigma: float) -> float:
        """Calculate probability of profit for long call"""
        try:
            # Simplified calculation - probability that S > breakeven at expiration
            # This is a rough approximation
            return 0.5 - (K - S) / (S * sigma * math.sqrt(T))
        except:
            return 0.5
    
    def _calculate_pop_iron_condor(self, S: float, lower_be: float, upper_be: float, 
                                  T: float, sigma: float) -> float:
        """Calculate probability of profit for iron condor"""
        try:
            # Probability that price stays between breakeven points
            # Simplified calculation
            range_width = upper_be - lower_be
            expected_move = S * sigma * math.sqrt(T)
            return max(0.1, min(0.9, range_width / (2 * expected_move)))
        except:
            return 0.5
    
    def _calculate_pop_straddle(self, S: float, lower_be: float, upper_be: float, 
                               T: float, sigma: float) -> float:
        """Calculate probability of profit for straddle"""
        try:
            # Probability that price moves outside breakeven points
            expected_move = S * sigma * math.sqrt(T)
            breakeven_range = upper_be - lower_be
            return max(0.1, min(0.9, expected_move / (breakeven_range / 2)))
        except:
            return 0.5


class OptionsEngine:
    """Main options trading engine"""
    
    def __init__(self, market_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        
        # Components
        self.bs_calculator = BlackScholesCalculator()
        self.strategy_builder = OptionsStrategyBuilder(self.bs_calculator)
        
        # Configuration
        self.enabled = settings.OPTIONS_TRADING_ENABLED
        self.max_expiry_days = settings.OPTIONS_MAX_EXPIRY_DAYS
        self.min_volume = settings.OPTIONS_MIN_VOLUME
        self.max_spread_percent = settings.OPTIONS_MAX_SPREAD_PERCENT
        
        # Risk management
        self.max_position_size = 0.05  # 5% of portfolio per position
        self.max_total_options_exposure = 0.20  # 20% total options exposure
        
        self.logger.info(f"[TARGET] Options Engine initialized - enabled: {self.enabled}")
    
    @performance_optimizer.performance_monitor("options_analysis")
    async def analyze_options_opportunity(self, symbol: str, 
                                        strategy_type: StrategyType = StrategyType.LONG_CALL) -> Optional[Dict[str, Any]]:
        """Analyze options trading opportunity for a symbol"""
        try:
            if not self.enabled:
                return None
            
            # Get current market data
            quote = await self._get_underlying_quote(symbol)
            if not quote:
                return None
            
            # Get options chain
            options_chain = await self._get_options_chain(symbol)
            if not options_chain:
                return None
            
            # Find optimal strategy
            optimal_strategy = await self._find_optimal_strategy(
                symbol, quote.price, strategy_type, options_chain
            )
            
            if not optimal_strategy:
                return None
            
            # Risk assessment
            risk_assessment = self._assess_strategy_risk(optimal_strategy, quote.price)
            
            return {
                'symbol': symbol,
                'strategy': optimal_strategy,
                'risk_assessment': risk_assessment,
                'current_price': quote.price,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing options opportunity for {symbol}: {e}")
            return None
    
    async def _get_underlying_quote(self, symbol: str) -> Optional[Quote]:
        """Get current quote for underlying asset"""
        try:
            if self.market_engine:
                return await self.market_engine.get_quote(symbol)
            else:
                # Mock data for testing
                return Quote(
                    symbol=symbol,
                    price=100.0,
                    bid=99.95,
                    ask=100.05,
                    volume=1000000,
                    change=1.25,
                    change_percent=1.25,
                    timestamp=datetime.now()
                )
        except Exception as e:
            self.logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def _get_options_chain(self, symbol: str) -> Optional[List[OptionContract]]:
        """Get options chain for symbol with real data integration"""
        try:
            # Try to get real options data first
            real_chain = await self._get_real_options_chain(symbol)
            if real_chain:
                return real_chain

            # Fallback to enhanced mock data with realistic pricing
            self.logger.warning(f"Using enhanced mock options data for {symbol}")
            return self._generate_enhanced_mock_options_chain(symbol)

        except Exception as e:
            self.logger.error(f"Error getting options chain for {symbol}: {e}")
            return None

    async def _get_real_options_chain(self, symbol: str) -> Optional[List[OptionContract]]:
        """Get real options chain from data provider"""
        try:
            if not self.market_engine:
                return None

            # Try to get options data from FMP or other provider
            # This would be implemented with actual options data API
            options_data = await self._fetch_options_from_provider(symbol)

            if options_data:
                return self._parse_options_data(symbol, options_data)

            return None

        except Exception as e:
            self.logger.error(f"Error fetching real options data for {symbol}: {e}")
            return None

    async def _fetch_options_from_provider(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch options data from external provider"""
        try:
            # This would integrate with a real options data provider
            # For now, return None to trigger fallback
            return None

        except Exception as e:
            self.logger.error(f"Error fetching from options provider: {e}")
            return None

    def _parse_options_data(self, symbol: str, options_data: Dict[str, Any]) -> List[OptionContract]:
        """Parse options data from provider into OptionContract objects"""
        contracts = []

        try:
            # This would parse real options data format
            # Implementation depends on data provider format
            pass

        except Exception as e:
            self.logger.error(f"Error parsing options data: {e}")

        return contracts
    
    def _generate_mock_options_chain(self, symbol: str) -> List[OptionContract]:
        """Generate enhanced mock options chain with realistic pricing"""
        contracts = []

        # Get realistic base price
        base_price = 175.25  # Realistic price for major stocks like AAPL

        # Generate multiple expiration dates
        expirations = [
            datetime.now() + timedelta(days=7),   # Weekly
            datetime.now() + timedelta(days=30),  # Monthly
            datetime.now() + timedelta(days=60),  # Quarterly
        ]

        for exp_idx, expiration in enumerate(expirations):
            days_to_exp = (expiration - datetime.now()).days
            time_to_exp = max(0.01, days_to_exp / 365.0)

            # Generate strikes with realistic spacing
            strike_spacing = 5.0
            strikes = [base_price + (i - 5) * strike_spacing for i in range(11)]

            for strike in strikes:
                # Calculate realistic implied volatility
                moneyness = abs(strike - base_price) / base_price if base_price > 0 else 0
                base_iv = 0.20 + moneyness * 0.10  # IV smile effect

                # Calculate option prices using Black-Scholes
                call_price = self.bs_calculator.calculate_option_price(
                    base_price, strike, time_to_exp, 0.02, base_iv, OptionType.CALL
                )
                put_price = self.bs_calculator.calculate_option_price(
                    base_price, strike, time_to_exp, 0.02, base_iv, OptionType.PUT
                )

                # Calculate Greeks
                call_greeks = self.bs_calculator.calculate_greeks(
                    base_price, strike, time_to_exp, 0.02, base_iv, OptionType.CALL
                )
                put_greeks = self.bs_calculator.calculate_greeks(
                    base_price, strike, time_to_exp, 0.02, base_iv, OptionType.PUT
                )

                # Realistic volume based on moneyness and time to expiration
                volume_factor = max(0.1, 1.0 - moneyness * 2) * (1.0 - exp_idx * 0.3)
                base_volume = int(500 * volume_factor)
                base_oi = int(2000 * volume_factor)

                # Call option
                call_contract = OptionContract(
                    symbol=f"{symbol}_{expiration.strftime('%y%m%d')}C{int(strike):03d}",
                    underlying=symbol,
                    option_type=OptionType.CALL,
                    strike=strike,
                    expiration=expiration,
                    bid=max(0.01, call_price - 0.05),
                    ask=max(0.05, call_price + 0.05),
                    last=call_price,
                    volume=max(10, base_volume),
                    open_interest=max(100, base_oi),
                    implied_volatility=base_iv,
                    delta=call_greeks["delta"],
                    gamma=call_greeks["gamma"],
                    theta=call_greeks["theta"],
                    vega=call_greeks["vega"],
                    rho=call_greeks["rho"]
                )
                contracts.append(call_contract)

                # Put option
                put_contract = OptionContract(
                    symbol=f"{symbol}_{expiration.strftime('%y%m%d')}P{int(strike):03d}",
                    underlying=symbol,
                    option_type=OptionType.PUT,
                    strike=strike,
                    expiration=expiration,
                    bid=max(0.01, put_price - 0.05),
                    ask=max(0.05, put_price + 0.05),
                    last=put_price,
                    volume=max(10, int(base_volume * 0.8)),
                    open_interest=max(100, int(base_oi * 0.9)),
                    implied_volatility=base_iv,
                    delta=put_greeks["delta"],
                    gamma=put_greeks["gamma"],
                    theta=put_greeks["theta"],
                    vega=put_greeks["vega"],
                    rho=put_greeks["rho"]
                )
                contracts.append(put_contract)

        return contracts
    
    async def _find_optimal_strategy(self, symbol: str, current_price: float,
                                   strategy_type: StrategyType, 
                                   options_chain: List[OptionContract]) -> Optional[OptionsStrategy]:
        """Find optimal strategy based on current market conditions"""
        try:
            # Filter options by criteria
            filtered_options = self._filter_options(options_chain)
            
            if not filtered_options:
                return None
            
            # Build strategy based on type
            if strategy_type == StrategyType.LONG_CALL:
                # Find ATM or slightly OTM call
                target_strike = current_price * 1.02  # 2% OTM
                best_call = min(filtered_options, 
                              key=lambda x: abs(x.strike - target_strike) 
                              if x.option_type == OptionType.CALL else float('inf'))
                
                if best_call.option_type == OptionType.CALL:
                    return self.strategy_builder.build_long_call(
                        symbol, best_call.strike, best_call.expiration,
                        current_price, best_call.implied_volatility
                    )
            
            elif strategy_type == StrategyType.IRON_CONDOR:
                # Find strikes for iron condor
                calls = [opt for opt in filtered_options if opt.option_type == OptionType.CALL]
                puts = [opt for opt in filtered_options if opt.option_type == OptionType.PUT]
                
                if len(calls) >= 2 and len(puts) >= 2:
                    # Simple iron condor selection
                    short_call = min(calls, key=lambda x: abs(x.strike - current_price * 1.05))
                    long_call = min(calls, key=lambda x: abs(x.strike - current_price * 1.10))
                    short_put = min(puts, key=lambda x: abs(x.strike - current_price * 0.95))
                    long_put = min(puts, key=lambda x: abs(x.strike - current_price * 0.90))
                    
                    return self.strategy_builder.build_iron_condor(
                        symbol, short_call.strike, long_call.strike,
                        short_put.strike, long_put.strike, short_call.expiration,
                        current_price, short_call.implied_volatility
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding optimal strategy: {e}")
            return None
    
    def _filter_options(self, options_chain: List[OptionContract]) -> List[OptionContract]:
        """Filter options based on volume, spread, and expiry criteria"""
        filtered = []
        
        for option in options_chain:
            # Check volume
            if option.volume < self.min_volume:
                continue
            
            # Check bid-ask spread
            if option.ask > 0:
                spread_percent = (option.ask - option.bid) / option.ask * 100
                if spread_percent > self.max_spread_percent:
                    continue
            
            # Check expiry
            days_to_expiry = (option.expiration - datetime.now()).days
            if days_to_expiry > self.max_expiry_days:
                continue
            
            filtered.append(option)
        
        return filtered
    
    def _assess_strategy_risk(self, strategy: OptionsStrategy, current_price: float) -> Dict[str, Any]:
        """Assess risk metrics for the strategy"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # Max loss risk
            if strategy.max_loss and current_price > 0:
                loss_percent = strategy.max_loss / current_price
                if loss_percent > 0.10:  # 10% max loss
                    risk_score += 0.3
                    risk_factors.append("High maximum loss")
            
            # Probability of profit
            if strategy.probability_of_profit < 0.4:  # Less than 40% PoP
                risk_score += 0.2
                risk_factors.append("Low probability of profit")
            
            # Risk-reward ratio
            if strategy.risk_reward_ratio and strategy.risk_reward_ratio < 1.0:
                risk_score += 0.2
                risk_factors.append("Poor risk-reward ratio")
            
            # Time decay risk (for long options)
            if strategy.strategy_type in [StrategyType.LONG_CALL, StrategyType.LONG_PUT, StrategyType.STRADDLE]:
                risk_score += 0.1
                risk_factors.append("Time decay risk")
            
            # Overall risk level
            if risk_score <= 0.3:
                risk_level = "LOW"
            elif risk_score <= 0.6:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'max_loss': strategy.max_loss,
                'max_profit': strategy.max_profit,
                'probability_of_profit': strategy.probability_of_profit,
                'risk_reward_ratio': strategy.risk_reward_ratio
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing strategy risk: {e}")
            return {'risk_level': 'HIGH', 'risk_score': 1.0}


# Global options engine instance
options_engine = OptionsEngine()
