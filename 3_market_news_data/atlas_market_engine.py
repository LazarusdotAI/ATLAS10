"""
A.T.L.A.S Market Engine - Real-time Data and TTM Squeeze Scanner
Market data integration with Predicto API and lazy loading
"""

# CRITICAL: Import startup initialization FIRST to ensure Windows-compatible logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '4_helper_tools'))

try:
    from atlas_startup_init import initialize_component_logging
    logger = initialize_component_logging('atlas_market_engine')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from urllib.parse import quote_plus

from config import get_api_config
from models import Quote, TTMSqueezeSignal, SignalStrength, EngineStatus, PredictoForecast

# Optional web search imports with graceful fallbacks
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

# Logger already initialized above - don't override it

# Import enhanced scanner suite
try:
    from atlas_enhanced_scanner_suite import enhanced_scanner_suite
    ENHANCED_SCANNER_AVAILABLE = True
    logger.info("[OK] Enhanced Scanner Suite available")
except ImportError:
    ENHANCED_SCANNER_AVAILABLE = False
    logger.warning("[WARN] Enhanced Scanner Suite not available")


class AtlasMarketEngine:
    """
    Market data engine with real-time quotes, TTM Squeeze scanning, and Predicto integration
    """
    
    def __init__(self):
        self.alpaca_config = get_api_config("alpaca")
        self.fmp_config = get_api_config("fmp")
        self.predicto_config = get_api_config("predicto")
        self.validation_mode = self.fmp_config.get("validation_mode", False)

        self.status = EngineStatus.INITIALIZING

        # API clients (lazy loaded)
        self._alpaca_client = None
        self._fmp_session = None
        self._predicto_session = None

        # Web search configuration
        self.web_search_config = self._initialize_web_search_config()
        self._google_service = None

        # Data cache
        self.quote_cache = {}
        self.cache_ttl = 60  # seconds
        self.news_cache = {}
        self.news_cache_ttl = 300  # 5 minutes for news
        
        # TTM Squeeze scanner
        self.scanner_active = False
        self.scan_symbols = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]
        
        logger.info("[DATA] Market Engine created - API clients will load on demand")

    def _initialize_web_search_config(self) -> Dict[str, Any]:
        """Initialize web search provider configurations"""
        try:
            import os

            config = {
                "google": {
                    "enabled": bool(os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID")),
                    "api_key": os.getenv("GOOGLE_SEARCH_API_KEY"),
                    "engine_id": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
                    "available": GOOGLE_SEARCH_AVAILABLE
                },
                "bing": {
                    "enabled": bool(os.getenv("BING_SEARCH_API_KEY")),
                    "api_key": os.getenv("BING_SEARCH_API_KEY"),
                    "available": False  # Not implemented yet
                },
                "duckduckgo": {
                    "enabled": True,  # Always available as fallback
                    "available": DUCKDUCKGO_AVAILABLE
                }
            }

            # Determine primary provider
            if config["google"]["enabled"] and config["google"]["available"]:
                config["primary"] = "google"
            elif config["duckduckgo"]["available"]:
                config["primary"] = "duckduckgo"
            else:
                config["primary"] = None

            logger.info(f"[SEARCH] Web search configured - Primary: {config['primary']}")
            return config

        except Exception as e:
            logger.warning(f"Web search configuration failed: {e}")
            return {"primary": None, "google": {"enabled": False}, "duckduckgo": {"enabled": False}}

    async def initialize(self):
        """Initialize market engine with connection testing"""
        try:
            if self.validation_mode:
                # In validation mode, skip API-dependent initialization
                logger.info("[WARN] Market Engine validation mode - skipping API initialization")
                self.status = EngineStatus.INACTIVE
                logger.info("[OK] Market Engine validation mode initialization completed")
                return

            # Test API connections
            await self._test_connections()

            # Initialize enhanced scanner suite
            if ENHANCED_SCANNER_AVAILABLE:
                await enhanced_scanner_suite.initialize(self)
                logger.info("[OK] Enhanced Scanner Suite integrated")

            self.status = EngineStatus.ACTIVE
            logger.info("[OK] Market Engine initialization completed")

        except Exception as e:
            logger.error(f"[ERROR] Market Engine initialization failed: {e}")
            self.status = EngineStatus.DEGRADED
            # Continue with limited functionality
    
    async def _test_connections(self):
        """Test API connections"""
        try:
            # Test FMP connection
            await self._ensure_fmp_session()
            test_quote = await self._get_fmp_quote("AAPL")
            if test_quote:
                logger.info("[OK] FMP API connection tested successfully")
            
            # Test Predicto if configured and not using placeholder URL
            if self.predicto_config.get("enabled") and "api.predic.to" not in self.predicto_config.get('base_url', ''):
                await self._ensure_predicto_session()
                logger.info("[OK] Predicto API connection ready")
            elif self.predicto_config.get("enabled"):
                logger.info("[INFO] Predicto API configured with placeholder URL - skipping connection test")
            
        except Exception as e:
            logger.warning(f"[WARN] Some API connections failed: {e}")
    
    async def _ensure_alpaca_client(self):
        """Ensure Alpaca client is initialized"""
        if self._alpaca_client is None:
            try:
                import alpaca_trade_api as tradeapi
                self._alpaca_client = tradeapi.REST(
                    self.alpaca_config["api_key"],
                    self.alpaca_config["secret_key"],
                    self.alpaca_config["base_url"],
                    api_version='v2'
                )
                logger.info("[OK] Alpaca client initialized")
            except Exception as e:
                logger.error(f"[ERROR] Alpaca client initialization failed: {e}")
                raise
        return self._alpaca_client
    
    async def _ensure_fmp_session(self):
        """Ensure FMP HTTP session is initialized"""
        if self._fmp_session is None:
            self._fmp_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            logger.info("[OK] FMP session initialized")
        return self._fmp_session
    
    async def _ensure_predicto_session(self):
        """Ensure Predicto HTTP session is initialized"""
        if self._predicto_session is None and self.predicto_config.get("enabled"):
            self._predicto_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"Authorization": f"Bearer {self.predicto_config['api_key']}"}
            )
            logger.info("[OK] Predicto session initialized")
        return self._predicto_session
    
    async def get_quote(self, symbol: str) -> Quote:
        """Get real-time quote with caching"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{datetime.now().minute}"
            if cache_key in self.quote_cache:
                cached_time = self.quote_cache[cache_key]["timestamp"]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    return Quote(**self.quote_cache[cache_key])
            
            # Fetch fresh data
            quote_data = await self._get_fmp_quote(symbol)
            if quote_data:
                quote = Quote(
                    symbol=symbol,
                    price=quote_data["price"],
                    bid=quote_data.get("bid"),
                    ask=quote_data.get("ask"),
                    volume=quote_data.get("volume"),
                    timestamp=datetime.now()
                )
                
                # Cache the quote
                self.quote_cache[cache_key] = quote.dict()
                
                return quote
            else:
                raise Exception(f"No quote data available for {symbol}")
                
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            raise
    
    async def _get_fmp_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote from Financial Modeling Prep"""
        try:
            session = await self._ensure_fmp_session()
            
            url = f"{self.fmp_config['base_url']}/v3/quote/{symbol}"
            params = {"apikey": self.fmp_config["api_key"]}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        quote = data[0]
                        return {
                            "price": quote.get("price", 0.0),
                            "bid": quote.get("bid"),
                            "ask": quote.get("ask"),
                            "volume": quote.get("volume")
                        }
                else:
                    logger.error(f"FMP API error {response.status} for {symbol}")
                    
        except Exception as e:
            logger.error(f"FMP quote error for {symbol}: {e}")
        
        return None
    
    async def scan_market(self, min_strength: str = "moderate") -> List[TTMSqueezeSignal]:
        """TTM Squeeze market scanner"""
        try:
            signals = []

            for symbol in self.scan_symbols:
                try:
                    # Get quote data
                    quote = await self.get_quote(symbol)

                    # Calculate TTM Squeeze (simplified)
                    signal = await self._calculate_ttm_squeeze(symbol, quote.price)

                    if signal and self._meets_strength_criteria(signal.signal_strength, min_strength):
                        signals.append(signal)

                except Exception as e:
                    logger.warning(f"Scan error for {symbol}: {e}")
                    continue

            # Sort by signal strength
            signals.sort(key=lambda x: self._strength_to_numeric(x.signal_strength), reverse=True)

            return signals[:20]  # Return top 20 signals

        except Exception as e:
            logger.error(f"Market scan error: {e}")
            return []

    async def scan_ttm_squeeze(self, symbols: List[str]) -> Dict[str, Any]:
        """Scan specific symbols for TTM Squeeze signals"""
        try:
            signals = []

            for symbol in symbols:
                try:
                    # Get quote data
                    quote = await self.get_quote(symbol)

                    # Calculate TTM Squeeze (simplified)
                    signal = await self._calculate_ttm_squeeze(symbol, quote.price)

                    if signal:
                        signals.append(signal)

                except Exception as e:
                    logger.warning(f"TTM Squeeze scan error for {symbol}: {e}")
                    continue

            return {
                "signals": [signal.dict() if hasattr(signal, 'dict') else signal for signal in signals],
                "count": len(signals),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"TTM Squeeze scan error: {e}")
            return {"signals": [], "count": 0, "error": str(e)}
    
    async def _calculate_ttm_squeeze(self, symbol: str, price: float) -> Optional[TTMSqueezeSignal]:
        """Calculate real TTM Squeeze signal using Bollinger Bands and Keltner Channels"""
        try:
            # Get historical data for technical analysis
            historical_data = await self._get_historical_data(symbol, period="1d", limit=50)
            if not historical_data or len(historical_data) < 20:
                logger.warning(f"Insufficient historical data for TTM Squeeze calculation: {symbol}")
                return None

            import pandas as pd
            import numpy as np

            # Convert to DataFrame for technical analysis
            df = pd.DataFrame(historical_data)
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)

            # Calculate Bollinger Bands (20-period, 2 std dev)
            bb_period = 20
            bb_std = 2.0
            df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
            bb_std_dev = df['close'].rolling(window=bb_period).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
            df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)

            # Calculate Keltner Channels (20-period, 1.5 multiplier)
            kc_period = 20
            kc_multiplier = 1.5
            df['kc_middle'] = df['close'].rolling(window=kc_period).mean()

            # True Range calculation for Keltner Channels
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = abs(df['high'] - df['close'].shift(1))
            df['tr3'] = abs(df['low'] - df['close'].shift(1))
            df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            df['atr'] = df['true_range'].rolling(window=kc_period).mean()

            df['kc_upper'] = df['kc_middle'] + (df['atr'] * kc_multiplier)
            df['kc_lower'] = df['kc_middle'] - (df['atr'] * kc_multiplier)

            # TTM Squeeze condition: Bollinger Bands inside Keltner Channels
            df['squeeze_active'] = (df['bb_upper'] <= df['kc_upper']) & (df['bb_lower'] >= df['kc_lower'])

            # Momentum calculation (Linear Regression of close prices)
            momentum_period = 12
            df['momentum'] = 0.0

            for i in range(momentum_period, len(df)):
                y = df['close'].iloc[i-momentum_period:i].values
                x = np.arange(len(y))
                if len(y) > 0:
                    # Linear regression slope as momentum
                    slope = np.polyfit(x, y, 1)[0]
                    df.loc[df.index[i], 'momentum'] = slope

            # Get current values
            current_squeeze = df['squeeze_active'].iloc[-1]
            current_momentum = df['momentum'].iloc[-1]
            previous_momentum = df['momentum'].iloc[-2] if len(df) > 1 else 0

            # Calculate histogram value (momentum change)
            histogram_value = current_momentum - previous_momentum

            # Determine signal strength based on momentum magnitude and squeeze status
            momentum_magnitude = abs(current_momentum)

            if current_squeeze:
                # During squeeze, lower threshold for signals
                if momentum_magnitude > 2.0:
                    strength = SignalStrength.VERY_STRONG
                elif momentum_magnitude > 1.5:
                    strength = SignalStrength.STRONG
                elif momentum_magnitude > 1.0:
                    strength = SignalStrength.MODERATE
                elif momentum_magnitude > 0.5:
                    strength = SignalStrength.WEAK
                else:
                    strength = SignalStrength.VERY_WEAK
            else:
                # Post-squeeze, higher threshold
                if momentum_magnitude > 3.0:
                    strength = SignalStrength.VERY_STRONG
                elif momentum_magnitude > 2.0:
                    strength = SignalStrength.STRONG
                elif momentum_magnitude > 1.5:
                    strength = SignalStrength.MODERATE
                elif momentum_magnitude > 1.0:
                    strength = SignalStrength.WEAK
                else:
                    strength = SignalStrength.VERY_WEAK

            # Determine momentum direction
            if current_momentum > 0.3:
                momentum_direction = "bullish"
            elif current_momentum < -0.3:
                momentum_direction = "bearish"
            else:
                momentum_direction = "neutral"

            # Calculate confidence based on multiple factors
            confidence = 0.5  # Base confidence

            # Higher confidence during squeeze breakouts
            if not current_squeeze and df['squeeze_active'].iloc[-2]:
                confidence += 0.2

            # Higher confidence with strong momentum
            if momentum_magnitude > 1.5:
                confidence += 0.2

            # Higher confidence with volume confirmation
            avg_volume = df['volume'].rolling(window=10).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            if current_volume > avg_volume * 1.2:
                confidence += 0.1

            confidence = min(confidence, 0.95)  # Cap at 95%

            # Calculate stop loss and target using ATR
            current_atr = df['atr'].iloc[-1]
            atr_multiplier = 2.0

            if momentum_direction == "bullish":
                stop_loss = price - (current_atr * atr_multiplier)
                target_price = price + (current_atr * atr_multiplier * 1.5)  # 1.5:1 R/R
            elif momentum_direction == "bearish":
                stop_loss = price + (current_atr * atr_multiplier)
                target_price = price - (current_atr * atr_multiplier * 1.5)
            else:
                stop_loss = price * 0.98
                target_price = price * 1.02

            return TTMSqueezeSignal(
                symbol=symbol,
                signal_strength=strength,
                histogram_value=float(histogram_value),
                squeeze_active=bool(current_squeeze),
                momentum_direction=momentum_direction,
                confidence=float(confidence),
                entry_price=price,
                stop_loss=float(stop_loss),
                target_price=float(target_price),
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"TTM Squeeze calculation error for {symbol}: {e}")
            # Fallback to basic calculation if technical analysis fails
            return await self._basic_ttm_fallback(symbol, price)

    async def _get_historical_data(self, symbol: str, period: str = "1d", limit: int = 50) -> List[Dict]:
        """Get historical price data for technical analysis"""
        try:
            # Ensure FMP session is initialized
            fmp_session = await self._ensure_fmp_session()
            if not fmp_session:
                logger.warning("FMP session not available for historical data")
                return []

            # Use FMP API to get historical data
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}"
            params = {
                'apikey': self.fmp_config.get('api_key'),
                'timeseries': limit
            }

            async with fmp_session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'historical' in data:
                        # Convert FMP format to our format
                        historical = []
                        for item in data['historical'][:limit]:
                            historical.append({
                                'close': item['close'],
                                'high': item['high'],
                                'low': item['low'],
                                'volume': item['volume'],
                                'date': item['date']
                            })
                        return list(reversed(historical))  # Oldest first for technical analysis

                logger.warning(f"No historical data available for {symbol}")
                return []

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

    async def _basic_ttm_fallback(self, symbol: str, price: float) -> TTMSqueezeSignal:
        """Fallback TTM Squeeze calculation when full technical analysis fails"""
        try:
            # Basic momentum estimation using recent price action
            recent_quotes = []
            for i in range(5):  # Get last 5 quotes if available
                cache_key = f"{symbol}_{i}"
                if cache_key in self.quote_cache:
                    recent_quotes.append(self.quote_cache[cache_key]['price'])

            if len(recent_quotes) >= 3:
                # Simple momentum: current vs average of recent prices
                avg_recent = sum(recent_quotes[:-1]) / len(recent_quotes[:-1])
                momentum = (price - avg_recent) / avg_recent * 100

                # Estimate signal strength
                if abs(momentum) > 3.0:
                    strength = SignalStrength.STRONG
                elif abs(momentum) > 2.0:
                    strength = SignalStrength.MODERATE
                elif abs(momentum) > 1.0:
                    strength = SignalStrength.WEAK
                else:
                    strength = SignalStrength.VERY_WEAK

                momentum_direction = "bullish" if momentum > 0.5 else "bearish" if momentum < -0.5 else "neutral"
                confidence = min(0.6, abs(momentum) / 5.0)  # Lower confidence for fallback

            else:
                # Minimal fallback
                strength = SignalStrength.WEAK
                momentum_direction = "neutral"
                confidence = 0.3
                momentum = 0.0

            return TTMSqueezeSignal(
                symbol=symbol,
                signal_strength=strength,
                histogram_value=momentum,
                squeeze_active=False,  # Conservative assumption
                momentum_direction=momentum_direction,
                confidence=confidence,
                entry_price=price,
                stop_loss=price * 0.98 if momentum_direction == "bullish" else price * 1.02,
                target_price=price * 1.03 if momentum_direction == "bullish" else price * 0.97,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Fallback TTM calculation error for {symbol}: {e}")
            # Ultimate fallback
            return TTMSqueezeSignal(
                symbol=symbol,
                signal_strength=SignalStrength.VERY_WEAK,
                histogram_value=0.0,
                squeeze_active=False,
                momentum_direction="neutral",
                confidence=0.2,
                entry_price=price,
                stop_loss=price * 0.98,
                target_price=price * 1.02,
                timestamp=datetime.now()
            )

    def _meets_strength_criteria(self, signal_strength: SignalStrength, min_strength: str) -> bool:
        """Check if signal meets minimum strength criteria"""
        strength_order = {
            "very_weak": 1,
            "weak": 2,
            "moderate": 3,
            "strong": 4,
            "very_strong": 5
        }
        
        signal_value = strength_order.get(signal_strength.value, 0)
        min_value = strength_order.get(min_strength, 3)
        
        return signal_value >= min_value
    
    def _strength_to_numeric(self, strength: SignalStrength) -> int:
        """Convert signal strength to numeric value for sorting"""
        strength_map = {
            SignalStrength.VERY_WEAK: 1,
            SignalStrength.WEAK: 2,
            SignalStrength.MODERATE: 3,
            SignalStrength.STRONG: 4,
            SignalStrength.VERY_STRONG: 5
        }
        return strength_map.get(strength, 0)

    def _calculate_5_star_rating(self, squeeze_active: bool, momentum_value: float,
                                bb_squeeze: bool, kc_squeeze: bool,
                                volume_data: List[float], price_data: List[float]) -> tuple[int, float]:
        """Calculate enhanced 5-star rating for TTM Squeeze signals"""
        try:
            star_rating = 1  # Start with 1 star
            confidence = 0.3

            # Factor 1: Momentum strength (0-2 stars)
            momentum_magnitude = abs(momentum_value)
            if momentum_magnitude > 3.0:
                star_rating += 2
                confidence += 0.3
            elif momentum_magnitude > 1.5:
                star_rating += 1
                confidence += 0.2
            elif momentum_magnitude > 0.5:
                confidence += 0.1

            # Factor 2: Squeeze status (0-1 star)
            if not squeeze_active:  # Squeeze fired
                star_rating += 1
                confidence += 0.2

            # Factor 3: Volume confirmation (0-1 star)
            if len(volume_data) >= 2:
                recent_volume = volume_data[-1]
                avg_volume = sum(volume_data[-5:]) / min(5, len(volume_data))
                if recent_volume > avg_volume * 1.5:  # 50% above average
                    star_rating += 1
                    confidence += 0.2

            # Factor 4: Price action confirmation (0-1 star)
            if len(price_data) >= 3:
                # Check for breakout pattern
                current_price = price_data[-1]
                prev_price = price_data[-2]
                price_change = (current_price - prev_price) / prev_price

                # Momentum and price change alignment
                if (momentum_value > 0 and price_change > 0.01) or \
                   (momentum_value < 0 and price_change < -0.01):
                    star_rating += 1
                    confidence += 0.1

            # Cap at 5 stars and normalize confidence
            star_rating = min(star_rating, 5)
            confidence = min(confidence, 0.95)

            return star_rating, confidence

        except Exception as e:
            logger.error(f"5-star rating calculation error: {e}")
            return 1, 0.3  # Default to 1 star, low confidence

    async def get_predicto_forecast(self, symbol: str, days: int = 5) -> Optional[PredictoForecast]:
        """Get Predicto AI forecast with graceful fallback"""
        try:
            if not self.predicto_config.get("enabled"):
                logger.debug(f"Predicto API disabled, skipping forecast for {symbol}")
                return None

            # Check if this is the placeholder URL that doesn't exist
            if "api.predic.to" in self.predicto_config.get('base_url', ''):
                logger.debug(f"Predicto API using placeholder URL, skipping forecast for {symbol}")
                return None

            session = await self._ensure_predicto_session()
            if not session:
                return None

            url = f"{self.predicto_config['base_url']}/forecast"
            data = {
                "symbol": symbol,
                "days": days,
                "model": "advanced"
            }

            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()

                    return PredictoForecast(
                        symbol=symbol,
                        forecast_days=days,
                        predicted_price=result.get("predicted_price", 0.0),
                        confidence=result.get("confidence", 0.5),
                        price_targets=result.get("price_targets"),
                        risk_factors=result.get("risk_factors"),
                        sentiment_score=result.get("sentiment_score"),
                        timestamp=datetime.now()
                    )
                else:
                    logger.warning(f"Predicto API error {response.status} for {symbol}")

        except Exception as e:
            # Don't log as error for connection failures to placeholder URLs
            if "api.predic.to" in str(e) or "getaddrinfo failed" in str(e):
                logger.debug(f"Predicto API unavailable (placeholder URL), skipping forecast for {symbol}")
            else:
                logger.error(f"Predicto forecast error for {symbol}: {e}")

        return None

    # ===== WEB SEARCH INTEGRATION =====

    async def search_market_context(self, symbol: str, query_type: str = "news") -> Dict[str, Any]:
        """Search for market context and news about a symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{query_type}"
            if cache_key in self.news_cache:
                cached_time = self.news_cache[cache_key].get("timestamp", datetime.min)
                if (datetime.now() - cached_time).seconds < self.news_cache_ttl:
                    logger.info(f"📰 Returning cached news for {symbol}")
                    return self.news_cache[cache_key]["data"]

            # Build search query
            query = self._build_search_query(symbol, query_type)

            # Perform search
            search_results = await self._perform_web_search(query)

            if search_results.get("success"):
                # Analyze sentiment and relevance
                analyzed_results = self._analyze_search_results(search_results["results"], symbol, query_type)

                # Cache results
                self.news_cache[cache_key] = {
                    "data": analyzed_results,
                    "timestamp": datetime.now()
                }

                logger.info(f"📰 Found {len(analyzed_results.get('results', []))} relevant results for {symbol}")
                return analyzed_results
            else:
                logger.warning(f"Web search failed for {symbol}: {search_results.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": "Web search not available",
                    "results": [],
                    "sentiment_score": 0.0,
                    "market_impact": "unknown"
                }

        except Exception as e:
            logger.error(f"Market context search error for {symbol}: {e}")
            return {
                "success": False,
                "error": f"Search error: {str(e)}",
                "results": [],
                "sentiment_score": 0.0,
                "market_impact": "unknown"
            }

    def _build_search_query(self, symbol: str, query_type: str) -> str:
        """Build search query based on symbol and query type"""
        base_queries = {
            "news": f"{symbol} stock news earnings latest",
            "earnings": f"{symbol} earnings report quarterly results",
            "analyst": f"{symbol} analyst rating price target upgrade downgrade",
            "volatility": f"{symbol} stock volatility unusual activity",
            "general": f"{symbol} stock market analysis"
        }

        return base_queries.get(query_type, base_queries["general"])

    async def _perform_web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search using available providers"""
        try:
            primary_provider = self.web_search_config.get("primary")

            if primary_provider == "google":
                return await self._google_search(query, max_results)
            elif primary_provider == "duckduckgo":
                return await self._duckduckgo_search(query, max_results)
            else:
                return {
                    "success": False,
                    "error": "No web search providers available",
                    "results": []
                }

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "results": []
            }

    async def _google_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform Google Custom Search"""
        try:
            if not GOOGLE_SEARCH_AVAILABLE:
                raise Exception("Google Search API not available")

            config = self.web_search_config["google"]
            if not config["enabled"]:
                raise Exception("Google Search not configured")

            # Initialize Google service if needed
            if not self._google_service:
                self._google_service = build("customsearch", "v1", developerKey=config["api_key"])

            # Perform search
            result = self._google_service.cse().list(
                q=query,
                cx=config["engine_id"],
                num=max_results
            ).execute()

            # Process results
            results = []
            for item in result.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": "google"
                })

            return {
                "success": True,
                "results": results,
                "total_results": len(results)
            }

        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {
                "success": False,
                "error": f"Google search failed: {str(e)}",
                "results": []
            }

    async def _duckduckgo_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform DuckDuckGo search"""
        try:
            if not DUCKDUCKGO_AVAILABLE:
                raise Exception("DuckDuckGo search not available")

            # Perform search
            with DDGS() as ddgs:
                results = []
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "url": result.get("href", ""),
                        "source": "duckduckgo"
                    })

            return {
                "success": True,
                "results": results,
                "total_results": len(results)
            }

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return {
                "success": False,
                "error": f"DuckDuckGo search failed: {str(e)}",
                "results": []
            }

    def _analyze_search_results(self, results: List[Dict], symbol: str, query_type: str) -> Dict[str, Any]:
        """Analyze search results for sentiment and relevance"""
        try:
            if not results:
                return {
                    "success": True,
                    "results": [],
                    "sentiment_score": 0.0,
                    "market_impact": "neutral",
                    "summary": "No relevant news found"
                }

            # Analyze sentiment for each result
            analyzed_results = []
            total_sentiment = 0.0

            for result in results:
                # Calculate relevance score
                relevance = self._calculate_market_relevance(result, symbol, query_type)

                # Analyze sentiment
                sentiment = self._analyze_market_sentiment(result.get("snippet", "") + " " + result.get("title", ""))

                analyzed_result = {
                    **result,
                    "relevance_score": relevance,
                    "sentiment": sentiment["sentiment"],
                    "sentiment_score": sentiment["score"],
                    "confidence": sentiment["confidence"]
                }

                analyzed_results.append(analyzed_result)
                total_sentiment += sentiment["score"] * relevance  # Weight by relevance

            # Calculate overall sentiment
            avg_sentiment = total_sentiment / len(results) if results else 0.0

            # Determine market impact
            market_impact = "neutral"
            if avg_sentiment > 0.3:
                market_impact = "positive"
            elif avg_sentiment < -0.3:
                market_impact = "negative"

            # Generate summary
            summary = self._generate_news_summary(analyzed_results, symbol, avg_sentiment)

            return {
                "success": True,
                "results": analyzed_results,
                "sentiment_score": avg_sentiment,
                "market_impact": market_impact,
                "summary": summary,
                "total_results": len(analyzed_results)
            }

        except Exception as e:
            logger.error(f"Search result analysis error: {e}")
            return {
                "success": True,
                "results": results,
                "sentiment_score": 0.0,
                "market_impact": "unknown",
                "summary": "Analysis failed but results available"
            }

    def _calculate_market_relevance(self, result: Dict, symbol: str, query_type: str) -> float:
        """Calculate relevance score for a search result"""
        try:
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            score = 0.0

            # Symbol mention
            if symbol.lower() in text:
                score += 0.4

            # Financial keywords
            financial_keywords = [
                "earnings", "revenue", "profit", "loss", "stock", "shares", "market",
                "analyst", "rating", "upgrade", "downgrade", "price target", "dividend",
                "quarterly", "annual", "guidance", "outlook", "forecast"
            ]

            for keyword in financial_keywords:
                if keyword in text:
                    score += 0.1

            # Query type specific keywords
            type_keywords = {
                "earnings": ["earnings", "quarterly", "revenue", "profit", "eps"],
                "analyst": ["analyst", "rating", "upgrade", "downgrade", "target"],
                "news": ["news", "announcement", "report", "update"],
                "volatility": ["volatility", "unusual", "volume", "spike", "drop"]
            }

            for keyword in type_keywords.get(query_type, []):
                if keyword in text:
                    score += 0.15

            return min(score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.error(f"Relevance calculation error: {e}")
            return 0.5  # Default relevance

    def _analyze_market_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of market-related text"""
        try:
            if not text:
                return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}

            text_lower = text.lower()

            # Positive indicators
            positive_words = [
                "beat", "beats", "strong", "growth", "gain", "gains", "up", "rise", "rises",
                "bullish", "positive", "good", "great", "excellent", "outperform", "buy",
                "upgrade", "raised", "increased", "higher", "record", "profit", "revenue"
            ]

            # Negative indicators
            negative_words = [
                "miss", "misses", "weak", "decline", "loss", "losses", "down", "fall", "falls",
                "bearish", "negative", "bad", "poor", "terrible", "underperform", "sell",
                "downgrade", "lowered", "decreased", "lower", "disappointing", "concern"
            ]

            # Count sentiment words
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            # Calculate sentiment score (-1 to 1)
            total_words = positive_count + negative_count
            if total_words == 0:
                sentiment_score = 0.0
                sentiment = "neutral"
                confidence = 0.1
            else:
                sentiment_score = (positive_count - negative_count) / max(total_words, 1)
                confidence = min(total_words / 10.0, 1.0)  # More words = higher confidence

                if sentiment_score > 0.2:
                    sentiment = "positive"
                elif sentiment_score < -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"

            return {
                "sentiment": sentiment,
                "score": sentiment_score,
                "confidence": confidence,
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.0}

    def _generate_news_summary(self, results: List[Dict], symbol: str, sentiment_score: float) -> str:
        """Generate a summary of news results"""
        try:
            if not results:
                return f"No recent news found for {symbol}"

            # Sentiment description
            if sentiment_score > 0.3:
                sentiment_desc = "[UP] Positive news sentiment"
            elif sentiment_score < -0.3:
                sentiment_desc = "[DOWN] Negative news sentiment"
            else:
                sentiment_desc = "😐 Neutral news sentiment"

            # Top result
            top_result = max(results, key=lambda x: x.get("relevance_score", 0))

            summary = f"{sentiment_desc} for {symbol}. "
            summary += f"Top story: {top_result.get('title', 'N/A')[:80]}..."

            if len(results) > 1:
                summary += f" Plus {len(results)-1} more stories."

            return summary

        except Exception as e:
            logger.error(f"News summary generation error: {e}")
            return f"Found {len(results)} news items for {symbol}"

    async def cleanup(self):
        """Cleanup market engine resources"""
        try:
            # Close HTTP sessions
            if self._fmp_session:
                await self._fmp_session.close()
            
            if self._predicto_session:
                await self._predicto_session.close()
            
            # Clear cache
            self.quote_cache.clear()
            
            logger.info("[OK] Market Engine cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during market engine cleanup: {e}")
