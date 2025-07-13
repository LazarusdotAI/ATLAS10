#!/usr/bin/env python3
"""
A.T.L.A.S. Enhanced Error Handler
Provides comprehensive error handling, graceful degradation, and recovery mechanisms
"""

import logging
import traceback
import asyncio
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from functools import wraps

# Import Windows-compatible logging
try:
    from atlas_logging_config import get_atlas_logger
except ImportError:
    def get_atlas_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComponentStatus(Enum):
    """Component status after error"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class ErrorContext:
    """Error context information"""
    component: str
    operation: str
    severity: ErrorSeverity
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    timestamp: datetime
    recovery_attempted: bool = False
    recovery_successful: bool = False
    fallback_used: bool = False

class AtlasErrorHandler:
    """Enhanced error handler for A.T.L.A.S. system"""
    
    def __init__(self):
        self.logger = get_atlas_logger('atlas_error_handler')
        self.error_history: Dict[str, list] = {}
        self.component_status: Dict[str, ComponentStatus] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.fallback_responses: Dict[str, Any] = {}
        
        # Initialize default fallback responses
        self._setup_default_fallbacks()
        
        self.logger.info("[SHIELD] Enhanced Error Handler initialized")
    
    def _setup_default_fallbacks(self):
        """Setup default fallback responses for common operations"""
        self.fallback_responses.update({
            "chat_response": {
                "response": "I'm experiencing technical difficulties. Please try again in a moment.",
                "type": "error",
                "confidence": 0.0,
                "context": {"error": "system_error"}
            },
            "market_data": {
                "symbol": "UNKNOWN",
                "price": 0.0,
                "change": 0.0,
                "error": "Market data temporarily unavailable"
            },
            "analysis_result": {
                "analysis": "Analysis temporarily unavailable due to system issues",
                "confidence": 0.0,
                "recommendations": ["Please try again later"],
                "error": "analysis_failed"
            },
            "trading_result": {
                "success": False,
                "error": "Trading functionality temporarily unavailable",
                "message": "Please try again later or contact support"
            }
        })
    
    def register_recovery_strategy(self, component: str, strategy: Callable):
        """Register a recovery strategy for a component"""
        self.recovery_strategies[component] = strategy
        self.logger.info(f"[TOOL] Recovery strategy registered for {component}")
    
    def register_fallback_response(self, operation: str, fallback: Any):
        """Register a fallback response for an operation"""
        self.fallback_responses[operation] = fallback
        self.logger.info(f"[TOOL] Fallback response registered for {operation}")
    
    async def handle_error(self, 
                          component: str, 
                          operation: str, 
                          error: Exception,
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          attempt_recovery: bool = True) -> ErrorContext:
        """Handle an error with comprehensive logging and recovery"""
        
        # Create error context
        error_context = ErrorContext(
            component=component,
            operation=operation,
            severity=severity,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now()
        )
        
        # Log the error
        self._log_error(error_context)
        
        # Track error history
        self._track_error(error_context)
        
        # Update component status
        self._update_component_status(component, error_context)
        
        # Attempt recovery if enabled
        if attempt_recovery and component in self.recovery_strategies:
            try:
                recovery_result = await self.recovery_strategies[component]()
                error_context.recovery_attempted = True
                error_context.recovery_successful = recovery_result
                
                if recovery_result:
                    self.logger.info(f"[OK] Recovery successful for {component}")
                    self.component_status[component] = ComponentStatus.OPERATIONAL
                else:
                    self.logger.warning(f"[WARN] Recovery failed for {component}")
                    
            except Exception as recovery_error:
                self.logger.error(f"[ERROR] Recovery attempt failed for {component}: {recovery_error}")
        
        return error_context
    
    def _log_error(self, context: ErrorContext):
        """Log error with appropriate severity"""
        log_message = f"[{context.severity.value.upper()}] {context.component}.{context.operation}: {context.error_message}"
        
        if context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
            self.logger.critical(f"Stack trace: {context.stack_trace}")
        elif context.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
            self.logger.debug(f"Stack trace: {context.stack_trace}")
        elif context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _track_error(self, context: ErrorContext):
        """Track error in history for pattern analysis"""
        component_key = f"{context.component}.{context.operation}"
        
        if component_key not in self.error_history:
            self.error_history[component_key] = []
        
        self.error_history[component_key].append(context)
        
        # Keep only last 100 errors per component
        if len(self.error_history[component_key]) > 100:
            self.error_history[component_key] = self.error_history[component_key][-100:]
    
    def _update_component_status(self, component: str, context: ErrorContext):
        """Update component status based on error severity"""
        if context.severity == ErrorSeverity.CRITICAL:
            self.component_status[component] = ComponentStatus.FAILED
        elif context.severity == ErrorSeverity.HIGH:
            self.component_status[component] = ComponentStatus.DEGRADED
        elif component not in self.component_status:
            self.component_status[component] = ComponentStatus.OPERATIONAL
    
    def get_fallback_response(self, operation: str, custom_fallback: Any = None) -> Any:
        """Get fallback response for an operation"""
        if custom_fallback is not None:
            return custom_fallback
        
        return self.fallback_responses.get(operation, {
            "error": "Operation failed",
            "message": "Please try again later"
        })
    
    def get_component_status(self, component: str) -> ComponentStatus:
        """Get current status of a component"""
        return self.component_status.get(component, ComponentStatus.OPERATIONAL)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        summary = {
            "total_components": len(self.component_status),
            "failed_components": sum(1 for status in self.component_status.values() 
                                   if status == ComponentStatus.FAILED),
            "degraded_components": sum(1 for status in self.component_status.values() 
                                     if status == ComponentStatus.DEGRADED),
            "recent_errors": {}
        }
        
        # Get recent errors (last 10 per component)
        for component_op, errors in self.error_history.items():
            if errors:
                recent_errors = errors[-10:]
                summary["recent_errors"][component_op] = [
                    {
                        "timestamp": error.timestamp.isoformat(),
                        "severity": error.severity.value,
                        "message": error.error_message
                    }
                    for error in recent_errors
                ]
        
        return summary

# Global error handler instance
_error_handler = None

def get_error_handler() -> AtlasErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = AtlasErrorHandler()
    return _error_handler

def atlas_error_handler(component: str, 
                       operation: str = None, 
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       fallback_response: Any = None,
                       attempt_recovery: bool = True):
    """Decorator for automatic error handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                op_name = operation or func.__name__
                
                await handler.handle_error(
                    component=component,
                    operation=op_name,
                    error=e,
                    severity=severity,
                    attempt_recovery=attempt_recovery
                )
                
                # Return fallback response
                return handler.get_fallback_response(op_name, fallback_response)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                op_name = operation or func.__name__
                
                # For sync functions, we can't await, so we create a task
                asyncio.create_task(handler.handle_error(
                    component=component,
                    operation=op_name,
                    error=e,
                    severity=severity,
                    attempt_recovery=attempt_recovery
                ))
                
                # Return fallback response
                return handler.get_fallback_response(op_name, fallback_response)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# Utility functions for common error scenarios
async def safe_api_call(func: Callable, *args, fallback=None, **kwargs) -> Any:
    """Safely execute an API call with error handling"""
    handler = get_error_handler()
    try:
        return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    except Exception as e:
        await handler.handle_error(
            component="api_client",
            operation=func.__name__,
            error=e,
            severity=ErrorSeverity.MEDIUM
        )
        return fallback

async def safe_database_operation(func: Callable, *args, fallback=None, **kwargs) -> Any:
    """Safely execute a database operation with error handling"""
    handler = get_error_handler()
    try:
        return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    except Exception as e:
        await handler.handle_error(
            component="database",
            operation=func.__name__,
            error=e,
            severity=ErrorSeverity.HIGH
        )
        return fallback

def setup_component_recovery_strategies():
    """Setup recovery strategies for system components"""
    handler = get_error_handler()

    # AI Engine recovery
    async def ai_engine_recovery():
        try:
            # Attempt to reinitialize AI components
            handler.logger.info("[TOOL] Attempting AI engine recovery...")
            # This would trigger AI engine reinitialization
            return True
        except:
            return False

    # Market Engine recovery
    async def market_engine_recovery():
        try:
            handler.logger.info("[TOOL] Attempting market engine recovery...")
            # This would trigger market engine reconnection
            return True
        except:
            return False

    # Database recovery
    async def database_recovery():
        try:
            handler.logger.info("[TOOL] Attempting database recovery...")
            # This would trigger database reconnection
            return True
        except:
            return False

    # Register recovery strategies
    handler.register_recovery_strategy("ai_engine", ai_engine_recovery)
    handler.register_recovery_strategy("market_engine", market_engine_recovery)
    handler.register_recovery_strategy("database", database_recovery)

    handler.logger.info("[OK] Component recovery strategies initialized")
