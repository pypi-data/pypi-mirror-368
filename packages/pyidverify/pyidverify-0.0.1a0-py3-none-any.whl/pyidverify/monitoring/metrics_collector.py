"""
PyIDVerify Metrics Collection System

Comprehensive metrics collection and monitoring for performance analysis,
usage tracking, and system optimization.

Author: PyIDVerify Team
License: MIT
"""

import time
import threading
import logging
from typing import Dict, Any, List, Optional, Callable, Union, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
import os

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"


class MetricUnit(Enum):
    """Units for metric values."""
    COUNT = "count"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    PERCENT = "percent"
    RATE_PER_SECOND = "rate_per_second"


@dataclass
class MetricValue:
    """A single metric measurement."""
    name: str
    value: Union[int, float]
    unit: MetricUnit
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int
    sum: float
    min: float
    max: float
    mean: float
    median: float
    p95: float
    p99: float
    unit: MetricUnit
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'count': self.count,
            'sum': self.sum,
            'min': self.min,
            'max': self.max,
            'mean': self.mean,
            'median': self.median,
            'p95': self.p95,
            'p99': self.p99,
            'unit': self.unit.value,
            'tags': self.tags
        }


class Metric:
    """Base class for metrics."""
    
    def __init__(self, name: str, unit: MetricUnit = MetricUnit.COUNT, 
                 tags: Optional[Dict[str, str]] = None):
        """
        Initialize metric.
        
        Args:
            name: Metric name
            unit: Unit of measurement
            tags: Additional tags for categorization
        """
        self.name = name
        self.unit = unit
        self.tags = tags or {}
        self.created_at = datetime.utcnow()
        self.lock = threading.RLock()
        
    def get_name(self) -> str:
        """Get metric name."""
        return self.name
        
    def get_tags(self) -> Dict[str, str]:
        """Get metric tags."""
        return self.tags.copy()
        
    def reset(self):
        """Reset metric to initial state."""
        raise NotImplementedError
        
    def get_value(self) -> Any:
        """Get current metric value."""
        raise NotImplementedError
        
    def get_summary(self) -> Dict[str, Any]:
        """Get metric summary."""
        raise NotImplementedError


class Counter(Metric):
    """Counter metric - monotonically increasing value."""
    
    def __init__(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                 tags: Optional[Dict[str, str]] = None):
        super().__init__(name, unit, tags)
        self.value = 0
        
    def increment(self, amount: Union[int, float] = 1):
        """Increment counter by amount."""
        with self.lock:
            self.value += amount
            
    def get_value(self) -> Union[int, float]:
        """Get current counter value."""
        with self.lock:
            return self.value
            
    def reset(self):
        """Reset counter to zero."""
        with self.lock:
            self.value = 0
            
    def get_summary(self) -> Dict[str, Any]:
        """Get counter summary."""
        return {
            'type': MetricType.COUNTER.value,
            'value': self.get_value(),
            'unit': self.unit.value,
            'tags': self.tags
        }


class Gauge(Metric):
    """Gauge metric - value that can go up or down."""
    
    def __init__(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                 tags: Optional[Dict[str, str]] = None):
        super().__init__(name, unit, tags)
        self.value = 0
        
    def set_value(self, value: Union[int, float]):
        """Set gauge value."""
        with self.lock:
            self.value = value
            
    def increment(self, amount: Union[int, float] = 1):
        """Increment gauge by amount."""
        with self.lock:
            self.value += amount
            
    def decrement(self, amount: Union[int, float] = 1):
        """Decrement gauge by amount."""
        with self.lock:
            self.value -= amount
            
    def get_value(self) -> Union[int, float]:
        """Get current gauge value."""
        with self.lock:
            return self.value
            
    def reset(self):
        """Reset gauge to zero."""
        with self.lock:
            self.value = 0
            
    def get_summary(self) -> Dict[str, Any]:
        """Get gauge summary."""
        return {
            'type': MetricType.GAUGE.value,
            'value': self.get_value(),
            'unit': self.unit.value,
            'tags': self.tags
        }


class Histogram(Metric):
    """Histogram metric - distribution of values."""
    
    def __init__(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                 tags: Optional[Dict[str, str]] = None, max_size: int = 10000):
        super().__init__(name, unit, tags)
        self.values = deque(maxlen=max_size)
        self.count = 0
        self.sum = 0.0
        
    def record(self, value: Union[int, float]):
        """Record a value in the histogram."""
        with self.lock:
            self.values.append(value)
            self.count += 1
            self.sum += value
            
    def get_value(self) -> List[Union[int, float]]:
        """Get all recorded values."""
        with self.lock:
            return list(self.values)
            
    def reset(self):
        """Reset histogram."""
        with self.lock:
            self.values.clear()
            self.count = 0
            self.sum = 0.0
            
    def get_summary(self) -> MetricSummary:
        """Get histogram summary with percentiles."""
        with self.lock:
            if not self.values:
                return MetricSummary(
                    name=self.name,
                    count=0,
                    sum=0.0,
                    min=0.0,
                    max=0.0,
                    mean=0.0,
                    median=0.0,
                    p95=0.0,
                    p99=0.0,
                    unit=self.unit,
                    tags=self.tags
                )
                
            sorted_values = sorted(self.values)
            count = len(sorted_values)
            
            return MetricSummary(
                name=self.name,
                count=count,
                sum=self.sum,
                min=min(sorted_values),
                max=max(sorted_values),
                mean=self.sum / count,
                median=statistics.median(sorted_values),
                p95=self._percentile(sorted_values, 95),
                p99=self._percentile(sorted_values, 99),
                unit=self.unit,
                tags=self.tags
            )
            
    def _percentile(self, sorted_values: List[Union[int, float]], percentile: int) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
            
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        if index.is_integer():
            return float(sorted_values[int(index)])
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class Timer(Metric):
    """Timer metric - measures duration of operations."""
    
    def __init__(self, name: str, unit: MetricUnit = MetricUnit.MILLISECONDS,
                 tags: Optional[Dict[str, str]] = None, max_size: int = 10000):
        super().__init__(name, unit, tags)
        self.histogram = Histogram(name, unit, tags, max_size)
        
    def record(self, duration: Union[int, float]):
        """Record a duration."""
        self.histogram.record(duration)
        
    def time_context(self):
        """Context manager for timing operations."""
        return TimerContext(self)
        
    def get_value(self) -> List[Union[int, float]]:
        """Get all recorded durations."""
        return self.histogram.get_value()
        
    def reset(self):
        """Reset timer."""
        self.histogram.reset()
        
    def get_summary(self) -> MetricSummary:
        """Get timer summary."""
        return self.histogram.get_summary()


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, timer: Timer):
        self.timer = timer
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            end_time = time.perf_counter()
            duration = (end_time - self.start_time)
            
            # Convert to appropriate unit
            if self.timer.unit == MetricUnit.SECONDS:
                duration = duration
            elif self.timer.unit == MetricUnit.MILLISECONDS:
                duration = duration * 1000
            elif self.timer.unit == MetricUnit.MICROSECONDS:
                duration = duration * 1000000
                
            self.timer.record(duration)


class MetricsCollector:
    """
    Comprehensive metrics collection system for PyIDVerify.
    
    Features:
    - Multiple metric types (counter, gauge, histogram, timer)
    - Automatic metric aggregation
    - Performance monitoring
    - Validation metrics
    - Error tracking
    - Export capabilities (JSON, CSV)
    - Real-time monitoring
    - Memory-efficient storage
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metrics collector."""
        self.config = config or {}
        self.metrics: Dict[str, Metric] = {}
        self.lock = threading.RLock()
        self.start_time = time.time()
        
        # Collection settings
        self.max_metric_age = timedelta(hours=self.config.get('max_metric_age_hours', 24))
        self.collection_interval = self.config.get('collection_interval', 60)  # seconds
        self.max_metrics = self.config.get('max_metrics', 1000)
        
        # Background collection
        self.collecting = False
        self.collection_thread: Optional[threading.Thread] = None
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        logger.info("MetricsCollector initialized")
        
    def _initialize_default_metrics(self):
        """Initialize default PyIDVerify metrics."""
        # Validation metrics
        self.register_counter('validations_total', MetricUnit.COUNT, 
                            tags={'component': 'validator'})
        self.register_counter('validations_successful', MetricUnit.COUNT,
                            tags={'component': 'validator'})
        self.register_counter('validations_failed', MetricUnit.COUNT,
                            tags={'component': 'validator'})
        self.register_timer('validation_duration', MetricUnit.MILLISECONDS,
                          tags={'component': 'validator'})
        
        # Error metrics
        self.register_counter('errors_total', MetricUnit.COUNT,
                            tags={'component': 'error'})
        self.register_counter('exceptions_total', MetricUnit.COUNT,
                            tags={'component': 'error'})
        
        # Security metrics
        self.register_counter('security_checks_total', MetricUnit.COUNT,
                            tags={'component': 'security'})
        self.register_counter('rate_limits_hit', MetricUnit.COUNT,
                            tags={'component': 'security'})
        self.register_counter('suspicious_patterns_detected', MetricUnit.COUNT,
                            tags={'component': 'security'})
        
        # Performance metrics
        self.register_gauge('active_validations', MetricUnit.COUNT,
                          tags={'component': 'performance'})
        self.register_histogram('memory_usage', MetricUnit.MEGABYTES,
                              tags={'component': 'performance'})
        self.register_histogram('cpu_usage', MetricUnit.PERCENT,
                              tags={'component': 'performance'})
        
    def register_counter(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                        tags: Optional[Dict[str, str]] = None) -> Counter:
        """Register a counter metric."""
        counter = Counter(name, unit, tags)
        with self.lock:
            self.metrics[name] = counter
        logger.debug(f"Registered counter metric: {name}")
        return counter
        
    def register_gauge(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                      tags: Optional[Dict[str, str]] = None) -> Gauge:
        """Register a gauge metric."""
        gauge = Gauge(name, unit, tags)
        with self.lock:
            self.metrics[name] = gauge
        logger.debug(f"Registered gauge metric: {name}")
        return gauge
        
    def register_histogram(self, name: str, unit: MetricUnit = MetricUnit.COUNT,
                          tags: Optional[Dict[str, str]] = None,
                          max_size: int = 10000) -> Histogram:
        """Register a histogram metric."""
        histogram = Histogram(name, unit, tags, max_size)
        with self.lock:
            self.metrics[name] = histogram
        logger.debug(f"Registered histogram metric: {name}")
        return histogram
        
    def register_timer(self, name: str, unit: MetricUnit = MetricUnit.MILLISECONDS,
                      tags: Optional[Dict[str, str]] = None,
                      max_size: int = 10000) -> Timer:
        """Register a timer metric."""
        timer = Timer(name, unit, tags, max_size)
        with self.lock:
            self.metrics[name] = timer
        logger.debug(f"Registered timer metric: {name}")
        return timer
        
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name."""
        with self.lock:
            return self.metrics.get(name)
            
    def increment_counter(self, name: str, amount: Union[int, float] = 1,
                         tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        metric = self.get_metric(name)
        if isinstance(metric, Counter):
            metric.increment(amount)
        else:
            # Create counter if it doesn't exist
            counter = self.register_counter(name, tags=tags)
            counter.increment(amount)
            
    def set_gauge(self, name: str, value: Union[int, float],
                 tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        metric = self.get_metric(name)
        if isinstance(metric, Gauge):
            metric.set_value(value)
        else:
            # Create gauge if it doesn't exist
            gauge = self.register_gauge(name, tags=tags)
            gauge.set_value(value)
            
    def record_histogram(self, name: str, value: Union[int, float],
                        tags: Optional[Dict[str, str]] = None):
        """Record a value in histogram."""
        metric = self.get_metric(name)
        if isinstance(metric, Histogram):
            metric.record(value)
        else:
            # Create histogram if it doesn't exist
            histogram = self.register_histogram(name, tags=tags)
            histogram.record(value)
            
    def record_timer(self, name: str, duration: Union[int, float],
                    tags: Optional[Dict[str, str]] = None):
        """Record a duration in timer."""
        metric = self.get_metric(name)
        if isinstance(metric, Timer):
            metric.record(duration)
        else:
            # Create timer if it doesn't exist
            timer = self.register_timer(name, tags=tags)
            timer.record(duration)
            
    def time_operation(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Get timer context for timing operations."""
        metric = self.get_metric(name)
        if not isinstance(metric, Timer):
            metric = self.register_timer(name, tags=tags)
        return metric.time_context()
        
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics."""
        with self.lock:
            return self.metrics.copy()
            
    def get_metric_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summaries of all metrics."""
        summaries = {}
        with self.lock:
            for name, metric in self.metrics.items():
                try:
                    summaries[name] = metric.get_summary()
                    if hasattr(summaries[name], 'to_dict'):
                        summaries[name] = summaries[name].to_dict()
                except Exception as e:
                    logger.error(f"Error getting summary for metric {name}: {str(e)}")
                    summaries[name] = {'error': str(e)}
        return summaries
        
    def reset_metric(self, name: str):
        """Reset a specific metric."""
        metric = self.get_metric(name)
        if metric:
            metric.reset()
            logger.debug(f"Reset metric: {name}")
            
    def reset_all_metrics(self):
        """Reset all metrics."""
        with self.lock:
            for metric in self.metrics.values():
                metric.reset()
        logger.info("Reset all metrics")
        
    def remove_metric(self, name: str):
        """Remove a metric."""
        with self.lock:
            if name in self.metrics:
                del self.metrics[name]
        logger.debug(f"Removed metric: {name}")
        
    def export_to_json(self, file_path: Optional[str] = None) -> str:
        """Export metrics to JSON format."""
        summaries = self.get_metric_summaries()
        
        export_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'total_metrics': len(summaries),
            'metrics': summaries
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        if file_path:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(json_data)
                logger.info(f"Exported metrics to: {file_path}")
            except Exception as e:
                logger.error(f"Error exporting metrics to file: {str(e)}")
                
        return json_data
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            import psutil
            
            # Update system metrics
            self.set_gauge('memory_usage', psutil.virtual_memory().percent)
            self.set_gauge('cpu_usage', psutil.cpu_percent())
            
            # Get active validation count (placeholder)
            active_validations = self.get_metric('active_validations')
            if isinstance(active_validations, Gauge):
                active_count = active_validations.get_value()
            else:
                active_count = 0
                
            return {
                'memory_usage_percent': psutil.virtual_memory().percent,
                'cpu_usage_percent': psutil.cpu_percent(),
                'active_validations': active_count,
                'total_validations': self.get_metric('validations_total').get_value() if self.get_metric('validations_total') else 0,
                'uptime_seconds': time.time() - self.start_time
            }
            
        except ImportError:
            return {
                'error': 'psutil not available for system metrics',
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            return {
                'error': f'System metrics error: {str(e)}',
                'uptime_seconds': time.time() - self.start_time
            }
            
    def start_collection(self):
        """Start background metrics collection."""
        if self.collecting:
            return
            
        self.collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")
        
    def stop_collection(self):
        """Stop background metrics collection."""
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
        
    def _collection_loop(self):
        """Background collection loop."""
        while self.collecting:
            try:
                # Update system metrics
                self.get_system_metrics()
                
                # Cleanup old metrics if needed
                self._cleanup_metrics()
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                
            # Wait for next collection
            time.sleep(self.collection_interval)
            
    def _cleanup_metrics(self):
        """Clean up old or excessive metrics."""
        with self.lock:
            # Remove excess metrics if we have too many
            if len(self.metrics) > self.max_metrics:
                # Remove oldest metrics (simple FIFO)
                metrics_to_remove = list(self.metrics.keys())[:-self.max_metrics]
                for name in metrics_to_remove:
                    del self.metrics[name]
                logger.debug(f"Cleaned up {len(metrics_to_remove)} excess metrics")
                
    # Convenience methods for common PyIDVerify operations
    
    def record_validation_success(self, validator_type: str, duration_ms: float):
        """Record a successful validation."""
        self.increment_counter('validations_total', tags={'type': validator_type})
        self.increment_counter('validations_successful', tags={'type': validator_type})
        self.record_timer('validation_duration', duration_ms, tags={'type': validator_type})
        
    def record_validation_failure(self, validator_type: str, duration_ms: float, error: str):
        """Record a failed validation."""
        self.increment_counter('validations_total', tags={'type': validator_type})
        self.increment_counter('validations_failed', tags={'type': validator_type, 'error': error})
        self.record_timer('validation_duration', duration_ms, tags={'type': validator_type})
        
    def record_security_event(self, event_type: str, details: Optional[Dict[str, str]] = None):
        """Record a security-related event."""
        tags = {'event_type': event_type}
        if details:
            tags.update(details)
        self.increment_counter('security_checks_total', tags=tags)
        
    def record_error(self, error_type: str, component: str):
        """Record an error occurrence."""
        self.increment_counter('errors_total', tags={'type': error_type, 'component': component})


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(config: Optional[Dict[str, Any]] = None) -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(config)
    return _metrics_collector


def initialize_metrics_collection(config: Optional[Dict[str, Any]] = None,
                                 start_collection: bool = True) -> MetricsCollector:
    """Initialize and optionally start metrics collection."""
    collector = get_metrics_collector(config)
    
    if start_collection:
        collector.start_collection()
        
    return collector
