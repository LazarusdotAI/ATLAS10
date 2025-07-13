"""
A.T.L.A.S Goal-Based Trading Strategy Generator
AI-powered trading strategy generation based on user goals and timeframes
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from config import settings
from models import AIResponse, EngineStatus

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class StrategyType(Enum):
    """Trading strategy types"""
    SCALPING = "scalping"
    DAY_TRADING = "day_trading"
    SWING_TRADING = "swing_trading"
    POSITION_TRADING = "position_trading"
    OPTIONS_STRATEGIES = "options_strategies"


@dataclass
class TradingGoal:
    """User trading goal specification"""
    target_amount: float
    target_date: datetime
    current_capital: float
    risk_tolerance: RiskLevel
    timeframe_days: int
    required_daily_return: float
    feasibility_score: float
    
    def __post_init__(self):
        """Calculate derived metrics"""
        self.timeframe_days = (self.target_date - datetime.now()).days
        if self.timeframe_days > 0 and self.current_capital > 0:
            self.required_daily_return = (self.target_amount / self.current_capital) / self.timeframe_days
        else:
            self.required_daily_return = 0.0
        
        # Calculate feasibility (0-1 score)
        self.feasibility_score = self._calculate_feasibility()
    
    def _calculate_feasibility(self) -> float:
        """Calculate goal feasibility based on market realities"""
        # Conservative feasibility assessment
        if self.required_daily_return <= 0.005:  # 0.5% daily
            return 0.9
        elif self.required_daily_return <= 0.01:  # 1% daily
            return 0.7
        elif self.required_daily_return <= 0.02:  # 2% daily
            return 0.5
        elif self.required_daily_return <= 0.05:  # 5% daily
            return 0.3
        else:
            return 0.1  # Very unrealistic


@dataclass
class PositionSizing:
    """Position sizing recommendations"""
    max_position_size: float
    risk_per_trade: float
    max_daily_risk: float
    stop_loss_percentage: float
    position_count: int
    diversification_rules: List[str]


@dataclass
class TradingStrategy:
    """Complete trading strategy recommendation"""
    goal: TradingGoal
    strategy_type: StrategyType
    position_sizing: PositionSizing
    recommended_stocks: List[Dict[str, Any]]
    timeline_milestones: List[Dict[str, Any]]
    risk_management_rules: List[str]
    success_probability: float
    alternative_strategies: List[str]
    educational_resources: List[str]


class GoalBasedStrategyGenerator:
    """
    AI-powered trading strategy generator that creates comprehensive trading plans
    based on user goals, timeframes, and risk tolerance
    """
    
    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        self.market_engine = None
        self.risk_engine = None
        self.ml_predictor = None
        self.sentiment_analyzer = None
        
        # Strategy templates
        self.strategy_templates = {
            StrategyType.SCALPING: {
                "min_timeframe_days": 1,
                "max_timeframe_days": 7,
                "typical_daily_return": 0.005,
                "max_position_hold": "minutes to hours",
                "required_capital": 1000
            },
            StrategyType.DAY_TRADING: {
                "min_timeframe_days": 1,
                "max_timeframe_days": 30,
                "typical_daily_return": 0.01,
                "max_position_hold": "same day",
                "required_capital": 2500
            },
            StrategyType.SWING_TRADING: {
                "min_timeframe_days": 7,
                "max_timeframe_days": 90,
                "typical_daily_return": 0.008,
                "max_position_hold": "2-10 days",
                "required_capital": 5000
            },
            StrategyType.POSITION_TRADING: {
                "min_timeframe_days": 30,
                "max_timeframe_days": 365,
                "typical_daily_return": 0.003,
                "max_position_hold": "weeks to months",
                "required_capital": 10000
            }
        }
    
    async def initialize(self, market_engine=None, risk_engine=None, ml_predictor=None, sentiment_analyzer=None):
        """Initialize with engine references"""
        try:
            self.market_engine = market_engine
            self.risk_engine = risk_engine
            self.ml_predictor = ml_predictor
            self.sentiment_analyzer = sentiment_analyzer
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Goal-Based Strategy Generator initialized")
            
        except Exception as e:
            logger.error(f"[ERROR] Goal-Based Strategy Generator initialization failed: {e}")
            self.status = EngineStatus.FAILED
            raise
    
    async def parse_user_goal(self, message: str, current_capital: float = 10000) -> Optional[TradingGoal]:
        """Parse user goal from natural language"""
        try:
            # Extract target amount
            amount_patterns = [
                r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?) dollars?',
                r'make (\d+(?:,\d{3})*(?:\.\d{2})?)',
            ]
            
            target_amount = None
            for pattern in amount_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    amount_str = match.group(1).replace(',', '')
                    target_amount = float(amount_str)
                    break
            
            if not target_amount:
                return None
            
            # Extract timeframe
            target_date = self._parse_timeframe(message)
            if not target_date:
                # Default to 30 days if no timeframe specified
                target_date = datetime.now() + timedelta(days=30)
            
            # Determine risk tolerance from language
            risk_tolerance = self._parse_risk_tolerance(message)
            
            return TradingGoal(
                target_amount=target_amount,
                target_date=target_date,
                current_capital=current_capital,
                risk_tolerance=risk_tolerance,
                timeframe_days=0,  # Will be calculated in __post_init__
                required_daily_return=0.0,  # Will be calculated in __post_init__
                feasibility_score=0.0  # Will be calculated in __post_init__
            )
            
        except Exception as e:
            logger.error(f"Error parsing user goal: {e}")
            return None
    
    def _parse_timeframe(self, message: str) -> Optional[datetime]:
        """Parse timeframe from natural language"""
        message_lower = message.lower()
        
        # Look for specific dates
        date_patterns = [
            r'by (\d{1,2})/(\d{1,2})/(\d{4})',
            r'by (\d{1,2})-(\d{1,2})-(\d{4})',
            r'by (\w+) (\d{1,2})',  # "by March 15"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    if len(match.groups()) == 3:
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                except:
                    continue
        
        # Look for relative timeframes
        relative_patterns = [
            (r'(\d+) days?', lambda x: datetime.now() + timedelta(days=int(x))),
            (r'(\d+) weeks?', lambda x: datetime.now() + timedelta(weeks=int(x))),
            (r'(\d+) months?', lambda x: datetime.now() + timedelta(days=int(x)*30)),
            (r'today', lambda x: datetime.now() + timedelta(days=1)),
            (r'tomorrow', lambda x: datetime.now() + timedelta(days=1)),
            (r'this week', lambda x: datetime.now() + timedelta(days=7)),
            (r'next week', lambda x: datetime.now() + timedelta(days=14)),
            (r'this month', lambda x: datetime.now() + timedelta(days=30)),
        ]
        
        for pattern, date_func in relative_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    if match.groups():
                        return date_func(match.group(1))
                    else:
                        return date_func(None)
                except:
                    continue
        
        return None
    
    def _parse_risk_tolerance(self, message: str) -> RiskLevel:
        """Parse risk tolerance from natural language"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['conservative', 'safe', 'low risk', 'careful']):
            return RiskLevel.CONSERVATIVE
        elif any(word in message_lower for word in ['aggressive', 'high risk', 'risky', 'fast']):
            return RiskLevel.AGGRESSIVE
        elif any(word in message_lower for word in ['very aggressive', 'extremely risky', 'all in']):
            return RiskLevel.VERY_AGGRESSIVE
        else:
            return RiskLevel.MODERATE
    
    async def generate_strategy(self, goal: TradingGoal) -> TradingStrategy:
        """Generate comprehensive trading strategy based on goal"""
        try:
            # Determine optimal strategy type
            strategy_type = self._determine_strategy_type(goal)
            
            # Calculate position sizing
            position_sizing = self._calculate_position_sizing(goal, strategy_type)
            
            # Get stock recommendations
            recommended_stocks = await self._get_stock_recommendations(goal, strategy_type)
            
            # Create timeline milestones
            timeline_milestones = self._create_timeline_milestones(goal)
            
            # Generate risk management rules
            risk_management_rules = self._generate_risk_rules(goal, strategy_type)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(goal, strategy_type)
            
            # Generate alternative strategies
            alternative_strategies = self._generate_alternatives(goal)
            
            # Educational resources
            educational_resources = self._get_educational_resources(strategy_type)
            
            return TradingStrategy(
                goal=goal,
                strategy_type=strategy_type,
                position_sizing=position_sizing,
                recommended_stocks=recommended_stocks,
                timeline_milestones=timeline_milestones,
                risk_management_rules=risk_management_rules,
                success_probability=success_probability,
                alternative_strategies=alternative_strategies,
                educational_resources=educational_resources
            )
            
        except Exception as e:
            logger.error(f"Error generating strategy: {e}")
            raise


    def _determine_strategy_type(self, goal: TradingGoal) -> StrategyType:
        """Determine optimal strategy type based on goal parameters"""
        timeframe_days = goal.timeframe_days
        required_return = goal.required_daily_return

        # Strategy selection logic
        if timeframe_days <= 7 and required_return > 0.02:
            return StrategyType.SCALPING
        elif timeframe_days <= 30 and required_return > 0.01:
            return StrategyType.DAY_TRADING
        elif timeframe_days <= 90:
            return StrategyType.SWING_TRADING
        else:
            return StrategyType.POSITION_TRADING

    def _calculate_position_sizing(self, goal: TradingGoal, strategy_type: StrategyType) -> PositionSizing:
        """Calculate position sizing based on risk management principles"""
        # Risk per trade based on risk tolerance
        risk_per_trade_map = {
            RiskLevel.CONSERVATIVE: 0.01,  # 1%
            RiskLevel.MODERATE: 0.02,      # 2%
            RiskLevel.AGGRESSIVE: 0.03,    # 3%
            RiskLevel.VERY_AGGRESSIVE: 0.05 # 5%
        }

        risk_per_trade = risk_per_trade_map[goal.risk_tolerance]
        max_daily_risk = risk_per_trade * 3  # Maximum 3 trades per day risk

        # Position sizing based on strategy type
        if strategy_type == StrategyType.SCALPING:
            max_position_size = goal.current_capital * 0.1  # 10% per position
            position_count = 5
            stop_loss_percentage = 0.005  # 0.5%
        elif strategy_type == StrategyType.DAY_TRADING:
            max_position_size = goal.current_capital * 0.2  # 20% per position
            position_count = 3
            stop_loss_percentage = 0.01   # 1%
        elif strategy_type == StrategyType.SWING_TRADING:
            max_position_size = goal.current_capital * 0.25 # 25% per position
            position_count = 4
            stop_loss_percentage = 0.02   # 2%
        else:  # Position trading
            max_position_size = goal.current_capital * 0.33 # 33% per position
            position_count = 3
            stop_loss_percentage = 0.05   # 5%

        diversification_rules = [
            f"Maximum {position_count} positions simultaneously",
            "No more than 30% in single sector",
            "Maintain 20% cash reserve",
            f"Stop loss at {stop_loss_percentage*100:.1f}% per trade"
        ]

        return PositionSizing(
            max_position_size=max_position_size,
            risk_per_trade=risk_per_trade,
            max_daily_risk=max_daily_risk,
            stop_loss_percentage=stop_loss_percentage,
            position_count=position_count,
            diversification_rules=diversification_rules
        )

    async def _get_stock_recommendations(self, goal: TradingGoal, strategy_type: StrategyType) -> List[Dict[str, Any]]:
        """Get stock recommendations based on strategy type and market conditions"""
        recommendations = []

        # Default recommendations if market engine not available
        if not self.market_engine:
            return self._get_default_recommendations(strategy_type)

        try:
            # Get TTM Squeeze signals for swing/position trading
            if strategy_type in [StrategyType.SWING_TRADING, StrategyType.POSITION_TRADING]:
                signals = await self.market_engine.scan_ttm_squeeze(min_strength="moderate")
                for signal in signals[:3]:  # Top 3 signals
                    recommendations.append({
                        "symbol": signal.get("symbol", ""),
                        "entry_price": signal.get("entry_price", 0),
                        "target_price": signal.get("target_price", 0),
                        "stop_loss": signal.get("stop_loss", 0),
                        "confidence": signal.get("confidence", 0),
                        "reason": "TTM Squeeze signal detected",
                        "timeframe": "2-10 days" if strategy_type == StrategyType.SWING_TRADING else "weeks to months"
                    })

            # Get high-volume stocks for day trading/scalping
            elif strategy_type in [StrategyType.DAY_TRADING, StrategyType.SCALPING]:
                # Use popular liquid stocks
                liquid_stocks = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA"]
                for symbol in liquid_stocks[:3]:
                    try:
                        quote = await self.market_engine.get_quote(symbol)
                        recommendations.append({
                            "symbol": symbol,
                            "entry_price": quote.get("price", 0),
                            "target_price": quote.get("price", 0) * 1.01,  # 1% target
                            "stop_loss": quote.get("price", 0) * 0.995,    # 0.5% stop
                            "confidence": 0.7,
                            "reason": "High liquidity and volatility",
                            "timeframe": "intraday"
                        })
                    except:
                        continue

        except Exception as e:
            logger.error(f"Error getting stock recommendations: {e}")
            return self._get_default_recommendations(strategy_type)

        return recommendations if recommendations else self._get_default_recommendations(strategy_type)

    def _get_default_recommendations(self, strategy_type: StrategyType) -> List[Dict[str, Any]]:
        """Get default stock recommendations when market engine unavailable"""
        if strategy_type in [StrategyType.DAY_TRADING, StrategyType.SCALPING]:
            return [
                {
                    "symbol": "SPY",
                    "entry_price": 450.0,
                    "target_price": 454.5,
                    "stop_loss": 447.75,
                    "confidence": 0.7,
                    "reason": "High liquidity ETF",
                    "timeframe": "intraday"
                },
                {
                    "symbol": "QQQ",
                    "entry_price": 380.0,
                    "target_price": 383.8,
                    "stop_loss": 378.1,
                    "confidence": 0.7,
                    "reason": "Tech sector ETF with good volatility",
                    "timeframe": "intraday"
                }
            ]
        else:
            return [
                {
                    "symbol": "AAPL",
                    "entry_price": 175.0,
                    "target_price": 185.0,
                    "stop_loss": 170.0,
                    "confidence": 0.8,
                    "reason": "Strong fundamentals and technical setup",
                    "timeframe": "2-4 weeks"
                },
                {
                    "symbol": "MSFT",
                    "entry_price": 340.0,
                    "target_price": 360.0,
                    "stop_loss": 330.0,
                    "confidence": 0.75,
                    "reason": "AI growth story and solid earnings",
                    "timeframe": "3-6 weeks"
                }
            ]

    def _create_timeline_milestones(self, goal: TradingGoal) -> List[Dict[str, Any]]:
        """Create timeline milestones for goal tracking"""
        milestones = []
        total_days = goal.timeframe_days

        # Create weekly milestones
        weeks = max(1, total_days // 7)
        target_per_week = goal.target_amount / weeks

        for week in range(1, min(weeks + 1, 5)):  # Max 4 milestones
            milestone_date = datetime.now() + timedelta(weeks=week)
            cumulative_target = target_per_week * week

            milestones.append({
                "week": week,
                "date": milestone_date.strftime("%Y-%m-%d"),
                "cumulative_target": cumulative_target,
                "weekly_target": target_per_week,
                "success_criteria": f"Achieve ${cumulative_target:.2f} total profit",
                "review_actions": [
                    "Review position performance",
                    "Adjust strategy if needed",
                    "Reassess risk management"
                ]
            })

        return milestones

    def _generate_risk_rules(self, goal: TradingGoal, strategy_type: StrategyType) -> List[str]:
        """Generate risk management rules based on strategy and goal"""
        rules = [
            f"Never risk more than {goal.risk_tolerance.value} per trade",
            "Always set stop-loss before entering position",
            "Take partial profits at 50% of target",
            "Review and adjust strategy weekly",
            "Maintain detailed trading journal"
        ]

        # Strategy-specific rules
        if strategy_type == StrategyType.SCALPING:
            rules.extend([
                "Exit all positions before market close",
                "Focus on high-volume, liquid stocks only",
                "Use tight stop-losses (0.5% max)"
            ])
        elif strategy_type == StrategyType.DAY_TRADING:
            rules.extend([
                "No overnight positions",
                "Maximum 3 trades per day",
                "Wait for clear technical setups"
            ])
        elif strategy_type == StrategyType.SWING_TRADING:
            rules.extend([
                "Hold positions 2-10 days maximum",
                "Use wider stop-losses (2-3%)",
                "Focus on earnings and catalyst plays"
            ])
        else:  # Position trading
            rules.extend([
                "Focus on fundamental analysis",
                "Use 5% stop-losses",
                "Review positions monthly"
            ])

        return rules

    def _calculate_success_probability(self, goal: TradingGoal, strategy_type: StrategyType) -> float:
        """Calculate realistic success probability"""
        base_probability = 0.5  # 50% base

        # Adjust for feasibility
        base_probability *= goal.feasibility_score

        # Adjust for strategy type (some are more reliable)
        strategy_multipliers = {
            StrategyType.POSITION_TRADING: 1.2,
            StrategyType.SWING_TRADING: 1.1,
            StrategyType.DAY_TRADING: 0.9,
            StrategyType.SCALPING: 0.8
        }

        base_probability *= strategy_multipliers.get(strategy_type, 1.0)

        # Adjust for risk tolerance (conservative = higher success)
        risk_multipliers = {
            RiskLevel.CONSERVATIVE: 1.2,
            RiskLevel.MODERATE: 1.0,
            RiskLevel.AGGRESSIVE: 0.8,
            RiskLevel.VERY_AGGRESSIVE: 0.6
        }

        base_probability *= risk_multipliers.get(goal.risk_tolerance, 1.0)

        return min(max(base_probability, 0.1), 0.9)  # Cap between 10-90%

    def _generate_alternatives(self, goal: TradingGoal) -> List[str]:
        """Generate alternative strategy suggestions"""
        alternatives = []

        if goal.feasibility_score < 0.5:
            alternatives.extend([
                "Consider extending your timeframe for more realistic returns",
                "Reduce target amount to improve success probability",
                "Focus on learning and paper trading first",
                "Consider index fund investing for steady growth"
            ])

        if goal.required_daily_return > 0.02:
            alternatives.extend([
                "Options strategies for leveraged exposure",
                "Cryptocurrency trading (higher risk/reward)",
                "Forex trading with proper risk management"
            ])

        alternatives.extend([
            "Dollar-cost averaging into quality stocks",
            "Covered call strategies for income",
            "Dividend growth investing approach"
        ])

        return alternatives

    def _get_educational_resources(self, strategy_type: StrategyType) -> List[str]:
        """Get relevant educational resources"""
        base_resources = [
            "Trading in the Zone - Mark Douglas",
            "Technical Analysis Explained - Martin Pring",
            "Risk management fundamentals",
            "Position sizing calculator"
        ]

        strategy_resources = {
            StrategyType.SCALPING: [
                "Level II order book reading",
                "Tape reading techniques",
                "High-frequency trading basics"
            ],
            StrategyType.DAY_TRADING: [
                "Chart pattern recognition",
                "Volume analysis techniques",
                "Market opening strategies"
            ],
            StrategyType.SWING_TRADING: [
                "Multi-timeframe analysis",
                "Earnings calendar strategies",
                "Catalyst-based trading"
            ],
            StrategyType.POSITION_TRADING: [
                "Fundamental analysis basics",
                "Sector rotation strategies",
                "Long-term trend analysis"
            ]
        }

        return base_resources + strategy_resources.get(strategy_type, [])

    async def format_strategy_response(self, strategy: TradingStrategy) -> str:
        """Format strategy as conversational response"""
        goal = strategy.goal

        # Feasibility assessment
        if goal.feasibility_score < 0.3:
            feasibility_msg = "[WARN] **REALITY CHECK**: This goal is very challenging and may not be realistic."
        elif goal.feasibility_score < 0.6:
            feasibility_msg = "[WARN] **MODERATE RISK**: This goal is ambitious but possible with disciplined execution."
        else:
            feasibility_msg = "[OK] **ACHIEVABLE**: This goal is realistic with proper strategy execution."

        response = f"""[TARGET] **GOAL-BASED TRADING STRATEGY**
**A.T.L.A.S powered by Predicto**

**Your Goal**: Make ${goal.target_amount:,.2f} by {goal.target_date.strftime('%B %d, %Y')}
**Timeframe**: {goal.timeframe_days} days
**Required Daily Return**: {goal.required_daily_return*100:.2f}%
**Success Probability**: {strategy.success_probability*100:.1f}%

{feasibility_msg}

[DATA] **RECOMMENDED STRATEGY: {strategy.strategy_type.value.upper().replace('_', ' ')}**

[MONEY] **POSITION SIZING**
• Maximum position size: ${strategy.position_sizing.max_position_size:,.2f}
• Risk per trade: {strategy.position_sizing.risk_per_trade*100:.1f}%
• Stop loss: {strategy.position_sizing.stop_loss_percentage*100:.1f}%
• Maximum positions: {strategy.position_sizing.position_count}

[TARGET] **TOP STOCK RECOMMENDATIONS**"""

        for i, stock in enumerate(strategy.recommended_stocks[:3], 1):
            response += f"""
{i}. **{stock['symbol']}**
   • Entry: ${stock['entry_price']:.2f}
   • Target: ${stock['target_price']:.2f}
   • Stop: ${stock['stop_loss']:.2f}
   • Confidence: {stock['confidence']*100:.0f}%
   • Reason: {stock['reason']}"""

        response += f"""

📅 **TIMELINE MILESTONES**"""
        for milestone in strategy.timeline_milestones[:3]:
            response += f"""
Week {milestone['week']} ({milestone['date']}): Target ${milestone['cumulative_target']:,.2f}"""

        response += f"""

[SHIELD] **RISK MANAGEMENT RULES**"""
        for rule in strategy.risk_management_rules[:5]:
            response += f"\n• {rule}"

        if goal.feasibility_score < 0.5:
            response += f"""

[IDEA] **ALTERNATIVE APPROACHES**"""
            for alt in strategy.alternative_strategies[:3]:
                response += f"\n• {alt}"

        response += f"""

[LIBRARY] **EDUCATIONAL RESOURCES**"""
        for resource in strategy.educational_resources[:3]:
            response += f"\n• {resource}"

        response += f"""

[WARN] **IMPORTANT DISCLAIMERS**
• This is for educational purposes only
• Past performance doesn't guarantee future results
• Always use proper risk management
• Consider paper trading first

Would you like me to explain any part of this strategy in more detail?"""

        return response


# Global instance
goal_based_strategy_generator = GoalBasedStrategyGenerator()
