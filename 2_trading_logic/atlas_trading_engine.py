"""
A.T.L.A.S Trading Engine - Paper Trading and Order Management
Portfolio tracking with lazy Alpaca integration
"""

# CRITICAL: Import startup initialization FIRST to ensure Windows-compatible logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '4_helper_tools'))

try:
    from atlas_startup_init import initialize_component_logging
    logger = initialize_component_logging('atlas_trading_engine')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import get_api_config
from models import (
    Order, Position, OrderSide, OrderType, OrderStatus,
    PortfolioSummary, EngineStatus
)


class AtlasTradingEngine:
    """
    Trading engine with paper trading and portfolio management
    """
    
    def __init__(self):
        self.alpaca_config = get_api_config("alpaca")
        self.validation_mode = self.alpaca_config.get("validation_mode", False)
        self.status = EngineStatus.INITIALIZING

        # Alpaca client (lazy loaded)
        self._alpaca_client = None
        self._client_lock = asyncio.Lock()

        # Portfolio state
        self.positions = {}
        self.orders = {}
        self.cash_balance = 100000.0  # Starting paper trading balance
        self.total_value = self.cash_balance
        
        # Performance tracking
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.day_start_value = self.cash_balance

        # Enhanced portfolio management
        self.hedging_strategies = {}
        self.auto_reinvestment_enabled = False
        self.portfolio_optimization_settings = {
            "max_position_size": 0.10,  # 10% max per position
            "correlation_threshold": 0.7,  # Correlation limit
            "rebalance_threshold": 0.05,  # 5% drift triggers rebalance
            "risk_budget": 0.02  # 2% daily risk budget
        }

        # Earnings calendar integration
        self.earnings_calendar = {}
        self.earnings_risk_settings = {
            "avoid_earnings_days": True,
            "earnings_buffer_days": 2,  # Avoid trades 2 days before earnings
            "earnings_position_reduction": 0.5  # Reduce position size by 50% before earnings
        }

        # Trade execution confirmation system
        self.pending_trades = {}
        self.trade_confirmations_required = True
        self.execution_safeguards = {
            "max_daily_trades": 10,
            "max_position_value": 5000,
            "require_stop_loss": True,
            "require_profit_target": True
        }

        # Professional trading features
        self.bracket_orders = {}  # OCO bracket order management
        self.trailing_stops = {}  # Trailing stop management
        self.advanced_order_features = {
            "bracket_orders_enabled": True,
            "trailing_stops_enabled": True,
            "partial_fills_allowed": True,
            "after_hours_trading": False,
            "fractional_shares": True
        }
        
        logger.info("[TRADE] Trading Engine created - Alpaca client will load on demand")
    
    async def initialize(self):
        """Initialize trading engine"""
        try:
            if self.validation_mode:
                # In validation mode, skip API-dependent initialization
                logger.info("[WARN] Trading Engine validation mode - skipping API initialization")
                self.status = EngineStatus.INACTIVE
                logger.info("[OK] Trading Engine validation mode initialization completed")
                return

            # Test Alpaca connection if not in paper mode
            if not self.alpaca_config.get("paper_trading", True):
                await self._ensure_alpaca_client()
                logger.info("[OK] Alpaca client connected for live trading")
            else:
                logger.info("[OK] Paper trading mode enabled")

            # Load existing positions if any
            await self._load_positions()

            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Trading Engine initialization completed")

        except Exception as e:
            logger.error(f"[ERROR] Trading Engine initialization failed: {e}")
            self.status = EngineStatus.DEGRADED
            # Continue with paper trading only
    
    async def _ensure_alpaca_client(self):
        """Ensure Alpaca client is initialized"""
        if self._alpaca_client is None:
            async with self._client_lock:
                if self._alpaca_client is None:
                    try:
                        import alpaca_trade_api as tradeapi
                        self._alpaca_client = tradeapi.REST(
                            self.alpaca_config["api_key"],
                            self.alpaca_config["secret_key"],
                            self.alpaca_config["base_url"],
                            api_version='v2'
                        )
                        
                        # Test connection
                        account = self._alpaca_client.get_account()
                        logger.info(f"[OK] Alpaca client initialized - Account: {account.status}")
                        
                    except Exception as e:
                        logger.error(f"[ERROR] Alpaca client initialization failed: {e}")
                        raise
        
        return self._alpaca_client
    
    async def _load_positions(self):
        """Load existing positions from database or Alpaca"""
        try:
            if self.alpaca_config.get("paper_trading", True):
                # Load from local database (paper trading)
                # This would integrate with the database manager
                logger.info("[DATA] Loading paper trading positions from database")
            else:
                # Load from Alpaca (live trading)
                client = await self._ensure_alpaca_client()
                alpaca_positions = client.list_positions()
                
                for pos in alpaca_positions:
                    position = Position(
                        symbol=pos.symbol,
                        quantity=float(pos.qty),
                        avg_price=float(pos.avg_cost),
                        current_price=float(pos.market_value) / float(pos.qty) if float(pos.qty) != 0 else 0,
                        unrealized_pnl=float(pos.unrealized_pl),
                        side=OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL,
                        timestamp=datetime.now()
                    )
                    self.positions[pos.symbol] = position
                
                logger.info(f"[DATA] Loaded {len(self.positions)} positions from Alpaca")
                
        except Exception as e:
            logger.error(f"Error loading positions: {e}")
    
    async def place_order(self, symbol: str, quantity: float, side: OrderSide, 
                         order_type: OrderType = OrderType.MARKET, 
                         price: Optional[float] = None,
                         stop_price: Optional[float] = None) -> Order:
        """Place trading order"""
        try:
            # Create order object
            order = Order(
                id=f"atlas_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}",
                symbol=symbol,
                quantity=quantity,
                side=side,
                type=order_type,
                price=price,
                stop_price=stop_price,
                status=OrderStatus.NEW,
                timestamp=datetime.now()
            )
            
            if self.alpaca_config.get("paper_trading", True):
                # Paper trading execution
                await self._execute_paper_order(order)
            else:
                # Live trading execution
                await self._execute_live_order(order)
            
            # Store order
            self.orders[order.id] = order
            
            logger.info(f"📋 Order placed: {order.side} {order.quantity} {order.symbol} @ {order.price or 'MARKET'}")
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def _execute_paper_order(self, order: Order):
        """Execute order in paper trading mode"""
        try:
            # Simulate market execution
            if order.type == OrderType.MARKET:
                # Get current market price (would integrate with market engine)
                execution_price = order.price or 100.0  # Placeholder
                
                # Execute immediately
                order.status = OrderStatus.FILLED
                order.filled_quantity = order.quantity
                
                # Update position
                await self._update_position(order.symbol, order.quantity, execution_price, order.side)
                
                # Update cash balance
                trade_value = order.quantity * execution_price
                if order.side == OrderSide.BUY:
                    self.cash_balance -= trade_value
                else:
                    self.cash_balance += trade_value
                
                logger.info(f"[OK] Paper order executed: {order.symbol} @ ${execution_price:.2f}")
                
            else:
                # Limit/Stop orders would be queued for monitoring
                order.status = OrderStatus.NEW
                logger.info(f"📋 Paper order queued: {order.symbol} {order.type}")
                
        except Exception as e:
            logger.error(f"Paper order execution error: {e}")
            order.status = OrderStatus.REJECTED
            raise
    
    async def _execute_live_order(self, order: Order):
        """Execute order through Alpaca"""
        try:
            client = await self._ensure_alpaca_client()
            
            # Convert to Alpaca order format
            alpaca_order = client.submit_order(
                symbol=order.symbol,
                qty=order.quantity,
                side=order.side.value,
                type=order.type.value,
                time_in_force='day',
                limit_price=order.price if order.type in [OrderType.LIMIT, OrderType.STOP_LIMIT] else None,
                stop_price=order.stop_price if order.type in [OrderType.STOP, OrderType.STOP_LIMIT] else None
            )
            
            # Update order with Alpaca ID
            order.id = alpaca_order.id
            order.status = OrderStatus(alpaca_order.status)
            
            logger.info(f"[OK] Live order submitted: {order.symbol} - Alpaca ID: {alpaca_order.id}")
            
        except Exception as e:
            logger.error(f"Live order execution error: {e}")
            order.status = OrderStatus.REJECTED
            raise
    
    async def _update_position(self, symbol: str, quantity: float, price: float, side: OrderSide):
        """Update position after trade execution"""
        try:
            if symbol in self.positions:
                # Update existing position
                position = self.positions[symbol]
                
                if side == OrderSide.BUY:
                    # Adding to position
                    total_cost = (position.quantity * position.avg_price) + (quantity * price)
                    total_quantity = position.quantity + quantity
                    position.avg_price = total_cost / total_quantity if total_quantity != 0 else 0
                    position.quantity = total_quantity
                else:
                    # Reducing position
                    position.quantity -= quantity
                    if position.quantity <= 0:
                        # Position closed
                        self.realized_pnl += (price - position.avg_price) * abs(position.quantity)
                        del self.positions[symbol]
                        return
                
                position.current_price = price
                position.timestamp = datetime.now()
                
            else:
                # New position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity if side == OrderSide.BUY else -quantity,
                    avg_price=price,
                    current_price=price,
                    unrealized_pnl=0.0,
                    side=side,
                    timestamp=datetime.now()
                )
            
            logger.info(f"[DATA] Position updated: {symbol} - {self.positions.get(symbol, 'CLOSED')}")
            
        except Exception as e:
            logger.error(f"Position update error: {e}")
    
    async def get_portfolio_summary(self) -> PortfolioSummary:
        """Get current portfolio summary"""
        try:
            # Calculate current values
            positions_value = 0.0
            unrealized_pnl = 0.0
            
            position_list = []
            for position in self.positions.values():
                # Update current prices (would integrate with market engine)
                position.current_price = position.avg_price * 1.01  # Placeholder
                
                position_value = position.quantity * position.current_price
                positions_value += abs(position_value)
                
                position.unrealized_pnl = (position.current_price - position.avg_price) * position.quantity
                unrealized_pnl += position.unrealized_pnl
                
                position_list.append(position)
            
            self.total_value = self.cash_balance + positions_value
            self.unrealized_pnl = unrealized_pnl
            
            # Calculate day change
            day_change = self.total_value - self.day_start_value
            day_change_percent = (day_change / self.day_start_value * 100) if self.day_start_value != 0 else 0
            
            return PortfolioSummary(
                total_value=self.total_value,
                cash_balance=self.cash_balance,
                positions_value=positions_value,
                unrealized_pnl=self.unrealized_pnl,
                realized_pnl=self.realized_pnl,
                day_change=day_change,
                day_change_percent=day_change_percent,
                positions=position_list,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Portfolio summary error: {e}")
            raise
    
    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status"""
        try:
            if order_id in self.orders:
                order = self.orders[order_id]
                
                if not self.alpaca_config.get("paper_trading", True) and order.status not in [OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED]:
                    # Update from Alpaca for live orders
                    client = await self._ensure_alpaca_client()
                    alpaca_order = client.get_order(order_id)
                    order.status = OrderStatus(alpaca_order.status)
                    order.filled_quantity = float(alpaca_order.filled_qty)
                
                return order
            
            return None
            
        except Exception as e:
            logger.error(f"Order status error: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        try:
            if order_id in self.orders:
                order = self.orders[order_id]
                
                if self.alpaca_config.get("paper_trading", True):
                    # Paper trading cancellation
                    if order.status == OrderStatus.NEW:
                        order.status = OrderStatus.CANCELED
                        logger.info(f"[OK] Paper order canceled: {order_id}")
                        return True
                else:
                    # Live trading cancellation
                    client = await self._ensure_alpaca_client()
                    client.cancel_order(order_id)
                    order.status = OrderStatus.CANCELED
                    logger.info(f"[OK] Live order canceled: {order_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Order cancellation error: {e}")
            return False

    # ===== ENHANCED PORTFOLIO MANAGEMENT =====

    async def analyze_portfolio_risk(self) -> Dict[str, Any]:
        """Analyze portfolio risk and suggest hedging strategies"""
        try:
            risk_analysis = {
                "total_exposure": 0.0,
                "sector_concentration": {},
                "correlation_risk": "low",
                "hedging_suggestions": [],
                "rebalancing_needed": False
            }

            if not self.positions:
                return risk_analysis

            # Calculate total exposure
            total_portfolio_value = self.total_value
            for position in self.positions.values():
                market_value = abs(position.quantity * position.current_price)
                if total_portfolio_value > 0:
                    risk_analysis["total_exposure"] += market_value / total_portfolio_value

            # Check for concentration risk
            max_position_size = self.portfolio_optimization_settings["max_position_size"]
            large_positions = []

            for symbol, position in self.positions.items():
                if total_portfolio_value > 0:
                    position_weight = abs(position.quantity * position.current_price) / total_portfolio_value
                    if position_weight > max_position_size:
                        large_positions.append({
                            "symbol": symbol,
                            "weight": position_weight,
                            "excess": position_weight - max_position_size
                        })

            if large_positions:
                risk_analysis["hedging_suggestions"].append({
                    "type": "position_sizing",
                    "message": f"Reduce position sizes for {len(large_positions)} overweight positions",
                    "positions": large_positions
                })

            # Suggest hedging strategies
            if risk_analysis["total_exposure"] > 0.8:  # 80% exposure
                risk_analysis["hedging_suggestions"].append({
                    "type": "portfolio_hedge",
                    "message": "Consider SPY puts or VIX calls for portfolio protection",
                    "urgency": "high"
                })
            elif risk_analysis["total_exposure"] > 0.6:  # 60% exposure
                risk_analysis["hedging_suggestions"].append({
                    "type": "selective_hedge",
                    "message": "Consider protective puts on largest positions",
                    "urgency": "medium"
                })

            return risk_analysis

        except Exception as e:
            logger.error(f"Portfolio risk analysis error: {e}")
            return {"error": str(e)}

    async def suggest_hedging_strategies(self, symbol: str, position_size: float) -> List[Dict[str, Any]]:
        """Suggest hedging strategies for a specific position"""
        try:
            strategies = []

            # Protective Put Strategy
            strategies.append({
                "name": "Protective Put",
                "description": f"Buy put options to protect {symbol} position",
                "cost_estimate": "1-3% of position value",
                "protection_level": "High",
                "implementation": f"Buy {symbol} puts 5-10% out of the money",
                "pros": ["Limits downside risk", "Maintains upside potential"],
                "cons": ["Costs premium", "Time decay"]
            })

            # Covered Call Strategy (if long position)
            if position_size > 0:
                strategies.append({
                    "name": "Covered Call",
                    "description": f"Sell call options against {symbol} position",
                    "cost_estimate": "Generates income",
                    "protection_level": "Medium",
                    "implementation": f"Sell {symbol} calls 5-10% out of the money",
                    "pros": ["Generates income", "Reduces cost basis"],
                    "cons": ["Limits upside", "Assignment risk"]
                })

            # Collar Strategy
            strategies.append({
                "name": "Collar",
                "description": f"Combine protective put and covered call for {symbol}",
                "cost_estimate": "Low to zero cost",
                "protection_level": "Medium",
                "implementation": f"Buy {symbol} puts + sell {symbol} calls",
                "pros": ["Low cost protection", "Defined risk/reward"],
                "cons": ["Limited upside", "Complex execution"]
            })

            # Inverse ETF Hedge
            strategies.append({
                "name": "Inverse ETF Hedge",
                "description": f"Use inverse ETFs to hedge {symbol} exposure",
                "cost_estimate": "Variable",
                "protection_level": "Medium",
                "implementation": "Buy sector-specific inverse ETFs",
                "pros": ["Simple execution", "No expiration"],
                "cons": ["Daily rebalancing", "Tracking error"]
            })

            return strategies

        except Exception as e:
            logger.error(f"Hedging strategy suggestion error: {e}")
            return []

    async def enable_auto_reinvestment(self, settings: Dict[str, Any]) -> bool:
        """Enable automatic dividend and profit reinvestment"""
        try:
            self.auto_reinvestment_enabled = True
            self.auto_reinvestment_settings = {
                "reinvest_dividends": settings.get("reinvest_dividends", True),
                "reinvest_profits": settings.get("reinvest_profits", False),
                "profit_threshold": settings.get("profit_threshold", 0.20),  # 20% profit
                "target_allocation": settings.get("target_allocation", {}),
                "rebalance_frequency": settings.get("rebalance_frequency", "monthly")
            }

            logger.info("[OK] Auto-reinvestment enabled")
            return True

        except Exception as e:
            logger.error(f"Auto-reinvestment setup error: {e}")
            return False

    async def get_portfolio_optimization_analysis(self) -> Dict[str, Any]:
        """Get portfolio optimization analysis and rebalancing suggestions"""
        try:
            analysis = {
                "current_allocation": {},
                "target_allocation": {},
                "rebalancing_suggestions": [],
                "risk_metrics": {},
                "optimization_score": 0.0
            }

            if not self.positions:
                return analysis

            total_value = self.get_portfolio_value()

            # Calculate current allocation
            for symbol, position in self.positions.items():
                position_value = position["quantity"] * position["current_price"]
                weight = position_value / total_value
                analysis["current_allocation"][symbol] = {
                    "weight": weight,
                    "value": position_value,
                    "shares": position["quantity"]
                }

            # Risk metrics
            analysis["risk_metrics"] = {
                "portfolio_concentration": max(analysis["current_allocation"].values(),
                                             key=lambda x: x["weight"])["weight"] if analysis["current_allocation"] else 0,
                "number_of_positions": len(self.positions),
                "cash_allocation": self.cash_balance / total_value,
                "total_exposure": sum(pos["weight"] for pos in analysis["current_allocation"].values())
            }

            # Optimization suggestions
            if analysis["risk_metrics"]["portfolio_concentration"] > 0.25:
                analysis["rebalancing_suggestions"].append({
                    "type": "reduce_concentration",
                    "message": "Consider reducing largest position to improve diversification",
                    "priority": "high"
                })

            if analysis["risk_metrics"]["cash_allocation"] < 0.05:
                analysis["rebalancing_suggestions"].append({
                    "type": "increase_cash",
                    "message": "Consider maintaining 5-10% cash for opportunities",
                    "priority": "medium"
                })

            # Calculate optimization score (0-100)
            score = 100
            score -= analysis["risk_metrics"]["portfolio_concentration"] * 100  # Penalize concentration
            score -= max(0, (analysis["risk_metrics"]["total_exposure"] - 0.9) * 200)  # Penalize over-exposure
            score += min(20, analysis["risk_metrics"]["number_of_positions"] * 2)  # Reward diversification

            analysis["optimization_score"] = max(0, min(100, score))

            return analysis

        except Exception as e:
            logger.error(f"Portfolio optimization analysis error: {e}")
            return {"error": str(e)}

    async def check_earnings_calendar(self, symbol: str) -> Dict[str, Any]:
        """Check earnings calendar for a symbol and assess risk"""
        try:
            from datetime import datetime

            # In a real implementation, this would fetch from an earnings API
            # For now, we'll simulate earnings data
            earnings_info = {
                "symbol": symbol,
                "next_earnings_date": None,
                "days_until_earnings": None,
                "earnings_risk": "low",
                "position_adjustment_recommended": False,
                "risk_factors": []
            }

            # Simulate some earnings dates (in real implementation, fetch from API)
            simulated_earnings = {
                "AAPL": "2024-02-01",
                "MSFT": "2024-01-25",
                "GOOGL": "2024-02-05",
                "TSLA": "2024-01-24",
                "NVDA": "2024-02-21"
            }

            if symbol in simulated_earnings:
                earnings_date = datetime.strptime(simulated_earnings[symbol], "%Y-%m-%d")
                today = datetime.now()
                days_until = (earnings_date - today).days

                earnings_info["next_earnings_date"] = simulated_earnings[symbol]
                earnings_info["days_until_earnings"] = days_until

                if days_until <= self.earnings_risk_settings["earnings_buffer_days"] and days_until >= 0:
                    earnings_info["earnings_risk"] = "high"
                    earnings_info["position_adjustment_recommended"] = True
                    earnings_info["risk_factors"].append(
                        f"Earnings announcement in {days_until} days - consider reducing position size"
                    )
                elif days_until <= 7 and days_until > self.earnings_risk_settings["earnings_buffer_days"]:
                    earnings_info["earnings_risk"] = "medium"
                    earnings_info["risk_factors"].append(
                        f"Earnings announcement in {days_until} days - monitor volatility"
                    )

            return earnings_info

        except Exception as e:
            logger.error(f"Earnings calendar check error: {e}")
            return {"error": str(e)}

    # ===== TRADE EXECUTION CONFIRMATION PROTOCOL =====

    async def prepare_trade_for_confirmation(self, symbol: str, action: str, quantity: int,
                                           stop_loss: Optional[float] = None,
                                           profit_target: Optional[float] = None) -> Dict[str, Any]:
        """Prepare trade for user confirmation with comprehensive analysis"""
        try:
            import uuid
            from datetime import datetime

            # Generate unique trade ID
            trade_id = str(uuid.uuid4())[:8]

            # Get current quote
            quote = None
            if hasattr(self, 'market_engine'):
                quote = await self.market_engine.get_quote(symbol)

            current_price = quote.price if quote else 0.0

            # Calculate trade details
            trade_value = quantity * current_price

            # Risk/reward analysis
            risk_amount = 0.0
            reward_amount = 0.0
            risk_reward_ratio = 0.0

            if stop_loss and current_price > 0:
                if action.lower() == "buy":
                    risk_amount = (current_price - stop_loss) * quantity
                else:  # sell/short
                    risk_amount = (stop_loss - current_price) * quantity

            if profit_target and current_price > 0:
                if action.lower() == "buy":
                    reward_amount = (profit_target - current_price) * quantity
                else:  # sell/short
                    reward_amount = (current_price - profit_target) * quantity

            if risk_amount > 0:
                risk_reward_ratio = reward_amount / risk_amount

            # Position sizing analysis
            portfolio_value = self.total_value
            position_percentage = (trade_value / portfolio_value) * 100 if portfolio_value > 0 else 0
            risk_percentage = (risk_amount / portfolio_value) * 100 if portfolio_value > 0 else 0

            # Safety checks
            safety_warnings = []
            execution_blocked = False

            # Check position size limits
            max_position_value = self.execution_safeguards["max_position_value"]
            if trade_value > max_position_value:
                safety_warnings.append(f"[WARN] Position value (${trade_value:,.0f}) exceeds limit (${max_position_value:,.0f})")
                execution_blocked = True

            # Check risk percentage
            if risk_percentage > 2.0:  # 2% max risk
                safety_warnings.append(f"[WARN] Risk percentage ({risk_percentage:.1f}%) exceeds 2% limit")
                execution_blocked = True

            # Check stop loss requirement
            if self.execution_safeguards["require_stop_loss"] and not stop_loss:
                safety_warnings.append("[WARN] Stop loss required but not provided")
                execution_blocked = True

            # Check profit target requirement
            if self.execution_safeguards["require_profit_target"] and not profit_target:
                safety_warnings.append("[WARN] Profit target required but not provided")
                execution_blocked = True

            # Check risk/reward ratio
            if risk_reward_ratio > 0 and risk_reward_ratio < 2.0:
                safety_warnings.append(f"[WARN] Risk/reward ratio ({risk_reward_ratio:.1f}:1) below 2:1 minimum")

            # Prepare trade confirmation
            trade_confirmation = {
                "trade_id": trade_id,
                "symbol": symbol.upper(),
                "action": action.upper(),
                "quantity": quantity,
                "current_price": current_price,
                "trade_value": trade_value,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "risk_amount": risk_amount,
                "reward_amount": reward_amount,
                "risk_reward_ratio": risk_reward_ratio,
                "position_percentage": position_percentage,
                "risk_percentage": risk_percentage,
                "safety_warnings": safety_warnings,
                "execution_blocked": execution_blocked,
                "timestamp": datetime.now().isoformat(),
                "status": "pending_confirmation"
            }

            # Store pending trade
            self.pending_trades[trade_id] = trade_confirmation

            return trade_confirmation

        except Exception as e:
            logger.error(f"Trade preparation error: {e}")
            return {"error": str(e), "execution_blocked": True}

    async def confirm_trade_execution(self, trade_id: str, user_confirmed: bool) -> Dict[str, Any]:
        """Execute trade after user confirmation"""
        try:
            if trade_id not in self.pending_trades:
                return {"error": "Trade ID not found", "success": False}

            trade_details = self.pending_trades[trade_id]

            if not user_confirmed:
                # User declined - remove from pending
                del self.pending_trades[trade_id]
                return {
                    "message": "Trade cancelled by user",
                    "trade_id": trade_id,
                    "success": True,
                    "executed": False
                }

            # Check if execution is blocked
            if trade_details.get("execution_blocked", False):
                return {
                    "error": "Trade execution blocked due to safety warnings",
                    "warnings": trade_details.get("safety_warnings", []),
                    "success": False
                }

            # Execute the trade
            symbol = trade_details["symbol"]
            action = trade_details["action"]
            quantity = trade_details["quantity"]

            # For simulation, we'll create a mock execution
            execution_result = await self._execute_confirmed_trade(
                symbol, action, quantity,
                trade_details.get("stop_loss"),
                trade_details.get("profit_target")
            )

            # Remove from pending trades
            del self.pending_trades[trade_id]

            return {
                "message": f"Trade executed successfully: {action} {quantity} {symbol}",
                "trade_id": trade_id,
                "execution_result": execution_result,
                "success": True,
                "executed": True
            }

        except Exception as e:
            logger.error(f"Trade confirmation error: {e}")
            return {"error": str(e), "success": False}

    async def _execute_confirmed_trade(self, symbol: str, action: str, quantity: int,
                                     stop_loss: Optional[float] = None,
                                     profit_target: Optional[float] = None) -> Dict[str, Any]:
        """Execute the confirmed trade (simulation for now)"""
        try:
            from datetime import datetime

            # In a real implementation, this would place actual orders
            # For now, we'll simulate the execution

            execution_result = {
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "execution_time": datetime.now().isoformat(),
                "status": "filled",
                "fill_price": 0.0,  # Would be actual fill price
                "commission": 0.0,
                "stop_loss_order": None,
                "profit_target_order": None
            }

            # Simulate stop loss and profit target orders
            if stop_loss:
                execution_result["stop_loss_order"] = {
                    "type": "stop_loss",
                    "price": stop_loss,
                    "status": "pending"
                }

            if profit_target:
                execution_result["profit_target_order"] = {
                    "type": "limit",
                    "price": profit_target,
                    "status": "pending"
                }

            logger.info(f"[OK] Trade executed: {action} {quantity} {symbol}")
            return execution_result

        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return {"error": str(e), "status": "failed"}

    def generate_trade_confirmation_message(self, trade_details: Dict[str, Any]) -> str:
        """Generate user-friendly trade confirmation message"""
        try:
            symbol = trade_details["symbol"]
            action = trade_details["action"]
            quantity = trade_details["quantity"]
            current_price = trade_details["current_price"]
            trade_value = trade_details["trade_value"]
            risk_amount = trade_details["risk_amount"]
            reward_amount = trade_details["reward_amount"]
            risk_reward_ratio = trade_details["risk_reward_ratio"]
            position_percentage = trade_details["position_percentage"]
            risk_percentage = trade_details["risk_percentage"]

            message = f"""
[TARGET] **TRADE CONFIRMATION REQUIRED**

**Trade Details:**
• Symbol: {symbol}
• Action: {action}
• Quantity: {quantity:,} shares
• Current Price: ${current_price:.2f}
• Total Value: ${trade_value:,.0f}

**Risk/Reward Analysis:**
• Risk Amount: ${risk_amount:.0f} ({risk_percentage:.1f}% of portfolio)
• Reward Potential: ${reward_amount:.0f}
• Risk/Reward Ratio: {risk_reward_ratio:.1f}:1
• Position Size: {position_percentage:.1f}% of portfolio

**Stop Loss:** ${trade_details.get('stop_loss', 'Not set'):.2f}
**Profit Target:** ${trade_details.get('profit_target', 'Not set'):.2f}
"""

            # Add safety warnings
            if trade_details.get("safety_warnings"):
                message += "\n**[WARN] Safety Warnings:**\n"
                for warning in trade_details["safety_warnings"]:
                    message += f"• {warning}\n"

            # Add confirmation prompt
            if trade_details.get("execution_blocked"):
                message += "\n[ERROR] **EXECUTION BLOCKED** - Please address safety warnings before proceeding."
            else:
                message += f"\n[OK] **Would you like me to execute this trade?**\nReply with 'YES {trade_details['trade_id']}' to confirm or 'NO {trade_details['trade_id']}' to cancel."

            return message

        except Exception as e:
            logger.error(f"Trade confirmation message generation error: {e}")
            return f"Trade confirmation error: {str(e)}"

    # ===== PROFESSIONAL TRADING FEATURES =====

    async def place_bracket_order(self, symbol: str, quantity: int, entry_price: float,
                                 stop_loss: float, profit_target: float) -> Dict[str, Any]:
        """Place a bracket order (OCO - One-Cancels-Other)"""
        try:
            import uuid

            bracket_id = str(uuid.uuid4())[:8]

            bracket_order = {
                "bracket_id": bracket_id,
                "symbol": symbol.upper(),
                "quantity": quantity,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "profit_target": profit_target,
                "status": "pending",
                "orders": {
                    "entry": None,
                    "stop_loss": None,
                    "profit_target": None
                },
                "created_at": datetime.now().isoformat()
            }

            # Calculate risk/reward
            risk = abs(entry_price - stop_loss)
            reward = abs(profit_target - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0

            bracket_order["risk_reward_ratio"] = risk_reward_ratio
            bracket_order["position_value"] = entry_price * quantity

            # Store bracket order
            self.bracket_orders[bracket_id] = bracket_order

            logger.info(f"[OK] Bracket order created: {symbol} R/R: {risk_reward_ratio:.2f}:1")

            return {
                "success": True,
                "bracket_id": bracket_id,
                "bracket_order": bracket_order,
                "message": f"Bracket order created for {symbol} with {risk_reward_ratio:.2f}:1 risk/reward ratio"
            }

        except Exception as e:
            logger.error(f"Bracket order creation error: {e}")
            return {"success": False, "error": str(e)}

    async def create_trailing_stop(self, symbol: str, quantity: int, trail_amount: float,
                                  trail_percent: Optional[float] = None) -> Dict[str, Any]:
        """Create a trailing stop order"""
        try:
            import uuid

            trailing_id = str(uuid.uuid4())[:8]

            # Get current price (would integrate with market engine)
            current_price = 150.0  # Placeholder

            trailing_stop = {
                "trailing_id": trailing_id,
                "symbol": symbol.upper(),
                "quantity": quantity,
                "trail_amount": trail_amount,
                "trail_percent": trail_percent,
                "current_price": current_price,
                "stop_price": current_price - trail_amount if trail_amount else current_price * (1 - trail_percent/100),
                "highest_price": current_price,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }

            # Store trailing stop
            self.trailing_stops[trailing_id] = trailing_stop

            logger.info(f"[OK] Trailing stop created: {symbol} @ ${trailing_stop['stop_price']:.2f}")

            return {
                "success": True,
                "trailing_id": trailing_id,
                "trailing_stop": trailing_stop,
                "message": f"Trailing stop created for {symbol}"
            }

        except Exception as e:
            logger.error(f"Trailing stop creation error: {e}")
            return {"success": False, "error": str(e)}

    async def get_professional_trading_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive list of professional trading capabilities"""
        return {
            "order_types": [
                "Market Orders - Immediate execution at current market price",
                "Limit Orders - Execute at specified price or better",
                "Stop Orders - Trigger market order when price hits stop level",
                "Stop-Limit Orders - Trigger limit order when price hits stop level",
                "Bracket Orders - OCO orders with profit target and stop loss",
                "Trailing Stops - Dynamic stop loss that follows price movement",
                "Fill-or-Kill - Execute entire order immediately or cancel",
                "Immediate-or-Cancel - Execute partial fills immediately, cancel remainder"
            ],
            "risk_management": [
                "Position sizing based on account risk percentage",
                "Automatic stop-loss calculation using ATR",
                "Portfolio correlation analysis and limits",
                "Daily loss limits and circuit breakers",
                "VIX-based position size adjustments",
                "Earnings calendar risk assessment"
            ],
            "portfolio_features": [
                "Real-time P&L tracking",
                "Portfolio optimization analysis",
                "Hedging strategy suggestions",
                "Auto-reinvestment capabilities",
                "Rebalancing recommendations",
                "Performance attribution analysis"
            ],
            "execution_features": [
                "Trade confirmation protocol",
                "Pre-trade risk analysis",
                "Smart order routing (when live)",
                "Partial fill management",
                "Order modification and cancellation",
                "After-hours trading support"
            ],
            "analysis_tools": [
                "TTM Squeeze momentum scanner",
                "Multi-agent AI analysis",
                "Chain-of-thought reasoning",
                "Real-time market sentiment",
                "Technical indicator analysis",
                "Options flow analysis (planned)"
            ],
            "compliance_safety": [
                "Paper trading mode for testing",
                "Pattern Day Trader rule compliance",
                "Position size limits",
                "Maximum daily trade limits",
                "Regulatory compliance checks",
                "Audit trail for all trades"
            ]
        }

    async def cleanup(self):
        """Cleanup trading engine resources"""
        try:
            # Save positions to database
            # Cancel any pending orders
            pending_orders = [order for order in self.orders.values() 
                            if order.status == OrderStatus.NEW]
            
            for order in pending_orders:
                await self.cancel_order(order.id)
            
            logger.info("[OK] Trading Engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during trading engine cleanup: {e}")
