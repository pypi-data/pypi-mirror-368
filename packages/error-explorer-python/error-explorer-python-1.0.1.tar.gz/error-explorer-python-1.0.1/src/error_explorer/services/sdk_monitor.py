"""SDK monitoring service for Error Explorer Python SDK."""

import sys
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque, defaultdict


@dataclass
class MonitoringConfig:
    """Configuration for SDK monitoring."""
    enable_performance_tracking: bool = True
    enable_health_monitoring: bool = True
    max_request_history: int = 100
    health_check_interval_seconds: int = 60
    slow_request_threshold_seconds: float = 5.0
    memory_check_enabled: bool = True


@dataclass
class RequestMetrics:
    """Metrics for individual requests."""
    timestamp: float
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    response_size_bytes: Optional[int] = None
    retry_count: int = 0


@dataclass
class HealthStatus:
    """Overall SDK health status."""
    is_healthy: bool
    last_check: float
    issues: List[str]
    uptime_seconds: float
    success_rate: float
    average_response_time_ms: float


class SDKMonitor:
    """
    Real-time SDK health monitoring and performance tracking.
    
    Features:
    - Real-time SDK health monitoring
    - Performance metrics tracking
    - Request success/failure rates
    - Response time monitoring
    - Health status assessment
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize SDK monitor.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config or MonitoringConfig()
        self._lock = threading.Lock()
        
        # Initialize tracking
        self.start_time = time.time()
        self.request_history: deque = deque(maxlen=self.config.max_request_history)
        
        # Health status
        self.current_health = HealthStatus(
            is_healthy=True,
            last_check=time.time(),
            issues=[],
            uptime_seconds=0,
            success_rate=100.0,
            average_response_time_ms=0.0
        )
        
        # Performance counters
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        
        # Memory tracking
        self.memory_usage_history = deque(maxlen=50)  # Keep last 50 readings
        
        # Last health check
        self._last_health_check = 0
    
    def record_request(
        self,
        duration_ms: float,
        success: bool,
        error_type: Optional[str] = None,
        response_size_bytes: Optional[int] = None,
        retry_count: int = 0
    ) -> None:
        """
        Record metrics for a request.
        
        Args:
            duration_ms: Request duration in milliseconds
            success: Whether request was successful
            error_type: Type of error if failed
            response_size_bytes: Response size in bytes
            retry_count: Number of retries attempted
        """
        with self._lock:
            # Create metrics record
            metrics = RequestMetrics(
                timestamp=time.time(),
                duration_ms=duration_ms,
                success=success,
                error_type=error_type,
                response_size_bytes=response_size_bytes,
                retry_count=retry_count
            )
            
            # Add to history
            self.request_history.append(metrics)
            
            # Update counters
            self.counters['total_requests'] += 1
            if success:
                self.counters['successful_requests'] += 1
            else:
                self.counters['failed_requests'] += 1
            
            if retry_count > 0:
                self.counters['requests_with_retries'] += 1
                self.counters['total_retries'] += retry_count
            
            # Track slow requests
            if duration_ms > self.config.slow_request_threshold_seconds * 1000:
                self.counters['slow_requests'] += 1
            
            # Update response time tracking
            self.timers['response_times'].append(duration_ms)
            if len(self.timers['response_times']) > 100:
                self.timers['response_times'] = self.timers['response_times'][-100:]
            
            # Update response size tracking
            if response_size_bytes:
                self.timers['response_sizes'].append(response_size_bytes)
                if len(self.timers['response_sizes']) > 100:
                    self.timers['response_sizes'] = self.timers['response_sizes'][-100:]
    
    def record_memory_usage(self) -> None:
        """Record current memory usage."""
        if not self.config.memory_check_enabled:
            return
        
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            with self._lock:
                self.memory_usage_history.append({
                    'timestamp': time.time(),
                    'rss_mb': memory_info.rss / (1024 * 1024),
                    'vms_mb': memory_info.vms / (1024 * 1024),
                    'percent': process.memory_percent()
                })
        except ImportError:
            # psutil not available
            pass
        except Exception:
            # Failed to get memory info
            pass
    
    def check_health(self, force: bool = False) -> HealthStatus:
        """
        Check and update SDK health status.
        
        Args:
            force: Force health check even if recently checked
            
        Returns:
            Current health status
        """
        current_time = time.time()
        
        # Skip check if recently performed (unless forced)
        if not force and current_time - self._last_health_check < self.config.health_check_interval_seconds:
            return self.current_health
        
        with self._lock:
            issues = []
            
            # Calculate uptime
            uptime = current_time - self.start_time
            
            # Calculate success rate
            success_rate = 100.0
            if self.counters['total_requests'] > 0:
                success_rate = (self.counters['successful_requests'] / self.counters['total_requests']) * 100
            
            # Calculate average response time
            avg_response_time = 0.0
            if self.timers['response_times']:
                avg_response_time = sum(self.timers['response_times']) / len(self.timers['response_times'])
            
            # Health checks
            if success_rate < 95:
                issues.append(f"Low success rate: {success_rate:.1f}%")
            
            if avg_response_time > self.config.slow_request_threshold_seconds * 1000:
                issues.append(f"High average response time: {avg_response_time:.1f}ms")
            
            # Check for excessive retries
            if self.counters['total_requests'] > 0:
                retry_rate = (self.counters['requests_with_retries'] / self.counters['total_requests']) * 100
                if retry_rate > 20:  # More than 20% of requests needed retries
                    issues.append(f"High retry rate: {retry_rate:.1f}%")
            
            # Check memory usage trend
            if self.config.memory_check_enabled and len(self.memory_usage_history) > 10:
                recent_memory = [m['rss_mb'] for m in list(self.memory_usage_history)[-10:]]
                if len(recent_memory) >= 5:
                    # Check for memory growth trend
                    first_half = sum(recent_memory[:len(recent_memory)//2]) / (len(recent_memory)//2)
                    second_half = sum(recent_memory[len(recent_memory)//2:]) / (len(recent_memory) - len(recent_memory)//2)
                    
                    if second_half > first_half * 1.5:  # 50% increase
                        issues.append(f"Memory usage increasing: {first_half:.1f}MB → {second_half:.1f}MB")
            
            # Update health status
            self.current_health = HealthStatus(
                is_healthy=len(issues) == 0,
                last_check=current_time,
                issues=issues,
                uptime_seconds=uptime,
                success_rate=success_rate,
                average_response_time_ms=avg_response_time
            )
            
            self._last_health_check = current_time
            
            # Record memory usage during health check
            self.record_memory_usage()
            
            return self.current_health
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        with self._lock:
            current_time = time.time()
            
            # Calculate metrics from recent requests
            recent_requests = [r for r in self.request_history 
                             if current_time - r.timestamp < 3600]  # Last hour
            
            # Response time percentiles
            response_times = [r.duration_ms for r in recent_requests]
            percentiles = {}
            if response_times:
                response_times.sort()
                percentiles = {
                    'p50': self._percentile(response_times, 50),
                    'p90': self._percentile(response_times, 90),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99)
                }
            
            # Error breakdown
            error_types = defaultdict(int)
            for request in recent_requests:
                if not request.success and request.error_type:
                    error_types[request.error_type] += 1
            
            # Memory metrics
            memory_metrics = {}
            if self.memory_usage_history:
                recent_memory = list(self.memory_usage_history)[-10:]
                if recent_memory:
                    memory_metrics = {
                        'current_rss_mb': recent_memory[-1]['rss_mb'],
                        'current_vms_mb': recent_memory[-1]['vms_mb'],
                        'current_percent': recent_memory[-1]['percent'],
                        'peak_rss_mb': max(m['rss_mb'] for m in recent_memory),
                        'average_rss_mb': sum(m['rss_mb'] for m in recent_memory) / len(recent_memory)
                    }
            
            return {
                'uptime_seconds': current_time - self.start_time,
                'total_requests': self.counters['total_requests'],
                'successful_requests': self.counters['successful_requests'],
                'failed_requests': self.counters['failed_requests'],
                'success_rate': (self.counters['successful_requests'] / max(1, self.counters['total_requests'])) * 100,
                'requests_with_retries': self.counters['requests_with_retries'],
                'total_retries': self.counters['total_retries'],
                'slow_requests': self.counters['slow_requests'],
                'recent_requests_count': len(recent_requests),
                'response_time_percentiles': percentiles,
                'error_breakdown': dict(error_types),
                'memory_metrics': memory_metrics,
                'average_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
                'requests_per_minute': len([r for r in recent_requests if current_time - r.timestamp < 60])
            }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a sorted list."""
        if not data:
            return 0.0
        
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(data):
            return data[f] * (1 - c) + data[f + 1] * c
        else:
            return data[f]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of SDK health."""
        health = self.check_health()
        
        return {
            'is_healthy': health.is_healthy,
            'uptime_hours': health.uptime_seconds / 3600,
            'success_rate': health.success_rate,
            'average_response_time_ms': health.average_response_time_ms,
            'issues_count': len(health.issues),
            'issues': health.issues,
            'last_check_ago_seconds': time.time() - health.last_check,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'sdk_version': "2.0.0"  # Should be imported from package info
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (for testing)."""
        with self._lock:
            self.start_time = time.time()
            self.request_history.clear()
            self.counters.clear()
            self.timers.clear()
            self.memory_usage_history.clear()
            self._last_health_check = 0
            
            self.current_health = HealthStatus(
                is_healthy=True,
                last_check=time.time(),
                issues=[],
                uptime_seconds=0,
                success_rate=100.0,
                average_response_time_ms=0.0
            )
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring systems."""
        return {
            'health': asdict(self.current_health),
            'performance': self.get_performance_metrics(),
            'config': asdict(self.config),
            'export_timestamp': time.time()
        }