"""Rate limiting service for Error Explorer Python SDK."""

import hashlib
import threading
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from ..types import ErrorData


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests_per_minute: int = 10
    duplicate_window_seconds: int = 5
    enable_deduplication: bool = True
    max_tracking_entries: int = 1000


class RateLimiter:
    """
    Advanced rate limiter with intelligent deduplication.
    
    Features:
    - Request-based rate limiting (10/minute default)
    - Duplicate error prevention (5-second window)
    - Intelligent fingerprinting based on error type, message, and stack trace
    - Memory-efficient cleanup mechanisms
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self._lock = threading.Lock()
        
        # Track requests by minute window
        self._request_timestamps: deque = deque()
        
        # Track error fingerprints for deduplication
        self._error_fingerprints: Dict[str, float] = {}
        
        # Track request counts by type for monitoring
        self._request_counts: Dict[str, int] = defaultdict(int)
        
        # Last cleanup time to avoid excessive cleanup calls
        self._last_cleanup = time.time()
    
    def should_allow_request(self, error_data: Optional[ErrorData] = None) -> Tuple[bool, str]:
        """
        Check if request should be allowed.
        
        Args:
            error_data: Error data for deduplication check
            
        Returns:
            Tuple of (should_allow, reason)
        """
        with self._lock:
            current_time = time.time()
            
            # Cleanup old data periodically
            if current_time - self._last_cleanup > 60:  # Cleanup every minute
                self._cleanup_old_data(current_time)
                self._last_cleanup = current_time
            
            # Check rate limit
            if not self._check_rate_limit(current_time):
                self._request_counts['rate_limited'] += 1
                return False, "Rate limit exceeded"
            
            # Check for duplicates if error data provided
            if error_data and self.config.enable_deduplication:
                if self._is_duplicate_error(error_data, current_time):
                    self._request_counts['duplicate_filtered'] += 1
                    return False, "Duplicate error filtered"
            
            # Allow the request
            self._request_timestamps.append(current_time)
            if error_data:
                fingerprint = self._generate_error_fingerprint(error_data)
                self._error_fingerprints[fingerprint] = current_time
            
            self._request_counts['allowed'] += 1
            return True, "Request allowed"
    
    def _check_rate_limit(self, current_time: float) -> bool:
        """Check if current request rate is within limits."""
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        while self._request_timestamps and self._request_timestamps[0] < cutoff_time:
            self._request_timestamps.popleft()
        
        # Check if we're under the limit
        return len(self._request_timestamps) < self.config.max_requests_per_minute
    
    def _is_duplicate_error(self, error_data: ErrorData, current_time: float) -> bool:
        """Check if error is a duplicate within the window."""
        fingerprint = self._generate_error_fingerprint(error_data)
        
        if fingerprint in self._error_fingerprints:
            last_seen = self._error_fingerprints[fingerprint]
            if current_time - last_seen < self.config.duplicate_window_seconds:
                return True
        
        return False
    
    def _generate_error_fingerprint(self, error_data: ErrorData) -> str:
        """
        Generate a unique fingerprint for error deduplication.
        
        Uses error type, message, and stack trace for intelligent grouping.
        """
        # Create fingerprint components
        components = [
            error_data.exception_class or "Unknown",
            error_data.message or "No message",
            error_data.file or "unknown",
            str(error_data.line or 0)
        ]
        
        # Add stack trace signature (first few lines to avoid full trace comparison)
        if error_data.stack_trace:
            stack_lines = error_data.stack_trace.split('\n')[:5]  # First 5 lines
            components.extend(stack_lines)
        
        # Create hash
        fingerprint_string = "|".join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def _cleanup_old_data(self, current_time: float) -> None:
        """Clean up old tracking data to prevent memory leaks."""
        # Clean up old error fingerprints
        cutoff_time = current_time - self.config.duplicate_window_seconds
        expired_fingerprints = [
            fp for fp, timestamp in self._error_fingerprints.items()
            if timestamp < cutoff_time
        ]
        
        for fp in expired_fingerprints:
            del self._error_fingerprints[fp]
        
        # Limit tracking entries to prevent unbounded growth
        if len(self._error_fingerprints) > self.config.max_tracking_entries:
            # Remove oldest entries
            sorted_fingerprints = sorted(
                self._error_fingerprints.items(),
                key=lambda x: x[1]
            )
            
            keep_count = self.config.max_tracking_entries // 2
            self._error_fingerprints = dict(sorted_fingerprints[-keep_count:])
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics."""
        with self._lock:
            current_time = time.time()
            
            # Count recent requests
            cutoff_time = current_time - 60
            recent_requests = sum(1 for ts in self._request_timestamps if ts >= cutoff_time)
            
            return {
                "recent_requests": recent_requests,
                "max_requests_per_minute": self.config.max_requests_per_minute,
                "tracked_fingerprints": len(self._error_fingerprints),
                "request_counts": dict(self._request_counts),
                "rate_limit_usage": f"{recent_requests}/{self.config.max_requests_per_minute}",
                "memory_usage": {
                    "fingerprints": len(self._error_fingerprints),
                    "request_timestamps": len(self._request_timestamps)
                }
            }
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            self._request_counts.clear()