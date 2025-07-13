#!/usr/bin/env python3
"""
A.T.L.A.S. Advanced Features
Consolidated options engine, portfolio optimizer, and advanced strategies
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from scipy.optimize import minimize

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus, PortfolioPosition, RiskMetrics

settings = Settings()

class AtlasOptionsEngine:
    """Options trading and Black-Scholes pricing engine"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize options engine"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Options Engine initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Options Engine initialization failed: {e}")
            raise
    
    def black_scholes_call(self, S, K, T, r, sigma):
        """Calculate Black-Scholes call option price"""
        from scipy.stats import norm
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return call_price
    
    def calculate_greeks(self, S, K, T, r, sigma):
        """Calculate option Greeks"""
        from scipy.stats import norm
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
        vega = S * norm.pdf(d1) * np.sqrt(T)
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        
        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho
        }
    
    async def cleanup(self):
        """Cleanup options engine"""
        self.logger.info("Options engine cleanup completed")


class AtlasPortfolioOptimizer:
    """Portfolio optimization using Markowitz theory"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize portfolio optimizer"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Portfolio Optimizer initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Portfolio Optimizer initialization failed: {e}")
            raise
    
    def optimize_portfolio(self, returns, target_return=None):
        """Optimize portfolio using mean-variance optimization"""
        n_assets = len(returns.columns)
        
        mu = returns.mean()
        cov = returns.cov()
        
        def objective(weights):
            return np.dot(weights.T, np.dot(cov, weights))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        ]
        
        if target_return:
            constraints.append({
                'type': 'eq', 
                'fun': lambda x: np.dot(x, mu) - target_return
            })
        
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        x0 = np.array([1/n_assets] * n_assets)
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            portfolio_return = np.dot(optimal_weights, mu)
            portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov, optimal_weights)))
            
            return {
                "weights": optimal_weights.tolist(),
                "expected_return": portfolio_return,
                "risk": portfolio_risk,
                "sharpe_ratio": portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
            }
        else:
            return None
    
    async def cleanup(self):
        """Cleanup portfolio optimizer"""
        self.logger.info("Portfolio optimizer cleanup completed")


class AtlasAdvancedStrategies:
    """Advanced trading strategies"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize advanced strategies"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Advanced Strategies initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Advanced Strategies initialization failed: {e}")
            raise
    
    def momentum_strategy(self, prices, lookback=20):
        """Momentum trading strategy"""
        returns = prices.pct_change()
        momentum = returns.rolling(window=lookback).mean()
        
        signals = np.where(momentum > 0, 1, -1)
        return signals
    
    def mean_reversion_strategy(self, prices, lookback=20, threshold=2):
        """Mean reversion trading strategy"""
        rolling_mean = prices.rolling(window=lookback).mean()
        rolling_std = prices.rolling(window=lookback).std()
        
        z_score = (prices - rolling_mean) / rolling_std
        
        signals = np.where(z_score > threshold, -1, 
                          np.where(z_score < -threshold, 1, 0))
        return signals
    
    def pairs_trading_strategy(self, price1, price2, lookback=20, threshold=2):
        """Pairs trading strategy"""
        spread = price1 - price2
        rolling_mean = spread.rolling(window=lookback).mean()
        rolling_std = spread.rolling(window=lookback).std()
        
        z_score = (spread - rolling_mean) / rolling_std
        
        signals = np.where(z_score > threshold, -1,
                          np.where(z_score < -threshold, 1, 0))
        return signals
    
    async def cleanup(self):
        """Cleanup advanced strategies"""
        self.logger.info("Advanced strategies cleanup completed")
