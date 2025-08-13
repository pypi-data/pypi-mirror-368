"""Type definitions for Error Explorer Python SDK."""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ErrorExplorerConfig:
    """Enhanced configuration for Error Explorer client."""
    webhook_url: str
    project_name: str
    environment: str = "production"
    enabled: bool = True
    user_id: Optional[Union[str, int]] = None
    user_email: Optional[str] = None
    max_breadcrumbs: int = 50
    timeout: int = 5
    retries: int = 3
    before_send: Optional[callable] = None
    debug: bool = False
    
    # Rate limiting configuration
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 10
    enable_deduplication: bool = True
    duplicate_window_seconds: int = 5
    
    # Quota management configuration
    enable_quota_management: bool = True
    daily_limit: int = 1000
    monthly_limit: int = 10000
    burst_limit: int = 50
    max_payload_size_mb: float = 1.0
    
    # Offline queue configuration
    enable_offline_queue: bool = True
    max_queue_size: int = 50
    max_item_age_hours: int = 24
    queue_batch_size: int = 5
    
    # Security configuration
    enforce_https: bool = True
    enable_xss_protection: bool = True
    block_local_urls: bool = True
    sensitive_fields: Optional[List[str]] = None
    
    # Monitoring configuration
    enable_sdk_monitoring: bool = True
    enable_performance_tracking: bool = True
    slow_request_threshold_seconds: float = 5.0
    health_check_interval_seconds: int = 60
    
    # Retry configuration
    enable_jitter: bool = True
    exponential_base: float = 2.0
    max_delay_seconds: float = 60.0


@dataclass
class Breadcrumb:
    """Breadcrumb data structure."""
    message: str
    category: str
    level: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class UserContext:
    """User context data structure."""
    id: Optional[Union[str, int]] = None
    email: Optional[str] = None
    username: Optional[str] = None
    ip: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass
class RequestData:
    """HTTP request data structure."""
    url: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    query: Optional[Dict[str, Any]] = None
    body: Optional[Any] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class ServerData:
    """Server information data structure."""
    python_version: str
    platform: str
    hostname: str
    memory_usage: int
    pid: int
    thread_id: Optional[int] = None


@dataclass
class ErrorData:
    """Complete error data structure for sending to Error Explorer."""
    message: str
    exception_class: str
    stack_trace: str
    file: str
    line: int
    project: str
    environment: str
    timestamp: str
    http_status: Optional[int] = None
    request: Optional[RequestData] = None
    server: Optional[ServerData] = None
    context: Optional[Dict[str, Any]] = None
    breadcrumbs: Optional[List[Breadcrumb]] = None
    user: Optional[UserContext] = None


# Type aliases for backward compatibility
ErrorLevel = str  # 'debug', 'info', 'warning', 'error'
BreadcrumbLevel = str  # 'debug', 'info', 'warning', 'error'