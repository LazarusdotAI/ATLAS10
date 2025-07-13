"""
A.T.L.A.S Multi-Source Sentiment Analysis Module
DistilBERT sentiment analysis from news/Reddit/Twitter with auto-hedging
"""

import asyncio
import logging
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from collections import defaultdict
import time

from config import settings
from models import SentimentData, SentimentSignal, SignalStrength
from atlas_performance_optimizer import performance_optimizer

# Optional ML imports with graceful fallback
try:
    from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
    import torch
    import torch.nn.functional as F
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class MultiSourceSentimentAnalyzer:
    """
    Advanced sentiment analysis from multiple sources with DistilBERT
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enabled = settings.ML_MODELS_ENABLED and ML_AVAILABLE
        self.model_path = settings.SENTIMENT_MODEL_PATH
        self.confidence_threshold = settings.ML_PREDICTION_CONFIDENCE_THRESHOLD
        
        # API keys
        self.google_api_key = settings.GOOGLE_SEARCH_API_KEY
        self.google_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.twitter_bearer_token = settings.TWITTER_BEARER_TOKEN
        self.reddit_client_id = settings.REDDIT_CLIENT_ID
        self.reddit_client_secret = settings.REDDIT_CLIENT_SECRET
        
        # ML models (lazy loaded)
        self.model = None
        self.tokenizer = None
        
        # Caching
        self.sentiment_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Rate limiting
        self.last_request_times = defaultdict(float)
        self.min_request_interval = 1.0  # seconds
        
        self.logger.info(f"[THEATER] Sentiment Analyzer initialized - ML: {self.enabled}")
    
    async def initialize(self):
        """Initialize ML models if available"""
        if not self.enabled:
            self.logger.info("[THEATER] Sentiment analysis running in fallback mode (no ML models)")
            return
        
        try:
            self.logger.info("[TOOL] Loading DistilBERT sentiment model...")
            self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
            self.model = DistilBertForSequenceClassification.from_pretrained(self.model_path)
            self.model.eval()
            self.logger.info("[OK] DistilBERT sentiment model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to load sentiment model: {e}")
            self.enabled = False
    
    @performance_optimizer.performance_monitor("sentiment_analysis")
    async def analyze_sentiment(self, symbol: str, timeframe: str = "1hour") -> Optional[SentimentSignal]:
        """
        Analyze sentiment for a symbol from multiple sources
        """
        try:
            # Check cache
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.sentiment_cache:
                cached_data = self.sentiment_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_ttl:
                    return cached_data['signal']
            
            # Gather sentiment data from all sources
            sentiment_data = []
            
            # Get news sentiment
            news_data = await self._get_news_sentiment(symbol)
            sentiment_data.extend(news_data)
            
            # Get Reddit sentiment
            reddit_data = await self._get_reddit_sentiment(symbol)
            sentiment_data.extend(reddit_data)
            
            # Get Twitter sentiment (if available)
            if self.twitter_bearer_token:
                twitter_data = await self._get_twitter_sentiment(symbol)
                sentiment_data.extend(twitter_data)
            
            if not sentiment_data:
                self.logger.warning(f"No sentiment data found for {symbol}")
                return None
            
            # Aggregate sentiment
            signal = self._aggregate_sentiment(symbol, sentiment_data)
            
            # Get implied volatility for hedging decision
            signal.implied_volatility = await self._get_implied_volatility(symbol)
            
            # Determine hedging strategy
            signal.should_hedge, signal.hedge_symbol = self._should_hedge(symbol, signal)
            
            # Cache result
            self.sentiment_cache[cache_key] = {
                'signal': signal,
                'timestamp': time.time()
            }
            
            self.logger.info(f"[DATA] Sentiment analysis for {symbol}: {signal.overall_sentiment:.3f} ({signal.signal_strength})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return None
    
    async def _get_news_sentiment(self, symbol: str) -> List[SentimentData]:
        """Get news sentiment using Google Search API"""
        sentiment_data = []
        
        if not self.google_api_key or not self.google_engine_id:
            return sentiment_data
        
        try:
            # Rate limiting
            await self._rate_limit("google")
            
            query = f"{symbol} stock news earnings"
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_engine_id,
                'q': query,
                'num': 10,
                'dateRestrict': 'd1'  # Last 24 hours
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            title = item.get('title', '')
                            snippet = item.get('snippet', '')
                            text = f"{title} {snippet}"
                            
                            sentiment_score, confidence = self._analyze_text_sentiment(text)
                            
                            sentiment_data.append(SentimentData(
                                source='news',
                                symbol=symbol,
                                text=text,
                                sentiment_score=sentiment_score,
                                confidence=confidence,
                                timestamp=datetime.now(),
                                url=item.get('link')
                            ))
            
        except Exception as e:
            self.logger.error(f"Error getting news sentiment: {e}")
        
        return sentiment_data
    
    async def _get_reddit_sentiment(self, symbol: str) -> List[SentimentData]:
        """Get Reddit sentiment from relevant subreddits"""
        sentiment_data = []
        
        try:
            # Rate limiting
            await self._rate_limit("reddit")
            
            # Search relevant subreddits
            subreddits = ['stocks', 'investing', 'SecurityAnalysis', 'StockMarket']
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': symbol,
                    'sort': 'new',
                    'limit': 25,
                    't': 'day'  # Last 24 hours
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post in data.get('data', {}).get('children', []):
                                post_data = post.get('data', {})
                                title = post_data.get('title', '')
                                selftext = post_data.get('selftext', '')
                                text = f"{title} {selftext}"
                                
                                if len(text.strip()) > 10:  # Filter out very short posts
                                    sentiment_score, confidence = self._analyze_text_sentiment(text)
                                    
                                    sentiment_data.append(SentimentData(
                                        source='reddit',
                                        symbol=symbol,
                                        text=text,
                                        sentiment_score=sentiment_score,
                                        confidence=confidence,
                                        timestamp=datetime.now(),
                                        url=f"https://reddit.com{post_data.get('permalink', '')}"
                                    ))
        
        except Exception as e:
            self.logger.error(f"Error getting Reddit sentiment: {e}")
        
        return sentiment_data
    
    async def _get_twitter_sentiment(self, symbol: str) -> List[SentimentData]:
        """Get Twitter sentiment (requires Twitter API v2)"""
        sentiment_data = []
        
        if not self.twitter_bearer_token:
            return sentiment_data
        
        try:
            # Rate limiting
            await self._rate_limit("twitter")
            
            query = f"${symbol} OR {symbol} stock -is:retweet lang:en"
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {'Authorization': f'Bearer {self.twitter_bearer_token}'}
            params = {
                'query': query,
                'max_results': 100,
                'tweet.fields': 'created_at,public_metrics'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for tweet in data.get('data', []):
                            text = tweet.get('text', '')
                            
                            if len(text.strip()) > 10:  # Filter out very short tweets
                                sentiment_score, confidence = self._analyze_text_sentiment(text)
                                
                                sentiment_data.append(SentimentData(
                                    source='twitter',
                                    symbol=symbol,
                                    text=text,
                                    sentiment_score=sentiment_score,
                                    confidence=confidence,
                                    timestamp=datetime.now()
                                ))
        
        except Exception as e:
            self.logger.error(f"Error getting Twitter sentiment: {e}")
        
        return sentiment_data
    
    def _analyze_text_sentiment(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment of text using DistilBERT"""
        try:
            if not self.model or not self.tokenizer:
                # Fallback to simple keyword-based sentiment
                return self._simple_sentiment_analysis(text)
            
            # Clean and truncate text
            cleaned_text = self._clean_text(text)
            
            # Tokenize
            inputs = self.tokenizer(
                cleaned_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = F.softmax(outputs.logits, dim=-1)
                
                # Convert to sentiment score (-1 to 1)
                negative_prob = predictions[0][0].item()
                positive_prob = predictions[0][1].item()
                
                sentiment_score = positive_prob - negative_prob
                confidence = max(positive_prob, negative_prob)
                
                return sentiment_score, confidence
                
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Tuple[float, float]:
        """Simple keyword-based sentiment analysis fallback"""
        positive_words = ['buy', 'bull', 'bullish', 'up', 'rise', 'gain', 'profit', 'good', 'great', 'excellent', 'strong']
        negative_words = ['sell', 'bear', 'bearish', 'down', 'fall', 'loss', 'bad', 'terrible', 'weak', 'crash']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0, 0.0
        
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        confidence = min((positive_count + negative_count) / max(total_words, 1), 1.0)
        
        return sentiment_score, confidence
    
    def _clean_text(self, text: str) -> str:
        """Clean text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def _aggregate_sentiment(self, symbol: str, sentiment_data: List[SentimentData]) -> SentimentSignal:
        """Aggregate sentiment data into a single signal"""
        if not sentiment_data:
            return SentimentSignal(
                symbol=symbol,
                overall_sentiment=0.0,
                confidence=0.0,
                signal_strength=SignalStrength.WEAK,
                source_count=0,
                bullish_signals=0,
                bearish_signals=0,
                neutral_signals=0,
                timestamp=datetime.now()
            )
        
        # Weight by confidence and recency
        weighted_sentiment = 0.0
        total_weight = 0.0
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for data in sentiment_data:
            # Time decay (more recent = higher weight)
            age_hours = (datetime.now() - data.timestamp).total_seconds() / 3600
            time_weight = max(0.1, 1.0 - (age_hours / 24))  # Decay over 24 hours
            
            weight = data.confidence * time_weight
            weighted_sentiment += data.sentiment_score * weight
            total_weight += weight
            
            # Count signal types
            if data.sentiment_score > 0.1:
                bullish_count += 1
            elif data.sentiment_score < -0.1:
                bearish_count += 1
            else:
                neutral_count += 1
        
        overall_sentiment = weighted_sentiment / max(total_weight, 0.001)
        confidence = min(total_weight / len(sentiment_data), 1.0)
        
        # Determine signal strength
        signal_strength = SignalStrength.WEAK
        if abs(overall_sentiment) > 0.3 and confidence > 0.6:
            signal_strength = SignalStrength.STRONG
        elif abs(overall_sentiment) > 0.15 and confidence > 0.4:
            signal_strength = SignalStrength.MODERATE
        
        return SentimentSignal(
            symbol=symbol,
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            signal_strength=signal_strength,
            source_count=len(sentiment_data),
            bullish_signals=bullish_count,
            bearish_signals=bearish_count,
            neutral_signals=neutral_count,
            timestamp=datetime.now()
        )
    
    async def _get_implied_volatility(self, symbol: str) -> Optional[float]:
        """Get implied volatility for hedging decisions"""
        # This would integrate with options data provider
        # For now, return None as placeholder
        return None
    
    def _should_hedge(self, symbol: str, signal: SentimentSignal) -> Tuple[bool, Optional[str]]:
        """Determine if hedging is recommended"""
        # Simple hedging logic based on sentiment extremes
        if abs(signal.overall_sentiment) > 0.5 and signal.confidence > 0.7:
            # High confidence extreme sentiment suggests hedging
            if signal.overall_sentiment > 0:
                # Very bullish - consider put hedge
                return True, f"{symbol}_PUT"
            else:
                # Very bearish - consider call hedge
                return True, f"{symbol}_CALL"
        
        return False, None
    
    async def _rate_limit(self, source: str):
        """Simple rate limiting"""
        last_request = self.last_request_times[source]
        time_since_last = time.time() - last_request
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_times[source] = time.time()


# Global sentiment analyzer instance
sentiment_analyzer = MultiSourceSentimentAnalyzer()
