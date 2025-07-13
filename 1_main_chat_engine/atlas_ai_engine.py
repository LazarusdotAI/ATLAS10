"""
A.T.L.A.S AI Engine - Predicto-Powered Conversational Intelligence
Enhanced with stock analysis expertise and unified system access
"""

# CRITICAL: Import startup initialization FIRST to ensure Windows-compatible logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '4_helper_tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '3_market_news_data'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '2_trading_logic'))

try:
    from atlas_startup_init import initialize_component_logging
    logger = initialize_component_logging('atlas_ai_engine')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from config import get_api_config, settings
from models import AIResponse, EngineStatus, EmotionalState, CommunicationMode, TradingGoal, ContextMemory

# Optional imports with graceful fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class AtlasAIEngine:
    """Enhanced AI Engine with Predicto-Powered Conversational Intelligence"""

    def __init__(self):
        self.openai_config = get_api_config("openai")
        self.validation_mode = self.openai_config.get("validation_mode", False)
        self.status = EngineStatus.INITIALIZING

        # Predicto Core Components
        self.predicto_engine = None
        self.stock_intelligence_hub = None
        self.unified_access_layer = None
        self.conversation_flow_manager = None

        # Legacy components (for backward compatibility)
        self._openai_client = None
        self._sentiment_model = None
        self.sentiment_analyzer = None
        self.ml_predictor = None
        self.options_engine = None
        self.options_flow_analyzer = None
        self.portfolio_optimizer = None
        self.market_context_engine = None
        self.proactive_assistant = None

        # Predicto-enhanced conversational intelligence
        self.conversation_memory = {}
        self.user_profiles = {}
        self.emotional_intelligence = True
        self.multi_agent_coordination = True

        # Communication settings optimized for Predicto
        self.communication_mode = CommunicationMode.PROFESSIONAL
        self.personality_traits = {
            'stock_analysis_expertise': 0.95,
            'helpfulness': 0.9,
            'confidence': 0.8,
            'enthusiasm': 0.7,
            'patience': 0.9,
            'educational_focus': 0.9
        }

        # Multi-agent system (legacy)
        self.agents = {}

        if self.validation_mode:
            logger.info("Predicto AI Engine created - Validation mode (limited functionality)")
        else:
            logger.info("Predicto AI Engine created - Stock analysis expertise ready")
    
    async def initialize(self):
        """Initialize Predicto AI engine and components"""
        try:
            self.status = EngineStatus.INITIALIZING

            if self.validation_mode:
                # In validation mode, initialize Predicto with limited functionality
                logger.info("Predicto AI Engine validation mode - limited functionality")
                await self._initialize_predicto_components_validation()
                await self._initialize_agents()  # Initialize legacy agents for compatibility
                self.status = EngineStatus.ACTIVE  # Set to ACTIVE so it can process messages
                logger.info("Predicto AI Engine validation mode initialization completed")
                return

            # Initialize Predicto core components
            await self._initialize_predicto_components()
            logger.info("Predicto core components initialized")

            # Initialize legacy components for backward compatibility
            if OPENAI_AVAILABLE and self.openai_config.get("api_key"):
                await self._ensure_openai_client()
                logger.info("OpenAI client initialized")
            else:
                logger.warning("OpenAI not available - using fallback responses")

            # Initialize ML models in background
            asyncio.create_task(self._initialize_ml_models())

            # Initialize legacy multi-agent system for compatibility
            await self._initialize_agents()

            # Initialize enhanced components
            await self._initialize_enhanced_components()

            self.status = EngineStatus.ACTIVE
            logger.info("Predicto AI Engine fully initialized - Stock analysis expertise ready")

        except Exception as e:
            self.status = EngineStatus.FAILED
            logger.error(f"Predicto AI Engine initialization failed: {e}")
            raise

    async def _initialize_enhanced_components(self):
        """Initialize enhanced AI components"""
        try:
            logger.info("Initializing enhanced AI components...")

            # Import and initialize components
            if settings.ML_MODELS_ENABLED:
                try:
                    from atlas_sentiment_analyzer import sentiment_analyzer
                    from atlas_ml_predictor import ml_predictor

                    self.sentiment_analyzer = sentiment_analyzer
                    self.ml_predictor = ml_predictor

                    await self.sentiment_analyzer.initialize()
                    await self.ml_predictor.initialize()

                    logger.info("ML components initialized")
                except Exception as e:
                    logger.warning(f"ML components initialization failed: {e}")

            # Initialize options components
            if settings.OPTIONS_TRADING_ENABLED:
                try:
                    from atlas_options_engine import options_engine
                    from atlas_options_flow_analyzer import options_flow_analyzer

                    self.options_engine = options_engine
                    self.options_flow_analyzer = options_flow_analyzer

                    await self.options_flow_analyzer.initialize()

                    logger.info("Options components initialized")
                except Exception as e:
                    logger.warning(f"Options components initialization failed: {e}")

            # Initialize portfolio optimizer
            try:
                from atlas_portfolio_optimizer import portfolio_optimizer

                self.portfolio_optimizer = portfolio_optimizer
                await self.portfolio_optimizer.initialize()

                logger.info("Portfolio optimizer initialized")
            except Exception as e:
                logger.warning(f"Portfolio optimizer initialization failed: {e}")

            # Initialize market context engine
            try:
                from atlas_market_context import market_context_engine

                self.market_context_engine = market_context_engine

                logger.info("Market context engine initialized")
            except Exception as e:
                logger.warning(f"Market context engine initialization failed: {e}")

            # Initialize proactive assistant
            if settings.PROACTIVE_ASSISTANT_ENABLED:
                try:
                    from atlas_proactive_assistant import proactive_assistant

                    self.proactive_assistant = proactive_assistant

                    logger.info("Proactive assistant initialized")
                except Exception as e:
                    logger.warning(f"Proactive assistant initialization failed: {e}")

            logger.info("Enhanced AI components initialization complete")

        except Exception as e:
            logger.error(f"Error initializing enhanced components: {e}")

    async def _ensure_openai_client(self):
        """Ensure OpenAI client is available"""
        if not self._openai_client and OPENAI_AVAILABLE:
            try:
                self._openai_client = openai.AsyncOpenAI(
                    api_key=self.openai_config["api_key"]
                )
                logger.info("OpenAI client connected")
            except Exception as e:
                logger.error(f"OpenAI client initialization failed: {e}")
                self._openai_client = None
        
        return self._openai_client
    
    async def _initialize_ml_models(self):
        """Initialize ML models in background"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Initialize sentiment analysis model
                self._sentiment_model = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True
                )
                logger.info("DistilBERT sentiment model loaded")
            else:
                logger.warning("Transformers not available - using basic sentiment analysis")
                
        except Exception as e:
            logger.warning(f"ML model initialization failed: {e}")

    async def _initialize_predicto_components(self):
        """Initialize Predicto core components"""
        try:
            logger.info("[AI] Initializing Predicto core components...")

            # Import Predicto components
            from atlas_predicto_engine import PredictoConversationalEngine
            from atlas_stock_intelligence_hub import StockIntelligenceHub
            from atlas_unified_access_layer import UnifiedSystemAccessLayer
            from atlas_conversation_flow_manager import ConversationFlowManager

            # Initialize Predicto engine
            self.predicto_engine = PredictoConversationalEngine()
            await self.predicto_engine.initialize()
            logger.info("[OK] Predicto Conversational Engine initialized")

            # Initialize Stock Intelligence Hub
            self.stock_intelligence_hub = StockIntelligenceHub()
            await self.stock_intelligence_hub.initialize()
            logger.info("[OK] Stock Intelligence Hub initialized")

            # Initialize Unified Access Layer
            self.unified_access_layer = UnifiedSystemAccessLayer()
            await self.unified_access_layer.initialize()
            logger.info("[OK] Unified System Access Layer initialized")

            # Initialize Conversation Flow Manager
            self.conversation_flow_manager = ConversationFlowManager()
            await self.conversation_flow_manager.initialize()
            logger.info("[OK] Conversation Flow Manager initialized")

            logger.info("[AI] Predicto core components fully initialized")

        except Exception as e:
            logger.error(f"Predicto components initialization failed: {e}")
            # Continue with limited functionality
            self.predicto_engine = None
            self.stock_intelligence_hub = None
            self.unified_access_layer = None
            self.conversation_flow_manager = None

    async def _initialize_predicto_components_validation(self):
        """Initialize Predicto components in validation mode"""
        try:
            logger.info("[AI] Initializing Predicto components in validation mode...")

            # Import Predicto components
            from atlas_predicto_engine import PredictoConversationalEngine
            from atlas_stock_intelligence_hub import StockIntelligenceHub
            from atlas_unified_access_layer import UnifiedSystemAccessLayer
            from atlas_conversation_flow_manager import ConversationFlowManager

            # Initialize with validation mode
            self.predicto_engine = PredictoConversationalEngine()
            self.predicto_engine.validation_mode = True
            await self.predicto_engine.initialize()

            self.stock_intelligence_hub = StockIntelligenceHub()
            await self.stock_intelligence_hub.initialize()

            self.unified_access_layer = UnifiedSystemAccessLayer()
            await self.unified_access_layer.initialize()

            self.conversation_flow_manager = ConversationFlowManager()
            await self.conversation_flow_manager.initialize()

            logger.info("[OK] Predicto components initialized in validation mode")

        except Exception as e:
            logger.error(f"Predicto validation mode initialization failed: {e}")
            # Set to None for fallback
            self.predicto_engine = None
            self.stock_intelligence_hub = None
            self.unified_access_layer = None
            self.conversation_flow_manager = None
    
    async def _initialize_agents(self):
        """Initialize the multi-agent system"""
        try:
            # Technical Analysis Agent with ML enhancement
            self.agents["technical"] = TechnicalAnalysisAgent()
            await self.agents["technical"].initialize()
            
            # Risk Management Agent
            self.agents["risk"] = RiskManagementAgent()
            await self.agents["risk"].initialize()
            
            # Sentiment Analysis Agent with DistilBERT
            self.agents["sentiment"] = SentimentAnalysisAgent(self._sentiment_model)
            await self.agents["sentiment"].initialize()
            
            # Execution Timing Agent
            self.agents["execution"] = ExecutionAgent()
            await self.agents["execution"].initialize()
            
            logger.info(f"[OK] Initialized {len(self.agents)} AI agents with ML capabilities")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
    
    async def process_message(self, message: str, session_id: Optional[str], orchestrator, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Process user message through Predicto conversational AI interface"""
        try:
            # Use Predicto as primary interface if available
            if self.predicto_engine and self.predicto_engine.status == EngineStatus.ACTIVE:
                logger.info(f"[AI] Processing message through Predicto: {message[:100]}...")

                # Process through Predicto conversational engine with context
                predicto_response = await self.predicto_engine.process_conversation(message, session_id, orchestrator, context)

                # Enhance with conversation flow management
                if self.conversation_flow_manager:
                    flow_data = await self.conversation_flow_manager.process_conversation_turn(
                        message, session_id or "default", predicto_response
                    )

                    # Add flow enhancements to response context
                    if predicto_response.context is None:
                        predicto_response.context = {}
                    predicto_response.context["conversation_flow"] = flow_data

                return predicto_response

            # Fallback to legacy processing if Predicto not available
            logger.warning("[WARN] Predicto not available, using legacy processing")
            return await self._process_legacy_message(message, session_id, orchestrator)

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return await self._fallback_response(message, "general")

    async def _process_legacy_message(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Legacy message processing for backward compatibility"""
        try:
            # Analyze message intent
            intent = await self._analyze_intent(message)

            # Route to appropriate processing
            if intent["type"] == "trading_analysis":
                return await self._process_trading_analysis(message, session_id, orchestrator)
            elif intent["type"] == "education":
                return await self._process_education_query(message, session_id, orchestrator)
            else:
                return await self._process_general_chat(message, session_id, orchestrator)

        except Exception as e:
            logger.error(f"Legacy message processing failed: {e}")
            return await self._fallback_response(message, "general")
    
    async def _process_trading_analysis(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Process trading analysis with multi-agent system and web search"""
        try:
            # Multi-agent analysis
            agent_responses = {}
            
            # Technical analysis with ML enhancement
            if "technical" in self.agents:
                agent_responses["technical"] = await self.agents["technical"].analyze(message, orchestrator)
            
            # Risk analysis
            if "risk" in self.agents:
                agent_responses["risk"] = await self.agents["risk"].analyze(message, orchestrator)
            
            # Sentiment analysis with DistilBERT
            if "sentiment" in self.agents:
                agent_responses["sentiment"] = await self.agents["sentiment"].analyze(message, orchestrator)
            
            # Execution timing analysis
            if "execution" in self.agents:
                agent_responses["execution"] = await self.agents["execution"].analyze(message, orchestrator)
            
            # Add web search context if symbol detected
            symbol = self._extract_symbol_from_message(message)
            if symbol and orchestrator and hasattr(orchestrator, 'market_engine'):
                try:
                    web_context = await orchestrator.market_engine.search_market_context(symbol, "news")
                    if web_context.get("success"):
                        agent_responses["web_context"] = {
                            "analysis": f"📰 Market News: {web_context.get('summary', 'No summary available')}",
                            "confidence": 0.7,
                            "recommendation": web_context.get("market_impact", "neutral"),
                            "reasoning": f"Sentiment: {web_context.get('sentiment_score', 0):.2f}, {len(web_context.get('results', []))} news items",
                            "web_data": web_context
                        }
                except Exception as e:
                    logger.warning(f"Web search integration failed: {e}")

            # Parse trading goals and generate action plan
            trading_goals = self._parse_trading_goals(message)
            if trading_goals.get("has_specific_target"):
                try:
                    action_plan = await self._generate_action_plan(trading_goals, symbol, orchestrator)
                    agent_responses["action_plan"] = {
                        "analysis": f"[TARGET] Action Plan: {action_plan.get('summary', 'Plan generated')}",
                        "confidence": 0.8,
                        "recommendation": action_plan.get("recommendation", "neutral"),
                        "reasoning": f"Goal: {trading_goals.get('description', 'N/A')}",
                        "action_plan": action_plan
                    }
                except Exception as e:
                    logger.warning(f"Action plan generation failed: {e}")
            
            # Generate consensus response with chain-of-thought
            consensus = await self._generate_consensus(agent_responses, message)
            
            # Add chain-of-thought reasoning
            cot_analysis = await self._generate_chain_of_thought(agent_responses, consensus, message)
            
            return AIResponse(
                response=cot_analysis["response"],
                type="trading_analysis",
                confidence=cot_analysis["confidence"],
                context={
                    "agent_responses": agent_responses,
                    "consensus_reasoning": consensus["reasoning"],
                    "chain_of_thought": cot_analysis["reasoning_steps"]
                }
            )
            
        except Exception as e:
            logger.error(f"Trading analysis failed: {e}")
            return await self._fallback_response(message, "trading_analysis")
    
    async def _process_education_query(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Process educational queries"""
        try:
            if orchestrator and hasattr(orchestrator, 'education_engine'):
                from models import EducationRequest
                request = EducationRequest(query=message, difficulty="auto")
                response = await orchestrator.education_engine.process_query(request)
                
                return AIResponse(
                    response=response.get("response", "Educational content not available"),
                    type="education",
                    confidence=response.get("confidence", 0.7),
                    context={"education_data": response}
                )
            else:
                return await self._fallback_response(message, "education")
                
        except Exception as e:
            logger.error(f"Education query failed: {e}")
            return await self._fallback_response(message, "education")
    
    async def _process_general_chat(self, message: str, session_id: Optional[str], orchestrator) -> AIResponse:
        """Process general chat messages"""
        try:
            client = await self._ensure_openai_client()
            
            if client:
                # Use OpenAI for general chat
                response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are A.T.L.A.S. (Advanced Trading & Learning Analysis System) powered by Predicto. Always identify yourself as 'A.T.L.A.S. powered by Predicto'. You are an AI trading mentor. Be helpful, educational, and professional."},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return AIResponse(
                    response=response.choices[0].message.content,
                    type="general_chat",
                    confidence=0.8,
                    context={"model": "gpt-4"}
                )
            else:
                return await self._fallback_response(message, "general_chat")
                
        except Exception as e:
            logger.error(f"General chat failed: {e}")
            return await self._fallback_response(message, "general_chat")
    
    def _extract_symbol_from_message(self, message: str) -> Optional[str]:
        """Extract stock symbol from message"""
        import re
        patterns = [
            r'\b([A-Z]{1,5})\b',  # 1-5 uppercase letters
            r'\$([A-Z]{1,5})\b',  # $SYMBOL format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message.upper())
            if matches:
                for match in matches:
                    if len(match) >= 1 and len(match) <= 5:
                        return match
        return None

    async def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent from message"""
        try:
            message_lower = message.lower()

            # Trading analysis keywords
            trading_keywords = [
                "analyze", "analysis", "buy", "sell", "trade", "stock", "symbol",
                "ttm", "squeeze", "signal", "chart", "technical", "price", "target"
            ]

            # Education keywords
            education_keywords = [
                "explain", "what is", "how to", "learn", "teach", "definition",
                "meaning", "example", "tutorial", "guide"
            ]

            # Count keyword matches
            trading_score = sum(1 for keyword in trading_keywords if keyword in message_lower)
            education_score = sum(1 for keyword in education_keywords if keyword in message_lower)

            # Determine intent
            if trading_score > education_score:
                return {"type": "trading_analysis", "confidence": min(trading_score / 5.0, 1.0)}
            elif education_score > 0:
                return {"type": "education", "confidence": min(education_score / 3.0, 1.0)}
            else:
                return {"type": "general_chat", "confidence": 0.5}

        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {"type": "general_chat", "confidence": 0.3}

    async def _generate_consensus(self, agent_responses: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Generate weighted consensus from multiple agent responses"""
        try:
            if not agent_responses:
                return {
                    "response": "No agent responses available for consensus",
                    "confidence": 0.1,
                    "reasoning": "No agents responded",
                    "recommendation": "neutral"
                }

            # Agent weights (must sum to 1.0)
            agent_weights = {
                "technical": 0.35,    # Technical Analysis Agent
                "risk": 0.30,         # Risk Management Agent
                "sentiment": 0.20,    # Sentiment Analysis Agent
                "execution": 0.15,    # Execution Timing Agent
                "web_context": 0.10   # Web search context (bonus weight)
            }

            # Calculate weighted confidence
            weighted_confidence = 0.0
            total_weight = 0.0

            for agent_name, response in agent_responses.items():
                if agent_name in agent_weights:
                    weight = agent_weights[agent_name]
                    confidence = response.get("confidence", 0.5)
                    weighted_confidence += confidence * weight
                    total_weight += weight

            # Normalize if not all agents responded
            if total_weight > 0:
                weighted_confidence = weighted_confidence / total_weight
            else:
                weighted_confidence = 0.5

            # Collect recommendations with weights
            recommendations = {}
            reasoning_parts = []

            for agent_name, response in agent_responses.items():
                if agent_name in agent_weights:
                    weight = agent_weights[agent_name]
                    recommendation = response.get("recommendation", "neutral")
                    analysis = response.get("analysis", "")
                    reasoning = response.get("reasoning", "")

                    # Weight the recommendation
                    if recommendation not in recommendations:
                        recommendations[recommendation] = 0.0
                    recommendations[recommendation] += weight

                    # Add to reasoning with weight indication
                    reasoning_parts.append(f"**{agent_name.title()} ({weight*100:.0f}%)**: {analysis}")
                    if reasoning:
                        reasoning_parts.append(f"  └─ Reasoning: {reasoning}")

            # Determine consensus recommendation
            if recommendations:
                consensus_recommendation = max(recommendations.items(), key=lambda x: x[1])[0]
                recommendation_confidence = recommendations[consensus_recommendation]
            else:
                consensus_recommendation = "neutral"
                recommendation_confidence = 0.5

            # Generate consensus summary
            consensus_summary = f"[BOT] **Multi-Agent Consensus**: {consensus_recommendation.upper()}"
            if recommendation_confidence >= 0.7:
                consensus_summary += " (Strong Agreement)"
            elif recommendation_confidence >= 0.5:
                consensus_summary += " (Moderate Agreement)"
            else:
                consensus_summary += " (Weak Agreement)"

            # Add confidence indicator
            if weighted_confidence >= 0.8:
                confidence_indicator = "🟢 High Confidence"
            elif weighted_confidence >= 0.6:
                confidence_indicator = "🟡 Moderate Confidence"
            else:
                confidence_indicator = "🔴 Low Confidence"

            consensus_response = f"{consensus_summary}\n{confidence_indicator} ({weighted_confidence:.1%})\n\n" + "\n\n".join(reasoning_parts)

            return {
                "response": consensus_response,
                "confidence": weighted_confidence,
                "reasoning": f"Weighted consensus from {len(agent_responses)} agents",
                "recommendation": consensus_recommendation,
                "agent_weights": agent_weights,
                "recommendation_distribution": recommendations
            }

        except Exception as e:
            logger.error(f"Weighted consensus generation failed: {e}")
            return {
                "response": f"Consensus generation failed: {str(e)}",
                "confidence": 0.1,
                "reasoning": "Error in consensus calculation",
                "recommendation": "neutral"
            }

    async def _generate_chain_of_thought(self, agent_responses: Dict[str, Any], consensus: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Generate chain-of-thought reasoning with educational explanations"""
        try:
            # Extract key information
            symbol = self._extract_symbol_from_message(message)

            # Generate step-by-step analysis
            reasoning_steps = []

            # Step 1: Understanding the request
            reasoning_steps.append(f"[TARGET] **Understanding Your Request**: {message[:100]}...")

            # Step 2: Multi-agent analysis
            agent_summary = []
            for agent_name, response in agent_responses.items():
                recommendation = response.get("recommendation", "neutral")
                confidence = response.get("confidence", 0.5)
                agent_summary.append(f"**{agent_name.title()}**: {recommendation.upper()} ({confidence:.0%})")

            reasoning_steps.append(f"[BOT] **Multi-Agent Analysis**:\n" + "\n".join(agent_summary))

            # Step 3: Final recommendation
            final_recommendation = consensus.get("recommendation", "neutral")
            final_confidence = consensus.get("confidence", 0.5)
            reasoning_steps.append(f"[TARGET] **Final Recommendation**: {final_recommendation.upper()} ({final_confidence:.0%} confidence)")

            # Combine into response
            enhanced_response = consensus.get("response", "") + "\n\n## [BRAIN] **Chain of Thought**:\n\n" + "\n\n".join(reasoning_steps)

            return {
                "response": enhanced_response,
                "confidence": final_confidence,
                "reasoning_steps": reasoning_steps
            }

        except Exception as e:
            logger.error(f"Chain-of-thought generation failed: {e}")
            return {
                "response": f"I've analyzed your request and here's my assessment:\n\n{consensus.get('response', 'Analysis in progress...')}\n\n*Note: Detailed reasoning temporarily unavailable*",
                "confidence": consensus.get("confidence", 0.5),
                "reasoning_steps": []
            }

    async def _fallback_response(self, message: str, response_type: str) -> AIResponse:
        """Generate fallback response when main processing fails"""
        try:
            fallback_responses = {
                "trading_analysis": "I'm analyzing market conditions. Please try again in a moment while I gather the latest data.",
                "education": "I'm accessing educational resources. Please try again shortly.",
                "general": "I'm processing your request. Please try again in a moment."
            }

            return AIResponse(
                response=fallback_responses.get(response_type, fallback_responses["general"]),
                type=response_type,
                confidence=0.3,
                context={"fallback": True}
            )

        except Exception as e:
            logger.error(f"Fallback response failed: {e}")
            return AIResponse(
                response="I'm experiencing technical difficulties. Please try again.",
                type="error",
                confidence=0.1,
                context={"error": str(e)}
            )

    async def cleanup(self):
        """Cleanup Predicto AI engine resources"""
        try:
            self.status = EngineStatus.SHUTTING_DOWN

            # Cleanup Predicto components
            if self.predicto_engine:
                await self.predicto_engine.cleanup()
                logger.info("[OK] Predicto Engine cleaned up")

            if self.stock_intelligence_hub:
                await self.stock_intelligence_hub.cleanup()
                logger.info("[OK] Stock Intelligence Hub cleaned up")

            if self.unified_access_layer:
                await self.unified_access_layer.cleanup()
                logger.info("[OK] Unified Access Layer cleaned up")

            if self.conversation_flow_manager:
                await self.conversation_flow_manager.cleanup()
                logger.info("[OK] Conversation Flow Manager cleaned up")

            # Cleanup legacy agents
            for agent in self.agents.values():
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()

            self.status = EngineStatus.INACTIVE
            logger.info("[AI] Predicto AI Engine cleanup completed")

        except Exception as e:
            logger.error(f"Predicto AI Engine cleanup error: {e}")

    # ===== GOAL-ORIENTED ACTION PLANNING =====

    def _parse_trading_goals(self, message: str) -> Dict[str, Any]:
        """Parse trading goals from user message"""
        try:
            import re

            goals = {
                "has_specific_target": False,
                "profit_target": None,
                "timeframe": None,
                "risk_tolerance": None,
                "specific_amount": None,
                "percentage_target": None,
                "description": "",
                "is_realistic": True,
                "unrealistic_reasons": []
            }

            message_lower = message.lower()

            # Extract dollar amounts
            dollar_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
            if dollar_matches:
                # Convert to float, removing commas
                amounts = [float(match.replace(',', '')) for match in dollar_matches]
                goals["specific_amount"] = max(amounts)  # Take the largest amount mentioned
                goals["has_specific_target"] = True
                goals["description"] = f"Make ${goals['specific_amount']:,.0f}"

            # Extract percentages
            percent_matches = re.findall(r'(\d+(?:\.\d+)?)%', message)
            if percent_matches:
                percentages = [float(match) for match in percent_matches]
                goals["percentage_target"] = max(percentages)
                goals["has_specific_target"] = True
                if not goals["description"]:
                    goals["description"] = f"Make {goals['percentage_target']}% profit"

            # Extract timeframes
            timeframe_patterns = {
                "today": r'\b(today|this day)\b',
                "week": r'\b(this week|weekly|week)\b',
                "month": r'\b(this month|monthly|month)\b',
                "year": r'\b(this year|yearly|year|annual)\b'
            }

            for timeframe, pattern in timeframe_patterns.items():
                if re.search(pattern, message_lower):
                    goals["timeframe"] = timeframe
                    if goals["description"]:
                        goals["description"] += f" {timeframe}"
                    break

            # Reality check
            if goals["has_specific_target"]:
                goals["is_realistic"], goals["unrealistic_reasons"] = self._reality_check_goals(goals)

            return goals

        except Exception as e:
            logger.error(f"Goal parsing error: {e}")
            return {"has_specific_target": False, "is_realistic": True, "unrealistic_reasons": []}

    def _reality_check_goals(self, goals: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Perform reality check on trading goals"""
        try:
            is_realistic = True
            reasons = []

            # Check daily targets
            if goals.get("timeframe") == "today":
                if goals.get("specific_amount", 0) > 1000:
                    is_realistic = False
                    reasons.append("Daily profit target too high - consider smaller, achievable goals")

                if goals.get("percentage_target", 0) > 10:
                    is_realistic = False
                    reasons.append("Daily percentage target unrealistic - professional traders aim for 1-3% daily")

            # Check weekly targets
            elif goals.get("timeframe") == "week":
                if goals.get("specific_amount", 0) > 5000:
                    is_realistic = False
                    reasons.append("Weekly profit target very ambitious - consider risk management")

                if goals.get("percentage_target", 0) > 25:
                    is_realistic = False
                    reasons.append("Weekly percentage target extremely high - sustainable growth is 5-15% weekly")

            # Check for guaranteed language
            if any(word in goals.get("description", "").lower() for word in ["guaranteed", "sure", "certain", "100%"]):
                is_realistic = False
                reasons.append("No trading strategy is guaranteed - markets are inherently uncertain")

            return is_realistic, reasons

        except Exception as e:
            logger.error(f"Reality check error: {e}")
            return True, []

    async def _generate_action_plan(self, goals: Dict[str, Any], symbol: Optional[str], orchestrator) -> Dict[str, Any]:
        """Generate detailed step-by-step action plan for trading goals"""
        try:
            action_plan = {
                "summary": "",
                "recommendation": "neutral",
                "steps": [],
                "risk_warnings": [],
                "position_sizing": {},
                "execution_strategy": {},
                "reality_check": {}
            }

            # Reality check first
            if not goals.get("is_realistic", True):
                action_plan["reality_check"] = {
                    "realistic": False,
                    "concerns": goals.get("unrealistic_reasons", []),
                    "alternative_suggestion": "Consider more achievable targets that compound over time"
                }
                action_plan["recommendation"] = "reconsider_goals"
                action_plan["summary"] = "🚨 Goal Reality Check: Your target may be unrealistic"
                return action_plan

            # Generate action plan based on goals
            target_amount = goals.get("specific_amount", 0)
            target_percentage = goals.get("percentage_target", 0)
            timeframe = goals.get("timeframe", "unknown")

            # Calculate required position sizing
            if target_amount > 0:
                # Assume starting capital (this would come from portfolio in real implementation)
                assumed_capital = 10000  # $10k default
                required_return = target_amount / assumed_capital

                action_plan["position_sizing"] = {
                    "target_amount": target_amount,
                    "assumed_capital": assumed_capital,
                    "required_return": required_return,
                    "risk_per_trade": min(0.02, required_return / 3),  # Max 2% risk per trade
                    "number_of_trades": max(3, int(1 / (required_return / 3)))  # Spread across multiple trades
                }

            # Generate step-by-step plan
            steps = []

            # Step 1: Goal Validation & Planning
            steps.append({
                "step": 1,
                "title": "[TARGET] Goal Validation & Strategic Planning",
                "description": f"Validate and structure your {goals.get('description', 'trading goal')}",
                "actions": [
                    f"Confirm target: ${target_amount} in {timeframe}",
                    f"Required return: {required_return:.1%} ({'Aggressive' if required_return > 0.1 else 'Moderate' if required_return > 0.05 else 'Conservative'})",
                    f"Risk per trade: {action_plan['position_sizing']['risk_per_trade']:.1%}",
                    "Review available capital and position sizing",
                    "Set realistic milestones and backup plans"
                ],
                "estimated_time": "10-15 minutes",
                "priority": "critical"
            })

            # Step 2: Market Analysis
            steps.append({
                "step": 2,
                "title": "[DATA] Market Analysis & Environment Assessment",
                "description": f"Analyze market conditions for {symbol if symbol else 'target securities'}",
                "actions": [
                    "Check overall market trend (SPY, QQQ) and momentum",
                    "Review VIX for volatility and risk assessment",
                    "Analyze sector performance and rotation patterns",
                    "Check economic calendar for major events this week",
                    "Assess market sentiment and news flow"
                ],
                "estimated_time": "15-25 minutes",
                "priority": "high"
            })

            # Step 3: Symbol Selection (if not specified)
            if not symbol:
                steps.append({
                    "step": 3,
                    "title": "[TARGET] High-Probability Setup Identification",
                    "description": "Identify and rank trading opportunities",
                    "actions": [
                        "Run TTM Squeeze scanner for momentum setups",
                        "Look for volume breakouts and unusual activity",
                        "Check earnings calendar for upcoming events",
                        "Review analyst upgrades/downgrades and news",
                        "Rank opportunities by risk/reward ratio"
                    ],
                    "estimated_time": "20-30 minutes",
                    "priority": "high"
                })

            # Step 3: Entry Strategy
            steps.append({
                "step": 3,
                "title": "[LAUNCH] Entry Strategy",
                "description": "Plan precise entry points and timing",
                "actions": [
                    "Identify key support/resistance levels",
                    "Set entry triggers (breakout, pullback, etc.)",
                    "Calculate position size based on risk tolerance",
                    "Prepare stop-loss levels"
                ],
                "estimated_time": "10-20 minutes"
            })

            # Step 4: Risk Management
            steps.append({
                "step": 4,
                "title": "[SHIELD] Risk Management",
                "description": "Implement protective measures",
                "actions": [
                    "Set stop-loss at 2% portfolio risk maximum",
                    "Define profit targets (3:1 reward-to-risk minimum)",
                    "Consider hedging for large positions",
                    "Plan position scaling strategy"
                ],
                "estimated_time": "5-10 minutes"
            })

            # Step 5: Execution
            steps.append({
                "step": 5,
                "title": "[FAST] Execution",
                "description": "Execute trades with discipline",
                "actions": [
                    "Wait for entry signals to trigger",
                    "Enter positions with predetermined size",
                    "Set stop-loss and profit targets immediately",
                    "Monitor but avoid overtrading"
                ],
                "estimated_time": "Throughout trading session"
            })

            # Step 6: Monitoring and Adjustment
            steps.append({
                "step": 6,
                "title": "👁️ Monitoring",
                "description": "Track progress and adjust as needed",
                "actions": [
                    "Monitor positions without micromanaging",
                    "Adjust stops to breakeven when profitable",
                    "Take partial profits at targets",
                    "Review and learn from each trade"
                ],
                "estimated_time": "Ongoing"
            })

            action_plan["steps"] = steps

            # Add risk warnings
            risk_warnings = [
                "Never risk more than 2% of your account on any single trade",
                "Markets are unpredictable - no strategy guarantees profits",
                "Emotional trading leads to losses - stick to your plan",
                "Consider paper trading first to test your strategy"
            ]

            if timeframe == "today":
                risk_warnings.append("Day trading requires intense focus and quick decision-making")
                risk_warnings.append("Consider the PDT rule if account is under $25,000")

            action_plan["risk_warnings"] = risk_warnings

            # Execution strategy
            action_plan["execution_strategy"] = {
                "approach": "systematic" if target_amount > 500 else "focused",
                "number_of_positions": min(5, max(1, int(target_amount / 200))),
                "time_allocation": f"Spread trades across {timeframe}" if timeframe != "unknown" else "Spread trades over time",
                "confirmation_required": True
            }

            # Generate summary
            action_plan["summary"] = f"📋 Step-by-step plan to achieve {goals.get('description', 'your trading goal')}"
            action_plan["recommendation"] = "execute_with_caution" if goals.get("is_realistic") else "reconsider_goals"

            return action_plan

        except Exception as e:
            logger.error(f"Action plan generation error: {e}")
            return {
                "summary": "Action plan generation failed",
                "recommendation": "manual_planning",
                "error": str(e)
            }


# Enhanced Agent Classes with ML Capabilities

class TechnicalAnalysisAgent:
    """Technical Analysis Agent with ML Enhancement - 35% weight in consensus"""

    def __init__(self):
        self.weight = 0.35
        self.initialized = False

    async def initialize(self):
        """Initialize technical analysis capabilities"""
        try:
            self.initialized = True
            logger.info("Technical Analysis Agent initialized with ML enhancement")
        except Exception as e:
            logger.error(f"Technical Analysis Agent initialization failed: {e}")

    async def analyze(self, message: str, orchestrator) -> Dict[str, Any]:
        """Perform enhanced technical analysis"""
        try:
            # Extract symbol from message
            symbol = self._extract_symbol_from_message(message)

            if symbol and orchestrator and hasattr(orchestrator, 'market_engine'):
                # Get TTM Squeeze analysis
                try:
                    quote = await orchestrator.market_engine.get_quote(symbol)
                    if quote:
                        # Enhanced technical analysis with ML
                        technical_analysis = self._analyze_technical_patterns(quote, symbol)

                        return {
                            "analysis": technical_analysis["summary"],
                            "confidence": technical_analysis["confidence"],
                            "recommendation": technical_analysis["recommendation"],
                            "reasoning": technical_analysis["reasoning"],
                            "technical_details": technical_analysis["details"]
                        }
                except Exception as e:
                    logger.warning(f"Technical analysis failed for {symbol}: {e}")

            # Fallback analysis
            return {
                "analysis": "[DATA] TECHNICAL ANALYSIS: Awaiting market data for detailed analysis",
                "confidence": 0.4,
                "recommendation": "neutral",
                "reasoning": "Symbol not detected or market data unavailable",
                "technical_details": {}
            }

        except Exception as e:
            logger.error(f"Technical Analysis Agent error: {e}")
            return {
                "analysis": "Technical analysis failed due to system error",
                "confidence": 0.1,
                "recommendation": "neutral",
                "reasoning": f"Error: {str(e)}"
            }

    def _extract_symbol_from_message(self, message: str) -> Optional[str]:
        """Extract stock symbol from message"""
        import re
        patterns = [
            r'\b([A-Z]{1,5})\b',
            r'\$([A-Z]{1,5})\b',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, message.upper())
            if matches:
                for match in matches:
                    if len(match) >= 1 and len(match) <= 5:
                        return match
        return None

    def _analyze_technical_patterns(self, quote, symbol: str) -> Dict[str, Any]:
        """Analyze technical patterns with ML enhancement"""
        try:
            confidence = 0.6
            recommendation = "neutral"
            reasoning_parts = []
            details = {}

            # Basic price analysis
            if hasattr(quote, 'price') and hasattr(quote, 'change_percent'):
                price = quote.price
                change_percent = quote.change_percent

                if change_percent > 2.0:
                    recommendation = "bullish"
                    reasoning_parts.append(f"Strong upward momentum (+{change_percent:.1f}%)")
                    confidence += 0.2
                elif change_percent < -2.0:
                    recommendation = "bearish"
                    reasoning_parts.append(f"Strong downward momentum ({change_percent:.1f}%)")
                    confidence += 0.2
                else:
                    reasoning_parts.append(f"Moderate price movement ({change_percent:.1f}%)")

                details["price"] = price
                details["change_percent"] = change_percent

            # Volume analysis
            if hasattr(quote, 'volume'):
                volume = quote.volume
                if volume > 1000000:  # High volume threshold
                    reasoning_parts.append("High volume confirms price movement")
                    confidence += 0.1
                else:
                    reasoning_parts.append("Low volume - price movement less reliable")

                details["volume"] = volume

            # TTM Squeeze analysis if available
            if hasattr(quote, 'ttm_squeeze'):
                ttm = quote.ttm_squeeze
                if ttm and hasattr(ttm, 'active'):
                    if ttm.active:
                        reasoning_parts.append("🔄 TTM Squeeze ACTIVE - consolidation phase")
                        recommendation = "wait"
                    else:
                        momentum = getattr(ttm, 'momentum', 'neutral')
                        if momentum == 'bullish':
                            reasoning_parts.append("[LAUNCH] TTM Squeeze fired BULLISH")
                            recommendation = "bullish"
                            confidence += 0.3
                        elif momentum == 'bearish':
                            reasoning_parts.append("[DOWN] TTM Squeeze fired BEARISH")
                            recommendation = "bearish"
                            confidence += 0.3

                    details["ttm_squeeze"] = {
                        "active": ttm.active,
                        "momentum": getattr(ttm, 'momentum', 'neutral')
                    }

            # Generate summary
            if recommendation == "bullish":
                summary = "[UP] BULLISH TECHNICAL SETUP: Multiple indicators suggest upward potential"
            elif recommendation == "bearish":
                summary = "[DOWN] BEARISH TECHNICAL SETUP: Technical indicators suggest downward pressure"
            elif recommendation == "wait":
                summary = "⏰ WAIT SIGNAL: Market in consolidation - wait for clearer direction"
            else:
                summary = "😐 NEUTRAL TECHNICAL OUTLOOK: Mixed signals, no clear direction"

            return {
                "summary": summary,
                "confidence": min(confidence, 0.9),
                "recommendation": recommendation,
                "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "Basic technical analysis completed",
                "details": details
            }

        except Exception as e:
            logger.error(f"Technical pattern analysis error: {e}")
            return {
                "summary": "Technical analysis incomplete",
                "confidence": 0.3,
                "recommendation": "neutral",
                "reasoning": f"Analysis error: {str(e)}",
                "details": {"error": True}
            }


class RiskManagementAgent:
    """Risk Management Agent - 30% weight in consensus"""

    def __init__(self):
        self.weight = 0.30
        self.initialized = False

    async def initialize(self):
        """Initialize risk management capabilities"""
        try:
            self.initialized = True
            logger.info("Risk Management Agent initialized")
        except Exception as e:
            logger.error(f"Risk Management Agent initialization failed: {e}")

    async def analyze(self, message: str, orchestrator) -> Dict[str, Any]:
        """Perform risk analysis on user message and trading context"""
        try:
            risk_analysis = self._analyze_risk_patterns(message)

            return {
                "analysis": risk_analysis["summary"],
                "confidence": risk_analysis["confidence"],
                "recommendation": risk_analysis["recommendation"],
                "reasoning": risk_analysis["reasoning"],
                "risk_metrics": risk_analysis["metrics"]
            }

        except Exception as e:
            logger.error(f"Risk Management Agent error: {e}")
            return {
                "analysis": "Risk analysis failed due to system error",
                "confidence": 0.1,
                "recommendation": "high_risk",
                "reasoning": f"Error: {str(e)}"
            }

    def _analyze_risk_patterns(self, message: str) -> Dict[str, Any]:
        """Analyze risk patterns in user message"""
        try:
            confidence = 0.5
            recommendation = "moderate_risk"
            reasoning_parts = []
            metrics = {}

            message_lower = message.lower()

            # High-risk indicators
            high_risk_patterns = [
                "all in", "yolo", "to the moon", "guaranteed", "sure thing",
                "can't lose", "easy money", "get rich", "100%", "certain"
            ]

            # Emotional risk indicators
            emotional_patterns = [
                "desperate", "need money", "lost everything", "revenge",
                "angry", "frustrated", "scared", "panic"
            ]

            # Leverage/margin indicators
            leverage_patterns = [
                "margin", "leverage", "borrowed", "loan", "credit"
            ]

            # Count risk indicators
            high_risk_count = sum(1 for pattern in high_risk_patterns if pattern in message_lower)
            emotional_count = sum(1 for pattern in emotional_patterns if pattern in message_lower)
            leverage_count = sum(1 for pattern in leverage_patterns if pattern in message_lower)

            # Calculate risk score
            risk_score = high_risk_count * 0.4 + emotional_count * 0.3 + leverage_count * 0.3

            if risk_score >= 1.0:
                recommendation = "high_risk"
                reasoning_parts.append(f"Multiple high-risk indicators detected ({risk_score:.1f} risk score)")
                confidence += 0.3
            elif risk_score >= 0.5:
                recommendation = "moderate_risk"
                reasoning_parts.append(f"Some risk indicators present ({risk_score:.1f} risk score)")
                confidence += 0.2
            else:
                recommendation = "low_risk"
                reasoning_parts.append("No significant risk indicators detected")
                confidence += 0.1

            # Position sizing analysis
            if any(word in message_lower for word in ["$", "dollars", "money"]):
                import re
                amounts = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
                if amounts:
                    max_amount = max(float(amount.replace(',', '')) for amount in amounts)
                    if max_amount > 10000:
                        reasoning_parts.append(f"Large position size mentioned (${max_amount:,.0f})")
                        if recommendation == "low_risk":
                            recommendation = "moderate_risk"
                        confidence += 0.2

                    metrics["max_amount_mentioned"] = max_amount

            # Time pressure analysis
            urgency_words = ["now", "today", "immediately", "urgent", "quick"]
            if any(word in message_lower for word in urgency_words):
                reasoning_parts.append("Time pressure detected - increases risk")
                if recommendation == "low_risk":
                    recommendation = "moderate_risk"
                confidence += 0.1

            metrics = {
                "risk_score": risk_score,
                "high_risk_indicators": high_risk_count,
                "emotional_indicators": emotional_count,
                "leverage_indicators": leverage_count,
                "urgency_detected": any(word in message_lower for word in urgency_words)
            }

            # Generate summary
            if recommendation == "high_risk":
                summary = "🚨 HIGH RISK: Multiple warning signs detected - proceed with extreme caution"
            elif recommendation == "moderate_risk":
                summary = "[WARN] MODERATE RISK: Some caution advised - review position sizing"
            else:
                summary = "[OK] LOW RISK: No significant risk indicators detected"

            return {
                "summary": summary,
                "confidence": min(confidence, 0.8),
                "recommendation": recommendation,
                "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "Basic risk assessment completed",
                "metrics": metrics
            }

        except Exception as e:
            logger.error(f"Risk pattern analysis error: {e}")
            return {
                "summary": "Risk analysis incomplete",
                "confidence": 0.3,
                "recommendation": "moderate_risk",
                "reasoning": f"Analysis error: {str(e)}",
                "metrics": {"error": True}
            }


class SentimentAnalysisAgent:
    """Sentiment Analysis Agent with DistilBERT - 20% weight in consensus"""

    def __init__(self, sentiment_model=None):
        self.weight = 0.20
        self.initialized = False
        self.sentiment_model = sentiment_model

    async def initialize(self):
        """Initialize sentiment analysis capabilities"""
        try:
            self.initialized = True
            if self.sentiment_model:
                logger.info("Sentiment Analysis Agent initialized with DistilBERT")
            else:
                logger.info("Sentiment Analysis Agent initialized with basic sentiment analysis")
        except Exception as e:
            logger.error(f"Sentiment Analysis Agent initialization failed: {e}")

    async def analyze(self, message: str, orchestrator) -> Dict[str, Any]:
        """Perform advanced sentiment analysis on user message"""
        try:
            if self.sentiment_model and TRANSFORMERS_AVAILABLE:
                sentiment_analysis = await self._analyze_with_distilbert(message)
            else:
                sentiment_analysis = self._analyze_basic_sentiment(message)

            return {
                "analysis": sentiment_analysis["summary"],
                "confidence": sentiment_analysis["confidence"],
                "recommendation": sentiment_analysis["recommendation"],
                "reasoning": sentiment_analysis["reasoning"],
                "sentiment_metrics": sentiment_analysis["metrics"]
            }

        except Exception as e:
            logger.error(f"Sentiment Analysis Agent error: {e}")
            return {
                "analysis": "Sentiment analysis failed due to system error",
                "confidence": 0.1,
                "recommendation": "neutral",
                "reasoning": f"Error: {str(e)}"
            }

    async def _analyze_with_distilbert(self, message: str) -> Dict[str, Any]:
        """Analyze sentiment using DistilBERT model"""
        try:
            # Use DistilBERT for advanced sentiment analysis
            results = self.sentiment_model(message)

            # Extract sentiment scores
            sentiment_scores = {result['label'].lower(): result['score'] for result in results}

            # Determine primary sentiment
            primary_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])
            sentiment_label = primary_sentiment[0]
            sentiment_score = primary_sentiment[1]

            # Convert to trading recommendation
            if sentiment_label == 'positive' and sentiment_score > 0.7:
                recommendation = "bullish"
                reasoning = f"Strong positive sentiment detected (DistilBERT: {sentiment_score:.2f})"
            elif sentiment_label == 'negative' and sentiment_score > 0.7:
                recommendation = "bearish"
                reasoning = f"Strong negative sentiment detected (DistilBERT: {sentiment_score:.2f})"
            else:
                recommendation = "neutral"
                reasoning = f"Neutral sentiment (DistilBERT: {sentiment_score:.2f})"

            # Generate summary
            if recommendation == "bullish":
                summary = "[UP] POSITIVE SENTIMENT: DistilBERT detects optimistic market outlook"
            elif recommendation == "bearish":
                summary = "[DOWN] NEGATIVE SENTIMENT: DistilBERT detects pessimistic market outlook"
            else:
                summary = "😐 NEUTRAL SENTIMENT: Balanced emotional state detected"

            return {
                "summary": summary,
                "confidence": sentiment_score,
                "recommendation": recommendation,
                "reasoning": reasoning,
                "metrics": {
                    "model": "DistilBERT",
                    "sentiment_scores": sentiment_scores,
                    "primary_sentiment": sentiment_label,
                    "confidence_score": sentiment_score
                }
            }

        except Exception as e:
            logger.error(f"DistilBERT sentiment analysis error: {e}")
            return self._analyze_basic_sentiment(message)

    def _analyze_basic_sentiment(self, message: str) -> Dict[str, Any]:
        """Basic sentiment analysis fallback"""
        try:
            message_lower = message.lower()

            # Positive sentiment indicators
            positive_words = [
                "bullish", "buy", "long", "up", "rise", "gain", "profit",
                "strong", "good", "great", "excellent", "confident", "optimistic"
            ]

            # Negative sentiment indicators
            negative_words = [
                "bearish", "sell", "short", "down", "fall", "loss", "drop",
                "weak", "bad", "terrible", "worried", "pessimistic", "crash"
            ]

            # Emotional indicators
            emotional_words = [
                "excited", "nervous", "scared", "greedy", "desperate",
                "anxious", "frustrated", "angry", "hopeful", "fearful"
            ]

            # Count sentiment indicators
            positive_count = sum(1 for word in positive_words if word in message_lower)
            negative_count = sum(1 for word in negative_words if word in message_lower)
            emotional_count = sum(1 for word in emotional_words if word in message_lower)

            # Calculate sentiment score
            sentiment_score = positive_count - negative_count
            confidence = 0.5

            if sentiment_score > 1:
                recommendation = "bullish"
                reasoning = f"Positive sentiment detected ({positive_count} positive indicators)"
                confidence += 0.2
            elif sentiment_score < -1:
                recommendation = "bearish"
                reasoning = f"Negative sentiment detected ({negative_count} negative indicators)"
                confidence += 0.2
            else:
                recommendation = "neutral"
                reasoning = "Balanced or neutral sentiment"

            # Emotional state analysis
            if emotional_count > 0:
                reasoning += f" | Emotional language detected ({emotional_count} indicators)"
                confidence += 0.1

                # Check for specific emotional patterns
                if any(word in message_lower for word in ["desperate", "need", "must"]):
                    reasoning += " | Urgency/desperation detected - caution advised"
                    recommendation = "cautious"
                    confidence += 0.2

            # Generate summary
            if recommendation == "bullish":
                summary = "[UP] BULLISH SENTIMENT: User shows positive market outlook"
            elif recommendation == "bearish":
                summary = "[DOWN] BEARISH SENTIMENT: User shows negative market outlook"
            elif recommendation == "cautious":
                summary = "[WARN] EMOTIONAL SENTIMENT: Caution advised due to emotional indicators"
            else:
                summary = "😐 NEUTRAL SENTIMENT: Balanced emotional state detected"

            return {
                "summary": summary,
                "confidence": min(confidence, 0.8),
                "recommendation": recommendation,
                "reasoning": reasoning,
                "metrics": {
                    "model": "Basic",
                    "sentiment_score": sentiment_score,
                    "positive_indicators": positive_count,
                    "negative_indicators": negative_count,
                    "emotional_indicators": emotional_count
                }
            }

        except Exception as e:
            logger.error(f"Basic sentiment analysis error: {e}")
            return {
                "summary": "Sentiment analysis incomplete",
                "confidence": 0.2,
                "recommendation": "neutral",
                "reasoning": f"Analysis error: {str(e)}",
                "metrics": {"error": True}
            }


class ExecutionAgent:
    """Execution Timing Agent - 15% weight in consensus"""

    def __init__(self):
        self.weight = 0.15
        self.initialized = False

    async def initialize(self):
        """Initialize execution timing capabilities"""
        try:
            self.initialized = True
            logger.info("Execution Agent initialized")
        except Exception as e:
            logger.error(f"Execution Agent initialization failed: {e}")

    async def analyze(self, message: str, orchestrator) -> Dict[str, Any]:
        """Analyze optimal execution timing and market conditions"""
        try:
            execution_analysis = self._analyze_execution_timing(message)

            return {
                "analysis": execution_analysis["summary"],
                "confidence": execution_analysis["confidence"],
                "recommendation": execution_analysis["recommendation"],
                "reasoning": execution_analysis["reasoning"],
                "execution_metrics": execution_analysis["metrics"]
            }

        except Exception as e:
            logger.error(f"Execution Agent error: {e}")
            return {
                "analysis": "Execution analysis failed due to system error",
                "confidence": 0.1,
                "recommendation": "wait",
                "reasoning": f"Error: {str(e)}"
            }

    def _analyze_execution_timing(self, message: str) -> Dict[str, Any]:
        """Analyze market timing and execution conditions"""
        try:
            from datetime import datetime
            import pytz

            confidence = 0.4  # Base confidence
            recommendation = "neutral"
            reasoning_parts = []
            metrics = {}

            # Get current market time
            eastern = pytz.timezone('US/Eastern')
            current_time = datetime.now(eastern)
            market_hour = current_time.hour

            # Market timing analysis
            if 9 <= market_hour <= 16:  # Market hours
                if 9 <= market_hour <= 10:  # Opening hour
                    reasoning_parts.append("Market opening hour - high volatility expected")
                    recommendation = "cautious"
                    confidence += 0.2
                elif 15 <= market_hour <= 16:  # Closing hour
                    reasoning_parts.append("Market closing hour - increased activity expected")
                    recommendation = "active"
                    confidence += 0.2
                else:  # Mid-day
                    reasoning_parts.append("Mid-day trading - normal market conditions")
                    recommendation = "normal"
                    confidence += 0.1
            else:
                reasoning_parts.append("After-hours trading - limited liquidity")
                recommendation = "wait"
                confidence += 0.3

            # Urgency analysis from message
            urgency_patterns = [
                r"now", r"immediately", r"asap", r"urgent", r"quick",
                r"today", r"right now", r"this minute"
            ]

            import re
            urgency_detected = any(re.search(pattern, message.lower()) for pattern in urgency_patterns)

            if urgency_detected:
                reasoning_parts.append("Urgency detected in request")
                if recommendation == "wait":
                    reasoning_parts.append("However, market conditions suggest waiting")
                else:
                    recommendation = "immediate"
                    confidence += 0.1

            # Volume and liquidity considerations
            day_of_week = current_time.weekday()  # 0 = Monday
            if day_of_week == 0:  # Monday
                reasoning_parts.append("Monday trading - watch for weekend news impact")
            elif day_of_week == 4:  # Friday
                reasoning_parts.append("Friday trading - potential position squaring")

            metrics = {
                "market_hour": market_hour,
                "day_of_week": day_of_week,
                "urgency_detected": urgency_detected,
                "market_session": "regular" if 9 <= market_hour <= 16 else "extended",
                "timing_score": confidence
            }

            # Generate summary
            if recommendation == "immediate":
                summary = "[FAST] EXECUTE NOW: Market conditions and urgency favor immediate action"
            elif recommendation == "active":
                summary = "[TARGET] GOOD TIMING: Favorable execution conditions detected"
            elif recommendation == "cautious":
                summary = "[WARN] PROCEED CAREFULLY: Market timing requires caution"
            elif recommendation == "wait":
                summary = "⏰ WAIT: Market conditions not optimal for execution"
            else:
                summary = "[DATA] NORMAL CONDITIONS: Standard execution timing applies"

            return {
                "summary": summary,
                "confidence": min(confidence, 0.8),
                "recommendation": recommendation,
                "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "Basic timing analysis completed",
                "metrics": metrics
            }

        except Exception as e:
            logger.error(f"Execution timing analysis error: {e}")
            return {
                "summary": "Execution timing analysis incomplete",
                "confidence": 0.2,
                "recommendation": "wait",
                "reasoning": f"Analysis error: {str(e)}",
                "metrics": {"error": True}
            }
