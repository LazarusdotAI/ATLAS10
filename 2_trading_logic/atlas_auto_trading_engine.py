#!/usr/bin/env python3
"""
A.T.L.A.S. Auto-Trading Engine
Enhanced automated trade execution with user confirmation, position management, and risk controls
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoTradeStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class AutoTradeRequest:
    """Automated trade request with user confirmation requirements"""
    trade_id: str
    symbol: str
    action: str  # 'buy', 'sell', 'buy_to_open', 'sell_to_close'
    quantity: int
    order_type: str  # 'market', 'limit', 'stop'
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    
    # Risk management
    risk_level: RiskLevel = RiskLevel.MEDIUM
    max_loss: float = 0.0
    position_size_percent: float = 0.0
    
    # Confirmation requirements
    requires_confirmation: bool = True
    confirmation_timeout: int = 300  # 5 minutes
    
    # Metadata
    strategy_name: str = ""
    reasoning: str = ""
    confidence: float = 0.0
    created_at: datetime = None
    expires_at: datetime = None
    status: AutoTradeStatus = AutoTradeStatus.PENDING
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.confirmation_timeout)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['risk_level'] = self.risk_level.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data

@dataclass
class PositionManager:
    """Manages open positions and risk"""
    symbol: str
    current_quantity: int
    avg_cost: float
    unrealized_pnl: float
    realized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AtlasAutoTradingEngine:
    """Enhanced auto-trading engine with comprehensive risk management"""
    
    def __init__(self, db_path: str = "atlas_auto_trading.db"):
        self.logger = logger
        self.db_path = db_path
        self.pending_trades: Dict[str, AutoTradeRequest] = {}
        self.positions: Dict[str, PositionManager] = {}
        self.confirmation_callbacks: Dict[str, Callable] = {}
        
        # Risk management settings
        self.max_daily_loss = 1000.0  # $1000 max daily loss
        self.max_position_size = 0.10  # 10% max position size
        self.max_portfolio_risk = 0.20  # 20% max portfolio risk
        
        # Auto-trading settings
        self.auto_trading_enabled = False
        self.require_confirmation = True
        self.paper_trading_mode = True
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for trade tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    order_type TEXT NOT NULL,
                    limit_price REAL,
                    stop_price REAL,
                    risk_level TEXT NOT NULL,
                    max_loss REAL NOT NULL,
                    position_size_percent REAL NOT NULL,
                    requires_confirmation BOOLEAN NOT NULL,
                    strategy_name TEXT,
                    reasoning TEXT,
                    confidence REAL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    executed_at TEXT,
                    execution_price REAL,
                    execution_status TEXT
                )
            ''')
            
            # Create positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT PRIMARY KEY,
                    current_quantity INTEGER NOT NULL,
                    avg_cost REAL NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    realized_pnl REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    trailing_stop REAL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("[BOT] Auto-trading database initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    async def create_auto_trade(self, symbol: str, action: str, quantity: int,
                               strategy_name: str = "", reasoning: str = "",
                               confidence: float = 0.0, **kwargs) -> AutoTradeRequest:
        """Create a new auto-trade request"""
        try:
            trade_id = str(uuid.uuid4())[:8]
            
            # Calculate risk level based on position size and confidence
            risk_level = self._calculate_risk_level(symbol, quantity, confidence)
            
            # Create trade request
            trade_request = AutoTradeRequest(
                trade_id=trade_id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                order_type=kwargs.get('order_type', 'market'),
                limit_price=kwargs.get('limit_price'),
                stop_price=kwargs.get('stop_price'),
                risk_level=risk_level,
                max_loss=kwargs.get('max_loss', 0.0),
                position_size_percent=kwargs.get('position_size_percent', 0.0),
                requires_confirmation=kwargs.get('requires_confirmation', self.require_confirmation),
                strategy_name=strategy_name,
                reasoning=reasoning,
                confidence=confidence
            )
            
            # Store in pending trades
            self.pending_trades[trade_id] = trade_request
            
            # Save to database
            await self._save_trade_to_db(trade_request)
            
            self.logger.info(f"[BOT] Created auto-trade {trade_id}: {action} {quantity} {symbol}")
            
            return trade_request
            
        except Exception as e:
            self.logger.error(f"Error creating auto-trade: {e}")
            raise
    
    async def confirm_trade(self, trade_id: str, user_confirmation: bool = True) -> Dict[str, Any]:
        """Confirm or reject a pending trade"""
        try:
            if trade_id not in self.pending_trades:
                return {"error": f"Trade {trade_id} not found"}
            
            trade = self.pending_trades[trade_id]
            
            # Check if trade has expired
            if datetime.now() > trade.expires_at:
                trade.status = AutoTradeStatus.CANCELLED
                await self._update_trade_status(trade_id, AutoTradeStatus.CANCELLED)
                return {"error": f"Trade {trade_id} has expired"}
            
            if user_confirmation:
                # Execute the trade
                execution_result = await self._execute_trade(trade)
                
                if execution_result["success"]:
                    trade.status = AutoTradeStatus.EXECUTED
                    await self._update_trade_status(trade_id, AutoTradeStatus.EXECUTED)
                    
                    # Update position management
                    await self._update_position(trade, execution_result)
                    
                    self.logger.info(f"[OK] Trade {trade_id} executed successfully")
                    
                    return {
                        "success": True,
                        "trade_id": trade_id,
                        "execution_price": execution_result.get("execution_price"),
                        "message": f"Trade executed: {trade.action} {trade.quantity} {trade.symbol}"
                    }
                else:
                    trade.status = AutoTradeStatus.FAILED
                    await self._update_trade_status(trade_id, AutoTradeStatus.FAILED)
                    
                    return {
                        "success": False,
                        "error": execution_result.get("error", "Execution failed")
                    }
            else:
                # User rejected the trade
                trade.status = AutoTradeStatus.CANCELLED
                await self._update_trade_status(trade_id, AutoTradeStatus.CANCELLED)
                
                self.logger.info(f"[ERROR] Trade {trade_id} cancelled by user")
                
                return {
                    "success": True,
                    "message": f"Trade {trade_id} cancelled"
                }
                
        except Exception as e:
            self.logger.error(f"Error confirming trade {trade_id}: {e}")
            return {"error": str(e)}
    
    async def get_pending_trades(self) -> List[Dict[str, Any]]:
        """Get all pending trades requiring confirmation"""
        pending = []
        current_time = datetime.now()
        
        for trade_id, trade in self.pending_trades.items():
            if trade.status == AutoTradeStatus.PENDING:
                if current_time <= trade.expires_at:
                    pending.append(trade.to_dict())
                else:
                    # Auto-expire old trades
                    trade.status = AutoTradeStatus.CANCELLED
                    await self._update_trade_status(trade_id, AutoTradeStatus.CANCELLED)
        
        return pending
    
    async def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current position management data"""
        return {symbol: position.to_dict() for symbol, position in self.positions.items()}
    
    async def set_stop_loss(self, symbol: str, stop_price: float) -> Dict[str, Any]:
        """Set stop-loss for a position"""
        try:
            if symbol in self.positions:
                self.positions[symbol].stop_loss = stop_price
                await self._update_position_in_db(symbol, self.positions[symbol])
                
                self.logger.info(f"[SHIELD] Stop-loss set for {symbol}: ${stop_price:.2f}")
                
                return {
                    "success": True,
                    "message": f"Stop-loss set for {symbol} at ${stop_price:.2f}"
                }
            else:
                return {"error": f"No position found for {symbol}"}
                
        except Exception as e:
            self.logger.error(f"Error setting stop-loss for {symbol}: {e}")
            return {"error": str(e)}
    
    async def set_take_profit(self, symbol: str, target_price: float) -> Dict[str, Any]:
        """Set take-profit for a position"""
        try:
            if symbol in self.positions:
                self.positions[symbol].take_profit = target_price
                await self._update_position_in_db(symbol, self.positions[symbol])
                
                self.logger.info(f"[TARGET] Take-profit set for {symbol}: ${target_price:.2f}")
                
                return {
                    "success": True,
                    "message": f"Take-profit set for {symbol} at ${target_price:.2f}"
                }
            else:
                return {"error": f"No position found for {symbol}"}
                
        except Exception as e:
            self.logger.error(f"Error setting take-profit for {symbol}: {e}")
            return {"error": str(e)}
    
    def _calculate_risk_level(self, symbol: str, quantity: int, confidence: float) -> RiskLevel:
        """Calculate risk level for a trade"""
        # Base risk from position size (assuming $100 per share average)
        estimated_value = quantity * 100
        portfolio_percent = estimated_value / 100000  # Assume $100k portfolio
        
        # Risk factors
        size_risk = portfolio_percent > 0.05  # >5% position
        confidence_risk = confidence < 0.7  # Low confidence
        
        if portfolio_percent > 0.15 or (size_risk and confidence_risk):
            return RiskLevel.EXTREME
        elif portfolio_percent > 0.10 or size_risk:
            return RiskLevel.HIGH
        elif portfolio_percent > 0.05 or confidence_risk:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _execute_trade(self, trade: AutoTradeRequest) -> Dict[str, Any]:
        """Execute the actual trade (paper trading mode)"""
        try:
            # In paper trading mode, simulate execution
            if self.paper_trading_mode:
                # Simulate market price with small random variation
                import random
                base_price = 150.0  # Simulated price
                execution_price = base_price * (1 + random.uniform(-0.01, 0.01))
                
                self.logger.info(f"[DOC] Paper trade executed: {trade.action} {trade.quantity} {trade.symbol} @ ${execution_price:.2f}")
                
                return {
                    "success": True,
                    "execution_price": execution_price,
                    "execution_time": datetime.now().isoformat(),
                    "order_id": f"PAPER_{trade.trade_id}",
                    "mode": "paper_trading"
                }
            else:
                # Real trading would integrate with broker API (Alpaca, etc.)
                # This is a placeholder for real execution
                return {
                    "success": False,
                    "error": "Real trading not implemented - use paper trading mode"
                }
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_position(self, trade: AutoTradeRequest, execution_result: Dict[str, Any]):
        """Update position management after trade execution"""
        try:
            symbol = trade.symbol
            execution_price = execution_result.get("execution_price", 0.0)
            
            if symbol not in self.positions:
                # New position
                self.positions[symbol] = PositionManager(
                    symbol=symbol,
                    current_quantity=0,
                    avg_cost=0.0,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0
                )
            
            position = self.positions[symbol]
            
            if trade.action in ['buy', 'buy_to_open']:
                # Adding to position
                total_cost = position.current_quantity * position.avg_cost + trade.quantity * execution_price
                total_quantity = position.current_quantity + trade.quantity
                position.avg_cost = total_cost / total_quantity if total_quantity > 0 else 0.0
                position.current_quantity = total_quantity
                
            elif trade.action in ['sell', 'sell_to_close']:
                # Reducing position
                if position.current_quantity >= trade.quantity:
                    # Calculate realized P&L
                    realized_pnl = (execution_price - position.avg_cost) * trade.quantity
                    position.realized_pnl += realized_pnl
                    position.current_quantity -= trade.quantity
                    
                    if position.current_quantity == 0:
                        position.avg_cost = 0.0
            
            # Save updated position
            await self._update_position_in_db(symbol, position)
            
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
    
    async def _save_trade_to_db(self, trade: AutoTradeRequest):
        """Save trade to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO auto_trades (
                    trade_id, symbol, action, quantity, order_type, limit_price, stop_price,
                    risk_level, max_loss, position_size_percent, requires_confirmation,
                    strategy_name, reasoning, confidence, status, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.symbol, trade.action, trade.quantity, trade.order_type,
                trade.limit_price, trade.stop_price, trade.risk_level.value, trade.max_loss,
                trade.position_size_percent, trade.requires_confirmation, trade.strategy_name,
                trade.reasoning, trade.confidence, trade.status.value,
                trade.created_at.isoformat(), trade.expires_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving trade to database: {e}")
    
    async def _update_trade_status(self, trade_id: str, status: AutoTradeStatus):
        """Update trade status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE auto_trades SET status = ? WHERE trade_id = ?
            ''', (status.value, trade_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating trade status: {e}")
    
    async def _update_position_in_db(self, symbol: str, position: PositionManager):
        """Update position in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO positions (
                    symbol, current_quantity, avg_cost, unrealized_pnl, realized_pnl,
                    stop_loss, take_profit, trailing_stop, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, position.current_quantity, position.avg_cost, position.unrealized_pnl,
                position.realized_pnl, position.stop_loss, position.take_profit,
                position.trailing_stop, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating position in database: {e}")

# Test function
async def test_auto_trading():
    """Test the auto-trading engine"""
    engine = AtlasAutoTradingEngine()
    
    print("[BOT] Testing Auto-Trading Engine")
    print("=" * 50)
    
    # Test creating auto-trade
    print("\n1. Creating auto-trade request...")
    trade = await engine.create_auto_trade(
        symbol="AAPL",
        action="buy",
        quantity=10,
        strategy_name="TTM Squeeze Breakout",
        reasoning="Strong momentum breakout with volume confirmation",
        confidence=0.85
    )
    print(f"   Created trade {trade.trade_id}: {trade.action} {trade.quantity} {trade.symbol}")
    print(f"   Risk Level: {trade.risk_level.value}")
    print(f"   Requires Confirmation: {trade.requires_confirmation}")
    
    # Test getting pending trades
    print("\n2. Getting pending trades...")
    pending = await engine.get_pending_trades()
    print(f"   Found {len(pending)} pending trades")
    
    # Test confirming trade
    print("\n3. Confirming trade...")
    result = await engine.confirm_trade(trade.trade_id, user_confirmation=True)
    print(f"   Confirmation result: {result}")
    
    # Test position management
    print("\n4. Testing position management...")
    positions = await engine.get_positions()
    print(f"   Current positions: {len(positions)}")
    
    if "AAPL" in positions:
        stop_result = await engine.set_stop_loss("AAPL", 145.0)
        print(f"   Stop-loss result: {stop_result}")
        
        profit_result = await engine.set_take_profit("AAPL", 160.0)
        print(f"   Take-profit result: {profit_result}")
    
    print("\n[OK] Auto-Trading Engine test complete!")

if __name__ == "__main__":
    asyncio.run(test_auto_trading())
