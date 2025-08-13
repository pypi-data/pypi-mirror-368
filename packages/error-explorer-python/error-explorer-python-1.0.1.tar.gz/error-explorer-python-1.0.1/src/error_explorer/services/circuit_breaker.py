"""Circuit breaker implementation for Error Explorer Python SDK."""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    timeout: float = 30.0  # seconds
    reset_timeout: float = 60.0  # seconds


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker operations."""
    state: str = CircuitState.CLOSED.value
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    next_retry_time: Optional[float] = None


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.
    
    Features:
    - Three states: CLOSED, OPEN, HALF_OPEN
    - Configurable failure threshold and timeouts
    - Thread-safe operation
    - Detailed statistics and monitoring
    - Automatic state transitions
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._next_retry_time: Optional[float] = None
        self._lock = threading.Lock()
    
    def configure(self, config: CircuitBreakerConfig) -> None:
        """Update circuit breaker configuration.
        
        Args:
            config: New circuit breaker configuration
        """
        with self._lock:
            self.config = config
    
    def execute(self, operation: Callable[[], T]) -> T:
        """Execute an operation with circuit breaker protection.
        
        Args:
            operation: Function to execute
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If circuit breaker is open or operation fails
        """
        if not self.is_call_allowed():
            raise Exception("Circuit breaker is OPEN - calls are not allowed")
        
        try:
            result = operation()
            self.on_success()
            return result
        except Exception as error:
            self.on_failure()
            raise error
    
    def is_call_allowed(self) -> bool:
        """Check if calls are allowed based on current circuit state.
        
        Returns:
            True if calls are allowed, False otherwise
        """
        with self._lock:
            now = time.time()
            
            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.OPEN:
                # Check if we should transition to HALF_OPEN
                if self._next_retry_time and now >= self._next_retry_time:
                    self._state = CircuitState.HALF_OPEN
                    return True
                return False
            elif self._state == CircuitState.HALF_OPEN:
                return True
            
            return False
    
    def on_success(self) -> None:
        """Record a successful operation."""
        with self._lock:
            self._success_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Reset circuit breaker on successful call from HALF_OPEN
                self.reset()
    
    def on_failure(self) -> None:
        """Record a failed operation."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                # Go back to OPEN state on failure from HALF_OPEN
                self._trip_circuit()
            elif self._failure_count >= self.config.failure_threshold:
                # Trip circuit if failure threshold is reached
                self._trip_circuit()
    
    def _trip_circuit(self) -> None:
        """Trip the circuit breaker to OPEN state."""
        self._state = CircuitState.OPEN
        self._next_retry_time = time.time() + self.config.timeout
    
    def reset(self) -> None:
        """Reset circuit breaker to CLOSED state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._next_retry_time = None
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state.
        
        Returns:
            Current circuit state
        """
        with self._lock:
            return self._state
    
    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics.
        
        Returns:
            Current circuit breaker statistics
        """
        with self._lock:
            return CircuitBreakerStats(
                state=self._state.value,
                failure_count=self._failure_count,
                success_count=self._success_count,
                last_failure_time=self._last_failure_time,
                next_retry_time=self._next_retry_time
            )
    
    def force_open(self) -> None:
        """Force circuit breaker to OPEN state."""
        with self._lock:
            self._state = CircuitState.OPEN
            self._next_retry_time = time.time() + self.config.timeout
    
    def force_close(self) -> None:
        """Force circuit breaker to CLOSED state."""
        self.reset()
    
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is currently open.
        
        Returns:
            True if circuit is open and not allowing calls
        """
        return self._state == CircuitState.OPEN and not self.is_call_allowed()
    
    def get_time_until_retry(self) -> float:
        """Get time until next retry attempt (only relevant when circuit is OPEN).
        
        Returns:
            Seconds until retry, or 0 if not applicable
        """
        with self._lock:
            if self._state == CircuitState.OPEN and self._next_retry_time:
                return max(0, self._next_retry_time - time.time())
            return 0.0
    
    def get_failure_rate(self) -> float:
        """Get current failure rate.
        
        Returns:
            Failure rate as a float between 0 and 1
        """
        with self._lock:
            total_calls = self._success_count + self._failure_count
            return self._failure_count / total_calls if total_calls > 0 else 0.0
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
    
    def get_uptime(self) -> float:
        """Get uptime since last reset.
        
        Returns:
            Uptime in seconds
        """
        with self._lock:
            if self._last_failure_time:
                return time.time() - self._last_failure_time
            return 0.0


class CallableCircuitBreaker:
    """Decorator version of circuit breaker for easier function wrapping."""
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize callable circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.circuit_breaker = CircuitBreaker(config)
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Wrap function with circuit breaker protection.
        
        Args:
            func: Function to wrap
            
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs) -> T:
            return self.circuit_breaker.execute(lambda: func(*args, **kwargs))
        
        # Copy function metadata
        wrapper.__name__ = getattr(func, '__name__', 'wrapped_function')
        wrapper.__doc__ = getattr(func, '__doc__', None)
        
        return wrapper
    
    def get_circuit_breaker(self) -> CircuitBreaker:
        """Get underlying circuit breaker instance.
        
        Returns:
            Circuit breaker instance
        """
        return self.circuit_breaker


def circuit_breaker(
    failure_threshold: int = 5,
    timeout: float = 30.0,
    reset_timeout: float = 60.0
) -> CallableCircuitBreaker:
    """Convenience function to create a circuit breaker decorator.
    
    Args:
        failure_threshold: Number of failures before tripping
        timeout: Seconds to wait before allowing calls in HALF_OPEN
        reset_timeout: Seconds to wait before full reset
        
    Returns:
        Circuit breaker decorator
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        timeout=timeout,
        reset_timeout=reset_timeout
    )
    return CallableCircuitBreaker(config)