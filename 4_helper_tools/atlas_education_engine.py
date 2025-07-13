"""
A.T.L.A.S Education Engine - RAG System with Trading Books
Educational Q&A with lazy ChromaDB loading and trading literature
"""

# CRITICAL: Import startup initialization FIRST to ensure Windows-compatible logging
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from atlas_startup_init import initialize_component_logging
    logger = initialize_component_logging('atlas_education_engine')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import settings
from models import EducationRequest, AIResponse, EngineStatus


class AtlasEducationEngine:
    """
    Education engine with RAG system and trading book knowledge base
    """
    
    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        
        # Vector database (lazy loaded)
        self._chroma_client = None
        self._collection = None
        self._embeddings_model = None
        
        # Knowledge base
        self.trading_books = {
            "trading_in_the_zone": "Trading in the Zone by Mark Douglas",
            "market_wizards": "Market Wizards by Jack Schwager",
            "reminiscences": "Reminiscences of a Stock Operator by Edwin Lefèvre",
            "technical_analysis": "Technical Analysis of Financial Markets by John Murphy",
            "options_strategies": "Options as a Strategic Investment by Lawrence McMillan"
        }
        
        # Educational content cache
        self.content_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Difficulty levels
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        
        logger.info("[LIBRARY] Education Engine created - ChromaDB will load on demand")
    
    async def initialize(self):
        """Initialize education engine with lazy loading"""
        try:
            # Initialize basic educational content
            await self._load_basic_content()
            
            # Test vector database connection (lazy)
            # ChromaDB will be loaded when first needed
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Education Engine initialization completed")
            
        except Exception as e:
            logger.error(f"[ERROR] Education Engine initialization failed: {e}")
            self.status = EngineStatus.DEGRADED
            # Continue with basic educational responses
    
    async def _ensure_chroma_client(self):
        """Ensure ChromaDB client is initialized"""
        if self._chroma_client is None:
            try:
                import chromadb
                from chromadb.config import Settings as ChromaSettings
                
                # Initialize ChromaDB client
                self._chroma_client = chromadb.Client(ChromaSettings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="./atlas_education_db"
                ))
                
                # Get or create collection
                self._collection = self._chroma_client.get_or_create_collection(
                    name="trading_education",
                    metadata={"description": "Trading education knowledge base"}
                )
                
                logger.info("[OK] ChromaDB client initialized")
                
                # Initialize embeddings if collection is empty
                if self._collection.count() == 0:
                    await self._initialize_knowledge_base()
                
            except ImportError:
                logger.warning("[WARN] ChromaDB not available - using fallback responses")
                self._chroma_client = "unavailable"
            except Exception as e:
                logger.error(f"[ERROR] ChromaDB initialization failed: {e}")
                self._chroma_client = "unavailable"
        
        return self._chroma_client if self._chroma_client != "unavailable" else None
    
    async def _load_basic_content(self):
        """Load basic educational content"""
        try:
            # Basic trading concepts
            self.basic_content = {
                "what_is_trading": {
                    "question": "What is trading?",
                    "answer": """Trading is the buying and selling of financial instruments like stocks, bonds, commodities, or currencies with the goal of making a profit. Unlike investing, which typically involves holding assets for longer periods, trading usually involves shorter-term positions to capitalize on price movements.
                    
Key aspects of trading:
• **Timeframes**: Day trading (minutes to hours), swing trading (days to weeks), position trading (weeks to months)
• **Analysis**: Technical analysis (charts, patterns) and fundamental analysis (company/economic data)
• **Risk Management**: Using stop losses, position sizing, and diversification
• **Psychology**: Managing emotions like fear and greed""",
                    "difficulty": "beginner",
                    "topics": ["basics", "introduction"]
                },
                
                "risk_management": {
                    "question": "What is risk management in trading?",
                    "answer": """Risk management is the process of identifying, analyzing, and controlling potential losses in trading. It's arguably the most important aspect of successful trading.
                    
Key risk management principles:
• **Position Sizing**: Never risk more than 1-2% of your account on a single trade
• **Stop Losses**: Predetermined exit points to limit losses
• **Diversification**: Don't put all your money in one stock or sector
• **Risk-Reward Ratio**: Aim for trades where potential profit is at least 2x potential loss
• **Emotional Control**: Stick to your plan and don't let emotions drive decisions""",
                    "difficulty": "beginner",
                    "topics": ["risk", "management", "basics"]
                },
                
                "technical_analysis": {
                    "question": "What is technical analysis?",
                    "answer": """Technical analysis is the study of price charts and trading volume to predict future price movements. It's based on the idea that all relevant information is already reflected in the price.
                    
Key technical analysis tools:
• **Chart Patterns**: Head and shoulders, triangles, flags, support/resistance
• **Indicators**: Moving averages, RSI, MACD, Bollinger Bands
• **Volume Analysis**: Confirming price movements with trading volume
• **Trend Analysis**: Identifying uptrends, downtrends, and sideways markets
• **Candlestick Patterns**: Reading price action through candlestick formations""",
                    "difficulty": "intermediate",
                    "topics": ["technical", "analysis", "charts"]
                }
            }
            
            logger.info("[BOOK] Basic educational content loaded")
            
        except Exception as e:
            logger.error(f"Error loading basic content: {e}")
    
    async def _initialize_knowledge_base(self):
        """Initialize knowledge base with trading book content"""
        try:
            if not self._collection:
                return
            
            # Comprehensive trading book content database
            book_excerpts = self._get_comprehensive_trading_content()
            
            # Add to ChromaDB
            for excerpt in book_excerpts:
                self._collection.add(
                    documents=[excerpt["text"]],
                    metadatas=[{
                        "source": excerpt["source"],
                        "topic": excerpt["topic"],
                        "difficulty": excerpt["difficulty"]
                    }],
                    ids=[excerpt["id"]]
                )
            
            logger.info(f"[LIBRARY] Knowledge base initialized with {len(book_excerpts)} excerpts")
            
        except Exception as e:
            logger.error(f"Knowledge base initialization error: {e}")
    
    async def process_query(self, request: EducationRequest) -> AIResponse:
        """Process educational query with RAG system"""
        try:
            question = request.question.lower()
            
            # Check cache first
            cache_key = f"{question}_{request.difficulty_level}"
            if cache_key in self.content_cache:
                cached_time = self.content_cache[cache_key]["timestamp"]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    cached_response = self.content_cache[cache_key]["response"]
                    return AIResponse(
                        response=cached_response,
                        type="education",
                        confidence=0.8,
                        context={"source": "cache"}
                    )
            
            # Try RAG system first
            rag_response = await self._query_knowledge_base(request)
            if rag_response:
                # Cache the response
                self.content_cache[cache_key] = {
                    "response": rag_response,
                    "timestamp": datetime.now()
                }
                
                return AIResponse(
                    response=rag_response,
                    type="education",
                    confidence=0.9,
                    context={"source": "knowledge_base"}
                )
            
            # Fallback to basic content
            basic_response = await self._query_basic_content(request)
            if basic_response:
                return AIResponse(
                    response=basic_response,
                    type="education",
                    confidence=0.7,
                    context={"source": "basic_content"}
                )
            
            # Final fallback
            return await self._generate_fallback_response(request)
            
        except Exception as e:
            logger.error(f"Education query processing error: {e}")
            return AIResponse(
                response="I encountered an error processing your educational query. Please try rephrasing your question.",
                type="error",
                confidence=0.0
            )
    
    async def _query_knowledge_base(self, request: EducationRequest) -> Optional[str]:
        """Query ChromaDB knowledge base"""
        try:
            client = await self._ensure_chroma_client()
            if not client or not self._collection:
                return None
            
            # Search for relevant content
            results = self._collection.query(
                query_texts=[request.question],
                n_results=3,
                where={"difficulty": request.difficulty_level} if request.difficulty_level != "beginner" else None
            )
            
            if results["documents"] and len(results["documents"][0]) > 0:
                # Combine relevant excerpts
                relevant_content = []
                for i, doc in enumerate(results["documents"][0]):
                    source = results["metadatas"][0][i]["source"]
                    relevant_content.append(f"From '{source}':\n{doc}")
                
                # Generate comprehensive response
                combined_content = "\n\n".join(relevant_content)
                
                response = f"""Based on trading literature, here's what I found about your question:

{combined_content}

**Key Takeaways:**
• This information comes from respected trading books and experts
• Consider your experience level when applying these concepts
• Always practice risk management in your trading

Would you like me to explain any of these concepts in more detail?"""
                
                return response
            
        except Exception as e:
            logger.error(f"Knowledge base query error: {e}")
        
        return None
    
    async def _query_basic_content(self, request: EducationRequest) -> Optional[str]:
        """Query basic educational content"""
        try:
            question_lower = request.question.lower()
            
            # Simple keyword matching
            for content_id, content in self.basic_content.items():
                content_text = content["answer"].lower()
                question_text = content["question"].lower()
                
                # Check if question matches or contains key terms
                if any(keyword in question_lower for keyword in content["topics"]):
                    return f"""**{content['question']}**

{content['answer']}

**Difficulty Level:** {content['difficulty'].title()}

This is fundamental trading knowledge. Would you like me to elaborate on any specific aspect?"""
            
        except Exception as e:
            logger.error(f"Basic content query error: {e}")
        
        return None
    
    async def _generate_fallback_response(self, request: EducationRequest) -> AIResponse:
        """Generate fallback educational response"""
        try:
            fallback_responses = {
                "beginner": """I'd be happy to help with your trading education question! While I'm still loading my complete knowledge base, here are some fundamental concepts:

**Getting Started with Trading:**
• Start with paper trading to practice without risk
• Learn basic chart reading and technical indicators
• Understand risk management principles
• Study successful traders and their strategies

**Recommended Learning Path:**
1. Master the basics of market mechanics
2. Learn technical analysis fundamentals
3. Develop a trading plan and strategy
4. Practice with small positions
5. Continuously educate yourself

Would you like me to elaborate on any of these areas?""",
                
                "intermediate": """For intermediate trading concepts, I recommend focusing on:

**Advanced Technical Analysis:**
• Multiple timeframe analysis
• Advanced chart patterns
• Volume analysis techniques
• Market structure understanding

**Risk Management:**
• Position sizing strategies
• Portfolio correlation analysis
• Drawdown management
• Performance metrics

**Trading Psychology:**
• Emotional discipline
• Cognitive biases in trading
• Developing consistent routines

What specific area would you like to explore further?""",
                
                "advanced": """For advanced trading topics, consider these areas:

**Quantitative Analysis:**
• Statistical arbitrage
• Algorithmic trading concepts
• Options strategies
• Portfolio optimization

**Market Microstructure:**
• Order flow analysis
• Market making concepts
• Liquidity considerations

**Professional Trading:**
• Risk management systems
• Performance attribution
• Regulatory considerations

Which advanced topic interests you most?"""
            }
            
            response_text = fallback_responses.get(
                request.difficulty_level, 
                fallback_responses["beginner"]
            )
            
            return AIResponse(
                response=response_text,
                type="education",
                confidence=0.6,
                context={"source": "fallback", "difficulty": request.difficulty_level}
            )
            
        except Exception as e:
            logger.error(f"Fallback response generation error: {e}")
            return AIResponse(
                response="I'm currently setting up my educational systems. Please try your question again in a moment.",
                type="system_status",
                confidence=0.3
            )
    
    async def get_available_topics(self) -> List[str]:
        """Get list of available educational topics"""
        try:
            topics = set()
            
            # Add basic content topics
            for content in self.basic_content.values():
                topics.update(content["topics"])
            
            # Add knowledge base topics if available
            client = await self._ensure_chroma_client()
            if client and self._collection:
                # This would query unique topics from the knowledge base
                topics.update(["psychology", "discipline", "trends", "risk_management"])
            
            return sorted(list(topics))
            
        except Exception as e:
            logger.error(f"Error getting available topics: {e}")
            return ["basics", "risk_management", "technical_analysis"]
    
    async def cleanup(self):
        """Cleanup education engine resources"""
        try:
            # Clear cache
            self.content_cache.clear()
            
            # Close ChromaDB connection if needed
            if self._chroma_client and self._chroma_client != "unavailable":
                # ChromaDB client doesn't need explicit closing
                pass
            
            logger.info("[OK] Education Engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during education engine cleanup: {e}")

    def _get_comprehensive_trading_content(self) -> List[Dict]:
        """Get comprehensive trading book content for RAG system"""
        return [
            # Trading in the Zone - Psychology and Mindset
            {
                "id": "tz_001",
                "text": "The hard, cold reality is that every trade has an uncertain outcome. Unless you learn to completely accept the possibility of being wrong, you will try to avoid the possibility of being wrong. This will absolutely prevent you from learning how to be objective, which will keep you from recognizing what the market is telling you about the direction it wants to move.",
                "source": "Trading in the Zone",
                "topic": "psychology",
                "difficulty": "intermediate",
                "chapter": "The Psychology of Trading"
            },
            {
                "id": "tz_002",
                "text": "Winning traders have learned to trust themselves to do the right thing. They don't need the market to do anything to take care of themselves. They have learned to be objective and to recognize what the market is telling them about the direction it wants to move. Most important, they have learned to act on what they see without reservation or hesitation.",
                "source": "Trading in the Zone",
                "topic": "confidence",
                "difficulty": "intermediate",
                "chapter": "Winning vs Losing Mindset"
            },
            {
                "id": "tz_003",
                "text": "The typical trader does not predefine his risk, cut his losses, or systematically take profits. Instead, he hopes, worries, and fears what the market might do to him. He focuses on being right, rather than making money. These are all symptoms of not believing that trading is simply a probability game.",
                "source": "Trading in the Zone",
                "topic": "risk_management",
                "difficulty": "beginner",
                "chapter": "Probability and Risk"
            },
            {
                "id": "tz_004",
                "text": "The best traders have evolved to the point where they believe, without a shred of doubt or internal conflict, that 'anything can happen.' They don't just say the words. Their belief in uncertainty is so powerful that it actually prevents their minds from associating the 'now moment' with the outcomes of their past trades.",
                "source": "Trading in the Zone",
                "topic": "uncertainty",
                "difficulty": "advanced",
                "chapter": "Embracing Uncertainty"
            },

            # Market Wizards - Interviews with Top Traders
            {
                "id": "mw_001",
                "text": "The key to trading success is emotional discipline. If intelligence were the key, there would be a lot more people making money trading. I know this will sound like a cliché, but the single most important reason that people lose money in the financial markets is that they don't cut their losses short.",
                "source": "Market Wizards",
                "topic": "discipline",
                "difficulty": "intermediate",
                "chapter": "Ed Seykota Interview"
            },
            {
                "id": "mw_002",
                "text": "I always laugh at people who say 'I've never met a rich technician.' I love that! It's such an arrogant, nonsensical response. I used fundamentals for nine years and got rich as a technician. The irony is that most of the market timers who claim to use fundamentals are actually using technical analysis.",
                "source": "Market Wizards",
                "topic": "technical_analysis",
                "difficulty": "intermediate",
                "chapter": "Marty Schwartz Interview"
            },
            {
                "id": "mw_003",
                "text": "Risk management is the most important thing to be well understood. Undertrade, undertrade, undertrade is my second piece of advice. Whatever you think your position ought to be, cut it at least in half. My experience with novice traders is that they trade three to five times too big. They are taking 5 to 10 percent risks on a trade when they should be taking 1 to 2 percent risks.",
                "source": "Market Wizards",
                "topic": "position_sizing",
                "difficulty": "beginner",
                "chapter": "Bruce Kovner Interview"
            },
            {
                "id": "mw_004",
                "text": "The first rule of trading - there are probably many first rules - is don't get caught in a situation where you can lose a great deal of money for reasons you don't understand. Diversification is one way of making sure you don't take a big hit. Never risk more than 1% of your total equity in any one trade.",
                "source": "Market Wizards",
                "topic": "diversification",
                "difficulty": "beginner",
                "chapter": "Risk Management Principles"
            },

            # Technical Analysis Explained
            {
                "id": "ta_001",
                "text": "The trend is your friend until it ends. One of the most important concepts in technical analysis is the identification and following of market trends. Markets tend to move in trends, and these trends persist for extended periods. The key is to identify the trend early and ride it until there are clear signs of reversal.",
                "source": "Technical Analysis Explained",
                "topic": "trends",
                "difficulty": "beginner",
                "chapter": "Trend Analysis"
            },
            {
                "id": "ta_002",
                "text": "Support and resistance levels are among the most important concepts in technical analysis. Support is a price level where a downtrend can be expected to pause due to a concentration of demand. Resistance is a price level where an uptrend can be expected to pause due to a concentration of supply.",
                "source": "Technical Analysis Explained",
                "topic": "support_resistance",
                "difficulty": "beginner",
                "chapter": "Support and Resistance"
            },
            {
                "id": "ta_003",
                "text": "Volume is the fuel that drives price movements. When prices move on high volume, it suggests that the move is more likely to continue. When prices move on low volume, the move is more suspect and likely to reverse. Volume should always be analyzed in conjunction with price action.",
                "source": "Technical Analysis Explained",
                "topic": "volume",
                "difficulty": "intermediate",
                "chapter": "Volume Analysis"
            },
            {
                "id": "ta_004",
                "text": "Moving averages are one of the most popular and versatile technical analysis tools. They smooth out price data to help identify the direction of the trend. The most common types are simple moving averages (SMA) and exponential moving averages (EMA). When price is above the moving average, the trend is considered bullish.",
                "source": "Technical Analysis Explained",
                "topic": "moving_averages",
                "difficulty": "beginner",
                "chapter": "Moving Averages"
            },

            # How to Make Money in Stocks - William O'Neil
            {
                "id": "hm_001",
                "text": "The CAN SLIM method is a proven system for selecting winning stocks. C stands for Current quarterly earnings, A for Annual earnings growth, N for New products or services, S for Supply and demand, L for Leader or laggard, I for Institutional sponsorship, and M for Market direction.",
                "source": "How to Make Money in Stocks",
                "topic": "stock_selection",
                "difficulty": "intermediate",
                "chapter": "The CAN SLIM Method"
            },
            {
                "id": "hm_002",
                "text": "Cut your losses short and let your profits run. This is the golden rule of successful investing. Most investors do exactly the opposite - they hold losing stocks hoping they'll come back and sell winning stocks too early. You should cut losses at 7-8% and let winners run 20-25% or more.",
                "source": "How to Make Money in Stocks",
                "topic": "profit_loss",
                "difficulty": "beginner",
                "chapter": "When to Buy and Sell"
            },
            {
                "id": "hm_003",
                "text": "The best time to buy stocks is when the overall market is in a confirmed uptrend. You can identify this by watching major market indexes like the S&P 500 and NASDAQ. Look for a follow-through day - a day when the index closes up strongly on increased volume after a market correction.",
                "source": "How to Make Money in Stocks",
                "topic": "market_timing",
                "difficulty": "intermediate",
                "chapter": "Market Timing"
            },

            # Options as a Strategic Investment
            {
                "id": "os_001",
                "text": "Options provide leverage and can be used for speculation, hedging, or income generation. A call option gives you the right to buy a stock at a specific price, while a put option gives you the right to sell. The key to options success is understanding time decay, volatility, and the Greeks.",
                "source": "Options as a Strategic Investment",
                "topic": "options_basics",
                "difficulty": "intermediate",
                "chapter": "Options Fundamentals"
            },
            {
                "id": "os_002",
                "text": "The covered call strategy involves owning stock and selling call options against it. This generates income from the option premium but limits upside potential. It's best used in neutral to slightly bullish markets when you want to generate additional income from your stock holdings.",
                "source": "Options as a Strategic Investment",
                "topic": "covered_calls",
                "difficulty": "intermediate",
                "chapter": "Income Strategies"
            },
            {
                "id": "os_003",
                "text": "Protective puts act like insurance for your stock positions. By buying a put option, you establish a floor price for your stock. If the stock falls below the put's strike price, the put increases in value to offset the stock's decline. This strategy costs money but provides downside protection.",
                "source": "Options as a Strategic Investment",
                "topic": "protective_puts",
                "difficulty": "intermediate",
                "chapter": "Hedging Strategies"
            },

            # The New Trading for a Living
            {
                "id": "tl_001",
                "text": "Successful trading requires three essential components: a sound individual psychology, a logical trading system, and good money management. Most people focus on the system and ignore psychology and money management, which is why they fail.",
                "source": "The New Trading for a Living",
                "topic": "trading_pillars",
                "difficulty": "beginner",
                "chapter": "The Three Pillars of Trading"
            },
            {
                "id": "tl_002",
                "text": "The 2% Rule states that you should never risk more than 2% of your account equity on any single trade. This rule helps ensure that you can survive a string of losses and continue trading. If you have a $10,000 account, never risk more than $200 on any one trade.",
                "source": "The New Trading for a Living",
                "topic": "money_management",
                "difficulty": "beginner",
                "chapter": "Money Management Rules"
            },
            {
                "id": "tl_003",
                "text": "Keep a trading diary to track not just your trades, but your emotions and decision-making process. Write down why you entered each trade, what you expected to happen, and how you felt during the trade. This self-awareness is crucial for improving your trading performance.",
                "source": "The New Trading for a Living",
                "topic": "trading_journal",
                "difficulty": "beginner",
                "chapter": "Record Keeping"
            }
        ]
