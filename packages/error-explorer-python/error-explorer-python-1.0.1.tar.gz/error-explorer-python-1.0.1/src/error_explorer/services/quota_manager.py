"""Quota management service for Error Explorer Python SDK."""

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from ..types import ErrorData


@dataclass
class QuotaLimits:
    """Quota limit configuration."""
    daily_limit: int = 1000
    monthly_limit: int = 10000
    burst_limit: int = 50  # Max requests in 1 minute
    max_payload_size_mb: float = 1.0


@dataclass
class QuotaUsage:
    """Current quota usage tracking."""
    daily_count: int = 0
    monthly_count: int = 0
    burst_count: int = 0
    daily_reset_time: str = ""
    monthly_reset_time: str = ""
    burst_reset_time: str = ""
    total_payload_size_mb: float = 0.0


class QuotaManager:
    """
    Multi-tier quota management system.
    
    Features:
    - Daily, monthly, and burst limits
    - Persistent storage of quota usage
    - Automatic quota reset mechanisms
    - Size-based payload limiting
    """
    
    def __init__(
        self, 
        limits: Optional[QuotaLimits] = None,
        storage_path: Optional[str] = None
    ):
        """Initialize quota manager.
        
        Args:
            limits: Quota limits configuration
            storage_path: Path for persistent storage
        """
        self.limits = limits or QuotaLimits()
        self._lock = threading.Lock()
        
        # Setup storage
        if storage_path:
            self.storage_path = storage_path
        else:
            # Default to user's home directory or temp
            home_dir = os.path.expanduser("~")
            if os.access(home_dir, os.W_OK):
                self.storage_path = os.path.join(home_dir, ".error_explorer_quota.json")
            else:
                import tempfile
                self.storage_path = os.path.join(tempfile.gettempdir(), "error_explorer_quota.json")
        
        # Load existing usage or initialize
        self.usage = self._load_usage()
        
        # Check if resets are needed
        self._check_and_reset_quotas()
    
    def check_quota(self, error_data: Optional[ErrorData] = None) -> Tuple[bool, str, Dict[str, any]]:
        """
        Check if request is within quota limits.
        
        Args:
            error_data: Error data to check payload size
            
        Returns:
            Tuple of (within_quota, reason, quota_info)
        """
        with self._lock:
            current_time = time.time()
            
            # Check and reset quotas if needed
            self._check_and_reset_quotas()
            
            # Calculate payload size if error data provided
            payload_size_mb = 0.0
            if error_data:
                payload_size_mb = self._calculate_payload_size(error_data)
                
                # Check payload size limit
                if payload_size_mb > self.limits.max_payload_size_mb:
                    return False, f"Payload size ({payload_size_mb:.2f}MB) exceeds limit ({self.limits.max_payload_size_mb}MB)", self._get_quota_info()
            
            # Check burst limit (requests in last minute)
            if self._should_reset_burst():
                self.usage.burst_count = 0
                self.usage.burst_reset_time = self._get_next_minute_timestamp()
            
            if self.usage.burst_count >= self.limits.burst_limit:
                return False, f"Burst limit exceeded ({self.usage.burst_count}/{self.limits.burst_limit})", self._get_quota_info()
            
            # Check daily limit
            if self.usage.daily_count >= self.limits.daily_limit:
                return False, f"Daily limit exceeded ({self.usage.daily_count}/{self.limits.daily_limit})", self._get_quota_info()
            
            # Check monthly limit
            if self.usage.monthly_count >= self.limits.monthly_limit:
                return False, f"Monthly limit exceeded ({self.usage.monthly_count}/{self.limits.monthly_limit})", self._get_quota_info()
            
            # All checks passed - increment counters
            self.usage.burst_count += 1
            self.usage.daily_count += 1
            self.usage.monthly_count += 1
            self.usage.total_payload_size_mb += payload_size_mb
            
            # Save updated usage
            self._save_usage()
            
            return True, "Within quota limits", self._get_quota_info()
    
    def _calculate_payload_size(self, error_data: ErrorData) -> float:
        """Calculate approximate payload size in MB."""
        try:
            # Convert to JSON and measure size
            from ..client import ErrorExplorer
            dummy_client = ErrorExplorer.__new__(ErrorExplorer)  # Create instance without init
            data_dict = dummy_client._dataclass_to_dict(error_data)
            json_str = json.dumps(data_dict)
            size_bytes = len(json_str.encode('utf-8'))
            return size_bytes / (1024 * 1024)  # Convert to MB
        except Exception:
            # Fallback estimation
            return 0.01  # Assume 10KB if calculation fails
    
    def _check_and_reset_quotas(self) -> None:
        """Check if any quotas need to be reset."""
        current_time = datetime.now()
        
        # Check daily reset
        if self.usage.daily_reset_time:
            reset_time = datetime.fromisoformat(self.usage.daily_reset_time)
            if current_time >= reset_time:
                self.usage.daily_count = 0
                self.usage.daily_reset_time = self._get_next_day_timestamp()
                self.usage.total_payload_size_mb = 0.0
        else:
            self.usage.daily_reset_time = self._get_next_day_timestamp()
        
        # Check monthly reset
        if self.usage.monthly_reset_time:
            reset_time = datetime.fromisoformat(self.usage.monthly_reset_time)
            if current_time >= reset_time:
                self.usage.monthly_count = 0
                self.usage.monthly_reset_time = self._get_next_month_timestamp()
        else:
            self.usage.monthly_reset_time = self._get_next_month_timestamp()
    
    def _should_reset_burst(self) -> bool:
        """Check if burst counter should be reset."""
        if not self.usage.burst_reset_time:
            return True
        
        try:
            reset_time = datetime.fromisoformat(self.usage.burst_reset_time)
            return datetime.now() >= reset_time
        except ValueError:
            return True
    
    def _get_next_day_timestamp(self) -> str:
        """Get timestamp for next day reset."""
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return tomorrow.isoformat()
    
    def _get_next_month_timestamp(self) -> str:
        """Get timestamp for next month reset."""
        current = datetime.now()
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = current.replace(month=current.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return next_month.isoformat()
    
    def _get_next_minute_timestamp(self) -> str:
        """Get timestamp for next minute reset."""
        next_minute = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        return next_minute.isoformat()
    
    def _load_usage(self) -> QuotaUsage:
        """Load quota usage from persistent storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    return QuotaUsage(**data)
        except Exception:
            pass  # Fall back to default usage
        
        return QuotaUsage()
    
    def _save_usage(self) -> None:
        """Save quota usage to persistent storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(asdict(self.usage), f, indent=2)
        except Exception:
            pass  # Fail silently if can't save
    
    def _get_quota_info(self) -> Dict[str, any]:
        """Get current quota information."""
        return {
            "limits": asdict(self.limits),
            "usage": asdict(self.usage),
            "remaining": {
                "daily": max(0, self.limits.daily_limit - self.usage.daily_count),
                "monthly": max(0, self.limits.monthly_limit - self.usage.monthly_count),
                "burst": max(0, self.limits.burst_limit - self.usage.burst_count)
            },
            "reset_times": {
                "daily": self.usage.daily_reset_time,
                "monthly": self.usage.monthly_reset_time,
                "burst": self.usage.burst_reset_time
            }
        }
    
    def get_quota_status(self) -> Dict[str, any]:
        """Get detailed quota status."""
        with self._lock:
            self._check_and_reset_quotas()
            return self._get_quota_info()
    
    def reset_daily_quota(self) -> None:
        """Manually reset daily quota (for testing)."""
        with self._lock:
            self.usage.daily_count = 0
            self.usage.total_payload_size_mb = 0.0
            self.usage.daily_reset_time = self._get_next_day_timestamp()
            self._save_usage()
    
    def reset_monthly_quota(self) -> None:
        """Manually reset monthly quota (for testing)."""
        with self._lock:
            self.usage.monthly_count = 0
            self.usage.monthly_reset_time = self._get_next_month_timestamp()
            self._save_usage()
    
    def reset_all_quotas(self) -> None:
        """Manually reset all quotas (for testing)."""
        with self._lock:
            self.usage = QuotaUsage()
            self.usage.daily_reset_time = self._get_next_day_timestamp()
            self.usage.monthly_reset_time = self._get_next_month_timestamp()
            self.usage.burst_reset_time = self._get_next_minute_timestamp()
            self._save_usage()