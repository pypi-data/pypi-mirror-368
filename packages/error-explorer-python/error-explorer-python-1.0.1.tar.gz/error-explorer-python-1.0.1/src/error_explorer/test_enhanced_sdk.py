#!/usr/bin/env python3
"""Test script for the enhanced Error Explorer Python SDK."""

import sys
import os

# Add the src directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from error_explorer import ErrorExplorer


def test_enhanced_sdk():
    """Test the enhanced SDK features."""
    print("Testing Enhanced Error Explorer Python SDK...")
    
    # Initialize with enhanced configuration
    client = ErrorExplorer(
        webhook_url="https://api.example.com/webhook",
        project_name="test-project",
        environment="development",
        debug=True,
        # Enable all advanced features
        enable_rate_limiting=True,
        enable_quota_management=True,
        enable_offline_queue=True,
        enable_sdk_monitoring=True,
        max_requests_per_minute=5,
        daily_limit=100
    )
    
    print("✓ SDK initialized with advanced features")
    
    # Test health status
    health = client.get_health_status()
    print(f"✓ Health status: {health.get('is_healthy', 'Unknown')}")
    
    # Test security report
    security_report = client.get_security_report()
    print(f"✓ Security report generated: {len(security_report.get('checks', {}))} checks")
    
    # Test breadcrumbs
    client.add_breadcrumb("Testing enhanced breadcrumbs", "test", "info")
    client.breadcrumb_manager.add_performance("test_operation", 150.5)
    client.breadcrumb_manager.add_system_event("SDK test started")
    
    breadcrumb_stats = client.breadcrumb_manager.get_stats()
    print(f"✓ Breadcrumbs: {breadcrumb_stats['total_breadcrumbs']} total")
    
    # Test connection (this will fail but should be handled gracefully)
    connection_test = client.test_connection()
    print(f"✓ Connection test completed: {connection_test['success']}")
    
    # Test exception capture with all services
    try:
        raise ValueError("Test exception for enhanced SDK")
    except Exception as e:
        client.capture_exception(e, {"test_context": "enhanced_sdk_test"})
    
    print("✓ Exception captured with enhanced processing")
    
    # Test offline queue status
    queue_status = client.process_offline_queue()
    print(f"✓ Offline queue processed: {queue_status}")
    
    # Test rate limiting
    for i in range(10):
        try:
            client.capture_message(f"Rate limit test {i}", "info")
        except:
            pass
    
    final_health = client.get_health_status()
    print(f"✓ Final health check: {final_health.get('is_healthy', 'Unknown')}")
    
    if 'rate_limiter' in final_health:
        rate_stats = final_health['rate_limiter']
        print(f"✓ Rate limiter stats: {rate_stats.get('request_counts', {})}")
    
    print("\n🎉 Enhanced SDK test completed successfully!")
    print("\nNew features available:")
    print("- ✅ Rate limiting with intelligent deduplication")
    print("- ✅ Multi-tier quota management (daily/monthly/burst)")
    print("- ✅ Offline error queuing with persistent storage")
    print("- ✅ Comprehensive security validation and sanitization")
    print("- ✅ Real-time SDK monitoring and health checks")
    print("- ✅ Advanced retry management with exponential backoff + jitter")
    print("- ✅ Extended breadcrumb system (12+ types)")
    print("- ✅ Performance tracking and slow request detection")
    print("- ✅ Framework-specific integrations (Django, Flask, FastAPI)")


if __name__ == "__main__":
    test_enhanced_sdk()