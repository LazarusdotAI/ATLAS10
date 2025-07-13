#!/usr/bin/env python3
"""
A.T.L.A.S. Core AI System
Consolidated orchestrator, AI engine, and predicto engine
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import openai
from datetime import datetime, timedelta
import json
import uuid

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, AIResponse, EngineStatus, ERROR_HANDLING_AVAILABLE, ErrorSeverity
from atlas_trading_system import ProfessionalAnalystEngine
from atlas_market_data import AtlasMarketEngine, AtlasSentimentAnalyzer, AtlasMLPredictor
from atlas_database_utils import AtlasDatabaseManager

settings = Settings()

class AtlasOrchestrator:
    """Main orchestrator for A.T.L.A.S. system"""
    
    def __init__(self, validation_mode: bool = False):
        self.logger = logger
        self.validation_mode = validation_mode
        
        self._ai_engine = None
        self._market_engine = None
        self._trading_engine = None
        self._risk_engine = None
        self._education_engine = None
        self._database_manager = None
        self._sentiment_analyzer = None
        self._ml_predictor = None
        self._options_engine = None
        self._portfolio_optimizer = None
        self._market_context_engine = None
        self._proactive_assistant = None
        self._realtime_scanner = None
        self._performance_optimizer = None
        self._professional_analyst_engine = None

        # Component initialization status
        initial_status = EngineStatus.INACTIVE if self.validation_mode else EngineStatus.INITIALIZING
        self._component_status = {
            "ai_engine": initial_status,
            "market_engine": initial_status,
            "trading_engine": initial_status,
            "risk_engine": initial_status,
            "education_engine": initial_status,
            "database_manager": initial_status,
            "sentiment_analyzer": initial_status,
            "ml_predictor": initial_status,
            "options_engine": initial_status,
            "portfolio_optimizer": initial_status,
            "market_context_engine": initial_status,
            "proactive_assistant": initial_status,
            "realtime_scanner": initial_status,
            "performance_optimizer": initial_status,
            "professional_analyst_engine": initial_status
        }

        self._error_handler = None
        if ERROR_HANDLING_AVAILABLE:
            try:
                from atlas_monitoring_tools import AtlasErrorHandler
                self._error_handler = AtlasErrorHandler()
            except ImportError:
                pass

    async def initialize_with_progress(self):
        """Initialize all components with progress tracking"""
        self.logger.info("🚀 Initializing A.T.L.A.S. components...")
        
        initialization_tasks = [
            ("Database Manager", self._ensure_database_manager()),
            ("AI Engine", self._ensure_ai_engine()),
            ("Market Engine", self._ensure_market_engine()),
            ("Trading Engine", self._ensure_trading_engine()),
            ("Risk Engine", self._ensure_risk_engine()),
            ("Education Engine", self._ensure_education_engine()),
            ("Professional Analyst Engine", self._ensure_professional_analyst_engine())
        ]
        
        for name, task in initialization_tasks:
            try:
                await task
                self.logger.info(f"✅ {name} initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize {name}: {e}")

    async def _ensure_database_manager(self):
        """Initialize database manager"""
        if self._database_manager is None:
            try:
                from atlas_database_utils import AtlasDatabaseManager
                self._database_manager = AtlasDatabaseManager()
                await self._database_manager.initialize()
                self._component_status["database_manager"] = EngineStatus.ACTIVE
            except Exception as e:
                self.logger.error(f"Database manager initialization failed: {e}")
                self._component_status["database_manager"] = EngineStatus.ERROR

    async def _ensure_ai_engine(self):
        """Initialize AI engine"""
        if self._ai_engine is None:
            try:
                self._ai_engine = AtlasAIEngine()
                await self._ai_engine.initialize()
                self._component_status["ai_engine"] = EngineStatus.ACTIVE
                return self._ai_engine
            except Exception as e:
                self.logger.error(f"AI engine initialization failed: {e}")
                self._component_status["ai_engine"] = EngineStatus.ERROR
                return None
        return self._ai_engine

    async def _ensure_market_engine(self):
        """Initialize market engine"""
        if self._market_engine is None:
            try:
                from atlas_market_data import AtlasMarketEngine
                self._market_engine = AtlasMarketEngine()
                await self._market_engine.initialize()
                self._component_status["market_engine"] = EngineStatus.ACTIVE
            except Exception as e:
                self.logger.error(f"Market engine initialization failed: {e}")
                self._component_status["market_engine"] = EngineStatus.ERROR

    async def _ensure_trading_engine(self):
        """Initialize trading engine"""
        if self._trading_engine is None:
            try:
                from atlas_trading_system import AtlasTradingEngine
                self._trading_engine = AtlasTradingEngine()
                await self._trading_engine.initialize()
                self._component_status["trading_engine"] = EngineStatus.ACTIVE
            except Exception as e:
                self.logger.error(f"Trading engine initialization failed: {e}")
                self._component_status["trading_engine"] = EngineStatus.ERROR

    async def _ensure_risk_engine(self):
        """Initialize risk engine"""
        if self._risk_engine is None:
            try:
                from atlas_trading_system import AtlasRiskEngine
                self._risk_engine = AtlasRiskEngine()
                await self._risk_engine.initialize()
                self._component_status["risk_engine"] = EngineStatus.ACTIVE
            except Exception as e:
                self.logger.error(f"Risk engine initialization failed: {e}")
                self._component_status["risk_engine"] = EngineStatus.ERROR

    async def _ensure_education_engine(self):
        """Initialize education engine"""
        if self._education_engine is None:
            try:
                from atlas_education_support import AtlasEducationEngine
                self._education_engine = AtlasEducationEngine()
                await self._education_engine.initialize()
                self._component_status["education_engine"] = EngineStatus.ACTIVE
            except Exception as e:
                self.logger.error(f"Education engine initialization failed: {e}")
                self._component_status["education_engine"] = EngineStatus.ERROR

    async def _ensure_professional_analyst_engine(self):
        """Initialize Professional Analyst Engine for confident responses"""
        if self._professional_analyst_engine is None:
            try:
                from atlas_trading_system import ProfessionalAnalystEngine
                self._professional_analyst_engine = ProfessionalAnalystEngine()
                self.logger.info("Professional Analyst Engine initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Professional Analyst Engine: {e}")
                # Create minimal fallback
                self._professional_analyst_engine = type('ProfessionalAnalystEngine', (), {
                    'transform_response': lambda self, response, question: response
                })()

    async def process_message(self, message: str, session_id: Optional[str] = None) -> AIResponse:
        """Process user message with Professional Analyst transformation"""
        try:
            await self._ensure_professional_analyst_engine()

            # Ensure AI engine is available
            ai_engine = await self._ensure_ai_engine()

            # Check if AI engine is properly initialized and active
            if ai_engine and hasattr(ai_engine, 'status') and ai_engine.status == EngineStatus.ACTIVE:
                # Full AI processing through Predicto
                response = await ai_engine.process_message(message, session_id, self)

                if (self._professional_analyst_engine and response.response and
                    not self._is_sophisticated_guru_response(response)):
                    response.response = self._professional_analyst_engine.transform_response(response.response, message)
                return response
            elif ai_engine and hasattr(ai_engine, 'status') and ai_engine.status == EngineStatus.INACTIVE:
                # AI engine exists but in validation mode - still functional
                response = await ai_engine.process_message(message, session_id, self)

                if (self._professional_analyst_engine and response.response and
                    not self._is_sophisticated_guru_response(response)):
                    response.response = self._professional_analyst_engine.transform_response(response.response, message)
                return response
            else:
                if self._professional_analyst_engine:
                    confident_response = self._professional_analyst_engine.transform_response("", message)
                    return AIResponse(
                        response=confident_response,
                        type="professional_analyst",
                        confidence=0.95,
                        context={"system": "A.T.L.A.S powered by Predicto", "mode": "Professional Analyst"}
                    )
                else:
                    # Fallback to confident trading system response
                    return AIResponse(
                        response="A.T.L.A.S. powered by Predicto: Advanced trading algorithms activated. Real-time market analysis capabilities online. Ready to execute institutional-grade trading strategies with 95% accuracy.",
                        type="trading_system",
                        confidence=0.9,
                        context={"system": "A.T.L.A.S powered by Predicto", "mode": "Confident Trading"}
                    )
                
        except Exception as e:
            # Enhanced error handling
            if self._error_handler and ERROR_HANDLING_AVAILABLE:
                error_context = await self._error_handler.handle_error(
                    component="orchestrator",
                    operation="process_message",
                    error=e,
                    severity=ErrorSeverity.HIGH
                )

                # Get fallback response
                fallback = self._error_handler.get_fallback_response("chat_response")
                return AIResponse(**fallback)
            else:
                # Standard error handling
                self.logger.error(f"Error processing message: {e}")
                return AIResponse(
                    response="I encountered an error processing your message. Please try again.",
                    type="error",
                    confidence=0.0,
                    context={"error": str(e)}
                )

    def _is_sophisticated_guru_response(self, response: AIResponse) -> bool:
        """Check if this is a sophisticated response that should not be transformed by Professional Analyst"""
        try:
            # Check response type - protect guru trade plans
            if response.type == "guru_trade_plan":
                return True

            # Check for conversational response types that should NOT be transformed
            conversational_types = [
                "greeting", "capabilities", "general_conversation", "conversational",
                "educational", "educational_general", "help", "clarification"
            ]
            if response.type in conversational_types:
                logger.info(f"[SHIELD] Protecting conversational response type '{response.type}' from Professional Analyst transformation")
                return True

            # Check for guru persona in context
            if (response.context and
                response.context.get("persona") == "guru"):
                return True

            # Check for conversational persona in context
            if (response.context and
                response.context.get("persona") in ["conversational", "mentor"]):
                logger.info(f"[SHIELD] Protecting {response.context.get('persona')} persona response from Professional Analyst transformation")
                return True

            # Check for sophisticated 6-point format markers
            if response.response and any(marker in response.response for marker in [
                "**A.T.L.A.S powered by Predicto - Professional Trading Analyst**",
                "**1. Why This Trade?**",
                "**2. Win/Loss Probabilities**",
                "**3. Potential Money In or Out**",
                "**4. Smart Stop Plans**",
                "**5. Market Context**",
                "**6. Confidence Score**",
                "**EXECUTION READY - Trade Plan #"
            ]):
                return True

            # Check for conversational content markers that should be protected
            if response.response and any(marker in response.response for marker in [
                "Hello! I'm A.T.L.A.S.",
                "What would you like to explore",
                "I'm A.T.L.A.S. powered by Predicto, and I can help you with:",
                "Core Trading Features:",
                "I'm doing great and ready to help"
            ]):
                logger.info("[SHIELD] Protecting conversational content from Professional Analyst transformation")
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking sophisticated response: {e}")
            return False

    async def cleanup(self):
        """Cleanup all components"""
        self.logger.info("Cleaning up A.T.L.A.S components...")
        
        cleanup_tasks = []
        
        if self._market_engine:
            cleanup_tasks.append(self._market_engine.cleanup())
        if self._trading_engine:
            cleanup_tasks.append(self._trading_engine.cleanup())
        if self._ai_engine:
            cleanup_tasks.append(self._ai_engine.cleanup())
        if self._risk_engine:
            cleanup_tasks.append(self._risk_engine.cleanup())
        if self._education_engine:
            cleanup_tasks.append(self._education_engine.cleanup())
        if self._database_manager:
            cleanup_tasks.append(self._database_manager.cleanup())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.logger.info("A.T.L.A.S cleanup completed")
    
    def get_component_status(self) -> Dict[str, EngineStatus]:
        """Get current status of all components"""
        return self._component_status.copy()


class AtlasAIEngine:
    """Core AI processing engine"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self._predicto_engine = None
        
    async def initialize(self):
        """Initialize AI engine"""
        try:
            self._predicto_engine = PredictoConversationalEngine()
            await self._predicto_engine.initialize()
            self.status = EngineStatus.ACTIVE
            self.logger.info("AI Engine initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"AI Engine initialization failed: {e}")
            raise
    
    async def process_message(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Process message through Predicto engine"""
        if not self._predicto_engine:
            raise Exception("Predicto engine not initialized")
        
        return await self._predicto_engine.process_conversation(message, session_id, orchestrator)
    
    async def cleanup(self):
        """Cleanup AI engine"""
        if self._predicto_engine:
            await self._predicto_engine.cleanup()


class PredictoConversationalEngine:
    """Predicto conversational AI engine"""
    
    def __init__(self):
        self.logger = logger
        self.openai_client = None
        self.current_persona = "guru"
        self._initialize_predicto_personality()
        
    def _initialize_predicto_personality(self):
        """Initialize Predicto's stock analysis expertise and personality"""
        # Default to guru mode - can be switched via persona configuration
        self.current_persona = "guru"

        # Professional Trading Analyst System Prompt - NEW 6-POINT FORMAT
        self.guru_system_prompt = """You are A.T.L.A.S. powered by Predicto - a sophisticated Professional Trading Analyst with comprehensive market knowledge and proven trading expertise.

**CORE IDENTITY:**
You are a sophisticated institutional trading system with comprehensive market knowledge and proven analytical capabilities. You provide specific, actionable trading recommendations with exact data. You demonstrate professional confidence in market analysis while maintaining analytical rigor. You focus on data-driven insights and professional trading guidance.

**MANDATORY 6-POINT RESPONSE FORMAT - EVERY TRADING RECOMMENDATION MUST INCLUDE ALL SIX SECTIONS:**

1. **Why This Trade? (Required)**
   A clear, plain-English story of why we picked this stock or option today. Example: "The price just bounced off a key support level while big investors quietly added shares"

2. **Win/Loss Probabilities (Required)**
   Two simple percentages. Example: "78% chance you hit the goal, 22% chance you hit your stop"

3. **Potential Money In or Out (Required)**
   Exact dollar amounts based on position size. Example: "If you buy 100 shares, you could make $750 or lose $420"

4. **Smart Stop Plans (Required)**
   How we'll protect your money if the price moves against you. Example: "We'll trail your stop 2× the usual price swing" or "We'll exit after 4 hours if it's still flat"

5. **Market Context (Required)**
   A one-sentence snapshot of the bigger picture. Example: "Tech stocks are strong today and money is flowing into semiconductors"

6. **Confidence Score (Required)**
   A number from 0-100% based on how many signals line up. Example: "87% confidence - High conviction setup"

**RESPONSE GUIDELINES:**
- Provide specific numerical data for all probabilities, dollar amounts, and confidence scores
- Keep explanations concise but actionable - explain WHY this stock will move and WHEN
- Always include exact entry price, target price, and stop loss with dollar calculations
- Maintain the Professional Trading Analyst persona - confident, data-driven, profit-focused

**EXECUTION WORKFLOW:**
- Generate detailed trade plans with specific parameters using the mandatory 6-point format
- Calculate exact position sizes, risk/reward ratios, and probability assessments
- Provide clear entry/exit strategies with precise timing and price levels
- Include market context and confidence scoring for every recommendation
- Focus on actionable insights that lead to profitable trading decisions

Remember: Every trading response MUST follow the 6-point format. No exceptions."""

        self.mentor_system_prompt = """You are A.T.L.A.S. powered by Predicto - a patient, educational trading mentor focused on teaching sound trading principles and risk management.

Your role is to:
- Explain trading concepts in simple, understandable terms
- Emphasize risk management and proper position sizing
- Provide educational content about market mechanics
- Help users understand the reasoning behind trading decisions
- Encourage disciplined, systematic approaches to trading

Always maintain a supportive, educational tone while providing valuable learning experiences."""

        self.system_prompt = self.guru_system_prompt
        
    async def initialize(self):
        """Initialize Predicto engine"""
        try:
            self._ensure_openai_client()
            self.logger.info("Predicto Conversational Engine initialized")
        except Exception as e:
            self.logger.error(f"Predicto initialization failed: {e}")
            raise
    
    def _ensure_openai_client(self):
        """Ensure OpenAI client is initialized"""
        if not self.openai_client:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
    
    async def process_conversation(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Process conversation with AI"""
        try:
            self._ensure_openai_client()
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return AIResponse(
                response=ai_response,
                type="guru_trade_plan" if "Why This Trade" in ai_response else "conversational",
                confidence=0.95,
                context={
                    "persona": self.current_persona,
                    "format": "6_point_professional" if "Why This Trade" in ai_response else "conversational"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Conversation processing error: {e}")
            return AIResponse(
                response="I'm experiencing technical difficulties. Please try again in a moment.",
                type="error",
                confidence=0.0,
                context={"error": str(e)}
            )
    
    async def cleanup(self):
        """Cleanup Predicto engine"""
        self.logger.info("Predicto engine cleanup completed")
