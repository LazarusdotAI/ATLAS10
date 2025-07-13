#!/usr/bin/env python3
"""
A.T.L.A.S. Education Support System
Consolidated education engine, proactive assistant, and compliance
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
from datetime import datetime, timedelta

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus, AIResponse

settings = Settings()

class AtlasEducationEngine:
    """Educational content and trading guidance engine"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.educational_content = self._load_educational_content()
        
    async def initialize(self):
        """Initialize education engine"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Education Engine initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Education Engine initialization failed: {e}")
            raise
    
    def _load_educational_content(self):
        """Load educational content from trading books and resources"""
        return {
            "risk_management": {
                "title": "Risk Management Fundamentals",
                "content": "Risk management is the cornerstone of successful trading. Never risk more than 2% of your account on a single trade.",
                "examples": ["Position sizing", "Stop losses", "Diversification"]
            },
            "technical_analysis": {
                "title": "Technical Analysis Basics",
                "content": "Technical analysis involves studying price charts and patterns to predict future price movements.",
                "examples": ["Support and resistance", "Moving averages", "Chart patterns"]
            },
            "fundamental_analysis": {
                "title": "Fundamental Analysis",
                "content": "Fundamental analysis examines a company's financial health and market position.",
                "examples": ["P/E ratios", "Revenue growth", "Market share"]
            },
            "trading_psychology": {
                "title": "Trading Psychology",
                "content": "Emotional control is crucial for trading success. Fear and greed are the trader's worst enemies.",
                "examples": ["Discipline", "Patience", "Emotional control"]
            }
        }
    
    async def get_educational_content(self, topic: str) -> Dict[str, Any]:
        """Get educational content for specific topic"""
        try:
            if topic.lower() in self.educational_content:
                return self.educational_content[topic.lower()]
            else:
                return {
                    "title": "General Trading Education",
                    "content": "Trading requires continuous learning and practice. Focus on risk management, technical analysis, and emotional control.",
                    "examples": ["Start with paper trading", "Learn from mistakes", "Keep a trading journal"]
                }
        except Exception as e:
            self.logger.error(f"Error getting educational content: {e}")
            return {}
    
    async def generate_learning_plan(self, user_level: str) -> Dict[str, Any]:
        """Generate personalized learning plan"""
        try:
            if user_level.lower() == "beginner":
                return {
                    "level": "Beginner",
                    "duration": "4-6 weeks",
                    "modules": [
                        "Trading Basics",
                        "Risk Management",
                        "Chart Reading",
                        "Paper Trading Practice"
                    ],
                    "goals": "Understand fundamentals and practice with virtual money"
                }
            elif user_level.lower() == "intermediate":
                return {
                    "level": "Intermediate",
                    "duration": "6-8 weeks",
                    "modules": [
                        "Advanced Technical Analysis",
                        "Options Trading",
                        "Portfolio Management",
                        "Market Psychology"
                    ],
                    "goals": "Develop advanced strategies and risk management"
                }
            else:  # Advanced
                return {
                    "level": "Advanced",
                    "duration": "8-12 weeks",
                    "modules": [
                        "Algorithmic Trading",
                        "Derivatives Strategies",
                        "Risk Modeling",
                        "Professional Trading"
                    ],
                    "goals": "Master professional-level trading techniques"
                }
        except Exception as e:
            self.logger.error(f"Error generating learning plan: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup education engine"""
        self.logger.info("Education engine cleanup completed")


class AtlasProactiveAssistant:
    """Proactive trading assistant and alerts"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize proactive assistant"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Proactive Assistant initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Proactive Assistant initialization failed: {e}")
            raise
    
    async def generate_morning_briefing(self) -> Dict[str, Any]:
        """Generate morning market briefing"""
        try:
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "market_outlook": "Markets showing mixed signals with tech leading gains",
                "key_events": [
                    "Fed meeting minutes release at 2 PM",
                    "Earnings reports from major tech companies",
                    "Economic data: unemployment claims"
                ],
                "trading_opportunities": [
                    "AAPL showing bullish momentum",
                    "SPY approaching key resistance",
                    "Gold showing safe-haven demand"
                ],
                "risk_alerts": [
                    "High volatility expected around Fed announcement",
                    "Earnings season creating individual stock risk"
                ]
            }
        except Exception as e:
            self.logger.error(f"Error generating morning briefing: {e}")
            return {}
    
    async def check_portfolio_alerts(self, positions: List[Dict]) -> List[Dict]:
        """Check for portfolio-related alerts"""
        try:
            alerts = []
            
            for position in positions:
                if position.get('unrealized_pnl_percent', 0) < -5:
                    alerts.append({
                        "type": "stop_loss_warning",
                        "symbol": position['symbol'],
                        "message": f"{position['symbol']} down {abs(position['unrealized_pnl_percent']):.1f}%",
                        "severity": "high"
                    })
                
                if position.get('unrealized_pnl_percent', 0) > 10:
                    alerts.append({
                        "type": "profit_taking",
                        "symbol": position['symbol'],
                        "message": f"{position['symbol']} up {position['unrealized_pnl_percent']:.1f}% - consider taking profits",
                        "severity": "medium"
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error checking portfolio alerts: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup proactive assistant"""
        self.logger.info("Proactive assistant cleanup completed")


class AtlasComplianceEngine:
    """Trading compliance and regulatory oversight"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        
    async def initialize(self):
        """Initialize compliance engine"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Compliance Engine initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Compliance Engine initialization failed: {e}")
            raise
    
    async def check_trade_compliance(self, trade_data: Dict) -> Dict[str, Any]:
        """Check trade for compliance violations"""
        try:
            violations = []
            warnings = []
            
            if trade_data.get('position_size', 0) > settings.MAX_POSITION_SIZE:
                violations.append({
                    "type": "position_size_limit",
                    "message": f"Position size exceeds maximum limit of ${settings.MAX_POSITION_SIZE:,.2f}",
                    "severity": "high"
                })
            
            if trade_data.get('risk_percent', 0) > settings.RISK_TOLERANCE * 100:
                warnings.append({
                    "type": "risk_tolerance",
                    "message": f"Trade risk exceeds recommended {settings.RISK_TOLERANCE * 100}% limit",
                    "severity": "medium"
                })
            
            if trade_data.get('day_trades_count', 0) >= 3:
                warnings.append({
                    "type": "pattern_day_trading",
                    "message": "Approaching pattern day trading limits",
                    "severity": "medium"
                })
            
            return {
                "compliant": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking trade compliance: {e}")
            return {"compliant": False, "error": str(e)}
    
    async def log_compliance_event(self, event_data: Dict):
        """Log compliance event"""
        try:
            self.logger.info(f"Compliance event logged: {event_data}")
        except Exception as e:
            self.logger.error(f"Error logging compliance event: {e}")
    
    async def cleanup(self):
        """Cleanup compliance engine"""
        self.logger.info("Compliance engine cleanup completed")
