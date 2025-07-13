"""
A.T.L.A.S Stock Intelligence Hub - Predicto's Core Stock Analysis Engine
Advanced stock analysis capabilities with technical, fundamental, and predictive intelligence
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Tuple
import numpy as np

from config import settings
from models import (
    PredictoForecast, EngineStatus
)

logger = logging.getLogger(__name__)


class StockIntelligenceHub:
    """
    Predicto's core stock analysis intelligence hub
    Combines technical analysis, market intelligence, sentiment analysis, and predictions
    """

    def __init__(self):
        self.status = EngineStatus.INITIALIZING
        self.analysis_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Analysis modules
        self.technical_analyzer = TechnicalAnalysisModule()
        self.sentiment_analyzer = SentimentAnalysisModule()
        self.prediction_engine = PredictionEngineModule()
        self.market_intelligence = MarketIntelligenceModule()
        
        logger.info("[BRAIN] Stock Intelligence Hub created")

    async def initialize(self):
        """Initialize the stock intelligence hub"""
        try:
            self.status = EngineStatus.INITIALIZING
            
            # Initialize all analysis modules
            await self.technical_analyzer.initialize()
            await self.sentiment_analyzer.initialize()
            await self.prediction_engine.initialize()
            await self.market_intelligence.initialize()
            
            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Stock Intelligence Hub fully initialized")
            
        except Exception as e:
            logger.error(f"Stock Intelligence Hub initialization failed: {e}")
            self.status = EngineStatus.FAILED
            raise

    async def analyze_stock_comprehensive(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """
        Perform comprehensive stock analysis combining all intelligence modules
        This is Predicto's primary stock analysis capability
        """
        try:
            # Check cache first
            cache_key = f"comprehensive_{symbol}"
            if self._is_cache_valid(cache_key):
                return self.analysis_cache[cache_key]["data"]
            
            logger.info(f"[SEARCH] Performing comprehensive analysis for {symbol}")
            
            # Parallel execution of all analysis modules
            analysis_tasks = [
                self.technical_analyzer.analyze(symbol, orchestrator),
                self.sentiment_analyzer.analyze(symbol, orchestrator),
                self.prediction_engine.analyze(symbol, orchestrator),
                self.market_intelligence.analyze(symbol, orchestrator)
            ]
            
            # Execute all analyses concurrently
            technical_result, sentiment_result, prediction_result, intelligence_result = await asyncio.gather(
                *analysis_tasks, return_exceptions=True
            )
            
            # Compile comprehensive analysis
            comprehensive_analysis = {
                "symbol": symbol,
                "timestamp": datetime.now(),
                "technical_analysis": technical_result if not isinstance(technical_result, Exception) else {"error": str(technical_result)},
                "sentiment_analysis": sentiment_result if not isinstance(sentiment_result, Exception) else {"error": str(sentiment_result)},
                "prediction_analysis": prediction_result if not isinstance(prediction_result, Exception) else {"error": str(prediction_result)},
                "market_intelligence": intelligence_result if not isinstance(intelligence_result, Exception) else {"error": str(intelligence_result)}
            }
            
            # Generate overall assessment
            comprehensive_analysis["overall_assessment"] = await self._generate_overall_assessment(comprehensive_analysis)
            
            # Cache the result
            self._cache_result(cache_key, comprehensive_analysis)
            
            logger.info(f"[OK] Comprehensive analysis completed for {symbol}")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e), "timestamp": datetime.now()}

    async def analyze_stock_focused(self, symbol: str, focus_area: str, orchestrator) -> Dict[str, Any]:
        """
        Perform focused analysis on specific area (technical, sentiment, prediction, intelligence)
        """
        try:
            cache_key = f"focused_{symbol}_{focus_area}"
            if self._is_cache_valid(cache_key):
                return self.analysis_cache[cache_key]["data"]
            
            logger.info(f"[TARGET] Performing {focus_area} analysis for {symbol}")
            
            if focus_area == "technical":
                result = await self.technical_analyzer.analyze(symbol, orchestrator)
            elif focus_area == "sentiment":
                result = await self.sentiment_analyzer.analyze(symbol, orchestrator)
            elif focus_area == "prediction":
                result = await self.prediction_engine.analyze(symbol, orchestrator)
            elif focus_area == "intelligence":
                result = await self.market_intelligence.analyze(symbol, orchestrator)
            else:
                raise ValueError(f"Unknown focus area: {focus_area}")
            
            analysis = {
                "symbol": symbol,
                "focus_area": focus_area,
                "timestamp": datetime.now(),
                "analysis": result
            }
            
            self._cache_result(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Focused analysis failed for {symbol} ({focus_area}): {e}")
            return {"symbol": symbol, "focus_area": focus_area, "error": str(e), "timestamp": datetime.now()}

    async def compare_stocks(self, symbols: List[str], orchestrator) -> Dict[str, Any]:
        """
        Compare multiple stocks across all analysis dimensions
        """
        try:
            logger.info(f"[DATA] Comparing stocks: {', '.join(symbols)}")
            
            # Analyze each stock
            stock_analyses = {}
            for symbol in symbols[:5]:  # Limit to 5 stocks for performance
                analysis = await self.analyze_stock_comprehensive(symbol, orchestrator)
                stock_analyses[symbol] = analysis
            
            # Generate comparison insights
            comparison = {
                "symbols": symbols,
                "timestamp": datetime.now(),
                "individual_analyses": stock_analyses,
                "comparison_insights": await self._generate_comparison_insights(stock_analyses)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Stock comparison failed: {e}")
            return {"symbols": symbols, "error": str(e), "timestamp": datetime.now()}

    async def get_market_opportunities(self, criteria: Dict[str, Any], orchestrator) -> Dict[str, Any]:
        """
        Find market opportunities based on specified criteria
        """
        try:
            logger.info(f"[LAUNCH] Scanning for opportunities with criteria: {criteria}")
            
            # Use market intelligence to find opportunities
            opportunities = await self.market_intelligence.find_opportunities(criteria, orchestrator)
            
            # Enhance opportunities with quick analysis
            enhanced_opportunities = []
            for opportunity in opportunities[:10]:  # Limit to top 10
                symbol = opportunity.get("symbol")
                if symbol:
                    quick_analysis = await self.analyze_stock_focused(symbol, "technical", orchestrator)
                    opportunity["quick_analysis"] = quick_analysis
                enhanced_opportunities.append(opportunity)
            
            return {
                "criteria": criteria,
                "timestamp": datetime.now(),
                "opportunities": enhanced_opportunities,
                "count": len(enhanced_opportunities)
            }
            
        except Exception as e:
            logger.error(f"Opportunity scanning failed: {e}")
            return {"criteria": criteria, "error": str(e), "timestamp": datetime.now()}

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.analysis_cache:
            return False
        
        cached_time = self.analysis_cache[cache_key]["timestamp"]
        return (datetime.now() - cached_time).total_seconds() < self.cache_ttl

    def _cache_result(self, cache_key: str, data: Dict[str, Any]):
        """Cache analysis result"""
        self.analysis_cache[cache_key] = {
            "timestamp": datetime.now(),
            "data": data
        }
        
        # Clean old cache entries (keep last 100)
        if len(self.analysis_cache) > 100:
            oldest_keys = sorted(
                self.analysis_cache.keys(),
                key=lambda k: self.analysis_cache[k]["timestamp"]
            )[:20]
            for key in oldest_keys:
                del self.analysis_cache[key]

    async def _generate_overall_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment from comprehensive analysis"""
        try:
            assessment = {
                "overall_sentiment": "neutral",
                "confidence_score": 0.5,
                "key_insights": [],
                "risk_level": "medium",
                "recommendation": "hold"
            }
            
            # Analyze technical signals
            technical = analysis.get("technical_analysis", {})
            if "ttm_squeeze" in technical and technical["ttm_squeeze"]:
                assessment["key_insights"].append("TTM Squeeze signal detected")
                assessment["confidence_score"] += 0.2
            
            # Analyze sentiment
            sentiment = analysis.get("sentiment_analysis", {})
            if "overall_sentiment" in sentiment:
                sentiment_score = sentiment.get("sentiment_score", 0)
                if sentiment_score > 0.6:
                    assessment["overall_sentiment"] = "bullish"
                    assessment["confidence_score"] += 0.15
                elif sentiment_score < 0.4:
                    assessment["overall_sentiment"] = "bearish"
                    assessment["confidence_score"] += 0.15
            
            # Analyze predictions
            prediction = analysis.get("prediction_analysis", {})
            if "ml_prediction" in prediction and prediction["ml_prediction"]:
                pred_return = prediction["ml_prediction"].get("predicted_return", 0)
                if abs(pred_return) > 0.02:  # Significant prediction
                    direction = "positive" if pred_return > 0 else "negative"
                    assessment["key_insights"].append(f"ML prediction shows {direction} movement")
                    assessment["confidence_score"] += 0.1
            
            # Generate recommendation
            if assessment["confidence_score"] > 0.7 and assessment["overall_sentiment"] == "bullish":
                assessment["recommendation"] = "buy"
            elif assessment["confidence_score"] > 0.7 and assessment["overall_sentiment"] == "bearish":
                assessment["recommendation"] = "sell"
            
            # Cap confidence score
            assessment["confidence_score"] = min(assessment["confidence_score"], 0.95)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating overall assessment: {e}")
            return {"error": str(e)}

    async def _generate_comparison_insights(self, stock_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from stock comparison"""
        try:
            insights = {
                "strongest_technical": None,
                "most_bullish_sentiment": None,
                "highest_prediction": None,
                "best_overall": None,
                "summary": []
            }
            
            # Find strongest in each category
            best_scores = {}
            for symbol, analysis in stock_analyses.items():
                if "error" not in analysis:
                    overall = analysis.get("overall_assessment", {})
                    confidence = overall.get("confidence_score", 0)
                    best_scores[symbol] = confidence
            
            if best_scores:
                best_symbol = max(best_scores, key=best_scores.get)
                insights["best_overall"] = {
                    "symbol": best_symbol,
                    "confidence": best_scores[best_symbol]
                }
                insights["summary"].append(f"{best_symbol} shows the strongest overall signals")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comparison insights: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Stock Intelligence Hub...")
        
        # Clear cache
        self.analysis_cache.clear()
        
        # Cleanup modules
        await self.technical_analyzer.cleanup()
        await self.sentiment_analyzer.cleanup()
        await self.prediction_engine.cleanup()
        await self.market_intelligence.cleanup()
        
        logger.info("[OK] Stock Intelligence Hub cleanup completed")

    def get_status(self) -> EngineStatus:
        """Get current status"""
        return self.status


class TechnicalAnalysisModule:
    """Technical analysis module for stock intelligence"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TechnicalAnalysis")

    async def initialize(self):
        """Initialize technical analysis module"""
        self.logger.info("[OK] Technical Analysis Module initialized")

    async def analyze(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Perform technical analysis"""
        try:
            analysis = {"symbol": symbol, "timestamp": datetime.now()}

            # Get quote data
            if orchestrator and hasattr(orchestrator, 'market_engine'):
                quote = await orchestrator.market_engine.get_quote(symbol)
                analysis["quote"] = quote

                # Get TTM Squeeze signals
                ttm_signals = await orchestrator.market_engine.scan_ttm_squeeze([symbol])
                analysis["ttm_squeeze"] = ttm_signals

                # Calculate technical indicators
                analysis["technical_indicators"] = await self._calculate_indicators(symbol, orchestrator)

                # Identify chart patterns
                analysis["chart_patterns"] = await self._identify_patterns(symbol, orchestrator)

                # Support and resistance levels
                analysis["support_resistance"] = await self._find_support_resistance(symbol, orchestrator)

            return analysis

        except Exception as e:
            self.logger.error(f"Technical analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    async def _calculate_indicators(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Calculate technical indicators"""
        # This would integrate with the existing technical analysis capabilities
        return {
            "rsi": None,  # Would calculate RSI
            "macd": None,  # Would calculate MACD
            "bollinger_bands": None,  # Would calculate Bollinger Bands
            "moving_averages": None  # Would calculate moving averages
        }

    async def _identify_patterns(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Identify chart patterns"""
        return {
            "patterns_detected": [],
            "pattern_confidence": 0.0
        }

    async def _find_support_resistance(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Find support and resistance levels"""
        return {
            "support_levels": [],
            "resistance_levels": []
        }

    async def cleanup(self):
        """Cleanup resources"""
        pass


class SentimentAnalysisModule:
    """Sentiment analysis module for stock intelligence"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SentimentAnalysis")

    async def initialize(self):
        """Initialize sentiment analysis module"""
        self.logger.info("[OK] Sentiment Analysis Module initialized")

    async def analyze(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        try:
            analysis = {"symbol": symbol, "timestamp": datetime.now()}

            # Get sentiment from orchestrator's sentiment analyzer
            if orchestrator and hasattr(orchestrator, 'sentiment_analyzer'):
                sentiment_result = await orchestrator.sentiment_analyzer.analyze_symbol_sentiment(symbol)
                analysis["sentiment_data"] = sentiment_result

                # Get news sentiment
                analysis["news_sentiment"] = await self._analyze_news_sentiment(symbol, orchestrator)

                # Get social media sentiment
                analysis["social_sentiment"] = await self._analyze_social_sentiment(symbol, orchestrator)

                # Combine all sentiment sources
                analysis["combined_sentiment"] = await self._combine_sentiment_sources(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    async def _analyze_news_sentiment(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Analyze news sentiment"""
        # This would integrate with news sentiment analysis
        return {
            "news_sentiment_score": 0.5,
            "news_count": 0,
            "recent_headlines": []
        }

    async def _analyze_social_sentiment(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Analyze social media sentiment"""
        # This would integrate with social media sentiment analysis
        return {
            "social_sentiment_score": 0.5,
            "mention_count": 0,
            "trending_topics": []
        }

    async def _combine_sentiment_sources(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine sentiment from all sources"""
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.5,
            "confidence": 0.5
        }

    async def cleanup(self):
        """Cleanup resources"""
        pass


class PredictionEngineModule:
    """Prediction engine module for stock intelligence"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PredictionEngine")

    async def initialize(self):
        """Initialize prediction engine module"""
        self.logger.info("[OK] Prediction Engine Module initialized")

    async def analyze(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Perform prediction analysis"""
        try:
            analysis = {"symbol": symbol, "timestamp": datetime.now()}

            # Get ML predictions
            if orchestrator and hasattr(orchestrator, 'ml_predictor'):
                ml_prediction = await orchestrator.ml_predictor.predict_returns(symbol)
                analysis["ml_prediction"] = ml_prediction

            # Get Predicto forecasts
            if orchestrator and hasattr(orchestrator, 'market_engine'):
                predicto_forecast = await orchestrator.market_engine.get_predicto_forecast(symbol)
                analysis["predicto_forecast"] = predicto_forecast

            # Generate price targets
            analysis["price_targets"] = await self._generate_price_targets(symbol, analysis)

            # Risk assessment
            analysis["risk_assessment"] = await self._assess_prediction_risk(symbol, analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Prediction analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    async def _generate_price_targets(self, symbol: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate price targets based on predictions"""
        return {
            "short_term_target": None,
            "medium_term_target": None,
            "long_term_target": None
        }

    async def _assess_prediction_risk(self, symbol: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of predictions"""
        return {
            "prediction_confidence": 0.5,
            "risk_level": "medium",
            "volatility_forecast": None
        }

    async def cleanup(self):
        """Cleanup resources"""
        pass


class MarketIntelligenceModule:
    """Market intelligence module for stock intelligence"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MarketIntelligence")

    async def initialize(self):
        """Initialize market intelligence module"""
        self.logger.info("[OK] Market Intelligence Module initialized")

    async def analyze(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Perform market intelligence analysis"""
        try:
            analysis = {"symbol": symbol, "timestamp": datetime.now()}

            # Market context
            analysis["market_context"] = await self._get_market_context(symbol, orchestrator)

            # Sector analysis
            analysis["sector_analysis"] = await self._analyze_sector(symbol, orchestrator)

            # Institutional activity
            analysis["institutional_activity"] = await self._analyze_institutional_activity(symbol, orchestrator)

            # Options flow
            analysis["options_flow"] = await self._analyze_options_flow(symbol, orchestrator)

            return analysis

        except Exception as e:
            self.logger.error(f"Market intelligence analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    async def find_opportunities(self, criteria: Dict[str, Any], orchestrator) -> List[Dict[str, Any]]:
        """Find market opportunities based on criteria"""
        try:
            opportunities = []

            # Use TTM Squeeze scanner
            if orchestrator and hasattr(orchestrator, 'market_engine'):
                signals = await orchestrator.market_engine.scan_market("moderate")
                for signal in signals:
                    opportunities.append({
                        "symbol": signal.get("symbol"),
                        "type": "ttm_squeeze",
                        "strength": signal.get("strength"),
                        "description": f"TTM Squeeze signal detected"
                    })

            return opportunities[:20]  # Limit to top 20

        except Exception as e:
            self.logger.error(f"Opportunity finding failed: {e}")
            return []

    async def _get_market_context(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Get market context for symbol"""
        return {
            "market_regime": "neutral",
            "volatility_environment": "normal",
            "correlation_analysis": {}
        }

    async def _analyze_sector(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Analyze sector performance"""
        return {
            "sector": "unknown",
            "sector_performance": 0.0,
            "relative_strength": 0.0
        }

    async def _analyze_institutional_activity(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Analyze institutional activity"""
        return {
            "institutional_sentiment": "neutral",
            "large_block_activity": [],
            "insider_activity": []
        }

    async def _analyze_options_flow(self, symbol: str, orchestrator) -> Dict[str, Any]:
        """Analyze options flow"""
        return {
            "unusual_activity": [],
            "put_call_ratio": 1.0,
            "implied_volatility": None
        }

    async def cleanup(self):
        """Cleanup resources"""
        pass
