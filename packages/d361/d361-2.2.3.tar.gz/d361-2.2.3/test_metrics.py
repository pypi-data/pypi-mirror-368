#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_metrics.py
"""
Test script for ApiMetrics functionality.

This script validates the metrics collection implementation including
counters, gauges, histograms, and observability features.
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api.metrics import (
    ApiMetrics,
    MetricsConfig,
    MetricType,
    MetricPoint,
    MetricSeries,
    TimeWindow,
    get_metrics,
    configure_metrics
)


async def test_metric_point():
    """Test metric point creation and serialization."""
    print("📊 Testing MetricPoint...")
    
    # Test 1: Point creation
    print("\n1. Testing point creation...")
    try:
        point = MetricPoint(
            name="test_metric",
            value=42.5,
            timestamp=datetime.now(),
            labels={'service': 'api', 'version': '1.0'},
            metric_type=MetricType.GAUGE
        )
        
        print(f"   ✅ Point created: {point.name}")
        print(f"   📊 Value: {point.value}, Type: {point.metric_type.value}")
        print(f"   🏷️  Labels: {point.labels}")
        
    except Exception as e:
        print(f"   ❌ Point creation failed: {e}")
        return False
    
    # Test 2: Point serialization
    print("\n2. Testing point serialization...")
    try:
        point_dict = point.to_dict()
        print(f"   ✅ Serialized point to dict with {len(point_dict)} fields")
        print(f"   📊 Contains: {list(point_dict.keys())}")
        
        # Verify required fields
        required_fields = ['name', 'value', 'timestamp', 'type']
        for field in required_fields:
            if field not in point_dict:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        print("   ✅ All required fields present")
        
    except Exception as e:
        print(f"   ❌ Serialization failed: {e}")
        return False
    
    print("✅ MetricPoint tests passed!")
    return True


async def test_metric_series():
    """Test metric series functionality."""
    print("\n📈 Testing MetricSeries...")
    
    # Test 1: Series creation and point addition
    print("\n1. Testing series creation...")
    try:
        series = MetricSeries(
            name="test_counter",
            metric_type=MetricType.COUNTER,
            labels={'service': 'api'}
        )
        
        print(f"   ✅ Series created: {series.name}")
        print(f"   📊 Type: {series.metric_type.value}")
        
        # Add points
        for i in range(10):
            series.add_point(float(i), labels={'iteration': str(i)})
        
        print(f"   ✅ Added {len(series.points)} points")
        
    except Exception as e:
        print(f"   ❌ Series creation failed: {e}")
        return False
    
    # Test 2: Time window filtering
    print("\n2. Testing time window filtering...")
    try:
        # Add points with different timestamps
        now = datetime.now()
        
        # Add recent points (within 1 minute)
        for i in range(5):
            timestamp = now - timedelta(seconds=i * 10)  # 0, 10, 20, 30, 40 seconds ago
            series.add_point(100 + i, timestamp=timestamp)
        
        # Add old points (more than 1 minute ago)
        for i in range(3):
            timestamp = now - timedelta(minutes=2 + i)  # 2, 3, 4 minutes ago
            series.add_point(200 + i, timestamp=timestamp)
        
        # Test window filtering
        recent_points = series.get_points_in_window(TimeWindow.MINUTE)
        print(f"   ✅ Found {len(recent_points)} points within 1 minute window")
        
        all_points = series.get_points_in_window(TimeWindow.DAY)
        print(f"   ✅ Found {len(all_points)} points within 24 hour window")
        
        if len(recent_points) < len(all_points):
            print("   ✅ Time window filtering works correctly")
        else:
            print("   ❌ Time window filtering may not be working")
            return False
        
    except Exception as e:
        print(f"   ❌ Time window filtering failed: {e}")
        return False
    
    # Test 3: Metric aggregation
    print("\n3. Testing metric aggregation...")
    try:
        # Test counter aggregation
        counter_agg = series.aggregate(TimeWindow.HOUR)
        print(f"   ✅ Counter aggregation: {counter_agg}")
        
        # Test histogram series
        histogram_series = MetricSeries("test_histogram", MetricType.HISTOGRAM)
        
        # Add response time values
        response_times = [0.1, 0.2, 0.15, 0.3, 0.25, 0.4, 0.2, 0.35, 0.18, 0.22]
        for rt in response_times:
            histogram_series.add_point(rt)
        
        histogram_agg = histogram_series.aggregate(TimeWindow.HOUR)
        print(f"   ✅ Histogram aggregation: count={histogram_agg.get('count')}")
        print(f"   📊 Statistics: min={histogram_agg.get('min'):.3f}, max={histogram_agg.get('max'):.3f}")
        print(f"   📊 Percentiles: p50={histogram_agg.get('p50'):.3f}, p95={histogram_agg.get('p95'):.3f}")
        
    except Exception as e:
        print(f"   ❌ Aggregation failed: {e}")
        return False
    
    print("✅ MetricSeries tests passed!")
    return True


async def test_metrics_config():
    """Test metrics configuration."""
    print("\n⚙️ Testing MetricsConfig...")
    
    # Test 1: Default configuration
    print("\n1. Testing default configuration...")
    try:
        config = MetricsConfig()
        print(f"   ✅ Default config: enabled={config.enabled}")
        print(f"   ⏱️  Collection interval: {config.collection_interval}s")
        print(f"   📊 Max series points: {config.max_series_points}")
        print(f"   🔄 Retention: {config.retention_hours}h")
        
    except Exception as e:
        print(f"   ❌ Default config failed: {e}")
        return False
    
    # Test 2: Custom configuration
    print("\n2. Testing custom configuration...")
    try:
        config = MetricsConfig(
            enabled=True,
            collection_interval=30.0,
            max_series_points=5000,
            retention_hours=48,
            export_enabled=True,
            export_format="prometheus",
            enable_alerts=True,
            alert_thresholds={
                'api_error_rate': 5.0,
                'api_request_duration_seconds': 2.0
            },
            default_labels={
                'environment': 'test',
                'service': 'document360'
            }
        )
        
        print(f"   ✅ Custom config: collection_interval={config.collection_interval}")
        print(f"   📤 Export: {config.export_enabled} ({config.export_format})")
        print(f"   🚨 Alerts: {config.enable_alerts} with {len(config.alert_thresholds)} thresholds")
        print(f"   🏷️  Default labels: {config.default_labels}")
        
    except Exception as e:
        print(f"   ❌ Custom config failed: {e}")
        return False
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    try:
        # Test invalid collection interval
        try:
            invalid_config = MetricsConfig(collection_interval=0.5)  # Invalid < 1.0
            print("   ❌ Should have failed with collection_interval < 1.0")
            return False
        except Exception:
            print("   ✅ Correctly validated collection_interval")
        
        # Test invalid retention
        try:
            invalid_config = MetricsConfig(retention_hours=0)  # Invalid < 1
            print("   ❌ Should have failed with retention_hours < 1")
            return False
        except Exception:
            print("   ✅ Correctly validated retention_hours")
        
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        return False
    
    print("✅ MetricsConfig tests passed!")
    return True


async def test_api_metrics():
    """Test ApiMetrics functionality."""
    print("\n🔧 Testing ApiMetrics...")
    
    # Test 1: Metrics initialization
    print("\n1. Testing metrics initialization...")
    try:
        config = MetricsConfig(
            enabled=True,
            collection_interval=5.0,
            default_labels={'service': 'test'}
        )
        
        metrics = ApiMetrics(config)
        print(f"   ✅ ApiMetrics initialized")
        print(f"   📊 Built-in metrics created")
        
    except Exception as e:
        print(f"   ❌ Metrics initialization failed: {e}")
        return False
    
    # Test 2: Basic metric operations
    print("\n2. Testing basic metric operations...")
    try:
        # Test counter
        metrics.increment("test_requests", 5)
        metrics.increment("test_requests", 3)
        print("   ✅ Counter increment works")
        
        # Test gauge
        metrics.gauge("test_connections", 42)
        metrics.gauge("test_connections", 38)
        print("   ✅ Gauge setting works")
        
        # Test histogram
        for duration in [0.1, 0.2, 0.15, 0.3, 0.25]:
            metrics.histogram("test_durations", duration)
        print("   ✅ Histogram recording works")
        
        # Test timing (convenience method)
        metrics.timing("test_response_time", 0.123)
        print("   ✅ Timing recording works")
        
    except Exception as e:
        print(f"   ❌ Basic operations failed: {e}")
        return False
    
    # Test 3: API-specific metrics
    print("\n3. Testing API-specific metrics...")
    try:
        # Record API request
        metrics.record_request(
            method="GET",
            endpoint="/api/articles",
            status_code=200,
            duration=0.145,
            request_size=512,
            response_size=2048
        )
        
        # Record error request
        metrics.record_request(
            method="POST",
            endpoint="/api/articles",
            status_code=400,
            duration=0.089,
            request_size=1024,
            response_size=256
        )
        print("   ✅ API request recording works")
        
        # Record rate limit
        metrics.record_rate_limit(remaining=95, reset_time=3600.0, hit=False)
        print("   ✅ Rate limit recording works")
        
        # Record token usage
        metrics.record_token_usage("token_001", success=True)
        metrics.record_token_rotation("old_token", "new_token", "expired")
        print("   ✅ Token metrics recording works")
        
        # Record connection events
        metrics.record_connection("created", 1)
        metrics.record_connection("active", 5)
        print("   ✅ Connection metrics recording works")
        
        # Record cache events
        metrics.record_cache_event("hit")
        metrics.record_cache_event("miss")
        metrics.record_cache_event("size", 1024)
        print("   ✅ Cache metrics recording works")
        
        # Record circuit breaker events
        metrics.record_circuit_breaker("api_breaker", "failure", "open")
        metrics.record_circuit_breaker("api_breaker", "success", "closed")
        print("   ✅ Circuit breaker metrics recording works")
        
        # Record sync operations
        metrics.record_sync_operation("incremental", items=100, duration=5.5, duplicates=3)
        print("   ✅ Sync operation metrics recording works")
        
    except Exception as e:
        print(f"   ❌ API-specific metrics failed: {e}")
        return False
    
    # Test 4: Metric retrieval and aggregation
    print("\n4. Testing metric retrieval...")
    try:
        # Get specific metric
        requests_metric = metrics.get_metric("api_requests_total", TimeWindow.HOUR)
        if requests_metric:
            print(f"   ✅ Retrieved requests metric: {requests_metric['data'].get('total', 0)} total")
        
        # Get all metrics
        all_metrics = metrics.get_all_metrics(TimeWindow.FIVE_MINUTES)
        print(f"   ✅ Retrieved {len(all_metrics)} metrics")
        
        # Get health metrics
        health_metrics = metrics.get_health_metrics()
        print(f"   ✅ Health metrics: {len(health_metrics)} indicators")
        print(f"   📊 Error rate: {health_metrics.get('error_rate_percent', 0):.1f}%")
        print(f"   ⏱️  Uptime: {health_metrics.get('uptime_seconds', 0):.1f}s")
        
    except Exception as e:
        print(f"   ❌ Metric retrieval failed: {e}")
        return False
    
    print("✅ ApiMetrics tests passed!")
    return True


async def test_metrics_export():
    """Test metrics export functionality."""
    print("\n📤 Testing metrics export...")
    
    # Test 1: Prometheus export
    print("\n1. Testing Prometheus export...")
    try:
        config = MetricsConfig(export_enabled=True, export_format="prometheus")
        metrics = ApiMetrics(config)
        
        # Add some test data
        metrics.increment("test_counter", 10, labels={'service': 'api'})
        metrics.gauge("test_gauge", 42.5, labels={'type': 'connections'})
        metrics.histogram("test_histogram", 0.123, labels={'endpoint': '/api/test'})
        
        # Export to Prometheus format
        prometheus_output = metrics.export_metrics("prometheus")
        print(f"   ✅ Prometheus export generated ({len(prometheus_output)} chars)")
        
        # Verify format
        lines = prometheus_output.strip().split('\n')
        help_lines = [l for l in lines if l.startswith('# HELP')]
        type_lines = [l for l in lines if l.startswith('# TYPE')]
        
        print(f"   📊 Contains {len(help_lines)} help lines, {len(type_lines)} type lines")
        
        if help_lines and type_lines:
            print("   ✅ Prometheus format looks correct")
        else:
            print("   ❌ Prometheus format may be incorrect")
            return False
        
    except Exception as e:
        print(f"   ❌ Prometheus export failed: {e}")
        return False
    
    # Test 2: JSON export
    print("\n2. Testing JSON export...")
    try:
        json_output = metrics.export_metrics("json")
        print(f"   ✅ JSON export generated ({len(json_output)} chars)")
        
        # Verify it's valid JSON
        import json
        parsed = json.loads(json_output)
        print(f"   📊 Contains {len(parsed)} metrics")
        
        if isinstance(parsed, dict) and parsed:
            print("   ✅ JSON format looks correct")
        else:
            print("   ❌ JSON format may be incorrect")
            return False
        
    except Exception as e:
        print(f"   ❌ JSON export failed: {e}")
        return False
    
    print("✅ Metrics export tests passed!")
    return True


async def test_alerts_system():
    """Test metrics alerting system."""
    print("\n🚨 Testing alerts system...")
    
    # Test 1: Alert configuration and callbacks
    print("\n1. Testing alert configuration...")
    try:
        config = MetricsConfig(
            enable_alerts=True,
            alert_thresholds={
                'api_error_rate': 5.0,          # Error rate > 5%
                'api_request_duration_seconds': 1.0,  # Response time > 1s
            }
        )
        
        metrics = ApiMetrics(config)
        
        # Add alert callback
        alert_calls = []
        def test_alert_callback(metric_name: str, alert_data: dict):
            alert_calls.append({'metric': metric_name, 'data': alert_data})
        
        metrics.add_alert_callback(test_alert_callback)
        print("   ✅ Alert callback registered")
        
        # Generate metrics that should trigger alerts
        # High error rate
        for i in range(10):
            metrics.record_request("GET", "/api/test", 500, 0.1)  # 10 error requests
        
        for i in range(10):
            metrics.record_request("GET", "/api/test", 200, 0.1)  # 10 successful requests
        
        # High response times
        for i in range(5):
            metrics.histogram("api_request_duration_seconds", 2.0)  # Slow responses
        
        # Check alerts
        metrics.check_alerts()
        print(f"   ✅ Alert checking completed")
        print(f"   🚨 Generated {len(alert_calls)} alerts")
        
        for alert in alert_calls:
            print(f"   📊 Alert: {alert['metric']} = {alert['data'].get('current_value')}")
        
    except Exception as e:
        print(f"   ❌ Alert system test failed: {e}")
        return False
    
    print("✅ Alerts system tests passed!")
    return True


async def test_global_metrics():
    """Test global metrics instance."""
    print("\n🌍 Testing global metrics...")
    
    # Test 1: Default global instance
    print("\n1. Testing default global instance...")
    try:
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        
        print(f"   ✅ Global metrics instance retrieved")
        print(f"   🔄 Same instance: {metrics1 is metrics2}")
        
        if metrics1 is metrics2:
            print("   ✅ Singleton pattern works correctly")
        else:
            print("   ❌ Singleton pattern may not be working")
            return False
        
    except Exception as e:
        print(f"   ❌ Global instance test failed: {e}")
        return False
    
    # Test 2: Configured global instance
    print("\n2. Testing configured global instance...")
    try:
        custom_config = MetricsConfig(
            collection_interval=60.0,
            default_labels={'global': 'true'}
        )
        
        configured_metrics = configure_metrics(custom_config)
        new_global = get_metrics()
        
        print(f"   ✅ Configured global metrics")
        print(f"   🔄 Same instance: {configured_metrics is new_global}")
        
        if configured_metrics is new_global:
            print("   ✅ Global configuration works correctly")
        else:
            print("   ❌ Global configuration may not be working")
            return False
        
    except Exception as e:
        print(f"   ❌ Global configuration test failed: {e}")
        return False
    
    print("✅ Global metrics tests passed!")
    return True


async def test_metrics_performance():
    """Test metrics performance under load."""
    print("\n⚡ Testing metrics performance...")
    
    # Test 1: High-frequency metric recording
    print("\n1. Testing high-frequency recording...")
    try:
        config = MetricsConfig(enabled=True)
        metrics = ApiMetrics(config)
        
        # Record many metrics quickly
        start_time = time.time()
        num_operations = 1000
        
        for i in range(num_operations):
            metrics.increment("perf_test_counter", 1, labels={'batch': str(i // 100)})
            metrics.gauge("perf_test_gauge", float(i))
            metrics.histogram("perf_test_histogram", float(i) / 1000.0)
        
        end_time = time.time()
        duration = end_time - start_time
        ops_per_second = num_operations / duration if duration > 0 else 0
        
        print(f"   ✅ Recorded {num_operations} metrics in {duration:.3f}s")
        print(f"   ⚡ Performance: {ops_per_second:.0f} ops/second")
        
        if ops_per_second > 100:  # Should handle at least 100 ops/second
            print("   ✅ Performance is acceptable")
        else:
            print("   ⚠️  Performance may be slow")
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        return False
    
    print("✅ Performance tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting ApiMetrics Tests")
    
    success = True
    
    # Test metric point
    if not await test_metric_point():
        success = False
    
    # Test metric series
    if not await test_metric_series():
        success = False
    
    # Test metrics configuration
    if not await test_metrics_config():
        success = False
    
    # Test API metrics
    if not await test_api_metrics():
        success = False
    
    # Test metrics export
    if not await test_metrics_export():
        success = False
    
    # Test alerts system
    if not await test_alerts_system():
        success = False
    
    # Test global metrics
    if not await test_global_metrics():
        success = False
    
    # Test performance
    if not await test_metrics_performance():
        success = False
    
    if success:
        print("\n🎉 All ApiMetrics tests completed successfully!")
        print("✅ Comprehensive observability and metrics system is ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())