#!/usr/bin/env python3
"""
A.T.L.A.S. Value at Risk (VaR) Calculator

Implements comprehensive VaR calculation methods:
- Historical VaR
- Parametric VaR (Variance-Covariance)
- Monte Carlo VaR
- Conditional VaR (Expected Shortfall)
- Stress Testing
- Confidence Intervals
"""

import logging
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class VaRResult:
    """Value at Risk calculation result"""
    var_1_day: float
    var_5_day: float
    var_10_day: float
    conditional_var: float
    confidence_level: float
    method: str
    portfolio_value: float
    timestamp: datetime
    stress_test_results: Optional[Dict[str, float]] = None
    monte_carlo_details: Optional[Dict[str, Any]] = None

class VaRCalculator:
    """
    Comprehensive Value at Risk Calculator
    
    Implements multiple VaR methodologies for portfolio risk assessment
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default parameters
        self.confidence_levels = [0.95, 0.99, 0.999]  # 95%, 99%, 99.9%
        self.time_horizons = [1, 5, 10]  # Days
        self.monte_carlo_simulations = 10000
        self.historical_window = 252  # 1 year of trading days
        
    def calculate_portfolio_var(self, portfolio_returns: pd.Series, 
                               portfolio_value: float,
                               confidence_level: float = 0.95,
                               method: str = "historical") -> VaRResult:
        """
        Calculate Value at Risk for a portfolio
        
        Args:
            portfolio_returns: Historical portfolio returns (daily)
            portfolio_value: Current portfolio value
            confidence_level: Confidence level (0.95, 0.99, etc.)
            method: "historical", "parametric", "monte_carlo"
            
        Returns:
            VaRResult with comprehensive risk metrics
        """
        try:
            if portfolio_returns.empty:
                raise ValueError("Empty portfolio returns data")
            
            if method == "historical":
                var_results = self._calculate_historical_var(
                    portfolio_returns, portfolio_value, confidence_level
                )
            elif method == "parametric":
                var_results = self._calculate_parametric_var(
                    portfolio_returns, portfolio_value, confidence_level
                )
            elif method == "monte_carlo":
                var_results = self._calculate_monte_carlo_var(
                    portfolio_returns, portfolio_value, confidence_level
                )
            else:
                # Default to historical method
                var_results = self._calculate_historical_var(
                    portfolio_returns, portfolio_value, confidence_level
                )
            
            # Add stress testing
            stress_results = self._perform_stress_testing(
                portfolio_returns, portfolio_value, confidence_level
            )
            var_results.stress_test_results = stress_results
            
            self.logger.info(f"VaR calculated using {method} method: "
                           f"1-day VaR: ${var_results.var_1_day:,.2f}")
            
            return var_results
            
        except Exception as e:
            self.logger.error(f"VaR calculation error: {e}")
            return self._create_fallback_var_result(portfolio_value, confidence_level, method, str(e))
    
    def _calculate_historical_var(self, returns: pd.Series, portfolio_value: float,
                                 confidence_level: float) -> VaRResult:
        """Calculate Historical VaR using empirical distribution"""
        try:
            # Remove NaN values
            clean_returns = returns.dropna()
            
            if len(clean_returns) < 30:
                raise ValueError("Insufficient historical data (need at least 30 observations)")
            
            # Calculate percentiles for VaR
            alpha = 1 - confidence_level
            var_percentile = np.percentile(clean_returns, alpha * 100)
            
            # Convert to dollar amounts
            var_1_day = abs(var_percentile * portfolio_value)
            var_5_day = var_1_day * math.sqrt(5)  # Scale by square root of time
            var_10_day = var_1_day * math.sqrt(10)
            
            # Calculate Conditional VaR (Expected Shortfall)
            tail_returns = clean_returns[clean_returns <= var_percentile]
            if len(tail_returns) > 0:
                conditional_var = abs(tail_returns.mean() * portfolio_value)
            else:
                conditional_var = var_1_day * 1.3  # Estimate as 130% of VaR
            
            return VaRResult(
                var_1_day=var_1_day,
                var_5_day=var_5_day,
                var_10_day=var_10_day,
                conditional_var=conditional_var,
                confidence_level=confidence_level,
                method="historical",
                portfolio_value=portfolio_value,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Historical VaR calculation error: {e}")
            raise
    
    def _calculate_parametric_var(self, returns: pd.Series, portfolio_value: float,
                                 confidence_level: float) -> VaRResult:
        """Calculate Parametric VaR assuming normal distribution"""
        try:
            # Remove NaN values
            clean_returns = returns.dropna()
            
            if len(clean_returns) < 30:
                raise ValueError("Insufficient data for parametric VaR")
            
            # Calculate mean and standard deviation
            mean_return = clean_returns.mean()
            std_return = clean_returns.std()
            
            # Calculate z-score for confidence level
            z_score = stats.norm.ppf(1 - confidence_level)
            
            # Calculate VaR (assuming normal distribution)
            var_return = mean_return + z_score * std_return
            var_1_day = abs(var_return * portfolio_value)
            var_5_day = var_1_day * math.sqrt(5)
            var_10_day = var_1_day * math.sqrt(10)
            
            # Calculate Conditional VaR for normal distribution
            # CVaR = μ + σ * φ(Φ^(-1)(α)) / α
            phi_value = stats.norm.pdf(z_score)
            conditional_var_return = mean_return + std_return * phi_value / (1 - confidence_level)
            conditional_var = abs(conditional_var_return * portfolio_value)
            
            return VaRResult(
                var_1_day=var_1_day,
                var_5_day=var_5_day,
                var_10_day=var_10_day,
                conditional_var=conditional_var,
                confidence_level=confidence_level,
                method="parametric",
                portfolio_value=portfolio_value,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Parametric VaR calculation error: {e}")
            raise
    
    def _calculate_monte_carlo_var(self, returns: pd.Series, portfolio_value: float,
                                  confidence_level: float) -> VaRResult:
        """Calculate Monte Carlo VaR using simulation"""
        try:
            # Remove NaN values
            clean_returns = returns.dropna()
            
            if len(clean_returns) < 30:
                raise ValueError("Insufficient data for Monte Carlo VaR")
            
            # Estimate parameters from historical data
            mean_return = clean_returns.mean()
            std_return = clean_returns.std()
            
            # Generate random scenarios
            np.random.seed(42)  # For reproducibility
            simulated_returns = np.random.normal(
                mean_return, std_return, self.monte_carlo_simulations
            )
            
            # Calculate VaR from simulated distribution
            alpha = 1 - confidence_level
            var_percentile = np.percentile(simulated_returns, alpha * 100)
            
            var_1_day = abs(var_percentile * portfolio_value)
            var_5_day = var_1_day * math.sqrt(5)
            var_10_day = var_1_day * math.sqrt(10)
            
            # Calculate Conditional VaR
            tail_returns = simulated_returns[simulated_returns <= var_percentile]
            conditional_var = abs(tail_returns.mean() * portfolio_value)
            
            # Monte Carlo details
            mc_details = {
                "simulations": self.monte_carlo_simulations,
                "mean_simulated_return": float(simulated_returns.mean()),
                "std_simulated_return": float(simulated_returns.std()),
                "min_simulated_return": float(simulated_returns.min()),
                "max_simulated_return": float(simulated_returns.max()),
                "percentiles": {
                    "1%": float(np.percentile(simulated_returns, 1)),
                    "5%": float(np.percentile(simulated_returns, 5)),
                    "10%": float(np.percentile(simulated_returns, 10))
                }
            }
            
            result = VaRResult(
                var_1_day=var_1_day,
                var_5_day=var_5_day,
                var_10_day=var_10_day,
                conditional_var=conditional_var,
                confidence_level=confidence_level,
                method="monte_carlo",
                portfolio_value=portfolio_value,
                timestamp=datetime.now()
            )
            result.monte_carlo_details = mc_details
            
            return result
            
        except Exception as e:
            self.logger.error(f"Monte Carlo VaR calculation error: {e}")
            raise
    
    def _perform_stress_testing(self, returns: pd.Series, portfolio_value: float,
                               confidence_level: float) -> Dict[str, float]:
        """Perform stress testing scenarios"""
        try:
            clean_returns = returns.dropna()
            
            if len(clean_returns) < 30:
                return {}
            
            mean_return = clean_returns.mean()
            std_return = clean_returns.std()
            
            # Define stress scenarios
            stress_scenarios = {
                "market_crash_2008": -0.20,  # -20% single day loss
                "black_monday_1987": -0.22,  # -22% single day loss
                "covid_crash_2020": -0.12,   # -12% single day loss
                "two_sigma_event": mean_return - 2 * std_return,
                "three_sigma_event": mean_return - 3 * std_return,
                "worst_historical": clean_returns.min()
            }
            
            stress_results = {}
            for scenario_name, scenario_return in stress_scenarios.items():
                stress_loss = abs(scenario_return * portfolio_value)
                stress_results[scenario_name] = stress_loss
            
            return stress_results
            
        except Exception as e:
            self.logger.error(f"Stress testing error: {e}")
            return {}
    
    def calculate_component_var(self, portfolio_weights: Dict[str, float],
                               asset_returns: pd.DataFrame,
                               portfolio_value: float,
                               confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculate component VaR for individual assets in portfolio"""
        try:
            if asset_returns.empty:
                raise ValueError("Empty asset returns data")
            
            # Calculate portfolio returns
            portfolio_returns = pd.Series(index=asset_returns.index, dtype=float)
            
            for date in asset_returns.index:
                daily_return = 0
                for asset, weight in portfolio_weights.items():
                    if asset in asset_returns.columns:
                        daily_return += weight * asset_returns.loc[date, asset]
                portfolio_returns[date] = daily_return
            
            # Calculate portfolio VaR
            portfolio_var = self.calculate_portfolio_var(
                portfolio_returns, portfolio_value, confidence_level, "historical"
            )
            
            # Calculate component VaR for each asset
            component_vars = {}
            for asset, weight in portfolio_weights.items():
                if asset in asset_returns.columns:
                    # Calculate marginal VaR contribution
                    asset_value = weight * portfolio_value
                    
                    # Simplified component VaR calculation
                    asset_returns_series = asset_returns[asset].dropna()
                    if len(asset_returns_series) > 30:
                        alpha = 1 - confidence_level
                        asset_var_percentile = np.percentile(asset_returns_series, alpha * 100)
                        component_var = abs(asset_var_percentile * asset_value)
                    else:
                        component_var = asset_value * 0.05  # 5% default
                    
                    component_vars[asset] = {
                        "component_var": component_var,
                        "weight": weight,
                        "asset_value": asset_value,
                        "contribution_percent": (component_var / portfolio_var.var_1_day * 100) if portfolio_var.var_1_day > 0 else 0
                    }
            
            return {
                "portfolio_var": portfolio_var,
                "component_vars": component_vars,
                "total_component_var": sum(cv["component_var"] for cv in component_vars.values())
            }
            
        except Exception as e:
            self.logger.error(f"Component VaR calculation error: {e}")
            return {
                "portfolio_var": self._create_fallback_var_result(portfolio_value, confidence_level, "component", str(e)),
                "component_vars": {},
                "total_component_var": 0
            }
    
    def _create_fallback_var_result(self, portfolio_value: float, confidence_level: float,
                                   method: str, error_msg: str) -> VaRResult:
        """Create fallback VaR result when calculation fails"""
        # Conservative estimates based on portfolio value
        fallback_var_1_day = portfolio_value * 0.02  # 2% of portfolio
        
        return VaRResult(
            var_1_day=fallback_var_1_day,
            var_5_day=fallback_var_1_day * math.sqrt(5),
            var_10_day=fallback_var_1_day * math.sqrt(10),
            conditional_var=fallback_var_1_day * 1.3,
            confidence_level=confidence_level,
            method=f"{method}_fallback",
            portfolio_value=portfolio_value,
            timestamp=datetime.now(),
            stress_test_results={"calculation_error": error_msg}
        )


# Global VaR calculator instance
var_calculator = VaRCalculator()
