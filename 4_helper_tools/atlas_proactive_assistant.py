"""
A.T.L.A.S Proactive Trading Assistant
Provides morning briefings, real-time notifications, market protection, and time-sensitive alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json

from config import settings
from models import AlertPriority, AlertType, ProactiveAlert, TTMSqueezeSignal, Quote
from atlas_performance_optimizer import performance_optimizer

logger = logging.getLogger(__name__)


class ProactiveTradingAssistant:
    """
    Proactive trading assistant that monitors market conditions and user behavior
    to provide timely alerts, briefings, and protective measures
    """
    
    def __init__(self, market_engine=None, ai_engine=None):
        self.logger = logging.getLogger(__name__)
        self.market_engine = market_engine
        self.ai_engine = ai_engine
        
        # Configuration
        self.enabled = settings.PROACTIVE_ASSISTANT_ENABLED
        self.morning_briefing_time = self._parse_time(settings.MORNING_BRIEFING_TIME)
        self.alert_cooldown = settings.ALERT_COOLDOWN_MINUTES * 60  # Convert to seconds
        self.min_signal_strength = settings.MIN_SIGNAL_STRENGTH
        
        # Alert management
        self.active_alerts: List[ProactiveAlert] = []
        self.alert_callbacks: List[Callable] = []
        self.alert_history: List[ProactiveAlert] = []
        
        # Scheduling and state
        self.is_running = False
        self.last_briefing_date = None
        self.monitoring_tasks = []
        
        # Market protection thresholds
        self.vix_protection_threshold = 30.0
        self.market_drop_threshold = -2.0  # 2% drop
        self.volume_spike_threshold = 2.0  # 2x normal volume
        
        # Opportunity tracking
        self.last_opportunity_alerts = {}
        self.opportunity_cooldown = 300  # 5 minutes between similar alerts
        
        # Performance tracking
        self.alerts_sent_today = 0
        self.briefings_sent = 0
        
        self.logger.info(f"[BOT] Proactive Trading Assistant initialized - enabled: {self.enabled}")
    
    async def start_monitoring(self):
        """Start proactive monitoring and alert system"""
        if not self.enabled:
            self.logger.info("Proactive assistant disabled in configuration")
            return
        
        if self.is_running:
            self.logger.warning("Proactive assistant already running")
            return
        
        self.is_running = True
        self.logger.info("[LAUNCH] Starting proactive trading assistant monitoring...")
        
        try:
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._morning_briefing_scheduler()),
                asyncio.create_task(self._market_protection_monitor()),
                asyncio.create_task(self._opportunity_scanner()),
                asyncio.create_task(self._volatility_monitor()),
                asyncio.create_task(self._alert_cleanup_task())
            ]
            
            # Wait for all tasks
            await asyncio.gather(*self.monitoring_tasks)
            
        except asyncio.CancelledError:
            self.logger.info("Proactive assistant monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error in proactive assistant monitoring: {e}")
        finally:
            self.is_running = False
    
    def stop_monitoring(self):
        """Stop proactive monitoring"""
        if not self.is_running:
            return
        
        self.logger.info("🛑 Stopping proactive trading assistant...")
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
        
        self.is_running = False
    
    async def _morning_briefing_scheduler(self):
        """Schedule and send morning briefings"""
        while self.is_running:
            try:
                current_time = datetime.now().time()
                current_date = datetime.now().date()
                
                # Check if it's time for morning briefing
                if (current_time >= self.morning_briefing_time and 
                    self.last_briefing_date != current_date and
                    self._is_trading_day()):
                    
                    await self._send_morning_briefing()
                    self.last_briefing_date = current_date
                
                # Sleep for 1 minute before checking again
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in morning briefing scheduler: {e}")
                await asyncio.sleep(60)
    
    async def _send_morning_briefing(self):
        """Generate and send morning briefing"""
        try:
            self.logger.info("[DATA] Generating morning briefing...")
            
            # Gather market data
            market_summary = await self._get_market_summary()
            
            # Get overnight developments
            overnight_movers = await self._get_overnight_movers()
            
            # Get today's economic calendar
            economic_events = await self._get_economic_calendar()
            
            # Get portfolio status
            portfolio_status = await self._get_portfolio_status()
            
            # Generate TTM Squeeze signals
            ttm_signals = await self._get_morning_ttm_signals()
            
            # Create briefing message
            briefing_message = self._format_morning_briefing(
                market_summary, overnight_movers, economic_events, 
                portfolio_status, ttm_signals
            )
            
            # Create alert
            alert = ProactiveAlert(
                alert_type=AlertType.MORNING_BRIEFING,
                priority=AlertPriority.MEDIUM,
                title="🌅 Morning Trading Briefing",
                message=briefing_message,
                action_required=False,
                expiry_time=datetime.now() + timedelta(hours=8),
                metadata={
                    'market_summary': market_summary,
                    'overnight_movers': overnight_movers,
                    'economic_events': economic_events,
                    'ttm_signals': len(ttm_signals)
                },
                timestamp=datetime.now()
            )
            
            await self._send_alert(alert)
            self.briefings_sent += 1
            
            self.logger.info("[OK] Morning briefing sent successfully")
            
        except Exception as e:
            self.logger.error(f"Error sending morning briefing: {e}")
    
    async def _market_protection_monitor(self):
        """Monitor for market protection alerts"""
        while self.is_running:
            try:
                # Check VIX levels
                await self._check_vix_protection()
                
                # Check market drops
                await self._check_market_drops()
                
                # Check volume spikes
                await self._check_volume_spikes()
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in market protection monitor: {e}")
                await asyncio.sleep(300)
    
    async def _opportunity_scanner(self):
        """Scan for trading opportunities and send alerts"""
        while self.is_running:
            try:
                # Get TTM Squeeze signals
                if self.market_engine:
                    signals = await self.market_engine.scan_market("strong")
                    
                    for signal in signals:
                        if self._should_send_opportunity_alert(signal):
                            await self._send_opportunity_alert(signal)
                
                # Sleep for 2 minutes
                await asyncio.sleep(120)
                
            except Exception as e:
                self.logger.error(f"Error in opportunity scanner: {e}")
                await asyncio.sleep(120)
    
    async def _volatility_monitor(self):
        """Monitor volatility and send alerts"""
        while self.is_running:
            try:
                # Check for volatility spikes
                await self._check_volatility_spikes()
                
                # Sleep for 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                self.logger.error(f"Error in volatility monitor: {e}")
                await asyncio.sleep(600)
    
    async def _alert_cleanup_task(self):
        """Clean up expired alerts"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Remove expired alerts
                self.active_alerts = [
                    alert for alert in self.active_alerts
                    if not alert.expiry_time or alert.expiry_time > current_time
                ]
                
                # Clean up old opportunity alerts
                cutoff_time = current_time - timedelta(seconds=self.opportunity_cooldown)
                self.last_opportunity_alerts = {
                    symbol: timestamp for symbol, timestamp in self.last_opportunity_alerts.items()
                    if timestamp > cutoff_time
                }
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in alert cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _get_market_summary(self) -> Dict[str, Any]:
        """Get current market summary"""
        try:
            summary = {
                'spy_price': 0.0,
                'spy_change': 0.0,
                'vix_level': 0.0,
                'market_sentiment': 'neutral'
            }
            
            if self.market_engine:
                # Get SPY quote
                spy_quote = await self.market_engine.get_quote('SPY')
                if spy_quote:
                    summary['spy_price'] = spy_quote.price
                    summary['spy_change'] = spy_quote.change_percent
                
                # Get VIX level
                vix_quote = await self.market_engine.get_quote('VIX')
                if vix_quote:
                    summary['vix_level'] = vix_quote.price
                
                # Determine market sentiment
                if summary['spy_change'] > 1.0:
                    summary['market_sentiment'] = 'bullish'
                elif summary['spy_change'] < -1.0:
                    summary['market_sentiment'] = 'bearish'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return {'error': str(e)}
    
    async def _get_overnight_movers(self) -> List[Dict[str, Any]]:
        """Get overnight movers"""
        try:
            movers = []
            
            # This would integrate with market data provider
            # For now, return mock data
            mock_movers = [
                {'symbol': 'AAPL', 'change_percent': 2.5, 'reason': 'Earnings beat'},
                {'symbol': 'TSLA', 'change_percent': -3.2, 'reason': 'Production concerns'},
                {'symbol': 'NVDA', 'change_percent': 4.1, 'reason': 'AI partnership news'}
            ]
            
            return mock_movers
            
        except Exception as e:
            self.logger.error(f"Error getting overnight movers: {e}")
            return []
    
    async def _get_economic_calendar(self) -> List[Dict[str, Any]]:
        """Get today's economic calendar events"""
        try:
            # This would integrate with economic calendar API
            # For now, return mock data
            events = [
                {'time': '08:30', 'event': 'Initial Jobless Claims', 'importance': 'medium'},
                {'time': '14:00', 'event': 'FOMC Meeting Minutes', 'importance': 'high'}
            ]
            
            return events
            
        except Exception as e:
            self.logger.error(f"Error getting economic calendar: {e}")
            return []
    
    async def _get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        try:
            # This would integrate with portfolio management
            # For now, return mock data
            return {
                'total_value': 100000.0,
                'daily_pnl': 1250.0,
                'daily_pnl_percent': 1.25,
                'positions_count': 5,
                'cash_available': 25000.0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio status: {e}")
            return {}
    
    async def _get_morning_ttm_signals(self) -> List[TTMSqueezeSignal]:
        """Get morning TTM Squeeze signals"""
        try:
            if self.market_engine:
                return await self.market_engine.scan_market("moderate")
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting TTM signals: {e}")
            return []
    
    def _format_morning_briefing(self, market_summary: Dict, overnight_movers: List,
                               economic_events: List, portfolio_status: Dict,
                               ttm_signals: List) -> str:
        """Format morning briefing message"""
        try:
            briefing = "🌅 **MORNING TRADING BRIEFING**\n\n"
            
            # Market Summary
            briefing += "[DATA] **MARKET OVERVIEW**\n"
            if 'spy_change' in market_summary:
                briefing += f"• SPY: ${market_summary.get('spy_price', 0):.2f} ({market_summary.get('spy_change', 0):+.2f}%)\n"
            if 'vix_level' in market_summary:
                briefing += f"• VIX: {market_summary.get('vix_level', 0):.1f}\n"
            briefing += f"• Sentiment: {market_summary.get('market_sentiment', 'neutral').title()}\n\n"
            
            # Portfolio Status
            if portfolio_status:
                briefing += "[TRADE] **PORTFOLIO STATUS**\n"
                briefing += f"• Total Value: ${portfolio_status.get('total_value', 0):,.0f}\n"
                briefing += f"• Daily P&L: ${portfolio_status.get('daily_pnl', 0):+,.0f} ({portfolio_status.get('daily_pnl_percent', 0):+.2f}%)\n"
                briefing += f"• Positions: {portfolio_status.get('positions_count', 0)}\n\n"
            
            # Overnight Movers
            if overnight_movers:
                briefing += "[LAUNCH] **OVERNIGHT MOVERS**\n"
                for mover in overnight_movers[:3]:
                    briefing += f"• {mover['symbol']}: {mover['change_percent']:+.1f}% - {mover['reason']}\n"
                briefing += "\n"
            
            # Economic Events
            if economic_events:
                briefing += "📅 **TODAY'S EVENTS**\n"
                for event in economic_events:
                    briefing += f"• {event['time']} - {event['event']} ({event['importance']})\n"
                briefing += "\n"
            
            # TTM Signals
            if ttm_signals:
                briefing += f"[TARGET] **TTM SQUEEZE SIGNALS**\n"
                briefing += f"• {len(ttm_signals)} signals detected\n"
                for signal in ttm_signals[:3]:
                    briefing += f"• {signal.symbol}: {signal.signal_strength.value} ({signal.momentum_direction})\n"
                briefing += "\n"
            
            briefing += "Have a profitable trading day! [UP]"
            
            return briefing
            
        except Exception as e:
            self.logger.error(f"Error formatting briefing: {e}")
            return "Error generating morning briefing"
    
    def _should_send_opportunity_alert(self, signal: TTMSqueezeSignal) -> bool:
        """Check if opportunity alert should be sent"""
        try:
            # Check signal strength
            if self._signal_strength_to_numeric(signal.signal_strength) < self.min_signal_strength:
                return False
            
            # Check cooldown
            symbol = signal.symbol
            current_time = datetime.now()
            
            if symbol in self.last_opportunity_alerts:
                last_alert_time = self.last_opportunity_alerts[symbol]
                if (current_time - last_alert_time).total_seconds() < self.opportunity_cooldown:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking opportunity alert: {e}")
            return False
    
    async def _send_opportunity_alert(self, signal: TTMSqueezeSignal):
        """Send opportunity alert"""
        try:
            alert = ProactiveAlert(
                alert_type=AlertType.OPPORTUNITY_NOTIFICATION,
                priority=AlertPriority.HIGH,
                title=f"[TARGET] Trading Opportunity: {signal.symbol}",
                message=f"TTM Squeeze signal detected for {signal.symbol}\n"
                       f"Direction: {signal.momentum_direction}\n"
                       f"Strength: {signal.signal_strength.value}\n"
                       f"Entry: ${signal.entry_price:.2f}\n"
                       f"Target: ${signal.target_price:.2f}",
                action_required=True,
                expiry_time=datetime.now() + timedelta(hours=1),
                metadata={
                    'symbol': signal.symbol,
                    'signal_strength': signal.signal_strength.value,
                    'entry_price': signal.entry_price,
                    'target_price': signal.target_price,
                    'stop_loss': signal.stop_loss
                },
                timestamp=datetime.now()
            )
            
            await self._send_alert(alert)
            self.last_opportunity_alerts[signal.symbol] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error sending opportunity alert: {e}")
    
    async def _check_vix_protection(self):
        """Check VIX levels for protection alerts"""
        try:
            if not self.market_engine:
                return
            
            vix_quote = await self.market_engine.get_quote('VIX')
            if vix_quote and vix_quote.price > self.vix_protection_threshold:
                
                alert = ProactiveAlert(
                    alert_type=AlertType.MARKET_PROTECTION,
                    priority=AlertPriority.CRITICAL,
                    title="[WARN] High VIX Alert",
                    message=f"VIX at {vix_quote.price:.1f} - Consider protective measures",
                    action_required=True,
                    expiry_time=datetime.now() + timedelta(hours=2),
                    metadata={'vix_level': vix_quote.price},
                    timestamp=datetime.now()
                )
                
                await self._send_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error checking VIX protection: {e}")
    
    async def _check_market_drops(self):
        """Check for significant market drops"""
        try:
            if not self.market_engine:
                return
            
            spy_quote = await self.market_engine.get_quote('SPY')
            if spy_quote and spy_quote.change_percent < self.market_drop_threshold:
                
                alert = ProactiveAlert(
                    alert_type=AlertType.MARKET_PROTECTION,
                    priority=AlertPriority.HIGH,
                    title="[DOWN] Market Drop Alert",
                    message=f"SPY down {spy_quote.change_percent:.1f}% - Review positions",
                    action_required=True,
                    expiry_time=datetime.now() + timedelta(hours=1),
                    metadata={'spy_change': spy_quote.change_percent},
                    timestamp=datetime.now()
                )
                
                await self._send_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error checking market drops: {e}")
    
    async def _check_volume_spikes(self):
        """Check for volume spikes"""
        # Implementation would check volume vs average
        pass
    
    async def _check_volatility_spikes(self):
        """Check for volatility spikes"""
        # Implementation would check IV changes
        pass
    
    async def _send_alert(self, alert: ProactiveAlert):
        """Send alert to all registered callbacks"""
        try:
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
            self.alerts_sent_today += 1
            
            # Call all registered callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
            
            self.logger.info(f"📢 Alert sent: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except:
            return time(9, 0)  # Default to 9:00 AM
    
    def _is_trading_day(self) -> bool:
        """Check if today is a trading day"""
        # Simple check - weekdays only
        return datetime.now().weekday() < 5
    
    def _signal_strength_to_numeric(self, strength) -> int:
        """Convert signal strength to numeric value"""
        strength_map = {
            'very_weak': 1,
            'weak': 2,
            'moderate': 3,
            'strong': 4,
            'very_strong': 5
        }
        return strength_map.get(strength.value if hasattr(strength, 'value') else str(strength), 0)
    
    def get_assistant_status(self) -> Dict[str, Any]:
        """Get assistant status and metrics"""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'alerts_sent_today': self.alerts_sent_today,
            'briefings_sent': self.briefings_sent,
            'active_alerts_count': len(self.active_alerts),
            'last_briefing_date': self.last_briefing_date.isoformat() if self.last_briefing_date else None,
            'monitoring_tasks_count': len([t for t in self.monitoring_tasks if not t.done()]),
            'configuration': {
                'morning_briefing_time': self.morning_briefing_time.strftime('%H:%M'),
                'min_signal_strength': self.min_signal_strength,
                'alert_cooldown_minutes': self.alert_cooldown // 60
            }
        }


# Global proactive assistant instance
proactive_assistant = ProactiveTradingAssistant()
