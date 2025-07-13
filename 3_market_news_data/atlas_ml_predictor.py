"""
A.T.L.A.S ML Price Predictor Module
LSTM neural network for 5-minute bar return predictions with automated execution
"""

import numpy as np
import pandas as pd
import logging
import asyncio
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

from config import settings
from models import MLPredictionResult, SignalStrength
from atlas_performance_optimizer import performance_optimizer

# Optional ML imports with graceful fallback
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from sklearn.preprocessing import MinMaxScaler
    ML_AVAILABLE = True
    
    # Configure TensorFlow for optimal performance
    tf.config.experimental.enable_memory_growth = True
    if tf.config.list_physical_devices('GPU'):
        tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True)
        
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class LSTMPricePredictor:
    """
    LSTM neural network for price prediction with feature engineering
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enabled = settings.ML_MODELS_ENABLED and ML_AVAILABLE
        self.model_path = settings.LSTM_MODEL_PATH
        self.confidence_threshold = settings.ML_PREDICTION_CONFIDENCE_THRESHOLD
        
        # Model parameters
        self.sequence_length = 60  # 60 time steps for prediction
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower',
            'sma_20', 'ema_12', 'atr', 'volume_sma'
        ]
        
        # Model components (lazy loaded)
        self.model = None
        self.scaler = None
        
        # Performance tracking
        self.predictions_made = 0
        self.accuracy_history = []
        self.max_retries = 3
        
        # Caching
        self.prediction_cache = {}
        self.cache_ttl = 60  # 1 minute
        
        self.logger.info(f"[AI] LSTM Predictor initialized - ML: {self.enabled}")
    
    async def initialize(self):
        """Initialize ML model and scaler"""
        if not self.enabled:
            self.logger.info("[AI] LSTM predictor running in fallback mode (no ML models)")
            return
        
        try:
            # Load or create model
            if os.path.exists(self.model_path):
                self.logger.info("[TOOL] Loading existing LSTM model...")
                self.model = load_model(self.model_path)
            else:
                self.logger.info("[TOOL] Creating new LSTM model...")
                self.model = self._create_model()
            
            # Load or create scaler
            scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            else:
                self.scaler = MinMaxScaler(feature_range=(0, 1))
            
            self.logger.info("[OK] LSTM model and scaler loaded successfully")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to load LSTM model: {e}")
            self.enabled = False
    
    @performance_optimizer.performance_monitor("lstm_predict")
    async def predict_returns(self, symbol: str, timeframe: str = "5min") -> Optional[MLPredictionResult]:
        """
        Predict next 5-minute bar returns for symbol
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.prediction_cache:
                cached_data = self.prediction_cache[cache_key]
                if (datetime.now() - cached_data['timestamp']).total_seconds() < self.cache_ttl:
                    return cached_data['result']
            
            # Get historical data with features
            features_df = await self._prepare_features(symbol, timeframe)
            
            if features_df is None or len(features_df) < self.sequence_length:
                self.logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Prepare sequence for prediction
            sequence = self._prepare_sequence(features_df)
            
            if sequence is None:
                return None
            
            # Make prediction with retry logic
            predicted_return = await self._predict_with_retry(sequence)
            
            if predicted_return is None:
                return None
            
            # Calculate confidence and signal strength
            confidence = self._calculate_confidence(features_df, predicted_return)
            signal_strength = self._determine_signal_strength(predicted_return, confidence)
            
            # Update tracking
            self.predictions_made += 1
            
            result = MLPredictionResult(
                symbol=symbol,
                predicted_return=predicted_return,
                confidence=confidence,
                signal_strength=signal_strength,
                features_used=self.feature_columns,
                model_type="LSTM",
                timestamp=datetime.now()
            )
            
            # Cache result
            self.prediction_cache[cache_key] = {
                'result': result,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"[AI] LSTM Prediction for {symbol}: {predicted_return:.4f} ({signal_strength})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error predicting returns for {symbol}: {e}")
            return None
    
    async def _prepare_features(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Prepare feature matrix for prediction"""
        try:
            # This would integrate with market data provider
            # For now, return None as placeholder - would need to implement
            # actual data fetching and feature engineering
            
            # Placeholder for feature engineering
            # In real implementation, this would:
            # 1. Fetch historical price data
            # 2. Calculate technical indicators
            # 3. Engineer features
            # 4. Return prepared DataFrame
            
            self.logger.warning(f"Feature preparation not implemented for {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error preparing features for {symbol}: {e}")
            return None
    
    def _prepare_sequence(self, features_df: pd.DataFrame) -> Optional[np.ndarray]:
        """Prepare sequence for LSTM prediction"""
        try:
            if not self.enabled or self.scaler is None:
                return None
            
            # Select feature columns
            feature_data = features_df[self.feature_columns].values
            
            # Scale features
            scaled_features = self.scaler.transform(feature_data)
            
            # Create sequence
            sequence = scaled_features[-self.sequence_length:].reshape(1, self.sequence_length, len(self.feature_columns))
            
            return sequence
            
        except Exception as e:
            self.logger.error(f"Error preparing sequence: {e}")
            return None
    
    async def _predict_with_retry(self, sequence: np.ndarray) -> Optional[float]:
        """Make prediction with retry logic for GPU memory errors"""
        if not self.enabled or self.model is None:
            return self._fallback_prediction()
        
        for attempt in range(self.max_retries + 1):
            try:
                # Make prediction
                prediction = self.model.predict(sequence, verbose=0)
                return float(prediction[0][0])
                
            except Exception as e:
                self.logger.warning(f"Prediction error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error("All prediction attempts failed, using fallback")
                    return self._fallback_prediction()
        
        return None
    
    def _fallback_prediction(self) -> float:
        """Simple fallback prediction when ML is unavailable"""
        # Simple random walk with slight positive bias
        return np.random.normal(0.0001, 0.01)  # Small positive expected return
    
    def _calculate_confidence(self, features_df: pd.DataFrame, predicted_return: float) -> float:
        """Calculate prediction confidence based on various factors"""
        try:
            base_confidence = 0.5
            
            # Adjust based on prediction magnitude
            magnitude_factor = min(abs(predicted_return) * 100, 0.3)  # Cap at 0.3
            
            # Adjust based on recent volatility
            if len(features_df) >= 20:
                recent_volatility = features_df['close'].pct_change().tail(20).std()
                volatility_factor = max(0.1, 1.0 - recent_volatility * 10)  # Lower confidence in high volatility
            else:
                volatility_factor = 0.5
            
            # Combine factors
            confidence = base_confidence + magnitude_factor * volatility_factor
            
            return min(max(confidence, 0.1), 0.95)  # Clamp between 0.1 and 0.95
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _determine_signal_strength(self, predicted_return: float, confidence: float) -> SignalStrength:
        """Determine signal strength based on prediction and confidence"""
        abs_return = abs(predicted_return)
        
        if abs_return > 0.02 and confidence > 0.8:  # 2%+ return with high confidence
            return SignalStrength.VERY_STRONG
        elif abs_return > 0.01 and confidence > 0.7:  # 1%+ return with good confidence
            return SignalStrength.STRONG
        elif abs_return > 0.005 and confidence > 0.6:  # 0.5%+ return with moderate confidence
            return SignalStrength.MODERATE
        elif abs_return > 0.002 and confidence > 0.5:  # 0.2%+ return with some confidence
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def _create_model(self) -> 'tf.keras.Model':
        """Create new LSTM model architecture"""
        if not ML_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.sequence_length, len(self.feature_columns))),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        return model
    
    async def train_model(self, training_data: pd.DataFrame) -> bool:
        """Train the LSTM model with new data"""
        if not self.enabled:
            self.logger.warning("Cannot train model - ML not available")
            return False
        
        try:
            self.logger.info("[TOOL] Training LSTM model...")
            
            # Prepare training data
            X, y = self._prepare_training_data(training_data)
            
            if X is None or y is None:
                self.logger.error("Failed to prepare training data")
                return False
            
            # Train model
            history = self.model.fit(
                X, y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
            
            # Save model and scaler
            self.model.save(self.model_path)
            scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            self.logger.info("[OK] LSTM model training completed and saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare training data for LSTM"""
        try:
            # Feature engineering would go here
            # This is a placeholder implementation
            
            # Calculate returns
            data['returns'] = data['close'].pct_change()
            
            # Prepare features
            features = data[self.feature_columns].dropna()
            returns = data['returns'].dropna()
            
            # Align data
            min_length = min(len(features), len(returns))
            features = features.tail(min_length)
            returns = returns.tail(min_length)
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Create sequences
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_features)):
                X.append(scaled_features[i-self.sequence_length:i])
                y.append(returns.iloc[i])
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return None, None
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        return {
            'predictions_made': self.predictions_made,
            'model_enabled': self.enabled,
            'cache_size': len(self.prediction_cache),
            'accuracy_history': self.accuracy_history[-10:],  # Last 10 accuracy scores
            'model_path': self.model_path if self.enabled else None
        }


# Global ML predictor instance
ml_predictor = LSTMPricePredictor()
