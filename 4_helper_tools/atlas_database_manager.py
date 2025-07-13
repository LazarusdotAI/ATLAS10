"""
A.T.L.A.S Database Manager - Async SQLite Operations
Centralized database management with connection pooling and async operations
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager

from config import get_database_config, settings

logger = logging.getLogger(__name__)


class AtlasDatabaseManager:
    """
    Centralized database manager with async operations and connection pooling
    """
    
    def __init__(self):
        self.config = get_database_config()
        self.db_path = self.config["url"].replace("sqlite:///", "")
        self.pool_size = self.config["pool_size"]
        self.timeout = self.config["timeout"]

        # Multiple database paths for enhanced features
        self.db_paths = {
            'main': self.db_path,
            'memory': settings.MEMORY_DB_PATH,
            'rag': settings.RAG_DB_PATH,
            'compliance': settings.COMPLIANCE_DB_PATH,
            'feedback': settings.FEEDBACK_DB_PATH,
            'enhanced_memory': settings.ENHANCED_MEMORY_DB_PATH
        }

        # Connection pools for each database
        self._connection_pools = {}
        self._pools_initialized = False
        self._init_lock = asyncio.Lock()

        logger.info(f"Database manager created - main: {self.db_path}, enhanced: {len(self.db_paths)} databases")
    
    async def initialize(self):
        """Initialize all databases and connection pools"""
        async with self._init_lock:
            if not self._pools_initialized:
                try:
                    # Initialize connection pools for each database
                    for db_name, db_path in self.db_paths.items():
                        pool = asyncio.Queue(maxsize=self.pool_size)

                        # Create database schema
                        await self._create_schema(db_name, db_path)

                        # Initialize connection pool
                        for _ in range(self.pool_size):
                            conn = await aiosqlite.connect(db_path, timeout=self.timeout)
                            conn.row_factory = aiosqlite.Row
                            await pool.put(conn)

                        self._connection_pools[db_name] = pool
                        logger.info(f"Database '{db_name}' initialized: {db_path}")

                    self._pools_initialized = True
                    logger.info(f"All {len(self.db_paths)} databases initialized successfully")

                except Exception as e:
                    logger.error(f"Database initialization failed: {e}")
                    raise
    
    @asynccontextmanager
    async def get_connection(self, db_name: str = 'main'):
        """Get database connection from pool"""
        if not self._pools_initialized:
            await self.initialize()

        if db_name not in self._connection_pools:
            raise ValueError(f"Unknown database: {db_name}")

        pool = self._connection_pools[db_name]
        conn = await pool.get()
        try:
            yield conn
        finally:
            await pool.put(conn)
    
    async def _create_schema(self, db_name: str, db_path: str):
        """Create database schema based on database type"""
        if db_name == 'main':
            await self._create_main_schema(db_path)
        elif db_name == 'memory':
            await self._create_memory_schema(db_path)
        elif db_name == 'rag':
            await self._create_rag_schema(db_path)
        elif db_name == 'compliance':
            await self._create_compliance_schema(db_path)
        elif db_name == 'feedback':
            await self._create_feedback_schema(db_path)
        elif db_name == 'enhanced_memory':
            await self._create_enhanced_memory_schema(db_path)

    async def _create_main_schema(self, db_path: str):
        """Create main database schema"""
        schema_sql = """
        -- User sessions and profiles
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Chat history
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            message_type TEXT DEFAULT 'chat',
            confidence REAL DEFAULT 0.8,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
        );

        -- Trading positions
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL,
            side TEXT NOT NULL,
            unrealized_pnl REAL DEFAULT 0.0,
            realized_pnl REAL DEFAULT 0.0,
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Trading orders
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            side TEXT NOT NULL,
            order_type TEXT NOT NULL,
            price REAL,
            stop_price REAL,
            status TEXT DEFAULT 'new',
            filled_quantity REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Market data cache
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT PRIMARY KEY,
            price REAL NOT NULL,
            bid REAL,
            ask REAL,
            volume INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Technical indicators cache
        CREATE TABLE IF NOT EXISTS technical_indicators (
            symbol TEXT PRIMARY KEY,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            macd_histogram REAL,
            sma_20 REAL,
            sma_50 REAL,
            ema_12 REAL,
            ema_26 REAL,
            bollinger_upper REAL,
            bollinger_lower REAL,
            atr REAL,
            volume_sma REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- TTM Squeeze signals
        CREATE TABLE IF NOT EXISTS ttm_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            signal_strength TEXT NOT NULL,
            histogram_value REAL NOT NULL,
            squeeze_active BOOLEAN DEFAULT FALSE,
            momentum_direction TEXT,
            confidence REAL DEFAULT 0.8,
            entry_price REAL,
            stop_loss REAL,
            target_price REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Risk assessments
        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            risk_score REAL NOT NULL,
            position_size REAL NOT NULL,
            stop_loss_price REAL NOT NULL,
            risk_amount REAL NOT NULL,
            risk_percentage REAL NOT NULL,
            confidence_level REAL DEFAULT 0.8,
            risk_factors TEXT,
            recommendations TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- System performance metrics
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_type TEXT DEFAULT 'counter',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Educational content cache
        CREATE TABLE IF NOT EXISTS education_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            topic TEXT,
            difficulty_level TEXT DEFAULT 'beginner',
            book_source TEXT,
            confidence REAL DEFAULT 0.8,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
        CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp);
        CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
        CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
        CREATE INDEX IF NOT EXISTS idx_ttm_signals_symbol ON ttm_signals(symbol);
        CREATE INDEX IF NOT EXISTS idx_ttm_signals_timestamp ON ttm_signals(timestamp);
        CREATE INDEX IF NOT EXISTS idx_risk_assessments_symbol ON risk_assessments(symbol);
        CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp);
        """
        
        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"Main database schema created: {db_path}")

    async def _create_memory_schema(self, db_path: str):
        """Create memory database schema"""
        schema_sql = """
        -- Memory entries for conversation context
        CREATE TABLE IF NOT EXISTS memory_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp TEXT NOT NULL,
            importance_score REAL DEFAULT 0.5
        );

        -- User preferences and learning
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            preference_type TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_memory_session ON memory_entries(session_id);
        CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type);
        CREATE INDEX IF NOT EXISTS idx_memory_importance ON memory_entries(importance_score);
        """

        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"Memory database schema created: {db_path}")

    async def _create_rag_schema(self, db_path: str):
        """Create RAG database schema"""
        schema_sql = """
        -- Educational content and embeddings
        CREATE TABLE IF NOT EXISTS educational_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding BLOB,
            metadata TEXT,
            timestamp TEXT NOT NULL
        );

        -- Trading book content
        CREATE TABLE IF NOT EXISTS trading_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_title TEXT NOT NULL,
            chapter TEXT,
            section TEXT,
            content TEXT NOT NULL,
            embedding BLOB,
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_content_type ON educational_content(content_type);
        CREATE INDEX IF NOT EXISTS idx_book_title ON trading_books(book_title);
        """

        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"RAG database schema created: {db_path}")

    async def _create_compliance_schema(self, db_path: str):
        """Create compliance database schema"""
        schema_sql = """
        -- Compliance monitoring
        CREATE TABLE IF NOT EXISTS compliance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            details TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );

        -- Risk assessments
        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            assessment_type TEXT NOT NULL,
            risk_score REAL NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_compliance_session ON compliance_logs(session_id);
        CREATE INDEX IF NOT EXISTS idx_risk_symbol ON risk_assessments(symbol);
        """

        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"Compliance database schema created: {db_path}")

    async def _create_feedback_schema(self, db_path: str):
        """Create feedback database schema"""
        schema_sql = """
        -- User feedback
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            rating INTEGER,
            comment TEXT,
            timestamp TEXT NOT NULL
        );

        -- System performance feedback
        CREATE TABLE IF NOT EXISTS performance_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            duration REAL NOT NULL,
            error_message TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_feedback_session ON user_feedback(session_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback(feedback_type);
        """

        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"Feedback database schema created: {db_path}")

    async def _create_enhanced_memory_schema(self, db_path: str):
        """Create enhanced memory database schema"""
        schema_sql = """
        -- Enhanced context memory
        CREATE TABLE IF NOT EXISTS context_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            context_type TEXT NOT NULL,
            context_data TEXT NOT NULL,
            emotional_state TEXT,
            confidence_score REAL DEFAULT 0.5,
            timestamp TEXT NOT NULL
        );

        -- Trading goals and progress
        CREATE TABLE IF NOT EXISTS trading_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            goal_type TEXT NOT NULL,
            target_amount REAL,
            timeframe TEXT,
            status TEXT DEFAULT 'active',
            progress REAL DEFAULT 0.0,
            timestamp TEXT NOT NULL
        );

        -- Conversation flow tracking
        CREATE TABLE IF NOT EXISTS conversation_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            flow_state TEXT NOT NULL,
            previous_state TEXT,
            transition_reason TEXT,
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_context_session ON context_memory(session_id);
        CREATE INDEX IF NOT EXISTS idx_goals_session ON trading_goals(session_id);
        CREATE INDEX IF NOT EXISTS idx_flow_session ON conversation_flow(session_id);
        """

        async with aiosqlite.connect(db_path) as conn:
            await conn.executescript(schema_sql)
            await conn.commit()
            logger.info(f"Enhanced memory database schema created: {db_path}")
    
    # Chat and Session Management
    async def save_chat_message(self, session_id: str, message: str, response: str, 
                               message_type: str = "chat", confidence: float = 0.8):
        """Save chat message and response"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO chat_history (session_id, message, response, message_type, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, message, response, message_type, confidence))
            await conn.commit()
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT message, response, message_type, confidence, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def create_session(self, session_id: str, user_profile: str = None):
        """Create new user session"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO user_sessions (session_id, user_profile)
                VALUES (?, ?)
            """, (session_id, user_profile))
            await conn.commit()
    
    # Trading Data Management
    async def save_position(self, symbol: str, quantity: float, avg_price: float, 
                           side: str, current_price: float = None):
        """Save or update trading position"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO positions 
                (symbol, quantity, avg_price, side, current_price, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (symbol, quantity, avg_price, side, current_price))
            await conn.commit()
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT * FROM positions WHERE quantity != 0
                ORDER BY updated_at DESC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def save_order(self, order_data: Dict[str, Any]):
        """Save trading order"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO orders 
                (id, symbol, quantity, side, order_type, price, stop_price, status, filled_quantity, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                order_data.get("id"),
                order_data.get("symbol"),
                order_data.get("quantity"),
                order_data.get("side"),
                order_data.get("type"),
                order_data.get("price"),
                order_data.get("stop_price"),
                order_data.get("status"),
                order_data.get("filled_quantity", 0.0)
            ))
            await conn.commit()
    
    # Market Data Caching
    async def cache_market_data(self, symbol: str, price: float, bid: float = None, 
                               ask: float = None, volume: int = None):
        """Cache market data"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO market_data (symbol, price, bid, ask, volume, timestamp)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (symbol, price, bid, ask, volume))
            await conn.commit()
    
    async def get_cached_quote(self, symbol: str, max_age_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """Get cached market data if recent enough"""
        async with self.get_connection() as conn:
            cursor = await conn.execute("""
                SELECT * FROM market_data 
                WHERE symbol = ? AND timestamp > datetime('now', '-{} seconds')
            """.format(max_age_seconds), (symbol,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def cleanup(self):
        """Cleanup database connections"""
        try:
            # Close all connections in pool
            while not self._connection_pool.empty():
                conn = await self._connection_pool.get()
                await conn.close()
            
            logger.info("Database manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
    
    # Utility methods
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute custom query"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params or ())
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = None):
        """Execute update/insert query"""
        async with self.get_connection() as conn:
            await conn.execute(query, params or ())
            await conn.commit()
