#!/usr/bin/env python3
"""
A.T.L.A.S. Database Utilities
Consolidated database manager and all database-related utilities
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus, TradingSignal, MarketData, PortfolioPosition

settings = Settings()

class AtlasDatabaseManager:
    """Centralized database management"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.connections = {}
        self.database_paths = {
            'main': 'atlas.db',
            'memory': 'atlas_memory.db',
            'feedback': 'atlas_feedback.db',
            'compliance': 'atlas_compliance.db',
            'rag': 'atlas_rag.db',
            'enhanced_memory': 'atlas_enhanced_memory.db'
        }
        
    async def initialize(self):
        """Initialize all databases"""
        try:
            for db_name, db_path in self.database_paths.items():
                await self._initialize_database(db_name, db_path)
            
            self.status = EngineStatus.ACTIVE
            self.logger.info("Database Manager initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Database Manager initialization failed: {e}")
            raise
    
    async def _initialize_database(self, db_name: str, db_path: str):
        """Initialize individual database"""
        try:
            conn = sqlite3.connect(db_path)
            self.connections[db_name] = conn
            
            if db_name == 'main':
                await self._create_main_tables(conn)
            elif db_name == 'memory':
                await self._create_memory_tables(conn)
            elif db_name == 'feedback':
                await self._create_feedback_tables(conn)
            elif db_name == 'compliance':
                await self._create_compliance_tables(conn)
            elif db_name == 'rag':
                await self._create_rag_tables(conn)
            elif db_name == 'enhanced_memory':
                await self._create_enhanced_memory_tables(conn)
            
            conn.commit()
            self.logger.info(f"Database {db_name} initialized at {db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database {db_name}: {e}")
            raise
    
    async def _create_main_tables(self, conn):
        """Create main database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                reasoning TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                change_amount REAL,
                change_percent REAL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_cost REAL NOT NULL,
                current_price REAL NOT NULL,
                market_value REAL NOT NULL,
                unrealized_pnl REAL NOT NULL,
                unrealized_pnl_percent REAL NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def _create_memory_tables(self, conn):
        """Create memory database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                ai_response TEXT,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                preference_key TEXT,
                preference_value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def _create_feedback_tables(self, conn):
        """Create feedback database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message_id TEXT,
                rating INTEGER,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def _create_compliance_tables(self, conn):
        """Create compliance database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT,
                user_id TEXT,
                details TEXT,
                compliance_status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def _create_rag_tables(self, conn):
        """Create RAG database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT,
                content TEXT,
                embedding BLOB,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def _create_enhanced_memory_tables(self, conn):
        """Create enhanced memory database tables"""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                conversation_data TEXT,
                analysis_results TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def store_trading_signal(self, signal: TradingSignal):
        """Store trading signal in database"""
        try:
            conn = self.connections['main']
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trading_signals 
                (symbol, action, price, quantity, confidence, timestamp, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.symbol, signal.action, signal.price, signal.quantity,
                signal.confidence, signal.timestamp, signal.reasoning
            ))
            
            conn.commit()
            self.logger.info(f"Stored trading signal for {signal.symbol}")
            
        except Exception as e:
            self.logger.error(f"Error storing trading signal: {e}")
    
    async def store_market_data(self, data: MarketData):
        """Store market data in database"""
        try:
            conn = self.connections['main']
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO market_data 
                (symbol, price, volume, change_amount, change_percent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.symbol, data.price, data.volume, data.change,
                data.change_percent, data.timestamp
            ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing market data: {e}")
    
    async def get_recent_signals(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """Get recent trading signals"""
        try:
            conn = self.connections['main']
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute('''
                    SELECT * FROM trading_signals 
                    WHERE symbol = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (symbol, limit))
            else:
                cursor.execute('''
                    SELECT * FROM trading_signals 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting recent signals: {e}")
            return []
    
    async def store_conversation(self, session_id: str, user_message: str, ai_response: str, context: Dict):
        """Store conversation in memory database"""
        try:
            conn = self.connections['memory']
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_memory 
                (session_id, user_message, ai_response, context)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_message, ai_response, json.dumps(context)))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
    
    async def cleanup(self):
        """Cleanup database connections"""
        try:
            for db_name, conn in self.connections.items():
                conn.close()
                self.logger.info(f"Closed database connection: {db_name}")
            
            self.connections.clear()
            self.logger.info("Database manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")
