"""
A.T.L.A.S AI Trading System - Data Models and Schemas
Pydantic models for type safety and validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# Enums for type safety
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    BRACKET = "bracket"  # OCO (One-Cancels-Other) bracket orders
    TRAILING_STOP = "trailing_stop"
    FILL_OR_KILL = "fill_or_kill"
    IMMEDIATE_OR_CANCEL = "immediate_or_cancel"


class OrderStatus(str, Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


class EngineStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    FAILED = "failed"
    SHUTTING_DOWN = "shutting_down"


class SignalStrength(str, Enum):
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


# Core Data Models
class Quote(BaseModel):
    """Real-time market quote"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v


class Position(BaseModel):
    """Trading position"""
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    side: OrderSide
    timestamp: datetime


class Order(BaseModel):
    """Trading order"""
    id: Optional[str] = None
    symbol: str
    quantity: float
    side: OrderSide
    type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: float = 0.0
    timestamp: datetime
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""
    symbol: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    volume_sma: Optional[float] = None
    timestamp: datetime


class TTMSqueezeSignal(BaseModel):
    """TTM Squeeze trading signal"""
    symbol: str
    signal_strength: SignalStrength
    histogram_value: float
    squeeze_active: bool
    momentum_direction: str  # "bullish", "bearish", "neutral"
    confidence: float = Field(ge=0.0, le=1.0)
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None
    timestamp: datetime


class RiskAssessment(BaseModel):
    """Risk management assessment"""
    symbol: str
    risk_score: float = Field(ge=0.0, le=10.0)
    position_size: float
    stop_loss_price: float
    risk_amount: float
    risk_percentage: float
    confidence_level: float = Field(ge=0.0, le=1.0)
    risk_factors: List[str] = []
    recommendations: List[str] = []
    timestamp: datetime


class MarketContext(BaseModel):
    """Market context and sentiment"""
    overall_sentiment: str  # "bullish", "bearish", "neutral"
    vix_level: Optional[float] = None
    market_trend: Optional[str] = None
    sector_rotation: Optional[Dict[str, float]] = None
    news_sentiment: Optional[float] = None
    economic_indicators: Optional[Dict[str, Any]] = None
    timestamp: datetime


# API Request/Response Models
class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AIResponse(BaseModel):
    """AI response model"""
    response: str
    type: str = "chat"  # chat, analysis, error, system_status
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    context: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisRequest(BaseModel):
    """Market analysis request"""
    symbol: str = Field(pattern=r'^[A-Z]{1,5}$')
    timeframe: str = Field(default="1day", pattern=r'^(1min|5min|15min|30min|1hour|1day)$')
    include_technical: bool = True
    include_sentiment: bool = True
    include_risk: bool = True


class EducationRequest(BaseModel):
    """Educational query request"""
    question: str = Field(min_length=1, max_length=1000)
    topic: Optional[str] = None
    difficulty_level: str = Field(default="beginner", pattern=r'^(beginner|intermediate|advanced)$')
    book_filter: Optional[str] = None


class SystemStatus(BaseModel):
    """System health and status"""
    status: str  # healthy, degraded, initializing, failed
    timestamp: datetime
    version: str = "4.0.0"
    engines: Dict[str, EngineStatus]
    initialization_progress: Optional[Dict[str, float]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class PortfolioSummary(BaseModel):
    """Portfolio summary"""
    total_value: float
    cash_balance: float
    positions_value: float
    unrealized_pnl: float
    realized_pnl: float
    day_change: float
    day_change_percent: float
    positions: List[Position]
    timestamp: datetime


class ScanResult(BaseModel):
    """Market scan result"""
    symbol: str
    signal_type: str
    signal_strength: SignalStrength
    score: float = Field(ge=0.0, le=10.0)
    price: float
    volume: Optional[int] = None
    indicators: Optional[Dict[str, float]] = None
    reasoning: Optional[str] = None
    timestamp: datetime


class PredictoForecast(BaseModel):
    """Predicto AI forecast"""
    symbol: str
    forecast_days: int
    predicted_price: float
    confidence: float = Field(ge=0.0, le=1.0)
    price_targets: Optional[Dict[str, float]] = None
    risk_factors: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    timestamp: datetime


# Configuration Models
class UserProfile(BaseModel):
    """User trading profile"""
    experience_level: str = Field(default="beginner", pattern=r'^(beginner|intermediate|advanced|expert)$')
    risk_tolerance: str = Field(default="moderate", pattern=r'^(conservative|moderate|aggressive)$')
    account_size: float = Field(default=10000.0, ge=1000.0)
    communication_style: str = Field(default="mentor", pattern=r'^(mentor|professional|casual)$')
    trading_goals: Optional[List[str]] = None
    preferred_timeframes: Optional[List[str]] = None


class InitializationStatus(BaseModel):
    """System initialization tracking"""
    component: str
    status: EngineStatus
    progress: float = Field(ge=0.0, le=1.0)
    message: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# Export all models
# Enhanced Models for Advanced Features

class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of proactive alerts"""
    MORNING_BRIEFING = "morning_briefing"
    OPPORTUNITY_NOTIFICATION = "opportunity_notification"
    MARKET_PROTECTION = "market_protection"
    TIME_SENSITIVE_SETUP = "time_sensitive_setup"
    EARNINGS_WARNING = "earnings_warning"
    VOLATILITY_ALERT = "volatility_alert"


class OptionType(str, Enum):
    """Option types"""
    CALL = "call"
    PUT = "put"


class StrategyType(str, Enum):
    """Options strategy types"""
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    COVERED_CALL = "covered_call"
    CASH_SECURED_PUT = "cash_secured_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"


class CommunicationMode(str, Enum):
    """AI communication styles"""
    MENTOR = "mentor"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AGGRESSIVE = "aggressive"


class EmotionalState(str, Enum):
    """User emotional states"""
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    CURIOUS = "curious"


# Advanced Data Models

class ProactiveAlert(BaseModel):
    """Proactive alert data structure"""
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    action_required: bool
    expiry_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class SentimentData(BaseModel):
    """Sentiment analysis result"""
    source: str  # 'news', 'reddit', 'twitter'
    symbol: str
    text: str
    sentiment_score: float  # -1 to 1
    confidence: float
    timestamp: datetime
    url: Optional[str] = None


class SentimentSignal(BaseModel):
    """Aggregated sentiment signal"""
    symbol: str
    overall_sentiment: float  # -1 to 1
    confidence: float
    signal_strength: SignalStrength
    source_count: int
    bullish_signals: int
    bearish_signals: int
    neutral_signals: int
    implied_volatility: Optional[float] = None
    should_hedge: bool = False
    hedge_symbol: Optional[str] = None
    timestamp: datetime


class MLPredictionResult(BaseModel):
    """ML prediction result"""
    symbol: str
    predicted_return: float
    confidence: float
    signal_strength: SignalStrength
    features_used: List[str]
    model_type: str = "LSTM"
    timestamp: datetime


class OptionContract(BaseModel):
    """Option contract details"""
    symbol: str
    underlying: str
    option_type: OptionType
    strike: float
    expiration: datetime
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None


class OptionsStrategy(BaseModel):
    """Options trading strategy"""
    strategy_type: StrategyType
    underlying_symbol: str
    contracts: List[OptionContract]
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    breakeven_points: List[float] = Field(default_factory=list)
    probability_of_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    margin_requirement: Optional[float] = None


class TradingGoal(BaseModel):
    """User trading goal with context"""
    goal_type: str  # 'profit_target', 'risk_limit', 'learning', 'strategy_test'
    target_amount: Optional[float] = None
    timeframe: Optional[str] = None  # 'today', 'this_week', 'by_friday'
    risk_tolerance: str = 'moderate'  # 'conservative', 'moderate', 'aggressive'
    priority: int = 1  # 1=highest, 5=lowest
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = 'active'  # 'active', 'completed', 'cancelled'
    progress: float = 0.0  # 0.0 to 1.0


class ContextMemory(BaseModel):
    """Enhanced context memory entry"""
    session_id: str
    context_type: str
    context_data: str
    emotional_state: Optional[EmotionalState] = None
    confidence_score: float = 0.5
    timestamp: datetime = Field(default_factory=datetime.now)


class PerformanceMetrics(BaseModel):
    """Performance metrics tracking"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


__all__ = [
    # Enums
    "OrderSide", "OrderType", "OrderStatus", "EngineStatus", "SignalStrength",
    "AlertPriority", "AlertType", "OptionType", "StrategyType", "CommunicationMode", "EmotionalState",

    # Core Models
    "Quote", "Position", "Order", "TechnicalIndicators", "TTMSqueezeSignal",
    "RiskAssessment", "MarketContext",

    # API Models
    "ChatRequest", "AIResponse", "AnalysisRequest", "EducationRequest",
    "SystemStatus", "PortfolioSummary", "ScanResult", "PredictoForecast",

    # Configuration Models
    "UserProfile", "InitializationStatus",

    # Advanced Models
    "ProactiveAlert", "SentimentData", "SentimentSignal", "MLPredictionResult",
    "OptionContract", "OptionsStrategy", "TradingGoal", "ContextMemory", "PerformanceMetrics"
]
