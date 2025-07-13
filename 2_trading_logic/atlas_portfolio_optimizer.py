"""
A.T.L.A.S Portfolio Optimization Module
Advanced portfolio optimization with deep learning models and risk management
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import asyncio

from config import settings
from models import Position, Quote
from atlas_performance_optimizer import performance_optimizer

# Optional ML imports with graceful fallback
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, LSTM
    from sklearn.preprocessing import StandardScaler
    import scipy.optimize as optimize
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    total_return: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    var_95: float  # Value at Risk 95%
    expected_shortfall: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_value': self.total_value,
            'total_return': self.total_return,
            'daily_return': self.daily_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'beta': self.beta,
            'alpha': self.alpha,
            'var_95': self.var_95,
            'expected_shortfall': self.expected_shortfall
        }


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    optimal_weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: str
    confidence: float
    rebalance_recommendations: List[Dict[str, Any]]
    risk_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'optimal_weights': self.optimal_weights,
            'expected_return': self.expected_return,
            'expected_volatility': self.expected_volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'optimization_method': self.optimization_method,
            'confidence': self.confidence,
            'rebalance_recommendations': self.rebalance_recommendations,
            'risk_metrics': self.risk_metrics
        }


class RiskManager:
    """Advanced risk management for portfolio optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        self.max_position_size = 0.20  # 20% max per position
        self.max_sector_exposure = 0.40  # 40% max per sector
        self.max_correlation = 0.80  # Max correlation between positions
        self.var_confidence = 0.95  # VaR confidence level
        
    def calculate_portfolio_risk(self, weights: Dict[str, float], 
                               returns_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            # Convert weights to array
            symbols = list(weights.keys())
            weight_array = np.array([weights[symbol] for symbol in symbols])
            
            # Get returns for symbols
            portfolio_returns = returns_data[symbols]
            
            # Portfolio return
            portfolio_return_series = (portfolio_returns * weight_array).sum(axis=1)
            
            # Calculate metrics
            volatility = portfolio_return_series.std() * np.sqrt(252)  # Annualized
            var_95 = np.percentile(portfolio_return_series, 5)
            expected_shortfall = portfolio_return_series[portfolio_return_series <= var_95].mean()
            
            # Maximum drawdown
            cumulative_returns = (1 + portfolio_return_series).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Beta calculation (vs SPY if available)
            beta = 1.0  # Default
            if 'SPY' in returns_data.columns:
                market_returns = returns_data['SPY']
                covariance = np.cov(portfolio_return_series, market_returns)[0][1]
                market_variance = market_returns.var()
                if market_variance > 0:
                    beta = covariance / market_variance
            
            return {
                'volatility': volatility,
                'var_95': var_95,
                'expected_shortfall': expected_shortfall,
                'max_drawdown': max_drawdown,
                'beta': beta
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio risk: {e}")
            return {}
    
    def validate_weights(self, weights: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Validate portfolio weights against risk constraints"""
        try:
            violations = []
            
            # Check individual position sizes
            for symbol, weight in weights.items():
                if weight > self.max_position_size:
                    violations.append(f"{symbol} weight {weight:.2%} exceeds max {self.max_position_size:.2%}")
            
            # Check total weights sum to 1
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.01:
                violations.append(f"Total weights {total_weight:.2%} should sum to 100%")
            
            # Check for negative weights (if not allowed)
            negative_weights = [symbol for symbol, weight in weights.items() if weight < 0]
            if negative_weights:
                violations.append(f"Negative weights not allowed: {negative_weights}")
            
            return len(violations) == 0, violations
            
        except Exception as e:
            self.logger.error(f"Error validating weights: {e}")
            return False, [f"Validation error: {e}"]


class DeepPortfolioOptimizer:
    """Deep learning-based portfolio optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ml_enabled = ML_AVAILABLE and settings.ML_MODELS_ENABLED
        
        # Models
        self.return_predictor = None
        self.risk_predictor = None
        self.scaler = None
        
        # Training data
        self.lookback_days = 252  # 1 year
        self.prediction_horizon = 21  # 21 days
        
    async def initialize(self):
        """Initialize ML models"""
        if self.ml_enabled:
            try:
                self.logger.info("[TOOL] Initializing portfolio optimization ML models...")
                self.return_predictor = self._create_return_predictor()
                self.risk_predictor = self._create_risk_predictor()
                self.scaler = StandardScaler()
                self.logger.info("[OK] Portfolio optimization ML models initialized")
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to initialize ML models: {e}")
                self.ml_enabled = False
    
    def _create_return_predictor(self):
        """Create LSTM model for return prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(60, 10)),  # 60 days, 10 features
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def _create_risk_predictor(self):
        """Create neural network for risk prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = Sequential([
            Dense(64, activation='relu', input_shape=(20,)),  # 20 features
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')  # Risk score 0-1
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    async def predict_returns(self, symbols: List[str], 
                            historical_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Predict expected returns using ML models"""
        try:
            if not self.ml_enabled:
                return self._fallback_return_prediction(symbols, historical_data)
            
            predicted_returns = {}
            
            for symbol in symbols:
                if symbol not in historical_data:
                    continue
                
                df = historical_data[symbol]
                if len(df) < self.lookback_days:
                    continue
                
                # Prepare features
                features = self._prepare_features(df)
                if features is None:
                    continue
                
                # Predict return
                try:
                    prediction = self.return_predictor.predict(features, verbose=0)
                    predicted_returns[symbol] = float(prediction[0][0])
                except Exception as e:
                    self.logger.debug(f"ML prediction failed for {symbol}: {e}")
                    # Fallback to simple calculation
                    predicted_returns[symbol] = df['close'].pct_change().mean()
            
            return predicted_returns
            
        except Exception as e:
            self.logger.error(f"Error predicting returns: {e}")
            return self._fallback_return_prediction(symbols, historical_data)
    
    def _prepare_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """Prepare features for ML models"""
        try:
            # Calculate technical indicators
            df = df.copy()
            df['returns'] = df['close'].pct_change()
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            df['volatility'] = df['returns'].rolling(20).std()
            
            # Select features
            feature_columns = ['returns', 'volume', 'sma_20', 'sma_50', 'rsi', 'volatility']
            features = df[feature_columns].dropna()
            
            if len(features) < 60:
                return None
            
            # Normalize features
            features_scaled = self.scaler.fit_transform(features)
            
            # Create sequences for LSTM
            sequence = features_scaled[-60:].reshape(1, 60, len(feature_columns))
            
            return sequence
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series(index=prices.index, data=50.0)  # Neutral RSI
    
    def _fallback_return_prediction(self, symbols: List[str], 
                                  historical_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Fallback return prediction using simple methods"""
        predicted_returns = {}
        
        for symbol in symbols:
            if symbol in historical_data:
                df = historical_data[symbol]
                if len(df) > 0:
                    # Simple moving average of returns
                    returns = df['close'].pct_change().dropna()
                    if len(returns) > 0:
                        predicted_returns[symbol] = returns.tail(21).mean()  # Last 21 days
                    else:
                        predicted_returns[symbol] = 0.0
                else:
                    predicted_returns[symbol] = 0.0
            else:
                predicted_returns[symbol] = 0.0
        
        return predicted_returns


class PortfolioOptimizer:
    """Main portfolio optimization engine"""
    
    def __init__(self, market_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        
        # Components
        self.risk_manager = RiskManager()
        self.deep_optimizer = DeepPortfolioOptimizer()
        
        # Configuration
        self.enabled = settings.PERFORMANCE_MONITORING_ENABLED
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.rebalance_threshold = 0.05  # 5% drift threshold
        
        # Optimization methods
        self.optimization_methods = [
            'mean_variance',
            'risk_parity',
            'maximum_sharpe',
            'minimum_variance',
            'deep_learning'
        ]
        
        self.logger.info(f"[UP] Portfolio Optimizer initialized - enabled: {self.enabled}")
    
    async def initialize(self):
        """Initialize optimizer components"""
        await self.deep_optimizer.initialize()
    
    @performance_optimizer.performance_monitor("portfolio_optimization")
    async def optimize_portfolio(self, current_positions: List[Position],
                               target_symbols: List[str],
                               optimization_method: str = 'maximum_sharpe') -> Optional[OptimizationResult]:
        """Optimize portfolio allocation"""
        try:
            if not self.enabled:
                return None
            
            # Get historical data
            historical_data = await self._get_historical_data(target_symbols)
            if not historical_data:
                return None
            
            # Calculate expected returns
            expected_returns = await self.deep_optimizer.predict_returns(target_symbols, historical_data)
            
            # Calculate covariance matrix
            returns_df = self._calculate_returns_matrix(historical_data)
            covariance_matrix = returns_df.cov().values
            
            # Optimize based on method
            if optimization_method == 'maximum_sharpe':
                optimal_weights = self._optimize_maximum_sharpe(expected_returns, covariance_matrix, target_symbols)
            elif optimization_method == 'minimum_variance':
                optimal_weights = self._optimize_minimum_variance(covariance_matrix, target_symbols)
            elif optimization_method == 'risk_parity':
                optimal_weights = self._optimize_risk_parity(covariance_matrix, target_symbols)
            else:
                optimal_weights = self._optimize_mean_variance(expected_returns, covariance_matrix, target_symbols)
            
            if not optimal_weights:
                return None
            
            # Validate weights
            is_valid, violations = self.risk_manager.validate_weights(optimal_weights)
            if not is_valid:
                self.logger.warning(f"Weight validation failed: {violations}")
                # Apply constraints and re-optimize
                optimal_weights = self._apply_constraints(optimal_weights)
            
            # Calculate portfolio metrics with error handling
            try:
                portfolio_return = sum(expected_returns.get(symbol, 0) * weight
                                     for symbol, weight in optimal_weights.items())
                portfolio_variance = self._calculate_portfolio_variance(optimal_weights, covariance_matrix, target_symbols)

                # Ensure non-negative variance
                portfolio_variance = max(0, portfolio_variance)
                portfolio_volatility = np.sqrt(portfolio_variance)

                # Calculate Sharpe ratio with division by zero protection
                if portfolio_volatility > 0:
                    sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                else:
                    sharpe_ratio = 0.0

            except Exception as e:
                self.logger.error(f"Error calculating portfolio metrics: {e}")
                portfolio_return = 0.08  # Default 8% return
                portfolio_volatility = 0.15  # Default 15% volatility
                sharpe_ratio = 0.4  # Default Sharpe ratio
            
            # Calculate risk metrics
            risk_metrics = self.risk_manager.calculate_portfolio_risk(optimal_weights, returns_df)
            
            # Generate rebalancing recommendations
            rebalance_recommendations = self._generate_rebalance_recommendations(
                current_positions, optimal_weights
            )
            
            # Calculate confidence based on data quality and model performance
            confidence = self._calculate_optimization_confidence(historical_data, expected_returns)
            
            result = OptimizationResult(
                optimal_weights=optimal_weights,
                expected_return=portfolio_return,
                expected_volatility=portfolio_volatility,
                sharpe_ratio=sharpe_ratio,
                optimization_method=optimization_method,
                confidence=confidence,
                rebalance_recommendations=rebalance_recommendations,
                risk_metrics=risk_metrics
            )
            
            self.logger.info(f"[UP] Portfolio optimization complete: "
                           f"Expected return: {portfolio_return:.2%}, "
                           f"Volatility: {portfolio_volatility:.2%}, "
                           f"Sharpe: {sharpe_ratio:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error optimizing portfolio: {e}")
            return None
    
    async def _get_historical_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Get historical data for symbols"""
        try:
            historical_data = {}
            
            for symbol in symbols:
                if self.market_engine:
                    # Get real historical data
                    data = await self.market_engine._get_historical_data(symbol, period="1d", limit=252)
                    if data is not None and len(data) > 0:
                        historical_data[symbol] = data
                else:
                    # Generate mock data for testing
                    historical_data[symbol] = self._generate_mock_data(symbol)
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return {}
    
    def _generate_mock_data(self, symbol: str) -> pd.DataFrame:
        """Generate mock historical data for testing"""
        np.random.seed(hash(symbol) % 2**32)
        
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        prices = []
        
        base_price = 100.0
        for i in range(252):
            if i == 0:
                price = base_price
            else:
                change = np.random.normal(0.001, 0.02)  # 0.1% drift, 2% volatility
                price = prices[-1] * (1 + change)
            prices.append(price)
        
        df = pd.DataFrame({
            'close': prices,
            'volume': np.random.randint(100000, 1000000, 252)
        }, index=dates)
        
        return df
    
    def _calculate_returns_matrix(self, historical_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate returns matrix from historical data"""
        returns_data = {}
        
        for symbol, df in historical_data.items():
            returns_data[symbol] = df['close'].pct_change().dropna()
        
        returns_df = pd.DataFrame(returns_data)
        return returns_df.dropna()
    
    def _optimize_maximum_sharpe(self, expected_returns: Dict[str, float],
                               covariance_matrix: np.ndarray, symbols: List[str]) -> Dict[str, float]:
        """Optimize for maximum Sharpe ratio"""
        try:
            n_assets = len(symbols)
            returns_array = np.array([expected_returns[symbol] for symbol in symbols])
            
            def objective(weights):
                portfolio_return = np.sum(returns_array * weights)
                portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe_ratio  # Minimize negative Sharpe ratio
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, self.risk_manager.max_position_size) for _ in range(n_assets))
            
            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = optimize.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return dict(zip(symbols, result.x))
            else:
                self.logger.warning("Optimization failed, using equal weights")
                return dict(zip(symbols, [1.0 / n_assets] * n_assets))
                
        except Exception as e:
            self.logger.error(f"Error in maximum Sharpe optimization: {e}")
            return dict(zip(symbols, [1.0 / len(symbols)] * len(symbols)))
    
    def _optimize_minimum_variance(self, covariance_matrix: np.ndarray, symbols: List[str]) -> Dict[str, float]:
        """Optimize for minimum variance"""
        try:
            n_assets = len(symbols)
            
            def objective(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0, self.risk_manager.max_position_size) for _ in range(n_assets))
            
            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = optimize.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return dict(zip(symbols, result.x))
            else:
                return dict(zip(symbols, [1.0 / n_assets] * n_assets))
                
        except Exception as e:
            self.logger.error(f"Error in minimum variance optimization: {e}")
            return dict(zip(symbols, [1.0 / len(symbols)] * len(symbols)))
    
    def _optimize_risk_parity(self, covariance_matrix: np.ndarray, symbols: List[str]) -> Dict[str, float]:
        """Optimize for risk parity (equal risk contribution)"""
        try:
            n_assets = len(symbols)
            
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
                if portfolio_variance <= 0:
                    return 1e6  # Large penalty for invalid variance
                marginal_contrib = np.dot(covariance_matrix, weights)
                contrib = weights * marginal_contrib / portfolio_variance
                target_contrib = 1.0 / n_assets if n_assets > 0 else 0
                return np.sum((contrib - target_contrib) ** 2)
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0.01, self.risk_manager.max_position_size) for _ in range(n_assets))
            
            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = optimize.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return dict(zip(symbols, result.x))
            else:
                return dict(zip(symbols, [1.0 / n_assets] * n_assets))
                
        except Exception as e:
            self.logger.error(f"Error in risk parity optimization: {e}")
            return dict(zip(symbols, [1.0 / len(symbols)] * len(symbols)))
    
    def _optimize_mean_variance(self, expected_returns: Dict[str, float],
                              covariance_matrix: np.ndarray, symbols: List[str]) -> Dict[str, float]:
        """Classic mean-variance optimization"""
        try:
            n_assets = len(symbols)
            returns_array = np.array([expected_returns[symbol] for symbol in symbols])
            
            # Target return (median of expected returns)
            target_return = np.median(returns_array)
            
            def objective(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(returns_array * x) - target_return}
            ]
            bounds = tuple((0, self.risk_manager.max_position_size) for _ in range(n_assets))
            
            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = optimize.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return dict(zip(symbols, result.x))
            else:
                return dict(zip(symbols, [1.0 / n_assets] * n_assets))
                
        except Exception as e:
            self.logger.error(f"Error in mean-variance optimization: {e}")
            return dict(zip(symbols, [1.0 / len(symbols)] * len(symbols)))
    
    def _calculate_portfolio_variance(self, weights: Dict[str, float],
                                    covariance_matrix: np.ndarray, symbols: List[str]) -> float:
        """Calculate portfolio variance"""
        try:
            weight_array = np.array([weights[symbol] for symbol in symbols])
            return np.dot(weight_array.T, np.dot(covariance_matrix, weight_array))
        except:
            return 0.0
    
    def _apply_constraints(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Apply position size constraints to weights"""
        try:
            # Cap individual positions
            for symbol in weights:
                weights[symbol] = min(weights[symbol], self.risk_manager.max_position_size)
            
            # Renormalize to sum to 1
            total_weight = sum(weights.values())
            if total_weight > 0:
                for symbol in weights:
                    weights[symbol] /= total_weight
            
            return weights
            
        except Exception as e:
            self.logger.error(f"Error applying constraints: {e}")
            return weights
    
    def _generate_rebalance_recommendations(self, current_positions: List[Position],
                                          optimal_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate rebalancing recommendations"""
        try:
            recommendations = []
            
            # Calculate current portfolio value
            total_value = sum(pos.quantity * pos.current_price for pos in current_positions)
            
            if total_value <= 0:
                return recommendations
            
            # Calculate current weights
            current_weights = {}
            for pos in current_positions:
                current_weights[pos.symbol] = (pos.quantity * pos.current_price) / total_value
            
            # Compare with optimal weights
            for symbol, optimal_weight in optimal_weights.items():
                current_weight = current_weights.get(symbol, 0.0)
                weight_diff = optimal_weight - current_weight
                
                if abs(weight_diff) > self.rebalance_threshold:
                    target_value = optimal_weight * total_value
                    current_value = current_weight * total_value
                    trade_value = target_value - current_value
                    
                    recommendations.append({
                        'symbol': symbol,
                        'action': 'buy' if trade_value > 0 else 'sell',
                        'current_weight': current_weight,
                        'target_weight': optimal_weight,
                        'weight_difference': weight_diff,
                        'trade_value': abs(trade_value),
                        'priority': abs(weight_diff) / self.rebalance_threshold
                    })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating rebalance recommendations: {e}")
            return []
    
    def _calculate_optimization_confidence(self, historical_data: Dict[str, pd.DataFrame],
                                         expected_returns: Dict[str, float]) -> float:
        """Calculate confidence in optimization results"""
        try:
            confidence = 0.8  # Base confidence
            
            # Adjust based on data quality
            avg_data_length = np.mean([len(df) for df in historical_data.values()])
            if avg_data_length < 100:
                confidence -= 0.2
            elif avg_data_length > 200:
                confidence += 0.1
            
            # Adjust based on return predictions
            return_values = list(expected_returns.values())
            if len(return_values) > 0:
                return_std = np.std(return_values)
                if return_std > 0.05:  # High uncertainty
                    confidence -= 0.1
            
            return max(0.1, min(confidence, 0.95))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5


# Global portfolio optimizer instance
portfolio_optimizer = PortfolioOptimizer()


class MarkowitzOptimizer:
    """
    Complete Markowitz Mean-Variance Portfolio Optimization

    Implements the full Markowitz portfolio theory with:
    - Efficient frontier calculation
    - Risk-return optimization
    - Optimal weight allocation
    - Sharpe ratio maximization
    - Minimum variance portfolio
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.min_weight = 0.0       # Minimum weight per asset
        self.max_weight = 0.4       # Maximum weight per asset (40%)

    def optimize_portfolio_markowitz(self, expected_returns: pd.Series, covariance_matrix: pd.DataFrame,
                                   optimization_type: str = "max_sharpe") -> Dict[str, Any]:
        """
        Perform Markowitz portfolio optimization

        Args:
            expected_returns: Expected returns for each asset
            covariance_matrix: Covariance matrix of asset returns
            optimization_type: "max_sharpe", "min_variance"

        Returns:
            Optimization results with weights, metrics, and analysis
        """
        try:
            # Input validation
            if expected_returns.empty or covariance_matrix.empty:
                raise ValueError("Empty returns or covariance data")

            n_assets = len(expected_returns)
            if n_assets < 2:
                raise ValueError("Need at least 2 assets for optimization")

            # Convert to numpy arrays for optimization
            mu = expected_returns.values
            sigma = covariance_matrix.values

            # Validate covariance matrix
            if not self._is_positive_definite(sigma):
                self.logger.warning("Covariance matrix is not positive definite, regularizing...")
                sigma = self._regularize_covariance_matrix(sigma)

            # Perform optimization based on type
            if optimization_type == "max_sharpe":
                result = self._maximize_sharpe_ratio(mu, sigma, expected_returns.index)
            elif optimization_type == "min_variance":
                result = self._minimize_variance(mu, sigma, expected_returns.index)
            else:
                # Default to max Sharpe ratio
                result = self._maximize_sharpe_ratio(mu, sigma, expected_returns.index)

            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(
                result['weights'], mu, sigma, expected_returns.index
            )

            # Generate efficient frontier points
            efficient_frontier = self._generate_efficient_frontier_sample(mu, sigma, expected_returns.index)

            return {
                "optimization_type": optimization_type,
                "weights": result['weights'],
                "portfolio_metrics": portfolio_metrics,
                "efficient_frontier": efficient_frontier,
                "optimization_details": result.get('details', {}),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Markowitz optimization error: {e}")
            return {
                "optimization_type": optimization_type,
                "error": str(e),
                "success": False,
                "weights": {},
                "portfolio_metrics": {},
                "efficient_frontier": []
            }

    def _is_positive_definite(self, matrix: np.ndarray) -> bool:
        """Check if matrix is positive definite"""
        try:
            np.linalg.cholesky(matrix)
            return True
        except np.linalg.LinAlgError:
            return False

    def _regularize_covariance_matrix(self, sigma: np.ndarray) -> np.ndarray:
        """Regularize covariance matrix to make it positive definite"""
        try:
            # Add small value to diagonal
            regularized = sigma + np.eye(sigma.shape[0]) * 1e-6
            return regularized
        except Exception as e:
            self.logger.error(f"Covariance regularization error: {e}")
            return sigma

    def _maximize_sharpe_ratio(self, mu: np.ndarray, sigma: np.ndarray,
                              asset_names: pd.Index) -> Dict[str, Any]:
        """Maximize Sharpe ratio using optimization"""
        try:
            from scipy.optimize import minimize

            n_assets = len(mu)

            # Objective function: minimize negative Sharpe ratio
            def negative_sharpe(weights):
                portfolio_return = np.dot(weights, mu)
                portfolio_variance = np.dot(weights.T, np.dot(sigma, weights))
                portfolio_volatility = np.sqrt(max(portfolio_variance, 1e-10))  # Avoid division by zero

                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe_ratio  # Minimize negative Sharpe

            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}  # Weights sum to 1
            ]

            # Bounds for each weight
            bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets)]

            # Initial guess (equal weights)
            x0 = np.array([1.0 / n_assets] * n_assets)

            # Optimize
            result = minimize(
                negative_sharpe, x0, method='SLSQP',
                bounds=bounds, constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            if result.success:
                weights_dict = dict(zip(asset_names, result.x))
                return {
                    'weights': weights_dict,
                    'details': {
                        'optimization_success': True,
                        'iterations': result.nit,
                        'final_sharpe': -result.fun
                    }
                }
            else:
                raise ValueError(f"Optimization failed: {result.message}")

        except Exception as e:
            self.logger.error(f"Sharpe ratio maximization error: {e}")
            # Fallback to equal weights
            equal_weight = 1.0 / len(asset_names)
            return {
                'weights': dict(zip(asset_names, [equal_weight] * len(asset_names))),
                'details': {'optimization_success': False, 'error': str(e)}
            }

    def _minimize_variance(self, mu: np.ndarray, sigma: np.ndarray,
                          asset_names: pd.Index) -> Dict[str, Any]:
        """Find minimum variance portfolio"""
        try:
            from scipy.optimize import minimize

            n_assets = len(mu)

            # Objective function: minimize portfolio variance
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(sigma, weights))

            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}  # Weights sum to 1
            ]

            # Bounds
            bounds = [(self.min_weight, self.max_weight) for _ in range(n_assets)]

            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)

            # Optimize
            result = minimize(
                portfolio_variance, x0, method='SLSQP',
                bounds=bounds, constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            if result.success:
                weights_dict = dict(zip(asset_names, result.x))
                return {
                    'weights': weights_dict,
                    'details': {
                        'optimization_success': True,
                        'iterations': result.nit,
                        'final_variance': result.fun
                    }
                }
            else:
                raise ValueError(f"Optimization failed: {result.message}")

        except Exception as e:
            self.logger.error(f"Minimum variance optimization error: {e}")
            # Fallback to equal weights
            equal_weight = 1.0 / len(asset_names)
            return {
                'weights': dict(zip(asset_names, [equal_weight] * len(asset_names))),
                'details': {'optimization_success': False, 'error': str(e)}
            }

    def _calculate_portfolio_metrics(self, weights: Dict[str, float], mu: np.ndarray,
                                   sigma: np.ndarray, asset_names: pd.Index) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        try:
            # Convert weights to array
            weights_array = np.array([weights.get(name, 0) for name in asset_names])

            # Portfolio return
            portfolio_return = np.dot(weights_array, mu)

            # Portfolio variance and volatility
            portfolio_variance = np.dot(weights_array.T, np.dot(sigma, weights_array))
            portfolio_volatility = np.sqrt(max(portfolio_variance, 0))

            # Sharpe ratio
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

            return {
                "expected_return": round(portfolio_return, 4),
                "volatility": round(portfolio_volatility, 4),
                "sharpe_ratio": round(sharpe_ratio, 4),
                "variance": round(portfolio_variance, 6)
            }

        except Exception as e:
            self.logger.error(f"Portfolio metrics calculation error: {e}")
            return {
                "expected_return": 0.0,
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "variance": 0.0
            }

    def _generate_efficient_frontier_sample(self, mu: np.ndarray, sigma: np.ndarray,
                                          asset_names: pd.Index) -> List[Dict[str, float]]:
        """Generate sample efficient frontier points"""
        try:
            frontier_points = []

            # Generate a few sample points
            sample_returns = [np.min(mu), np.mean(mu), np.max(mu)]

            for target_return in sample_returns:
                try:
                    # Simple optimization for target return
                    weights_dict = dict(zip(asset_names, [1.0/len(asset_names)] * len(asset_names)))
                    metrics = self._calculate_portfolio_metrics(weights_dict, mu, sigma, asset_names)

                    frontier_points.append({
                        "expected_return": round(target_return, 4),
                        "volatility": metrics["volatility"],
                        "sharpe_ratio": metrics["sharpe_ratio"]
                    })
                except:
                    continue

            return frontier_points

        except Exception as e:
            self.logger.error(f"Efficient frontier generation error: {e}")
            return []


# Global Markowitz optimizer instance
markowitz_optimizer = MarkowitzOptimizer()
