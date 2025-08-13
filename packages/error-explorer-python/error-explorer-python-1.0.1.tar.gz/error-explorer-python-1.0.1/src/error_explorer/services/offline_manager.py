"""Offline queue management service for Error Explorer Python SDK."""

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from ..types import ErrorData


@dataclass
class OfflineQueueItem:
    """Item in the offline queue."""
    error_data: Dict[str, Any]  # Serialized ErrorData
    timestamp: float
    retry_count: int = 0
    
    
@dataclass
class OfflineConfig:
    """Configuration for offline queue management."""
    max_queue_size: int = 50
    max_item_age_hours: int = 24
    batch_size: int = 5
    retry_interval_seconds: int = 30
    max_retries: int = 3
    storage_enabled: bool = True


class OfflineManager:
    """
    Offline error queue management with persistent storage.
    
    Features:
    - Queues errors when offline (localStorage-based)
    - Automatic retry when back online
    - Configurable queue size (50 items) and age (24 hours)
    - Batch processing to prevent server overload
    """
    
    def __init__(
        self,
        config: Optional[OfflineConfig] = None,
        storage_path: Optional[str] = None,
        send_callback: Optional[Callable[[ErrorData], bool]] = None
    ):
        """Initialize offline manager.
        
        Args:
            config: Offline manager configuration
            storage_path: Path for persistent storage
            send_callback: Callback function to send errors when online
        """
        self.config = config or OfflineConfig()
        self.send_callback = send_callback
        self._lock = threading.Lock()
        
        # Setup storage path
        if storage_path:
            self.storage_path = storage_path
        else:
            # Default to user's home directory or temp
            home_dir = os.path.expanduser("~")
            if os.access(home_dir, os.W_OK):
                self.storage_path = os.path.join(home_dir, ".error_explorer_offline_queue.json")
            else:
                import tempfile
                self.storage_path = os.path.join(tempfile.gettempdir(), "error_explorer_offline_queue.json")
        
        # Initialize queue
        self.queue: List[OfflineQueueItem] = []
        
        # Load existing queue
        if self.config.storage_enabled:
            self._load_queue()
        
        # Track statistics
        self.stats = {
            "items_queued": 0,
            "items_sent": 0,
            "items_dropped": 0,
            "send_attempts": 0,
            "send_failures": 0
        }
        
        # Background processing
        self._last_process_time = 0
        self._processing = False
    
    def queue_error(self, error_data: ErrorData) -> bool:
        """
        Queue an error for later sending.
        
        Args:
            error_data: Error data to queue
            
        Returns:
            True if queued successfully, False if queue is full
        """
        with self._lock:
            # Clean old items first
            self._cleanup_old_items()
            
            # Check queue size
            if len(self.queue) >= self.config.max_queue_size:
                # Remove oldest item to make space
                if self.queue:
                    self.queue.pop(0)
                    self.stats["items_dropped"] += 1
            
            # Add new item
            item = OfflineQueueItem(
                error_data=self._serialize_error_data(error_data),
                timestamp=time.time()
            )
            
            self.queue.append(item)
            self.stats["items_queued"] += 1
            
            # Save to storage
            if self.config.storage_enabled:
                self._save_queue()
            
            return True
    
    def process_queue(self, force: bool = False) -> Dict[str, int]:
        """
        Process queued items by sending them.
        
        Args:
            force: Force processing even if recently processed
            
        Returns:
            Dictionary with processing statistics
        """
        if not self.send_callback:
            return {"processed": 0, "failed": 0, "remaining": len(self.queue)}
        
        current_time = time.time()
        
        # Avoid too frequent processing unless forced
        if not force and current_time - self._last_process_time < self.config.retry_interval_seconds:
            return {"processed": 0, "failed": 0, "remaining": len(self.queue)}
        
        with self._lock:
            if self._processing:
                return {"processed": 0, "failed": 0, "remaining": len(self.queue)}
            
            self._processing = True
            
        try:
            processed = 0
            failed = 0
            items_to_remove = []
            
            # Process up to batch_size items
            batch_items = self.queue[:self.config.batch_size]
            
            for i, item in enumerate(batch_items):
                try:
                    # Deserialize error data
                    error_data = self._deserialize_error_data(item.error_data)
                    
                    # Attempt to send
                    self.stats["send_attempts"] += 1
                    success = self.send_callback(error_data)
                    
                    if success:
                        items_to_remove.append(i)
                        processed += 1
                        self.stats["items_sent"] += 1
                    else:
                        # Increment retry count
                        item.retry_count += 1
                        if item.retry_count >= self.config.max_retries:
                            items_to_remove.append(i)
                            self.stats["items_dropped"] += 1
                        failed += 1
                        self.stats["send_failures"] += 1
                        
                except Exception as e:
                    # Failed to process item
                    item.retry_count += 1
                    if item.retry_count >= self.config.max_retries:
                        items_to_remove.append(i)
                        self.stats["items_dropped"] += 1
                    failed += 1
                    self.stats["send_failures"] += 1
            
            # Remove processed/failed items (in reverse order to maintain indices)
            for i in reversed(items_to_remove):
                self.queue.pop(i)
            
            # Save updated queue
            if self.config.storage_enabled:
                self._save_queue()
            
            self._last_process_time = current_time
            
            return {
                "processed": processed,
                "failed": failed,
                "remaining": len(self.queue)
            }
            
        finally:
            self._processing = False
    
    def _serialize_error_data(self, error_data: ErrorData) -> Dict[str, Any]:
        """Serialize ErrorData to dictionary."""
        # Import here to avoid circular imports
        from ..client import ErrorExplorer
        dummy_client = ErrorExplorer.__new__(ErrorExplorer)
        return dummy_client._dataclass_to_dict(error_data)
    
    def _deserialize_error_data(self, data: Dict[str, Any]) -> ErrorData:
        """Deserialize dictionary back to ErrorData."""
        # Convert nested dictionaries back to dataclasses
        from ..types import RequestData, ServerData, UserContext, Breadcrumb
        
        # Handle nested objects
        if data.get("request"):
            data["request"] = RequestData(**data["request"])
        
        if data.get("server"):
            data["server"] = ServerData(**data["server"])
        
        if data.get("user"):
            data["user"] = UserContext(**data["user"])
        
        if data.get("breadcrumbs"):
            data["breadcrumbs"] = [Breadcrumb(**bc) for bc in data["breadcrumbs"]]
        
        return ErrorData(**data)
    
    def _cleanup_old_items(self) -> None:
        """Remove items older than max_item_age_hours."""
        current_time = time.time()
        max_age_seconds = self.config.max_item_age_hours * 3600
        
        items_to_remove = []
        for i, item in enumerate(self.queue):
            if current_time - item.timestamp > max_age_seconds:
                items_to_remove.append(i)
        
        # Remove old items (in reverse order)
        for i in reversed(items_to_remove):
            self.queue.pop(i)
            self.stats["items_dropped"] += 1
    
    def _load_queue(self) -> None:
        """Load queue from persistent storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                    # Load queue items
                    if "queue" in data:
                        self.queue = [OfflineQueueItem(**item) for item in data["queue"]]
                    
                    # Load stats
                    if "stats" in data:
                        self.stats.update(data["stats"])
                        
                # Clean up old items after loading
                self._cleanup_old_items()
                    
        except Exception:
            # Start with empty queue if loading fails
            self.queue = []
    
    def _save_queue(self) -> None:
        """Save queue to persistent storage."""
        try:
            data = {
                "queue": [asdict(item) for item in self.queue],
                "stats": self.stats,
                "last_saved": time.time()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception:
            pass  # Fail silently if can't save
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and statistics."""
        with self._lock:
            self._cleanup_old_items()
            
            return {
                "queue_size": len(self.queue),
                "max_queue_size": self.config.max_queue_size,
                "oldest_item_age_minutes": self._get_oldest_item_age_minutes(),
                "stats": self.stats.copy(),
                "config": asdict(self.config),
                "is_processing": self._processing,
                "storage_path": self.storage_path if self.config.storage_enabled else None
            }
    
    def _get_oldest_item_age_minutes(self) -> Optional[float]:
        """Get age of oldest item in minutes."""
        if not self.queue:
            return None
        
        oldest_timestamp = min(item.timestamp for item in self.queue)
        age_seconds = time.time() - oldest_timestamp
        return age_seconds / 60
    
    def clear_queue(self) -> int:
        """Clear all items from queue. Returns number of items cleared."""
        with self._lock:
            count = len(self.queue)
            self.queue.clear()
            
            if self.config.storage_enabled:
                self._save_queue()
            
            return count
    
    def is_online(self) -> bool:
        """Check if we appear to be online (simple connectivity check)."""
        try:
            import urllib.request
            urllib.request.urlopen('https://8.8.8.8', timeout=3)
            return True
        except:
            return False