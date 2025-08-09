"""
PyIDVerify Health Check System

Comprehensive health monitoring system for the PyIDVerify library.
Provides endpoint health checks, system monitoring, and diagnostic information.

Author: PyIDVerify Team
License: MIT
"""

import os
import sys
import time
import psutil
import logging
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import json

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    name: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'status': self.status.value,
            'response_time_ms': self.response_time_ms,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'details': self.details,
            'error': self.error
        }


@dataclass
class SystemHealth:
    """Overall system health information."""
    overall_status: HealthStatus
    checks: List[HealthCheckResult]
    system_info: Dict[str, Any]
    uptime: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'overall_status': self.overall_status.value,
            'checks': [check.to_dict() for check in self.checks],
            'system_info': self.system_info,
            'uptime_seconds': self.uptime,
            'timestamp': self.timestamp.isoformat()
        }


class HealthChecker:
    """Individual health check implementation."""
    
    def __init__(self, name: str, check_func: Callable[[], Any], timeout: float = 5.0):
        """
        Initialize health checker.
        
        Args:
            name: Name of the health check
            check_func: Function to execute for health check
            timeout: Timeout in seconds for the check
        """
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.last_result: Optional[HealthCheckResult] = None
        self.consecutive_failures = 0
        
    async def check(self) -> HealthCheckResult:
        """Execute the health check."""
        start_time = time.time()
        timestamp = datetime.utcnow()
        
        try:
            # Run check with timeout
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = loop.run_in_executor(executor, self.check_func)
                
                try:
                    result = await asyncio.wait_for(future, timeout=self.timeout)
                    response_time = (time.time() - start_time) * 1000
                    
                    if isinstance(result, dict):
                        status = HealthStatus(result.get('status', 'healthy'))
                        message = result.get('message')
                        details = result.get('details', {})
                        error = result.get('error')
                    elif isinstance(result, bool):
                        status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                        message = "Check passed" if result else "Check failed"
                        details = {}
                        error = None
                    else:
                        status = HealthStatus.HEALTHY
                        message = str(result) if result is not None else "Check completed"
                        details = {}
                        error = None
                        
                    self.consecutive_failures = 0
                    
                    self.last_result = HealthCheckResult(
                        name=self.name,
                        status=status,
                        response_time_ms=response_time,
                        timestamp=timestamp,
                        message=message,
                        details=details,
                        error=error
                    )
                    
                except asyncio.TimeoutError:
                    response_time = (time.time() - start_time) * 1000
                    self.consecutive_failures += 1
                    
                    self.last_result = HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=response_time,
                        timestamp=timestamp,
                        message=f"Health check timeout after {self.timeout}s",
                        details={'consecutive_failures': self.consecutive_failures},
                        error="Timeout"
                    )
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.consecutive_failures += 1
            
            self.last_result = HealthCheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                timestamp=timestamp,
                message=f"Health check failed: {str(e)}",
                details={'consecutive_failures': self.consecutive_failures},
                error=str(e)
            )
            
        return self.last_result


class HealthMonitor:
    """
    Comprehensive health monitoring system for PyIDVerify.
    
    Features:
    - System resource monitoring (CPU, memory, disk)
    - Validator service health checks
    - Database connection health
    - API endpoint health
    - Custom health checks
    - Health history and trending
    - Alerting and notifications
    - Performance metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize health monitor."""
        self.config = config or {}
        self.checkers: Dict[str, HealthChecker] = {}
        self.start_time = time.time()
        self.check_interval = self.config.get('check_interval', 30)  # seconds
        self.history_size = self.config.get('history_size', 100)
        self.history: List[SystemHealth] = []
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        
        # Initialize default health checks
        self._register_default_checks()
        
        logger.info("HealthMonitor initialized")
        
    def _register_default_checks(self):
        """Register default system health checks."""
        # System resource checks
        self.register_check('cpu_usage', self._check_cpu_usage, timeout=2.0)
        self.register_check('memory_usage', self._check_memory_usage, timeout=2.0)
        self.register_check('disk_usage', self._check_disk_usage, timeout=3.0)
        
        # PyIDVerify specific checks
        self.register_check('validator_registry', self._check_validator_registry, timeout=5.0)
        self.register_check('security_modules', self._check_security_modules, timeout=3.0)
        self.register_check('configuration', self._check_configuration, timeout=2.0)
        
        # Optional external service checks
        if self.config.get('check_database', False):
            self.register_check('database_connection', self._check_database, timeout=10.0)
            
        if self.config.get('check_external_apis', False):
            self.register_check('external_apis', self._check_external_apis, timeout=15.0)
            
    def register_check(self, name: str, check_func: Callable[[], Any], timeout: float = 5.0):
        """
        Register a custom health check.
        
        Args:
            name: Unique name for the health check
            check_func: Function to execute for the check
            timeout: Timeout in seconds
        """
        with self.lock:
            self.checkers[name] = HealthChecker(name, check_func, timeout)
        logger.debug(f"Registered health check: {name}")
        
    def unregister_check(self, name: str):
        """Remove a health check."""
        with self.lock:
            if name in self.checkers:
                del self.checkers[name]
        logger.debug(f"Unregistered health check: {name}")
        
    async def check_health(self, checks: Optional[List[str]] = None) -> SystemHealth:
        """
        Perform comprehensive health check.
        
        Args:
            checks: Specific checks to run (None for all)
            
        Returns:
            SystemHealth object with all results
        """
        timestamp = datetime.utcnow()
        
        # Determine which checks to run
        if checks is None:
            checks_to_run = list(self.checkers.keys())
        else:
            checks_to_run = [name for name in checks if name in self.checkers]
            
        # Run all checks concurrently
        tasks = []
        with self.lock:
            for name in checks_to_run:
                if name in self.checkers:
                    tasks.append(self.checkers[name].check())
                    
        if tasks:
            check_results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            check_results = []
            
        # Process results
        health_results = []
        for result in check_results:
            if isinstance(result, HealthCheckResult):
                health_results.append(result)
            elif isinstance(result, Exception):
                # Handle exceptions from individual checks
                health_results.append(HealthCheckResult(
                    name="unknown",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=timestamp,
                    message=f"Health check exception: {str(result)}",
                    error=str(result)
                ))
                
        # Determine overall status
        overall_status = self._calculate_overall_status(health_results)
        
        # Get system information
        system_info = self._get_system_info()
        
        # Calculate uptime
        uptime = time.time() - self.start_time
        
        system_health = SystemHealth(
            overall_status=overall_status,
            checks=health_results,
            system_info=system_info,
            uptime=uptime,
            timestamp=timestamp
        )
        
        # Store in history
        with self.lock:
            self.history.append(system_health)
            if len(self.history) > self.history_size:
                self.history.pop(0)
                
        logger.debug(f"Health check completed: {overall_status.value}")
        return system_health
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of current health status."""
        if not self.history:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': 'No health data available',
                'uptime': time.time() - self.start_time
            }
            
        latest = self.history[-1]
        
        # Calculate failure rates
        failed_checks = [check for check in latest.checks if check.status != HealthStatus.HEALTHY]
        
        summary = {
            'overall_status': latest.overall_status.value,
            'total_checks': len(latest.checks),
            'failed_checks': len(failed_checks),
            'uptime_seconds': latest.uptime,
            'last_check': latest.timestamp.isoformat(),
            'system_info': {
                'cpu_usage': latest.system_info.get('cpu_usage_percent'),
                'memory_usage': latest.system_info.get('memory_usage_percent'),
                'disk_usage': latest.system_info.get('disk_usage_percent'),
            }
        }
        
        if failed_checks:
            summary['failed_check_names'] = [check.name for check in failed_checks]
            
        return summary
        
    def get_check_history(self, check_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get history for a specific check."""
        history = []
        
        with self.lock:
            for health in self.history[-limit:]:
                for check in health.checks:
                    if check.name == check_name:
                        history.append(check.to_dict())
                        break
                        
        return history
        
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
        
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
        
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.running:
            try:
                # Run health check in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                health = loop.run_until_complete(self.check_health())
                
                # Check for alerts
                self._process_alerts(health)
                
                loop.close()
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                
            # Wait for next check
            time.sleep(self.check_interval)
            
    def _process_alerts(self, health: SystemHealth):
        """Process health check results for alerts."""
        # Simple alerting - can be extended for notifications
        if health.overall_status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            failed_checks = [check.name for check in health.checks 
                           if check.status != HealthStatus.HEALTHY]
            logger.warning(f"Health alert: {health.overall_status.value} - Failed checks: {failed_checks}")
            
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall system status from individual check results."""
        if not results:
            return HealthStatus.UNKNOWN
            
        statuses = [result.status for result in results]
        
        # If any critical, overall is critical
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
            
        # Count different status levels
        unhealthy_count = statuses.count(HealthStatus.UNHEALTHY)
        degraded_count = statuses.count(HealthStatus.DEGRADED)
        total_count = len(statuses)
        
        # Determine overall status based on failure ratios
        unhealthy_ratio = unhealthy_count / total_count
        degraded_ratio = degraded_count / total_count
        
        if unhealthy_ratio > 0.5:  # More than half unhealthy
            return HealthStatus.UNHEALTHY
        elif unhealthy_ratio > 0.25 or degraded_ratio > 0.5:  # Significant degradation
            return HealthStatus.DEGRADED
        elif unhealthy_count > 0 or degraded_count > 0:  # Some issues
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
            
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Python information
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            return {
                'cpu_usage_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_usage_percent': memory.percent,
                'memory_total_gb': memory.total / (1024**3),
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage_percent': (disk.used / disk.total) * 100,
                'disk_total_gb': disk.total / (1024**3),
                'disk_free_gb': disk.free / (1024**3),
                'python_version': python_version,
                'platform': sys.platform,
                'process_id': os.getpid(),
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {'error': str(e)}
            
    # Default health check implementations
    
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage levels."""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > 90:
            status = HealthStatus.CRITICAL
            message = f"Critical CPU usage: {cpu_percent:.1f}%"
        elif cpu_percent > 75:
            status = HealthStatus.UNHEALTHY
            message = f"High CPU usage: {cpu_percent:.1f}%"
        elif cpu_percent > 50:
            status = HealthStatus.DEGRADED
            message = f"Elevated CPU usage: {cpu_percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Normal CPU usage: {cpu_percent:.1f}%"
            
        return {
            'status': status.value,
            'message': message,
            'details': {
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count()
            }
        }
        
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage levels."""
        memory = psutil.virtual_memory()
        
        if memory.percent > 95:
            status = HealthStatus.CRITICAL
            message = f"Critical memory usage: {memory.percent:.1f}%"
        elif memory.percent > 85:
            status = HealthStatus.UNHEALTHY  
            message = f"High memory usage: {memory.percent:.1f}%"
        elif memory.percent > 70:
            status = HealthStatus.DEGRADED
            message = f"Elevated memory usage: {memory.percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Normal memory usage: {memory.percent:.1f}%"
            
        return {
            'status': status.value,
            'message': message,
            'details': {
                'memory_percent': memory.percent,
                'memory_total_gb': memory.total / (1024**3),
                'memory_available_gb': memory.available / (1024**3)
            }
        }
        
    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage levels."""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent > 85:
                status = HealthStatus.UNHEALTHY
                message = f"High disk usage: {disk_percent:.1f}%"
            elif disk_percent > 75:
                status = HealthStatus.DEGRADED
                message = f"Elevated disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Normal disk usage: {disk_percent:.1f}%"
                
            return {
                'status': status.value,
                'message': message,
                'details': {
                    'disk_percent': disk_percent,
                    'disk_total_gb': disk.total / (1024**3),
                    'disk_free_gb': disk.free / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f"Disk check failed: {str(e)}",
                'error': str(e)
            }
            
    def _check_validator_registry(self) -> Dict[str, Any]:
        """Check PyIDVerify validator registry health."""
        try:
            # Try to import and check validator registry
            from ..core.validator_factory import ValidatorFactory
            
            factory = ValidatorFactory()
            validators = factory.list_validators()
            
            if len(validators) == 0:
                return {
                    'status': HealthStatus.CRITICAL.value,
                    'message': 'No validators registered',
                    'details': {'validator_count': 0}
                }
            elif len(validators) < 5:  # Expected minimum number
                return {
                    'status': HealthStatus.DEGRADED.value,
                    'message': f'Limited validators available: {len(validators)}',
                    'details': {'validator_count': len(validators), 'validators': validators}
                }
            else:
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'message': f'Validator registry healthy: {len(validators)} validators',
                    'details': {'validator_count': len(validators), 'validators': validators}
                }
                
        except ImportError:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': 'Validator factory not available',
                'error': 'Import error'
            }
        except Exception as e:
            return {
                'status': HealthStatus.UNHEALTHY.value,
                'message': f'Validator registry check failed: {str(e)}',
                'error': str(e)
            }
            
    def _check_security_modules(self) -> Dict[str, Any]:
        """Check security module availability."""
        modules_to_check = [
            'pyidverify.security.memory',
            'pyidverify.security.audit_logger',
            'pyidverify.security.rate_limiter',
            'pyidverify.security.tokenization'
        ]
        
        available_modules = []
        failed_modules = []
        
        for module_name in modules_to_check:
            try:
                __import__(module_name)
                available_modules.append(module_name)
            except ImportError as e:
                failed_modules.append({'module': module_name, 'error': str(e)})
                
        if len(failed_modules) == 0:
            return {
                'status': HealthStatus.HEALTHY.value,
                'message': 'All security modules available',
                'details': {
                    'available_modules': available_modules,
                    'total_modules': len(modules_to_check)
                }
            }
        elif len(failed_modules) < len(modules_to_check) / 2:
            return {
                'status': HealthStatus.DEGRADED.value,
                'message': f'Some security modules unavailable: {len(failed_modules)}',
                'details': {
                    'available_modules': available_modules,
                    'failed_modules': failed_modules,
                    'total_modules': len(modules_to_check)
                }
            }
        else:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Most security modules unavailable: {len(failed_modules)}',
                'details': {
                    'available_modules': available_modules,
                    'failed_modules': failed_modules,
                    'total_modules': len(modules_to_check)
                }
            }
            
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration health."""
        try:
            # Check for required configuration
            config_checks = {
                'logging_configured': logger.level != logging.NOTSET,
                'config_provided': self.config is not None,
                'required_modules': True  # Placeholder for module checks
            }
            
            failed_checks = [name for name, passed in config_checks.items() if not passed]
            
            if not failed_checks:
                return {
                    'status': HealthStatus.HEALTHY.value,
                    'message': 'Configuration is healthy',
                    'details': config_checks
                }
            elif len(failed_checks) == 1:
                return {
                    'status': HealthStatus.DEGRADED.value,
                    'message': f'Configuration issue: {failed_checks[0]}',
                    'details': config_checks
                }
            else:
                return {
                    'status': HealthStatus.UNHEALTHY.value,
                    'message': f'Multiple configuration issues: {failed_checks}',
                    'details': config_checks
                }
                
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Configuration check failed: {str(e)}',
                'error': str(e)
            }
            
    def _check_database(self) -> Dict[str, Any]:
        """Check database connection (if configured)."""
        # Placeholder for database health check
        return {
            'status': HealthStatus.HEALTHY.value,
            'message': 'Database check not implemented',
            'details': {'note': 'Placeholder implementation'}
        }
        
    def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity (if configured)."""
        # Placeholder for external API health checks
        return {
            'status': HealthStatus.HEALTHY.value,
            'message': 'External API check not implemented',
            'details': {'note': 'Placeholder implementation'}
        }


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor(config: Optional[Dict[str, Any]] = None) -> HealthMonitor:
    """Get global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor(config)
    return _health_monitor


def initialize_health_monitoring(config: Optional[Dict[str, Any]] = None, 
                                start_monitoring: bool = True) -> HealthMonitor:
    """Initialize and optionally start health monitoring."""
    monitor = get_health_monitor(config)
    
    if start_monitoring:
        monitor.start_monitoring()
        
    return monitor


async def quick_health_check() -> Dict[str, Any]:
    """Perform a quick health check and return summary."""
    monitor = get_health_monitor()
    health = await monitor.check_health(['cpu_usage', 'memory_usage'])
    return health.to_dict()
