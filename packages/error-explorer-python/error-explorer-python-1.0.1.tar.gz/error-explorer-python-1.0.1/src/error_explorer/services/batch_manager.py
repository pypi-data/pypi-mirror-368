"""Batch management for Error Explorer Python SDK."""

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from ..types import ErrorData


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 10
    batch_timeout: float = 5.0  # seconds
    max_payload_size: int = 1024 * 1024  # 1MB
    

@dataclass
class BatchStats:
    """Statistics for batch processing."""
    current_size: int = 0
    total_batches: int = 0
    total_errors: int = 0
    average_batch_size: float = 0.0
    last_sent_at: Optional[float] = None


class BatchManager:
    """
    Batch manager for grouping and sending multiple errors efficiently.
    
    Features:
    - Configurable batch size and timeout
    - Automatic batch sending when size or timeout threshold is reached
    - Payload size validation to prevent oversized requests
    - Thread-safe operation
    - Performance statistics
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize batch manager.
        
        Args:
            config: Batch configuration
        """
        self.config = config or BatchConfig()
        self._current_batch: List[ErrorData] = []
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None
        self._send_function: Optional[Callable[[List[ErrorData]], bool]] = None
        
        # Statistics
        self._stats = BatchStats()
        
    def configure(self, config: BatchConfig) -> None:
        """Update batch configuration.
        
        Args:
            config: New batch configuration
        """
        with self._lock:
            self.config = config
    
    def set_send_function(self, send_fn: Callable[[List[ErrorData]], bool]) -> None:
        """Set the function to call when sending batches.
        
        Args:
            send_fn: Function that takes a list of ErrorData and returns success status
        """
        self._send_function = send_fn
    
    def add_to_batch(self, error_data: ErrorData) -> None:
        """Add error data to current batch.
        
        Args:
            error_data: Error data to add to batch
        """
        with self._lock:
            self._current_batch.append(error_data)
            self._stats.current_size = len(self._current_batch)
            self._stats.total_errors += 1
            
            # Check if we should send the batch
            if self._should_send_batch():
                self._send_batch_now()
            elif len(self._current_batch) == 1:
                # Start timeout timer for first item
                self._start_timeout_timer()
    
    def flush(self) -> bool:
        """Flush current batch immediately.
        
        Returns:
            True if batch was sent successfully, False otherwise
        """
        with self._lock:
            if self._current_batch:
                return self._send_batch_now()
            return True
    
    def get_stats(self) -> BatchStats:
        """Get batch processing statistics.
        
        Returns:
            Current batch statistics
        """
        with self._lock:
            return BatchStats(
                current_size=self._stats.current_size,
                total_batches=self._stats.total_batches,
                total_errors=self._stats.total_errors,
                average_batch_size=self._stats.average_batch_size,
                last_sent_at=self._stats.last_sent_at
            )
    
    def _should_send_batch(self) -> bool:
        """Check if batch should be sent based on size or payload size.
        
        Returns:
            True if batch should be sent
        """
        if len(self._current_batch) >= self.config.batch_size:
            return True
        
        # Check payload size
        payload_size = self._calculate_payload_size()
        return payload_size >= self.config.max_payload_size
    
    def _calculate_payload_size(self) -> int:
        """Calculate current batch payload size in bytes.
        
        Returns:
            Payload size in bytes
        """
        try:
            # Convert batch to JSON to estimate size
            batch_data = []
            for error_data in self._current_batch:
                if hasattr(error_data, '__dict__'):
                    batch_data.append(error_data.__dict__)
                else:
                    batch_data.append(error_data)
            
            json_str = json.dumps(batch_data, default=str)
            return len(json_str.encode('utf-8'))
        except Exception:
            # Fallback estimation
            return len(self._current_batch) * 1024  # Assume 1KB per error
    
    def _start_timeout_timer(self) -> None:
        """Start timeout timer for batch sending."""
        if self._timer:
            self._timer.cancel()
        
        self._timer = threading.Timer(self.config.batch_timeout, self._timeout_callback)
        self._timer.start()
    
    def _timeout_callback(self) -> None:
        """Callback for batch timeout."""
        with self._lock:
            if self._current_batch:
                self._send_batch_now()
    
    def _send_batch_now(self) -> bool:
        """Send current batch immediately.
        
        Returns:
            True if batch was sent successfully, False otherwise
        """
        if not self._current_batch:
            return True
        
        if not self._send_function:
            # No send function configured, just clear the batch
            self._current_batch.clear()
            self._stats.current_size = 0
            return False
        
        # Copy batch and clear current batch
        batch_to_send = self._current_batch.copy()
        self._current_batch.clear()
        self._stats.current_size = 0
        
        # Cancel timeout timer
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
        try:
            # Send batch
            success = self._send_function(batch_to_send)
            
            if success:
                # Update statistics
                self._stats.total_batches += 1
                self._stats.last_sent_at = time.time()
                self._update_average_batch_size(len(batch_to_send))
            
            return success
            
        except Exception as e:
            # If sending failed, we could implement retry logic here
            # For now, just log and return False
            return False
    
    def _update_average_batch_size(self, batch_size: int) -> None:
        """Update average batch size statistic.
        
        Args:
            batch_size: Size of the batch that was just sent
        """
        total_batches = self._stats.total_batches
        if total_batches > 0:
            current_avg = self._stats.average_batch_size
            self._stats.average_batch_size = ((current_avg * (total_batches - 1)) + batch_size) / total_batches
    
    def reset(self) -> None:
        """Reset batch manager state and statistics."""
        with self._lock:
            self._current_batch.clear()
            if self._timer:
                self._timer.cancel()
                self._timer = None
            
            self._stats = BatchStats()
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)