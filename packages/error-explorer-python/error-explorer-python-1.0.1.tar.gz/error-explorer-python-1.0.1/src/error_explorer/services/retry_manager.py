"""Retry management service for Error Explorer Python SDK."""

import random
import time
import threading
from dataclasses import dataclass
from typing import Callable, Optional, Any, Tuple, List
from enum import Enum


class RetryReason(Enum):
    """Reasons for retry attempts."""
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    RATE_LIMITED = "rate_limited"
    TEMPORARY_FAILURE = "temporary_failure"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter_enabled: bool = True
    jitter_max_percentage: float = 0.1  # 10% jitter
    retry_on_status_codes: List[int] = None
    
    def __post_init__(self):
        if self.retry_on_status_codes is None:
            # Default to retry on server errors and rate limiting
            self.retry_on_status_codes = [429, 500, 502, 503, 504]


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    attempt_number: int
    delay_seconds: float
    reason: RetryReason
    timestamp: float
    error_message: Optional[str] = None


class RetryManager:
    """
    Advanced retry manager with exponential backoff and jitter.
    
    Features:
    - Exponential backoff with jitter
    - Intelligent retry logic based on error types
    - Configurable retry limits (3 attempts default)
    - Handles network errors, timeouts, and server errors
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry manager.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self._lock = threading.Lock()
        
        # Track retry statistics
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_retries": 0,
            "retries_by_reason": {reason.value: 0 for reason in RetryReason},
            "max_retries_reached": 0
        }
    
    def execute_with_retry(
        self,
        operation: Callable[[], Any],
        context: Optional[str] = None,
        custom_retry_condition: Optional[Callable[[Exception], bool]] = None
    ) -> Tuple[bool, Any, List[RetryAttempt]]:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Function to execute
            context: Optional context for logging
            custom_retry_condition: Custom function to determine if error should be retried
            
        Returns:
            Tuple of (success, result, retry_attempts)
        """
        with self._lock:
            self.stats["total_operations"] += 1
        
        retry_attempts = []
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):  # +1 for initial attempt
            try:
                result = operation()
                
                # Success
                with self._lock:
                    self.stats["successful_operations"] += 1
                    if attempt > 0:
                        self.stats["total_retries"] += attempt
                
                return True, result, retry_attempts
                
            except Exception as e:
                last_exception = e
                
                # Determine if we should retry
                should_retry, reason = self._should_retry(e, attempt, custom_retry_condition)
                
                if not should_retry or attempt >= self.config.max_retries:
                    break
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                
                # Record retry attempt
                retry_attempt = RetryAttempt(
                    attempt_number=attempt + 1,
                    delay_seconds=delay,
                    reason=reason,
                    timestamp=time.time(),
                    error_message=str(e)
                )
                retry_attempts.append(retry_attempt)
                
                # Update statistics
                with self._lock:
                    self.stats["retries_by_reason"][reason.value] += 1
                
                # Wait before retry
                time.sleep(delay)
        
        # All retries exhausted
        with self._lock:
            self.stats["failed_operations"] += 1
            if len(retry_attempts) >= self.config.max_retries:
                self.stats["max_retries_reached"] += 1
        
        return False, last_exception, retry_attempts
    
    def _should_retry(
        self,
        exception: Exception,
        attempt_number: int,
        custom_retry_condition: Optional[Callable[[Exception], bool]] = None
    ) -> Tuple[bool, RetryReason]:
        """
        Determine if an error should be retried and categorize the reason.
        
        Args:
            exception: The exception that occurred
            attempt_number: Current attempt number (0-based)
            custom_retry_condition: Custom retry logic
            
        Returns:
            Tuple of (should_retry, reason)
        """
        # Check custom retry condition first
        if custom_retry_condition and custom_retry_condition(exception):
            return True, RetryReason.TEMPORARY_FAILURE
        
        # Import requests here to avoid dependency issues
        try:
            import requests
            
            # Handle requests exceptions
            if isinstance(exception, requests.exceptions.ConnectionError):
                return True, RetryReason.NETWORK_ERROR
            
            if isinstance(exception, requests.exceptions.Timeout):
                return True, RetryReason.TIMEOUT
            
            if isinstance(exception, requests.exceptions.HTTPError):
                if hasattr(exception, 'response') and exception.response:
                    status_code = exception.response.status_code
                    
                    # Rate limiting
                    if status_code == 429:
                        return True, RetryReason.RATE_LIMITED
                    
                    # Server errors
                    if status_code in self.config.retry_on_status_codes:
                        return True, RetryReason.SERVER_ERROR
                    
                    # Don't retry client errors (4xx except 429)
                    if 400 <= status_code < 500:
                        return False, RetryReason.TEMPORARY_FAILURE
                
                return True, RetryReason.SERVER_ERROR
            
            # Handle other requests exceptions
            if isinstance(exception, requests.exceptions.RequestException):
                return True, RetryReason.NETWORK_ERROR
                
        except ImportError:
            pass
        
        # Handle common Python exceptions
        if isinstance(exception, (OSError, IOError)):
            return True, RetryReason.NETWORK_ERROR
        
        if isinstance(exception, TimeoutError):
            return True, RetryReason.TIMEOUT
        
        # Don't retry by default for unknown exceptions
        return False, RetryReason.TEMPORARY_FAILURE
    
    def _calculate_delay(self, attempt_number: int) -> float:
        """
        Calculate delay for retry attempt using exponential backoff with jitter.
        
        Args:
            attempt_number: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential backoff
        delay = self.config.base_delay_seconds * (self.config.exponential_base ** attempt_number)
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay_seconds)
        
        # Add jitter if enabled
        if self.config.jitter_enabled:
            jitter_range = delay * self.config.jitter_max_percentage
            jitter = random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay + jitter)
        
        return delay
    
    def get_stats(self) -> dict:
        """Get retry statistics."""
        with self._lock:
            stats_copy = self.stats.copy()
            
            # Calculate derived metrics
            if stats_copy["total_operations"] > 0:
                stats_copy["success_rate"] = (stats_copy["successful_operations"] / stats_copy["total_operations"]) * 100
                stats_copy["average_retries_per_operation"] = stats_copy["total_retries"] / stats_copy["total_operations"]
            else:
                stats_copy["success_rate"] = 0.0
                stats_copy["average_retries_per_operation"] = 0.0
            
            # Add configuration info
            stats_copy["config"] = {
                "max_retries": self.config.max_retries,
                "base_delay_seconds": self.config.base_delay_seconds,
                "max_delay_seconds": self.config.max_delay_seconds,
                "jitter_enabled": self.config.jitter_enabled
            }
            
            return stats_copy
    
    def reset_stats(self) -> None:
        """Reset retry statistics."""
        with self._lock:
            self.stats = {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "total_retries": 0,
                "retries_by_reason": {reason.value: 0 for reason in RetryReason},
                "max_retries_reached": 0
            }
    
    def calculate_next_delay(self, attempt_number: int) -> float:
        """
        Calculate what the delay would be for a given attempt number.
        Useful for planning or displaying retry schedules.
        
        Args:
            attempt_number: Attempt number to calculate delay for
            
        Returns:
            Delay in seconds
        """
        return self._calculate_delay(attempt_number)
    
    def get_retry_schedule(self, max_attempts: Optional[int] = None) -> List[float]:
        """
        Get the complete retry schedule showing delays for each attempt.
        
        Args:
            max_attempts: Maximum attempts to show (defaults to config max_retries)
            
        Returns:
            List of delays in seconds for each retry attempt
        """
        if max_attempts is None:
            max_attempts = self.config.max_retries
        
        schedule = []
        for attempt in range(max_attempts):
            delay = self._calculate_delay(attempt)
            schedule.append(delay)
        
        return schedule
    
    def is_retryable_error(self, exception: Exception) -> bool:
        """
        Check if an exception would be retried.
        
        Args:
            exception: Exception to check
            
        Returns:
            True if error would be retried
        """
        should_retry, _ = self._should_retry(exception, 0)
        return should_retry