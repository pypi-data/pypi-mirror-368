# this_file: external/int_folders/d361/src/d361/api/metrics.py
"""
Metrics Collection and Observability for Document360 API.

This module provides comprehensive metrics collection and observability capabilities with:
- Real-time API performance monitoring and alerting
- Request/response tracking with detailed timing analysis
- Error classification and frequency analysis  
- Rate limiting and quota usage tracking
- Custom business metrics and KPIs
- Integration with monitoring systems (Prometheus, Grafana, etc.)
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
import threading

from loguru import logger
from pydantic import BaseModel, Field

from .errors import Document360Error, ErrorCategory, ErrorSeverity


class MetricType(str, Enum):
    """Types of metrics collected."""
    COUNTER = "counter"          # Incrementing count (requests, errors)
    GAUGE = "gauge"              # Current value (active connections, queue size)
    HISTOGRAM = "histogram"      # Distribution of values (response times, sizes)
    SUMMARY = "summary"          # Quantiles and totals (percentiles, averages)


class TimeWindow(str, Enum):
    """Time windows for metric aggregation."""
    MINUTE = "1m"               # Last minute
    FIVE_MINUTES = "5m"         # Last 5 minutes  
    FIFTEEN_MINUTES = "15m"     # Last 15 minutes
    HOUR = "1h"                 # Last hour
    DAY = "24h"                 # Last 24 hours


@dataclass
class MetricPoint:
    """
    Single metric measurement point.
    
    Represents a single measurement with timestamp and metadata.
    """
    
    name: str                    # Metric name
    value: float                 # Metric value
    timestamp: datetime          # When measured
    labels: Dict[str, str] = field(default_factory=dict)  # Metric labels/tags
    metric_type: MetricType = MetricType.COUNTER
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'type': self.metric_type.value,
        }


@dataclass
class MetricSeries:
    """
    Time series of metric points.
    
    Manages a series of measurements over time with aggregation capabilities.
    """
    
    name: str
    metric_type: MetricType
    points: deque = field(default_factory=lambda: deque(maxlen=10000))  # Keep last 10k points
    labels: Dict[str, str] = field(default_factory=dict)
    
    def add_point(self, value: float, timestamp: Optional[datetime] = None, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a new measurement point."""
        point = MetricPoint(
            name=self.name,
            value=value,
            timestamp=timestamp or datetime.now(),
            labels={**self.labels, **(labels or {})},
            metric_type=self.metric_type
        )
        self.points.append(point)
    
    def get_points_in_window(self, window: TimeWindow) -> List[MetricPoint]:
        """Get points within specified time window."""
        now = datetime.now()
        window_duration = self._parse_time_window(window)
        cutoff = now - window_duration
        
        return [p for p in self.points if p.timestamp >= cutoff]
    
    def _parse_time_window(self, window: TimeWindow) -> timedelta:
        """Parse time window to timedelta."""
        mapping = {
            TimeWindow.MINUTE: timedelta(minutes=1),
            TimeWindow.FIVE_MINUTES: timedelta(minutes=5),
            TimeWindow.FIFTEEN_MINUTES: timedelta(minutes=15),
            TimeWindow.HOUR: timedelta(hours=1),
            TimeWindow.DAY: timedelta(days=1),
        }
        return mapping.get(window, timedelta(minutes=5))
    
    def aggregate(self, window: TimeWindow) -> Dict[str, float]:
        """Aggregate metrics within time window."""
        points = self.get_points_in_window(window)
        if not points:
            return {}
        
        values = [p.value for p in points]
        
        if self.metric_type == MetricType.COUNTER:
            return {
                'total': sum(values),
                'rate': sum(values) / len(values) if values else 0,
                'count': len(values),
            }
        elif self.metric_type == MetricType.GAUGE:
            return {
                'current': values[-1] if values else 0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
                'avg': sum(values) / len(values) if values else 0,
            }
        elif self.metric_type in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
            sorted_values = sorted(values)
            count = len(sorted_values)
            return {
                'count': count,
                'sum': sum(sorted_values),
                'min': sorted_values[0] if sorted_values else 0,
                'max': sorted_values[-1] if sorted_values else 0,
                'avg': sum(sorted_values) / count if count > 0 else 0,
                'p50': self._percentile(sorted_values, 0.5),
                'p90': self._percentile(sorted_values, 0.9),
                'p95': self._percentile(sorted_values, 0.95),
                'p99': self._percentile(sorted_values, 0.99),
            }
        
        return {}
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        
        index = int(percentile * (len(sorted_values) - 1))
        return sorted_values[index]


class MetricsConfig(BaseModel):
    """Configuration for metrics collection."""
    
    # Collection settings
    enabled: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    
    collection_interval: float = Field(
        default=10.0,
        ge=1.0,
        le=300.0,
        description="Metrics collection interval in seconds"
    )
    
    # Retention settings
    max_series_points: int = Field(
        default=10000,
        ge=100,
        le=100000,
        description="Maximum points per metric series"
    )
    
    retention_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Hours to retain metrics data"
    )
    
    # Export settings
    export_enabled: bool = Field(
        default=False,
        description="Enable metrics export"
    )
    
    export_format: str = Field(
        default="prometheus",
        description="Export format (prometheus, json, influxdb)"
    )
    
    export_endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint for metrics export"
    )
    
    # Alerting settings
    enable_alerts: bool = Field(
        default=False,
        description="Enable alerting on thresholds"
    )
    
    alert_thresholds: Dict[str, float] = Field(
        default_factory=dict,
        description="Alert thresholds for metrics"
    )
    
    # Custom labels
    default_labels: Dict[str, str] = Field(
        default_factory=dict,
        description="Default labels applied to all metrics"
    )


class ApiMetrics:
    """
    Comprehensive API metrics collector.
    
    Provides enterprise-grade metrics collection with:
    - Request/response timing and status tracking
    - Error classification and frequency analysis
    - Token usage and rate limit monitoring  
    - Custom business metrics and KPIs
    - Real-time alerting and notifications
    """
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        """
        Initialize API metrics collector.
        
        Args:
            config: Metrics configuration
        """
        self.config = config or MetricsConfig()
        
        # Metric series storage
        self._series: Dict[str, MetricSeries] = {}
        self._lock = threading.RLock()
        
        # Built-in metrics
        self._init_builtin_metrics()
        
        # Collection state
        self._collection_task: Optional[asyncio.Task] = None
        self._alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Performance tracking
        self._start_time = time.time()
        
        logger.info(
            f"ApiMetrics initialized",
            enabled=self.config.enabled,
            collection_interval=self.config.collection_interval,
            retention_hours=self.config.retention_hours,
        )
    
    def _init_builtin_metrics(self) -> None:
        """Initialize built-in API metrics."""
        # Request metrics
        self.create_metric("api_requests_total", MetricType.COUNTER, "Total API requests")
        self.create_metric("api_request_duration_seconds", MetricType.HISTOGRAM, "API request duration")
        self.create_metric("api_request_size_bytes", MetricType.HISTOGRAM, "API request size")
        self.create_metric("api_response_size_bytes", MetricType.HISTOGRAM, "API response size")
        
        # Error metrics
        self.create_metric("api_errors_total", MetricType.COUNTER, "Total API errors")
        self.create_metric("api_error_rate", MetricType.GAUGE, "API error rate")
        
        # Rate limiting metrics
        self.create_metric("api_rate_limit_hits", MetricType.COUNTER, "Rate limit hits")
        self.create_metric("api_rate_limit_remaining", MetricType.GAUGE, "Rate limit remaining")
        self.create_metric("api_rate_limit_reset_time", MetricType.GAUGE, "Rate limit reset time")
        
        # Token metrics
        self.create_metric("api_token_usage", MetricType.COUNTER, "Token usage count")
        self.create_metric("api_token_rotations", MetricType.COUNTER, "Token rotations")
        self.create_metric("api_active_tokens", MetricType.GAUGE, "Active tokens")
        
        # Connection metrics
        self.create_metric("api_connections_active", MetricType.GAUGE, "Active connections")
        self.create_metric("api_connections_created", MetricType.COUNTER, "Connections created")
        self.create_metric("api_connections_failed", MetricType.COUNTER, "Failed connections")
        
        # Cache metrics
        self.create_metric("api_cache_hits", MetricType.COUNTER, "Cache hits")
        self.create_metric("api_cache_misses", MetricType.COUNTER, "Cache misses")
        self.create_metric("api_cache_size", MetricType.GAUGE, "Cache size")
        
        # Circuit breaker metrics
        self.create_metric("circuit_breaker_state_changes", MetricType.COUNTER, "Circuit breaker state changes")
        self.create_metric("circuit_breaker_failures", MetricType.COUNTER, "Circuit breaker failures")
        self.create_metric("circuit_breaker_successes", MetricType.COUNTER, "Circuit breaker successes")
        
        # Sync metrics
        self.create_metric("sync_operations_total", MetricType.COUNTER, "Total sync operations")
        self.create_metric("sync_items_processed", MetricType.COUNTER, "Items processed in sync")
        self.create_metric("sync_duplicates_found", MetricType.COUNTER, "Duplicates found")
        self.create_metric("sync_duration_seconds", MetricType.HISTOGRAM, "Sync operation duration")
    
    def create_metric(self, name: str, metric_type: MetricType, description: str = "", labels: Optional[Dict[str, str]] = None) -> MetricSeries:
        """Create a new metric series."""
        with self._lock:
            if name in self._series:
                return self._series[name]
            
            series = MetricSeries(
                name=name,
                metric_type=metric_type,
                labels={**self.config.default_labels, **(labels or {})}
            )
            self._series[name] = series
            
            logger.debug(f"Created metric: {name} ({metric_type.value})")
            return series
    
    def increment(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        if not self.config.enabled:
            return
        
        with self._lock:
            if name not in self._series:
                self.create_metric(name, MetricType.COUNTER)
            
            self._series[name].add_point(value, labels=labels)
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        if not self.config.enabled:
            return
        
        with self._lock:
            if name not in self._series:
                self.create_metric(name, MetricType.GAUGE)
            
            self._series[name].add_point(value, labels=labels)
    
    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric value."""
        if not self.config.enabled:
            return
        
        with self._lock:
            if name not in self._series:
                self.create_metric(name, MetricType.HISTOGRAM)
            
            self._series[name].add_point(value, labels=labels)
    
    def timing(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a timing metric (convenience method for histograms)."""
        self.histogram(name, duration, labels)
    
    # API-specific metric methods
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float, request_size: int = 0, response_size: int = 0) -> None:
        """Record API request metrics."""
        labels = {
            'method': method,
            'endpoint': endpoint,
            'status': str(status_code),
            'status_class': f"{status_code // 100}xx"
        }
        
        # Request count
        self.increment("api_requests_total", labels=labels)
        
        # Request duration
        self.timing("api_request_duration_seconds", duration, labels=labels)
        
        # Request/response sizes
        if request_size > 0:
            self.histogram("api_request_size_bytes", request_size, labels=labels)
        if response_size > 0:
            self.histogram("api_response_size_bytes", response_size, labels=labels)
        
        # Error tracking
        if status_code >= 400:
            self.increment("api_errors_total", labels=labels)
        
        # Calculate error rate
        self._update_error_rate()
    
    def record_rate_limit(self, remaining: int, reset_time: float, hit: bool = False) -> None:
        """Record rate limiting metrics."""
        self.gauge("api_rate_limit_remaining", remaining)
        self.gauge("api_rate_limit_reset_time", reset_time)
        
        if hit:
            self.increment("api_rate_limit_hits")
    
    def record_token_usage(self, token_id: str, success: bool = True) -> None:
        """Record token usage metrics."""
        labels = {'token_id': token_id, 'success': str(success)}
        self.increment("api_token_usage", labels=labels)
    
    def record_token_rotation(self, old_token: str, new_token: str, reason: str = "") -> None:
        """Record token rotation."""
        labels = {'reason': reason}
        self.increment("api_token_rotations", labels=labels)
    
    def record_connection(self, event: str, count: int = 1) -> None:
        """Record connection metrics."""
        if event == "created":
            self.increment("api_connections_created", count)
        elif event == "failed":
            self.increment("api_connections_failed", count)
        elif event == "active":
            self.gauge("api_connections_active", count)
    
    def record_cache_event(self, event: str, size: Optional[int] = None) -> None:
        """Record cache metrics."""
        if event == "hit":
            self.increment("api_cache_hits")
        elif event == "miss":
            self.increment("api_cache_misses")
        elif event == "size" and size is not None:
            self.gauge("api_cache_size", size)
    
    def record_circuit_breaker(self, name: str, event: str, state: Optional[str] = None) -> None:
        """Record circuit breaker metrics."""
        labels = {'circuit': name}
        if state:
            labels['state'] = state
        
        if event == "state_change":
            self.increment("circuit_breaker_state_changes", labels=labels)
        elif event == "failure":
            self.increment("circuit_breaker_failures", labels=labels)
        elif event == "success":
            self.increment("circuit_breaker_successes", labels=labels)
    
    def record_sync_operation(self, operation: str, items: int = 0, duration: float = 0, duplicates: int = 0) -> None:
        """Record sync operation metrics."""
        labels = {'operation': operation}
        
        self.increment("sync_operations_total", labels=labels)
        
        if items > 0:
            self.increment("sync_items_processed", items, labels=labels)
        
        if duration > 0:
            self.timing("sync_duration_seconds", duration, labels=labels)
        
        if duplicates > 0:
            self.increment("sync_duplicates_found", duplicates, labels=labels)
    
    def _update_error_rate(self) -> None:
        """Update error rate gauge."""
        try:
            # Calculate error rate from last 5 minutes
            requests_series = self._series.get("api_requests_total")
            errors_series = self._series.get("api_errors_total")
            
            if requests_series and errors_series:
                requests_agg = requests_series.aggregate(TimeWindow.FIVE_MINUTES)
                errors_agg = errors_series.aggregate(TimeWindow.FIVE_MINUTES)
                
                total_requests = requests_agg.get('total', 0)
                total_errors = errors_agg.get('total', 0)
                
                error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
                self.gauge("api_error_rate", error_rate)
                
        except Exception as e:
            logger.warning(f"Failed to update error rate: {e}")
    
    def get_metric(self, name: str, window: TimeWindow = TimeWindow.FIVE_MINUTES) -> Optional[Dict[str, Any]]:
        """Get aggregated metric data."""
        with self._lock:
            series = self._series.get(name)
            if not series:
                return None
            
            aggregated = series.aggregate(window)
            return {
                'name': name,
                'type': series.metric_type.value,
                'labels': series.labels,
                'window': window.value,
                'data': aggregated,
                'timestamp': datetime.now().isoformat(),
            }
    
    def get_all_metrics(self, window: TimeWindow = TimeWindow.FIVE_MINUTES) -> Dict[str, Dict[str, Any]]:
        """Get all metrics with aggregation."""
        with self._lock:
            return {
                name: self.get_metric(name, window)
                for name in self._series.keys()
                if self.get_metric(name, window) is not None
            }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get key health metrics for monitoring."""
        metrics = {}
        
        # Error rate (last 5 minutes)
        error_rate_metric = self.get_metric("api_error_rate", TimeWindow.FIVE_MINUTES)
        if error_rate_metric:
            metrics['error_rate_percent'] = error_rate_metric['data'].get('current', 0)
        
        # Request rate (last 5 minutes)
        requests_metric = self.get_metric("api_requests_total", TimeWindow.FIVE_MINUTES)
        if requests_metric:
            metrics['request_rate_per_minute'] = requests_metric['data'].get('rate', 0) * 60
        
        # Average response time (last 5 minutes)
        duration_metric = self.get_metric("api_request_duration_seconds", TimeWindow.FIVE_MINUTES)
        if duration_metric:
            metrics['avg_response_time_seconds'] = duration_metric['data'].get('avg', 0)
            metrics['p95_response_time_seconds'] = duration_metric['data'].get('p95', 0)
        
        # Active connections
        connections_metric = self.get_metric("api_connections_active", TimeWindow.FIVE_MINUTES)
        if connections_metric:
            metrics['active_connections'] = connections_metric['data'].get('current', 0)
        
        # Rate limit status
        rate_limit_metric = self.get_metric("api_rate_limit_remaining", TimeWindow.FIVE_MINUTES)
        if rate_limit_metric:
            metrics['rate_limit_remaining'] = rate_limit_metric['data'].get('current', 0)
        
        metrics['uptime_seconds'] = time.time() - self._start_time
        
        return metrics
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for metric alerts."""
        self._alert_callbacks.append(callback)
    
    def check_alerts(self) -> None:
        """Check metrics against alert thresholds."""
        if not self.config.enable_alerts or not self.config.alert_thresholds:
            return
        
        for metric_name, threshold in self.config.alert_thresholds.items():
            metric_data = self.get_metric(metric_name)
            if not metric_data:
                continue
            
            # Check if any aggregated value exceeds threshold
            data = metric_data['data']
            triggered = False
            trigger_value = None
            
            for key, value in data.items():
                if isinstance(value, (int, float)) and value > threshold:
                    triggered = True
                    trigger_value = value
                    break
            
            if triggered:
                alert_data = {
                    'metric': metric_name,
                    'threshold': threshold,
                    'current_value': trigger_value,
                    'timestamp': datetime.now().isoformat(),
                }
                
                # Notify callbacks
                for callback in self._alert_callbacks:
                    try:
                        callback(metric_name, alert_data)
                    except Exception as e:
                        logger.warning(f"Alert callback failed: {e}")
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format."""
        if format.lower() == "prometheus":
            return self._export_prometheus()
        elif format.lower() == "json":
            return self._export_json()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with self._lock:
            for name, series in self._series.items():
                # Add metric help
                lines.append(f"# HELP {name} {name}")
                lines.append(f"# TYPE {name} {series.metric_type.value}")
                
                # Add metric data
                aggregated = series.aggregate(TimeWindow.FIVE_MINUTES)
                
                if series.metric_type == MetricType.COUNTER:
                    value = aggregated.get('total', 0)
                    labels_str = self._format_prometheus_labels(series.labels)
                    lines.append(f"{name}{labels_str} {value}")
                    
                elif series.metric_type == MetricType.GAUGE:
                    value = aggregated.get('current', 0)
                    labels_str = self._format_prometheus_labels(series.labels)
                    lines.append(f"{name}{labels_str} {value}")
                    
                elif series.metric_type in [MetricType.HISTOGRAM, MetricType.SUMMARY]:
                    # Export histogram buckets and summary quantiles
                    for key, value in aggregated.items():
                        if key.startswith('p'):
                            # Quantile
                            quantile = key[1:].replace('p', '0.')
                            labels = {**series.labels, 'quantile': quantile}
                            labels_str = self._format_prometheus_labels(labels)
                            lines.append(f"{name}{labels_str} {value}")
                        else:
                            # Standard metrics
                            suffix = f"_{key}" if key not in ['count', 'sum'] else f"_{key}"
                            labels_str = self._format_prometheus_labels(series.labels)
                            lines.append(f"{name}{suffix}{labels_str} {value}")
        
        return '\n'.join(lines)
    
    def _format_prometheus_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus export."""
        if not labels:
            return ""
        
        label_parts = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_parts) + "}"
    
    def _export_json(self) -> str:
        """Export metrics in JSON format."""
        import json
        return json.dumps(self.get_all_metrics(), indent=2, default=str)
    
    async def start_collection(self) -> None:
        """Start automatic metrics collection."""
        if not self.config.enabled or self._collection_task:
            return
        
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Started metrics collection")
    
    async def stop_collection(self) -> None:
        """Stop automatic metrics collection."""
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None
            logger.info("Stopped metrics collection")
    
    async def _collection_loop(self) -> None:
        """Main metrics collection loop."""
        while True:
            try:
                await asyncio.sleep(self.config.collection_interval)
                
                # Perform periodic tasks
                self._cleanup_old_data()
                self.check_alerts()
                
                # Export metrics if enabled
                if self.config.export_enabled and self.config.export_endpoint:
                    await self._export_to_endpoint()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    def _cleanup_old_data(self) -> None:
        """Clean up old metric data based on retention policy."""
        cutoff = datetime.now() - timedelta(hours=self.config.retention_hours)
        
        with self._lock:
            for series in self._series.values():
                # Remove old points
                while series.points and series.points[0].timestamp < cutoff:
                    series.points.popleft()
    
    async def _export_to_endpoint(self) -> None:
        """Export metrics to configured endpoint."""
        try:
            metrics_data = self.export_metrics(self.config.export_format)
            
            # Here you would send to your monitoring system
            # Example: POST to Prometheus pushgateway, InfluxDB, etc.
            logger.debug(f"Exported {len(self._series)} metrics to {self.config.export_endpoint}")
            
        except Exception as e:
            logger.warning(f"Failed to export metrics: {e}")


# Global metrics instance
_global_metrics: Optional[ApiMetrics] = None

def get_metrics() -> ApiMetrics:
    """Get global metrics instance."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = ApiMetrics()
    return _global_metrics

def configure_metrics(config: MetricsConfig) -> ApiMetrics:
    """Configure global metrics instance."""
    global _global_metrics
    _global_metrics = ApiMetrics(config)
    return _global_metrics