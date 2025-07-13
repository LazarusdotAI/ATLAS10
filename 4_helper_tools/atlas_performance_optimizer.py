"""
A.T.L.A.S Performance Optimization Module
Ensures <2 second response times, caching, and system optimization
"""

import asyncio
import time
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json
import threading
from functools import wraps
import weakref

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'duration': self.duration,
            'success': self.success,
            'error_message': self.error_message,
            'timestamp': datetime.fromtimestamp(self.end_time).isoformat()
        }


class AdvancedCache:
    """Advanced caching system with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            
            # Check TTL
            if time.time() > item['expires_at']:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return None
            
            # Update access time
            self.access_times[key] = time.time()
            return item['data']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache"""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            # Evict if at max size
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            expires_at = time.time() + ttl
            self.cache[key] = {
                'data': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            self.access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def _start_cleanup(self) -> None:
        """Start background cleanup task"""
        def cleanup_expired():
            while True:
                try:
                    current_time = time.time()
                    with self.lock:
                        expired_keys = [
                            key for key, item in self.cache.items()
                            if current_time > item['expires_at']
                        ]
                        for key in expired_keys:
                            del self.cache[key]
                            if key in self.access_times:
                                del self.access_times[key]
                    
                    time.sleep(60)  # Cleanup every minute
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: List[PerformanceMetrics] = []
        self.cache = AdvancedCache(max_size=1000, default_ttl=settings.CACHE_TTL)
        self.metrics_lock = threading.RLock()
        
        # System monitoring
        self.system_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'response_times': []
        }
        
        # Performance thresholds
        self.response_time_threshold = 2.0  # seconds
        self.memory_threshold = settings.MEMORY_USAGE_THRESHOLD
        self.cpu_threshold = settings.CPU_USAGE_THRESHOLD
        
        self.logger.info("[LAUNCH] Performance Optimizer initialized")
    
    def performance_monitor(self, operation_name: str):
        """Decorator for monitoring operation performance"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_message = None
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    metric = PerformanceMetrics(
                        operation=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        success=success,
                        error_message=error_message
                    )
                    
                    self._record_metric(metric)
                    
                    # Log slow operations
                    if duration > self.response_time_threshold:
                        self.logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_message = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    metric = PerformanceMetrics(
                        operation=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        success=success,
                        error_message=error_message
                    )
                    
                    self._record_metric(metric)
                    
                    # Log slow operations
                    if duration > self.response_time_threshold:
                        self.logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _record_metric(self, metric: PerformanceMetrics) -> None:
        """Record performance metric"""
        with self.metrics_lock:
            self.metrics.append(metric)
            
            # Keep only last 1000 metrics
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
            
            # Update system metrics
            self.system_metrics['response_times'].append(metric.duration)
            if len(self.system_metrics['response_times']) > 100:
                self.system_metrics['response_times'] = self.system_metrics['response_times'][-100:]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Calculate average response time
            avg_response_time = 0.0
            if self.system_metrics['response_times']:
                avg_response_time = sum(self.system_metrics['response_times']) / len(self.system_metrics['response_times'])
            
            # Calculate success rate
            recent_metrics = self.metrics[-100:] if len(self.metrics) >= 100 else self.metrics
            success_rate = 1.0
            if recent_metrics:
                successful = sum(1 for m in recent_metrics if m.success)
                success_rate = successful / len(recent_metrics)
            
            health_status = "healthy"
            if cpu_percent > self.cpu_threshold or memory.percent > self.memory_threshold:
                health_status = "warning"
            if avg_response_time > self.response_time_threshold or success_rate < 0.95:
                health_status = "critical"
            
            return {
                'status': health_status,
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'avg_response_time': avg_response_time,
                'success_rate': success_rate,
                'cache_size': len(self.cache.cache),
                'total_operations': len(self.metrics),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
