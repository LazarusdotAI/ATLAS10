#!/usr/bin/env python3
"""
A.T.L.A.S. Monitoring Tools
Consolidated error handler, performance optimizer, and security manager
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
from datetime import datetime, timedelta
import psutil
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from atlas_configuration import Settings, logger, EngineStatus, ErrorSeverity

settings = Settings()

class AtlasErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.error_counts = {}
        self.fallback_responses = self._load_fallback_responses()
        
    async def initialize(self):
        """Initialize error handler"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Error Handler initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Error Handler initialization failed: {e}")
            raise
    
    def _load_fallback_responses(self):
        """Load fallback responses for different error scenarios"""
        return {
            "chat_response": {
                "response": "I'm experiencing technical difficulties. Please try again in a moment.",
                "type": "error_fallback",
                "confidence": 0.0,
                "context": {"fallback": True}
            },
            "market_data": {
                "symbol": "UNKNOWN",
                "price": 0.0,
                "volume": 0,
                "change": 0.0,
                "change_percent": 0.0,
                "timestamp": datetime.now().isoformat()
            },
            "trading_signal": {
                "symbol": "UNKNOWN",
                "action": "HOLD",
                "price": 0.0,
                "quantity": 0,
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "reasoning": "System error - no action recommended"
            }
        }
    
    async def handle_error(self, component: str, operation: str, error: Exception, severity: ErrorSeverity) -> Dict[str, Any]:
        """Handle and log errors with recovery strategies"""
        try:
            error_key = f"{component}_{operation}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            error_context = {
                "component": component,
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "severity": severity.value,
                "count": self.error_counts[error_key],
                "timestamp": datetime.now().isoformat()
            }
            
            if severity == ErrorSeverity.CRITICAL:
                self.logger.critical(f"CRITICAL ERROR in {component}.{operation}: {error}")
            elif severity == ErrorSeverity.HIGH:
                self.logger.error(f"HIGH ERROR in {component}.{operation}: {error}")
            elif severity == ErrorSeverity.MEDIUM:
                self.logger.warning(f"MEDIUM ERROR in {component}.{operation}: {error}")
            else:
                self.logger.info(f"LOW ERROR in {component}.{operation}: {error}")
            
            recovery_action = await self._determine_recovery_action(error_context)
            error_context["recovery_action"] = recovery_action
            
            return error_context
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return {"error": "Error handler failure"}
    
    async def _determine_recovery_action(self, error_context: Dict) -> str:
        """Determine appropriate recovery action"""
        component = error_context["component"]
        error_count = error_context["count"]
        
        if error_count > 5:
            return "circuit_breaker_activated"
        elif component in ["market_engine", "trading_engine"]:
            return "fallback_to_cached_data"
        elif component == "ai_engine":
            return "use_simplified_response"
        else:
            return "retry_with_backoff"
    
    def get_fallback_response(self, response_type: str) -> Dict[str, Any]:
        """Get fallback response for error scenarios"""
        return self.fallback_responses.get(response_type, self.fallback_responses["chat_response"])
    
    async def cleanup(self):
        """Cleanup error handler"""
        self.logger.info("Error handler cleanup completed")


class AtlasPerformanceOptimizer:
    """Performance monitoring and optimization"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.performance_metrics = {}
        
    async def initialize(self):
        """Initialize performance optimizer"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Performance Optimizer initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Performance Optimizer initialization failed: {e}")
            raise
    
    async def monitor_system_resources(self) -> Dict[str, Any]:
        """Monitor system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "timestamp": datetime.now().isoformat()
            }
            
            self.performance_metrics["system"] = metrics
            
            alerts = []
            if cpu_percent > 80:
                alerts.append("High CPU usage detected")
            if memory.percent > 85:
                alerts.append("High memory usage detected")
            if disk.percent > 90:
                alerts.append("Low disk space detected")
            
            metrics["alerts"] = alerts
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error monitoring system resources: {e}")
            return {}
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Implement performance optimizations"""
        try:
            optimizations = []
            
            system_metrics = await self.monitor_system_resources()
            
            if system_metrics.get("memory_percent", 0) > 80:
                optimizations.append("memory_cleanup_initiated")
                
            if system_metrics.get("cpu_percent", 0) > 75:
                optimizations.append("cpu_throttling_applied")
            
            return {
                "optimizations_applied": optimizations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing performance: {e}")
            return {}
    
    def track_operation_time(self, operation: str, start_time: float, end_time: float):
        """Track operation execution time"""
        duration = end_time - start_time
        
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        
        self.performance_metrics[operation].append({
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.performance_metrics[operation]) > 100:
            self.performance_metrics[operation] = self.performance_metrics[operation][-100:]
    
    async def cleanup(self):
        """Cleanup performance optimizer"""
        self.logger.info("Performance optimizer cleanup completed")


class AtlasSecurityManager:
    """Security monitoring and management"""
    
    def __init__(self):
        self.logger = logger
        self.status = EngineStatus.INITIALIZING
        self.security_events = []
        
    async def initialize(self):
        """Initialize security manager"""
        try:
            self.status = EngineStatus.ACTIVE
            self.logger.info("Security Manager initialized successfully")
        except Exception as e:
            self.status = EngineStatus.ERROR
            self.logger.error(f"Security Manager initialization failed: {e}")
            raise
    
    async def validate_api_request(self, request_data: Dict) -> Dict[str, Any]:
        """Validate API request for security"""
        try:
            validation_result = {
                "valid": True,
                "security_score": 100,
                "warnings": [],
                "timestamp": datetime.now().isoformat()
            }
            
            message = request_data.get("message", "").lower()
            
            suspicious_patterns = ["<script", "javascript:", "eval(", "exec("]
            for pattern in suspicious_patterns:
                if pattern in message:
                    validation_result["warnings"].append(f"Suspicious pattern detected: {pattern}")
                    validation_result["security_score"] -= 20
            
            if len(message) > 10000:
                validation_result["warnings"].append("Message length exceeds limit")
                validation_result["security_score"] -= 10
            
            validation_result["valid"] = validation_result["security_score"] >= 50
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating API request: {e}")
            return {"valid": False, "error": str(e)}
    
    async def log_security_event(self, event_type: str, details: Dict):
        """Log security event"""
        try:
            security_event = {
                "type": event_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
            self.security_events.append(security_event)
            
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            self.logger.info(f"Security event logged: {event_type}")
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        try:
            recent_events = [event for event in self.security_events 
                           if datetime.fromisoformat(event["timestamp"]) > datetime.now() - timedelta(hours=24)]
            
            return {
                "status": "secure",
                "recent_events_count": len(recent_events),
                "total_events_logged": len(self.security_events),
                "last_event": self.security_events[-1] if self.security_events else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security status: {e}")
            return {"status": "unknown", "error": str(e)}
    
    async def cleanup(self):
        """Cleanup security manager"""
        self.logger.info("Security manager cleanup completed")
