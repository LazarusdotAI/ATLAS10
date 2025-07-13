"""
A.T.L.A.S Unified System Access Layer - Predicto's Gateway to All System Capabilities
Natural language interface to all 25+ A.T.L.A.S features through intelligent routing
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Callable
import re

from config import settings
from models import (
    AIResponse, EngineStatus, PredictoForecast
)

logger = logging.getLogger(__name__)


class UnifiedSystemAccessLayer:
    """
    Predicto's unified access layer to all A.T.L.A.S system capabilities
    Provides natural language interface to 25+ advanced features
    """

    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        
        # Feature access registry
        self.feature_registry = {}
        self.capability_map = {}
        self.access_patterns = {}
        
        # Initialize feature mappings
        self._initialize_feature_registry()
        self._initialize_capability_mappings()
        self._initialize_access_patterns()
        
        logger.info("[WEB] Unified System Access Layer created")

    def _initialize_feature_registry(self):
        """Initialize registry of all A.T.L.A.S features"""
        self.feature_registry = {
            # Core AI & ML Capabilities (1-3)
            "sentiment_analysis": {
                "description": "Multi-source sentiment analysis with DistilBERT",
                "access_method": "analyze_sentiment",
                "requires": ["symbol"],
                "engine": "sentiment_analyzer"
            },
            "lstm_prediction": {
                "description": "LSTM neural network price predictions",
                "access_method": "predict_price",
                "requires": ["symbol"],
                "engine": "ml_predictor"
            },
            "conversational_ai": {
                "description": "Advanced conversational intelligence",
                "access_method": "process_conversation",
                "requires": ["message"],
                "engine": "ai_engine"
            },
            
            # Market Analysis & Scanning (4-6)
            "ttm_squeeze_detection": {
                "description": "Advanced TTM Squeeze pattern detection",
                "access_method": "scan_ttm_squeeze",
                "requires": [],
                "engine": "market_engine"
            },
            "market_scanner": {
                "description": "Real-time market opportunity scanner",
                "access_method": "scan_market",
                "requires": [],
                "engine": "realtime_scanner"
            },
            "market_context": {
                "description": "Market regime and context intelligence",
                "access_method": "get_market_context",
                "requires": [],
                "engine": "market_context_engine"
            },
            
            # Options Trading (7-8)
            "options_analysis": {
                "description": "Options Greeks and strategy analysis",
                "access_method": "analyze_options",
                "requires": ["symbol"],
                "engine": "options_engine"
            },
            "options_flow": {
                "description": "Unusual options activity detection",
                "access_method": "analyze_flow",
                "requires": ["symbol"],
                "engine": "options_flow_analyzer"
            },
            
            # Portfolio Management (9-10)
            "portfolio_optimization": {
                "description": "Deep learning portfolio optimization",
                "access_method": "optimize_portfolio",
                "requires": ["portfolio_data"],
                "engine": "portfolio_optimizer"
            },
            "risk_management": {
                "description": "Comprehensive risk assessment",
                "access_method": "assess_risk",
                "requires": ["symbol", "position_size"],
                "engine": "risk_engine"
            },
            
            # Proactive Assistant (11-12)
            "morning_briefing": {
                "description": "Daily market briefing and analysis",
                "access_method": "generate_briefing",
                "requires": [],
                "engine": "proactive_assistant"
            },
            "alert_system": {
                "description": "Real-time opportunity alerts",
                "access_method": "setup_alerts",
                "requires": ["criteria"],
                "engine": "proactive_assistant"
            },
            
            # Educational System (13-15)
            "trading_education": {
                "description": "Educational content from 5 trading books",
                "access_method": "get_education",
                "requires": ["query"],
                "engine": "education_engine"
            },
            "concept_explanation": {
                "description": "Trading concept explanations",
                "access_method": "explain_concept",
                "requires": ["concept"],
                "engine": "education_engine"
            },
            "learning_progress": {
                "description": "Track learning progress and suggestions",
                "access_method": "track_progress",
                "requires": ["user_id"],
                "engine": "education_engine"
            },
            
            # Advanced Analytics (16-20)
            "predicto_forecast": {
                "description": "Predicto AI price forecasting",
                "access_method": "get_forecast",
                "requires": ["symbol"],
                "engine": "market_engine"
            },
            "web_search": {
                "description": "Market news and web search integration",
                "access_method": "search_market_context",
                "requires": ["query"],
                "engine": "market_engine"
            },
            "performance_monitoring": {
                "description": "System performance optimization",
                "access_method": "get_performance_metrics",
                "requires": [],
                "engine": "performance_optimizer"
            },
            "database_management": {
                "description": "Multi-database architecture access",
                "access_method": "query_database",
                "requires": ["query_type"],
                "engine": "database_manager"
            },
            "compliance_tracking": {
                "description": "Trading compliance and audit trails",
                "access_method": "check_compliance",
                "requires": ["action"],
                "engine": "database_manager"
            },
            
            # Trading Operations (21-25)
            "paper_trading": {
                "description": "Educational paper trading execution",
                "access_method": "execute_trade",
                "requires": ["symbol", "action", "quantity"],
                "engine": "trading_engine"
            },
            "position_tracking": {
                "description": "Real-time position monitoring",
                "access_method": "get_positions",
                "requires": [],
                "engine": "trading_engine"
            },
            "order_management": {
                "description": "Smart order routing and management",
                "access_method": "manage_orders",
                "requires": ["order_data"],
                "engine": "trading_engine"
            },
            "backtesting": {
                "description": "Strategy backtesting and validation",
                "access_method": "backtest_strategy",
                "requires": ["strategy", "timeframe"],
                "engine": "trading_engine"
            },
            "real_time_quotes": {
                "description": "Live market data and quotes",
                "access_method": "get_quote",
                "requires": ["symbol"],
                "engine": "market_engine"
            }
        }

    def _initialize_capability_mappings(self):
        """Initialize natural language to capability mappings"""
        self.capability_map = {
            # Analysis keywords
            "analyze": ["sentiment_analysis", "options_analysis", "market_context"],
            "analysis": ["sentiment_analysis", "options_analysis", "market_context"],
            "sentiment": ["sentiment_analysis"],
            "feeling": ["sentiment_analysis"],
            "mood": ["sentiment_analysis"],
            
            # Prediction keywords
            "predict": ["lstm_prediction", "predicto_forecast"],
            "prediction": ["lstm_prediction", "predicto_forecast"],
            "forecast": ["predicto_forecast", "lstm_prediction"],
            "future": ["lstm_prediction", "predicto_forecast"],
            "outlook": ["predicto_forecast", "market_context"],
            
            # Scanning keywords
            "scan": ["ttm_squeeze_detection", "market_scanner"],
            "find": ["market_scanner", "ttm_squeeze_detection"],
            "search": ["web_search", "market_scanner"],
            "opportunities": ["market_scanner", "ttm_squeeze_detection"],
            "signals": ["ttm_squeeze_detection", "market_scanner"],
            
            # Options keywords
            "options": ["options_analysis", "options_flow"],
            "greeks": ["options_analysis"],
            "strategy": ["options_analysis", "portfolio_optimization"],
            "hedge": ["options_analysis", "risk_management"],
            "flow": ["options_flow"],
            
            # Portfolio keywords
            "portfolio": ["portfolio_optimization", "position_tracking"],
            "optimize": ["portfolio_optimization"],
            "allocation": ["portfolio_optimization"],
            "diversify": ["portfolio_optimization"],
            "positions": ["position_tracking"],
            
            # Risk keywords
            "risk": ["risk_management"],
            "safety": ["risk_management"],
            "protect": ["risk_management"],
            "stop": ["risk_management"],
            
            # Education keywords
            "learn": ["trading_education", "concept_explanation"],
            "teach": ["trading_education", "concept_explanation"],
            "explain": ["concept_explanation"],
            "education": ["trading_education"],
            "book": ["trading_education"],
            
            # Trading keywords
            "trade": ["paper_trading", "order_management"],
            "buy": ["paper_trading", "order_management"],
            "sell": ["paper_trading", "order_management"],
            "order": ["order_management"],
            "execute": ["paper_trading"],
            
            # Market data keywords
            "quote": ["real_time_quotes"],
            "price": ["real_time_quotes", "lstm_prediction"],
            "data": ["real_time_quotes", "market_context"],
            
            # Alert keywords
            "alert": ["alert_system"],
            "notify": ["alert_system"],
            "watch": ["alert_system", "position_tracking"],
            
            # News and research keywords
            "news": ["web_search", "sentiment_analysis"],
            "research": ["web_search", "trading_education"],
            "briefing": ["morning_briefing"],
            "summary": ["morning_briefing", "market_context"]
        }

    def _initialize_access_patterns(self):
        """Initialize regex patterns for natural language access"""
        self.access_patterns = {
            # Stock analysis patterns
            r"analyze\s+([A-Z]{1,5})": "sentiment_analysis",
            r"what.*([A-Z]{1,5}).*looking": "sentiment_analysis",
            r"([A-Z]{1,5})\s+analysis": "sentiment_analysis",
            
            # Prediction patterns
            r"predict\s+([A-Z]{1,5})": "lstm_prediction",
            r"forecast.*([A-Z]{1,5})": "predicto_forecast",
            r"where.*([A-Z]{1,5}).*going": "lstm_prediction",
            
            # Scanning patterns
            r"scan.*squeeze": "ttm_squeeze_detection",
            r"find.*opportunities": "market_scanner",
            r"search.*signals": "market_scanner",
            
            # Options patterns
            r"([A-Z]{1,5}).*options": "options_analysis",
            r"options.*([A-Z]{1,5})": "options_analysis",
            r"greeks.*([A-Z]{1,5})": "options_analysis",
            
            # Portfolio patterns
            r"optimize.*portfolio": "portfolio_optimization",
            r"portfolio.*optimization": "portfolio_optimization",
            r"my.*positions": "position_tracking",
            
            # Educational patterns
            r"explain.*([a-zA-Z\s]+)": "concept_explanation",
            r"teach.*([a-zA-Z\s]+)": "trading_education",
            r"learn.*([a-zA-Z\s]+)": "trading_education",
            
            # Trading patterns
            r"buy\s+([A-Z]{1,5})": "paper_trading",
            r"sell\s+([A-Z]{1,5})": "paper_trading",
            r"trade\s+([A-Z]{1,5})": "paper_trading"
        }

    async def initialize(self):
        """Initialize the unified access layer"""
        try:
            self.status = EngineStatus.INITIALIZING
            
            logger.info(f"[WEB] Initializing access to {len(self.feature_registry)} A.T.L.A.S features")
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Unified System Access Layer fully initialized")
            
        except Exception as e:
            logger.error(f"Unified Access Layer initialization failed: {e}")
            self.status = EngineStatus.FAILED
            raise

    async def route_natural_language_request(self, message: str, orchestrator) -> Dict[str, Any]:
        """
        Route natural language request to appropriate system capabilities
        This is the main entry point for Predicto's system access
        """
        try:
            logger.info(f"[TARGET] Routing request: {message[:100]}...")
            
            # Parse the request to identify required capabilities
            required_capabilities = await self._parse_request_capabilities(message)
            
            # Extract parameters from the message
            parameters = await self._extract_parameters(message)
            
            # Execute the required capabilities
            results = await self._execute_capabilities(required_capabilities, parameters, orchestrator)
            
            return {
                "message": message,
                "capabilities_used": required_capabilities,
                "parameters": parameters,
                "results": results,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            return {
                "message": message,
                "error": str(e),
                "timestamp": datetime.now()
            }

    async def _parse_request_capabilities(self, message: str) -> List[str]:
        """Parse message to identify required capabilities"""
        capabilities = set()
        message_lower = message.lower()
        
        # Check keyword mappings
        for keyword, mapped_capabilities in self.capability_map.items():
            if keyword in message_lower:
                capabilities.update(mapped_capabilities)
        
        # Check regex patterns
        for pattern, capability in self.access_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                capabilities.add(capability)
        
        # Default to conversational AI if no specific capabilities identified
        if not capabilities:
            capabilities.add("conversational_ai")
        
        return list(capabilities)[:5]  # Limit to 5 capabilities for performance

    async def _extract_parameters(self, message: str) -> Dict[str, Any]:
        """Extract parameters from natural language message"""
        parameters = {}
        
        # Extract stock symbols
        symbols = re.findall(r'\b([A-Z]{1,5})\b', message)
        if symbols:
            # Filter out common words
            common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT'}
            symbols = [s for s in symbols if s not in common_words]
            if symbols:
                parameters["symbol"] = symbols[0]  # Use first symbol
                parameters["symbols"] = symbols[:3]  # Up to 3 symbols
        
        # Extract quantities
        quantities = re.findall(r'\b(\d+)\s*shares?\b', message, re.IGNORECASE)
        if quantities:
            parameters["quantity"] = int(quantities[0])
        
        # Extract actions
        if any(word in message.lower() for word in ["buy", "purchase", "long"]):
            parameters["action"] = "buy"
        elif any(word in message.lower() for word in ["sell", "short", "exit"]):
            parameters["action"] = "sell"
        
        # Extract timeframes
        if any(word in message.lower() for word in ["daily", "day", "1d"]):
            parameters["timeframe"] = "1day"
        elif any(word in message.lower() for word in ["hourly", "hour", "1h"]):
            parameters["timeframe"] = "1hour"
        elif any(word in message.lower() for word in ["minute", "5m", "5min"]):
            parameters["timeframe"] = "5min"
        
        # Extract query for educational requests
        if any(word in message.lower() for word in ["explain", "teach", "learn"]):
            # Extract the concept to explain
            explain_patterns = [
                r"explain\s+(.+?)(?:\?|$)",
                r"teach.*about\s+(.+?)(?:\?|$)",
                r"learn.*about\s+(.+?)(?:\?|$)"
            ]
            for pattern in explain_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    parameters["query"] = match.group(1).strip()
                    break
        
        return parameters

    async def _execute_capabilities(self, capabilities: List[str], parameters: Dict[str, Any],
                                  orchestrator) -> Dict[str, Any]:
        """Execute the identified capabilities"""
        results = {}

        for capability in capabilities:
            try:
                if capability in self.feature_registry:
                    feature_info = self.feature_registry[capability]
                    result = await self._execute_single_capability(capability, feature_info, parameters, orchestrator)
                    results[capability] = result
                else:
                    results[capability] = {"error": f"Unknown capability: {capability}"}

            except Exception as e:
                logger.error(f"Error executing {capability}: {e}")
                results[capability] = {"error": str(e)}

        return results

    async def _execute_single_capability(self, capability: str, feature_info: Dict[str, Any],
                                       parameters: Dict[str, Any], orchestrator) -> Dict[str, Any]:
        """Execute a single capability"""
        try:
            engine_name = feature_info["engine"]
            access_method = feature_info["access_method"]
            required_params = feature_info["requires"]

            # Check if orchestrator has the required engine
            if not orchestrator:
                return {"error": "Orchestrator not available"}

            # Get the engine
            engine = await self._get_engine(engine_name, orchestrator)
            if not engine:
                return {"error": f"Engine {engine_name} not available"}

            # Validate required parameters
            missing_params = [param for param in required_params if param not in parameters]
            if missing_params and capability != "conversational_ai":
                return {"error": f"Missing required parameters: {missing_params}"}

            # Execute the capability
            return await self._call_engine_method(engine, access_method, parameters, capability)

        except Exception as e:
            logger.error(f"Error executing capability {capability}: {e}")
            return {"error": str(e)}

    async def _get_engine(self, engine_name: str, orchestrator) -> Optional[Any]:
        """Get the specified engine from orchestrator"""
        try:
            if engine_name == "sentiment_analyzer":
                return getattr(orchestrator, 'sentiment_analyzer', None)
            elif engine_name == "ml_predictor":
                return getattr(orchestrator, 'ml_predictor', None)
            elif engine_name == "ai_engine":
                return await orchestrator._ensure_ai_engine() if hasattr(orchestrator, '_ensure_ai_engine') else None
            elif engine_name == "market_engine":
                return getattr(orchestrator, 'market_engine', None)
            elif engine_name == "realtime_scanner":
                return await orchestrator.realtime_scanner if hasattr(orchestrator, 'realtime_scanner') else None
            elif engine_name == "options_engine":
                return getattr(orchestrator, 'options_engine', None)
            elif engine_name == "options_flow_analyzer":
                return getattr(orchestrator, 'options_flow_analyzer', None)
            elif engine_name == "portfolio_optimizer":
                return getattr(orchestrator, 'portfolio_optimizer', None)
            elif engine_name == "risk_engine":
                return getattr(orchestrator, 'risk_engine', None)
            elif engine_name == "proactive_assistant":
                return getattr(orchestrator, 'proactive_assistant', None)
            elif engine_name == "education_engine":
                return getattr(orchestrator, 'education_engine', None)
            elif engine_name == "trading_engine":
                return getattr(orchestrator, 'trading_engine', None)
            elif engine_name == "database_manager":
                return getattr(orchestrator, 'database_manager', None)
            elif engine_name == "performance_optimizer":
                return getattr(orchestrator, 'performance_optimizer', None)
            elif engine_name == "market_context_engine":
                return getattr(orchestrator, 'market_context_engine', None)
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting engine {engine_name}: {e}")
            return None

    async def _call_engine_method(self, engine: Any, method_name: str, parameters: Dict[str, Any],
                                capability: str) -> Dict[str, Any]:
        """Call the specified method on the engine"""
        try:
            # Handle different capability types with appropriate method calls
            if capability == "sentiment_analysis":
                if hasattr(engine, 'analyze_symbol_sentiment') and "symbol" in parameters:
                    result = await engine.analyze_symbol_sentiment(parameters["symbol"])
                    return {"sentiment_result": result}

            elif capability == "lstm_prediction":
                if hasattr(engine, 'predict_returns') and "symbol" in parameters:
                    timeframe = parameters.get("timeframe", "5min")
                    result = await engine.predict_returns(parameters["symbol"], timeframe)
                    return {"prediction_result": result}

            elif capability == "ttm_squeeze_detection":
                if hasattr(engine, 'scan_market'):
                    strength = parameters.get("strength", "moderate")
                    result = await engine.scan_market(strength)
                    return {"ttm_signals": result}

            elif capability == "market_scanner":
                if hasattr(engine, 'scan_opportunities'):
                    result = await engine.scan_opportunities()
                    return {"opportunities": result}

            elif capability == "options_analysis":
                if hasattr(engine, 'analyze_options') and "symbol" in parameters:
                    result = await engine.analyze_options(parameters["symbol"])
                    return {"options_analysis": result}

            elif capability == "portfolio_optimization":
                if hasattr(engine, 'optimize_portfolio'):
                    portfolio_data = parameters.get("portfolio_data", {})
                    result = await engine.optimize_portfolio(portfolio_data)
                    return {"optimization_result": result}

            elif capability == "risk_management":
                if hasattr(engine, 'assess_risk') and "symbol" in parameters:
                    position_size = parameters.get("position_size", 100)
                    result = await engine.assess_risk(parameters["symbol"], position_size)
                    return {"risk_assessment": result}

            elif capability == "trading_education":
                if hasattr(engine, 'process_query'):
                    query = parameters.get("query", "general trading")
                    request = {"query": query}
                    result = await engine.process_query(request)
                    return {"education_result": result}

            elif capability == "real_time_quotes":
                if hasattr(engine, 'get_quote') and "symbol" in parameters:
                    result = await engine.get_quote(parameters["symbol"])
                    return {"quote": result}

            elif capability == "predicto_forecast":
                if hasattr(engine, 'get_predicto_forecast') and "symbol" in parameters:
                    days = parameters.get("days", 5)
                    result = await engine.get_predicto_forecast(parameters["symbol"], days)
                    return {"forecast": result}

            elif capability == "web_search":
                if hasattr(engine, 'search_market_context'):
                    query = parameters.get("query", "market news")
                    result = await engine.search_market_context(query, "news")
                    return {"search_result": result}

            elif capability == "paper_trading":
                if hasattr(engine, 'execute_trade'):
                    symbol = parameters.get("symbol")
                    action = parameters.get("action", "buy")
                    quantity = parameters.get("quantity", 100)
                    if symbol:
                        result = await engine.execute_trade(symbol, action, quantity)
                        return {"trade_result": result}

            elif capability == "position_tracking":
                if hasattr(engine, 'get_positions'):
                    result = await engine.get_positions()
                    return {"positions": result}

            # Default: try to call the method directly
            if hasattr(engine, method_name):
                method = getattr(engine, method_name)
                if callable(method):
                    result = await method(**parameters)
                    return {"result": result}

            return {"error": f"Method {method_name} not found on engine"}

        except Exception as e:
            logger.error(f"Error calling engine method {method_name}: {e}")
            return {"error": str(e)}

    def get_available_capabilities(self) -> Dict[str, Any]:
        """Get list of all available capabilities"""
        return {
            "total_capabilities": len(self.feature_registry),
            "capabilities": {
                name: {
                    "description": info["description"],
                    "requires": info["requires"]
                }
                for name, info in self.feature_registry.items()
            },
            "natural_language_keywords": list(self.capability_map.keys())
        }

    def get_capability_help(self, capability: str) -> Dict[str, Any]:
        """Get help information for a specific capability"""
        if capability in self.feature_registry:
            info = self.feature_registry[capability]
            return {
                "capability": capability,
                "description": info["description"],
                "required_parameters": info["requires"],
                "engine": info["engine"],
                "access_method": info["access_method"]
            }
        else:
            return {"error": f"Unknown capability: {capability}"}

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Unified System Access Layer...")

        # Clear registries
        self.feature_registry.clear()
        self.capability_map.clear()
        self.access_patterns.clear()

        logger.info("[OK] Unified System Access Layer cleanup completed")

    def get_status(self) -> EngineStatus:
        """Get current status"""
        return self.status
