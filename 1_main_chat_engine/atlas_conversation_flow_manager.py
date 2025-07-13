"""
A.T.L.A.S Conversation Flow Manager - Sophisticated Dialogue Management
Enables seamless transitions between system features through natural conversation flow
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from config import settings
from models import AIResponse, EngineStatus, EmotionalState, CommunicationMode

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation state enumeration"""
    GREETING = "greeting"
    STOCK_ANALYSIS = "stock_analysis"
    MARKET_SCANNING = "market_scanning"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    OPTIONS_TRADING = "options_trading"
    EDUCATION = "education"
    RISK_MANAGEMENT = "risk_management"
    GENERAL_CHAT = "general_chat"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"


@dataclass
class ConversationContext:
    """Conversation context data structure"""
    session_id: str
    current_state: ConversationState
    previous_states: List[ConversationState]
    active_symbols: List[str]
    user_preferences: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    pending_actions: List[Dict[str, Any]]
    last_analysis: Optional[Dict[str, Any]]
    emotional_state: EmotionalState
    expertise_level: str  # beginner, intermediate, advanced
    created_at: datetime
    last_activity: datetime


class ConversationFlowManager:
    """
    Sophisticated dialogue management for seamless feature transitions
    Maintains context and provides intelligent conversation flow
    """

    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        
        # Conversation management
        self.active_conversations = {}
        self.conversation_templates = {}
        self.transition_rules = {}
        self.suggestion_engine = ConversationSuggestionEngine()
        
        # Flow configuration
        self.max_conversation_history = 50
        self.context_retention_hours = 24
        self.suggestion_threshold = 0.7
        
        # Initialize conversation flow rules
        self._initialize_conversation_templates()
        self._initialize_transition_rules()
        
        logger.info("[CHAT] Conversation Flow Manager created")

    async def initialize(self):
        """Initialize the conversation flow manager"""
        try:
            self.status = EngineStatus.INITIALIZING
            
            # Initialize suggestion engine
            await self.suggestion_engine.initialize()
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Conversation Flow Manager fully initialized")
            
        except Exception as e:
            logger.error(f"Conversation Flow Manager initialization failed: {e}")
            self.status = EngineStatus.FAILED
            raise

    async def process_conversation_turn(self, message: str, session_id: str, 
                                      system_response: AIResponse) -> Dict[str, Any]:
        """
        Process a conversation turn and manage flow transitions
        """
        try:
            # Get or create conversation context
            context = self._get_conversation_context(session_id)
            
            # Analyze conversation intent and determine state
            intent_analysis = await self._analyze_conversation_intent(message, context)
            
            # Update conversation state
            new_state = await self._determine_conversation_state(intent_analysis, context)
            await self._update_conversation_state(context, new_state, message, system_response)
            
            # Generate conversation flow enhancements
            flow_enhancements = await self._generate_flow_enhancements(context, system_response)
            
            # Generate intelligent suggestions
            suggestions = await self.suggestion_engine.generate_suggestions(context, intent_analysis)
            
            # Update conversation context
            context.last_activity = datetime.now()
            self.active_conversations[session_id] = context
            
            return {
                "conversation_context": context,
                "flow_enhancements": flow_enhancements,
                "suggestions": suggestions,
                "state_transition": {
                    "previous_state": context.previous_states[-1] if context.previous_states else None,
                    "current_state": context.current_state,
                    "transition_reason": intent_analysis.get("transition_reason")
                }
            }
            
        except Exception as e:
            logger.error(f"Conversation turn processing failed: {e}")
            return {"error": str(e)}

    def _get_conversation_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context"""
        if session_id not in self.active_conversations:
            self.active_conversations[session_id] = ConversationContext(
                session_id=session_id,
                current_state=ConversationState.GREETING,
                previous_states=[],
                active_symbols=[],
                user_preferences={},
                conversation_history=[],
                pending_actions=[],
                last_analysis=None,
                emotional_state=EmotionalState.NEUTRAL,
                expertise_level="beginner",
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
        
        return self.active_conversations[session_id]

    async def _analyze_conversation_intent(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Analyze conversation intent and context"""
        intent = {
            "message": message,
            "detected_symbols": self._extract_symbols(message),
            "intent_type": self._classify_intent(message),
            "emotional_indicators": self._detect_emotional_indicators(message),
            "expertise_indicators": self._detect_expertise_level(message),
            "follow_up_indicators": self._detect_follow_up_intent(message, context),
            "transition_reason": None
        }
        
        # Determine if this is a natural transition
        if context.current_state != ConversationState.GREETING:
            intent["transition_reason"] = self._analyze_transition_reason(message, context)
        
        return intent

    async def _determine_conversation_state(self, intent_analysis: Dict[str, Any], 
                                          context: ConversationContext) -> ConversationState:
        """Determine the appropriate conversation state"""
        message = intent_analysis["message"].lower()
        intent_type = intent_analysis["intent_type"]
        
        # State determination logic
        if any(word in message for word in ["hello", "hi", "hey", "start"]):
            return ConversationState.GREETING
        elif intent_type == "stock_analysis" or intent_analysis["detected_symbols"]:
            return ConversationState.STOCK_ANALYSIS
        elif any(word in message for word in ["scan", "find", "search", "opportunities"]):
            return ConversationState.MARKET_SCANNING
        elif any(word in message for word in ["portfolio", "optimize", "allocation"]):
            return ConversationState.PORTFOLIO_MANAGEMENT
        elif any(word in message for word in ["options", "strategy", "hedge", "greeks"]):
            return ConversationState.OPTIONS_TRADING
        elif any(word in message for word in ["learn", "teach", "explain", "education"]):
            return ConversationState.EDUCATION
        elif any(word in message for word in ["risk", "safety", "protect", "stop"]):
            return ConversationState.RISK_MANAGEMENT
        elif intent_analysis["follow_up_indicators"]:
            return ConversationState.FOLLOW_UP
        else:
            return ConversationState.GENERAL_CHAT

    async def _update_conversation_state(self, context: ConversationContext, new_state: ConversationState,
                                       message: str, system_response: AIResponse):
        """Update conversation state and history"""
        # Update state history
        if context.current_state != new_state:
            context.previous_states.append(context.current_state)
            context.current_state = new_state
            
            # Keep only recent state history
            if len(context.previous_states) > 10:
                context.previous_states = context.previous_states[-10:]
        
        # Update conversation history
        conversation_entry = {
            "timestamp": datetime.now(),
            "user_message": message,
            "system_response": system_response.response,
            "state": new_state.value,
            "confidence": system_response.confidence,
            "response_type": system_response.type
        }
        
        context.conversation_history.append(conversation_entry)
        
        # Keep only recent conversation history
        if len(context.conversation_history) > self.max_conversation_history:
            context.conversation_history = context.conversation_history[-self.max_conversation_history:]
        
        # Update active symbols
        detected_symbols = self._extract_symbols(message)
        for symbol in detected_symbols:
            if symbol not in context.active_symbols:
                context.active_symbols.append(symbol)
        
        # Keep only recent symbols
        if len(context.active_symbols) > 10:
            context.active_symbols = context.active_symbols[-10:]

    async def _generate_flow_enhancements(self, context: ConversationContext, 
                                        system_response: AIResponse) -> Dict[str, Any]:
        """Generate conversation flow enhancements"""
        enhancements = {
            "context_continuity": self._generate_context_continuity(context),
            "natural_transitions": self._generate_natural_transitions(context),
            "proactive_suggestions": self._generate_proactive_suggestions(context),
            "conversation_memory": self._generate_conversation_memory(context)
        }
        
        return enhancements

    def _generate_context_continuity(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate context continuity information"""
        return {
            "active_symbols": context.active_symbols,
            "recent_states": [state.value for state in context.previous_states[-3:]],
            "conversation_theme": self._identify_conversation_theme(context),
            "user_focus": self._identify_user_focus(context)
        }

    def _generate_natural_transitions(self, context: ConversationContext) -> List[str]:
        """Generate natural transition suggestions"""
        transitions = []
        current_state = context.current_state
        
        # State-specific transition suggestions
        if current_state == ConversationState.STOCK_ANALYSIS and context.active_symbols:
            symbol = context.active_symbols[-1]
            transitions.extend([
                f"Would you like me to scan for similar opportunities to {symbol}?",
                f"I can also analyze options strategies for {symbol} if you're interested.",
                f"Should I check the risk profile for a position in {symbol}?"
            ])
        
        elif current_state == ConversationState.MARKET_SCANNING:
            transitions.extend([
                "Would you like me to analyze any of these opportunities in detail?",
                "I can help you assess the risk for any of these positions.",
                "Should I explain the technical patterns behind these signals?"
            ])
        
        elif current_state == ConversationState.EDUCATION:
            transitions.extend([
                "Would you like to see how this applies to current market conditions?",
                "I can find real examples of this concept in today's market.",
                "Should we practice this with a paper trading scenario?"
            ])
        
        return transitions[:3]  # Limit to 3 suggestions

    def _generate_proactive_suggestions(self, context: ConversationContext) -> List[str]:
        """Generate proactive suggestions based on context"""
        suggestions = []
        
        # Time-based suggestions
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 10:  # Market open
            suggestions.append("The market just opened - would you like a morning briefing?")
        elif 15 <= current_hour <= 16:  # Market close
            suggestions.append("Market is closing soon - should I summarize today's activity?")
        
        # Activity-based suggestions
        if len(context.active_symbols) > 1:
            suggestions.append("I notice you're tracking multiple symbols - would you like a comparison analysis?")
        
        if context.current_state == ConversationState.STOCK_ANALYSIS:
            suggestions.append("Would you like me to set up alerts for any significant changes?")
        
        return suggestions[:2]  # Limit to 2 proactive suggestions

    def _generate_conversation_memory(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate conversation memory references"""
        memory = {
            "recent_topics": [],
            "user_interests": [],
            "preferred_analysis_types": []
        }
        
        # Analyze recent conversation for patterns
        recent_history = context.conversation_history[-10:]
        
        # Extract topics
        for entry in recent_history:
            if entry["state"] in ["stock_analysis", "market_scanning"]:
                memory["recent_topics"].append(entry["state"])
        
        # Identify user interests
        state_counts = {}
        for entry in recent_history:
            state = entry["state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        
        if state_counts:
            most_common_state = max(state_counts, key=state_counts.get)
            memory["user_interests"].append(most_common_state)
        
        return memory

    def _initialize_conversation_templates(self):
        """Initialize conversation templates for different states"""
        self.conversation_templates = {
            ConversationState.GREETING: {
                "welcome_messages": [
                    "Hello! I'm Predicto, your AI stock analysis expert. What would you like to explore today?",
                    "Hi there! I'm here to help with stock analysis and trading insights. What's on your mind?",
                    "Welcome! I can analyze stocks, scan for opportunities, and help with trading decisions. How can I assist you?"
                ],
                "follow_up_prompts": [
                    "You can ask me to analyze any stock symbol, scan for trading opportunities, or explain trading concepts.",
                    "Try asking: 'Analyze AAPL' or 'Scan for TTM Squeeze signals' or 'Explain options trading'."
                ]
            },
            ConversationState.STOCK_ANALYSIS: {
                "transition_phrases": [
                    "Based on this analysis,",
                    "Looking at the data,",
                    "From what I can see,"
                ],
                "follow_up_suggestions": [
                    "Would you like me to analyze another symbol?",
                    "Should I scan for similar opportunities?",
                    "Would you like to see options strategies for this stock?"
                ]
            }
        }

    def _initialize_transition_rules(self):
        """Initialize conversation transition rules"""
        self.transition_rules = {
            (ConversationState.STOCK_ANALYSIS, ConversationState.MARKET_SCANNING): {
                "trigger_phrases": ["find similar", "scan for", "other opportunities"],
                "transition_message": "Let me scan the market for similar opportunities..."
            },
            (ConversationState.MARKET_SCANNING, ConversationState.STOCK_ANALYSIS): {
                "trigger_phrases": ["analyze", "tell me more about", "details on"],
                "transition_message": "Let me provide a detailed analysis..."
            },
            (ConversationState.STOCK_ANALYSIS, ConversationState.OPTIONS_TRADING): {
                "trigger_phrases": ["options", "strategy", "hedge"],
                "transition_message": "Let me explore options strategies for this stock..."
            }
        }

    # Helper methods
    def _extract_symbols(self, message: str) -> List[str]:
        """Extract stock symbols from message"""
        import re
        pattern = r'\b([A-Z]{1,5})\b'
        potential_symbols = re.findall(pattern, message)
        common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT'}
        return [symbol for symbol in potential_symbols if symbol not in common_words][:5]

    def _classify_intent(self, message: str) -> str:
        """Classify the intent of the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["analyze", "analysis", "look at"]):
            return "stock_analysis"
        elif any(word in message_lower for word in ["scan", "find", "search"]):
            return "market_scanning"
        elif any(word in message_lower for word in ["learn", "teach", "explain"]):
            return "education"
        elif any(word in message_lower for word in ["portfolio", "optimize"]):
            return "portfolio_management"
        elif any(word in message_lower for word in ["options", "strategy"]):
            return "options_trading"
        elif any(word in message_lower for word in ["risk", "safety"]):
            return "risk_management"
        else:
            return "general"

    def _detect_emotional_indicators(self, message: str) -> List[str]:
        """Detect emotional indicators in message"""
        indicators = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["worried", "concerned", "scared"]):
            indicators.append("anxiety")
        elif any(word in message_lower for word in ["excited", "bullish", "optimistic"]):
            indicators.append("excitement")
        elif any(word in message_lower for word in ["confused", "don't understand"]):
            indicators.append("confusion")
        
        return indicators

    def _detect_expertise_level(self, message: str) -> str:
        """Detect user expertise level from message"""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ["what is", "explain", "i'm new", "beginner"]):
            return "beginner"
        elif any(phrase in message_lower for phrase in ["advanced", "complex", "sophisticated"]):
            return "advanced"
        else:
            return "intermediate"

    def _detect_follow_up_intent(self, message: str, context: ConversationContext) -> bool:
        """Detect if message is a follow-up to previous conversation"""
        message_lower = message.lower()
        follow_up_indicators = [
            "also", "and", "what about", "how about", "can you", "tell me more",
            "explain that", "show me", "what if", "compare"
        ]
        
        return any(indicator in message_lower for indicator in follow_up_indicators)

    def _analyze_transition_reason(self, message: str, context: ConversationContext) -> Optional[str]:
        """Analyze reason for state transition"""
        # This would analyze why the conversation is transitioning
        return "natural_flow"

    def _identify_conversation_theme(self, context: ConversationContext) -> str:
        """Identify the overall theme of the conversation"""
        # Analyze conversation history to identify theme
        return "stock_analysis"

    def _identify_user_focus(self, context: ConversationContext) -> str:
        """Identify what the user is most focused on"""
        # Analyze user's primary interests
        return "learning"

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Conversation Flow Manager...")
        
        # Clear active conversations
        self.active_conversations.clear()
        
        # Cleanup suggestion engine
        await self.suggestion_engine.cleanup()
        
        logger.info("[OK] Conversation Flow Manager cleanup completed")

    def get_status(self) -> EngineStatus:
        """Get current status"""
        return self.status


class ConversationSuggestionEngine:
    """Engine for generating intelligent conversation suggestions"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SuggestionEngine")
    
    async def initialize(self):
        """Initialize suggestion engine"""
        self.logger.info("[OK] Conversation Suggestion Engine initialized")
    
    async def generate_suggestions(self, context: ConversationContext, 
                                 intent_analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent suggestions based on context"""
        suggestions = []
        
        # Context-based suggestions
        if context.active_symbols:
            symbol = context.active_symbols[-1]
            suggestions.append(f"Compare {symbol} with similar stocks")
            suggestions.append(f"Set up alerts for {symbol}")
        
        # State-based suggestions
        if context.current_state == ConversationState.STOCK_ANALYSIS:
            suggestions.extend([
                "Scan for similar opportunities",
                "Analyze options strategies",
                "Check risk assessment"
            ])
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    async def cleanup(self):
        """Cleanup resources"""
        pass
