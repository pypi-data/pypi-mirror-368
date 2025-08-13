"""Main Error Explorer client implementation."""

import json
import os
import platform
import sys
import threading
import traceback
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests

from .breadcrumbs import BreadcrumbManager
from .services import (
    RateLimiter, RateLimitConfig,
    QuotaManager, QuotaLimits,
    OfflineManager, OfflineConfig,
    SecurityValidator, SecurityConfig,
    SDKMonitor, MonitoringConfig,
    RetryManager, RetryConfig
)
from .types import (
    ErrorData,
    ErrorExplorerConfig,
    RequestData,
    ServerData,
    UserContext,
)


class ErrorExplorer:
    """Enhanced Error Explorer client with enterprise-grade features."""
    
    def __init__(
        self,
        webhook_url: str,
        project_name: str,
        environment: str = "production",
        **kwargs
    ):
        """Initialize Error Explorer client.
        
        Args:
            webhook_url: The webhook URL for your Error Explorer project
            project_name: Name of your project
            environment: Environment (development, staging, production)
            **kwargs: Additional configuration options
        """
        self.config = ErrorExplorerConfig(
            webhook_url=webhook_url,
            project_name=project_name,
            environment=environment,
            **kwargs
        )
        
        # Initialize core components
        self.breadcrumb_manager = BreadcrumbManager(self.config.max_breadcrumbs)
        self._user_context: Optional[UserContext] = None
        self._context_lock = threading.Lock()
        self.commit_hash = self._detect_commit_hash()
        
        # Initialize advanced services
        self._init_advanced_services()
        
        # Set initial user context if provided
        if self.config.user_id or self.config.user_email:
            self.set_user({
                "id": self.config.user_id,
                "email": self.config.user_email
            })
        
        # Add initialization breadcrumb
        self.breadcrumb_manager.add_lifecycle_event(
            "init", 
            "ErrorExplorer", 
            {"environment": environment, "project": project_name}
        )
    
    def _init_advanced_services(self) -> None:
        """Initialize advanced services based on configuration."""
        # Rate limiter
        if self.config.enable_rate_limiting:
            rate_config = RateLimitConfig(
                max_requests_per_minute=self.config.max_requests_per_minute,
                duplicate_window_seconds=self.config.duplicate_window_seconds,
                enable_deduplication=self.config.enable_deduplication
            )
            self.rate_limiter = RateLimiter(rate_config)
        else:
            self.rate_limiter = None
        
        # Quota manager
        if self.config.enable_quota_management:
            quota_limits = QuotaLimits(
                daily_limit=self.config.daily_limit,
                monthly_limit=self.config.monthly_limit,
                burst_limit=self.config.burst_limit,
                max_payload_size_mb=self.config.max_payload_size_mb
            )
            self.quota_manager = QuotaManager(quota_limits)
        else:
            self.quota_manager = None
        
        # Security validator
        security_config = SecurityConfig(
            enforce_https=self.config.enforce_https,
            max_payload_size_mb=self.config.max_payload_size_mb,
            enable_xss_protection=self.config.enable_xss_protection,
            sensitive_fields=self.config.sensitive_fields,
            block_local_urls=self.config.block_local_urls
        )
        self.security_validator = SecurityValidator(security_config)
        
        # SDK monitor
        if self.config.enable_sdk_monitoring:
            monitor_config = MonitoringConfig(
                enable_performance_tracking=self.config.enable_performance_tracking,
                slow_request_threshold_seconds=self.config.slow_request_threshold_seconds,
                health_check_interval_seconds=self.config.health_check_interval_seconds
            )
            self.sdk_monitor = SDKMonitor(monitor_config)
        else:
            self.sdk_monitor = None
        
        # Retry manager
        retry_config = RetryConfig(
            max_retries=self.config.retries,
            jitter_enabled=self.config.enable_jitter,
            exponential_base=self.config.exponential_base,
            max_delay_seconds=self.config.max_delay_seconds
        )
        self.retry_manager = RetryManager(retry_config)
        
        # Offline manager
        if self.config.enable_offline_queue:
            offline_config = OfflineConfig(
                max_queue_size=self.config.max_queue_size,
                max_item_age_hours=self.config.max_item_age_hours,
                batch_size=self.config.queue_batch_size
            )
            self.offline_manager = OfflineManager(
                offline_config, 
                send_callback=self._send_error_direct
            )
        else:
            self.offline_manager = None
    
    def set_user(self, user: Dict[str, Any]) -> None:
        """Set user context.
        
        Args:
            user: User context data
        """
        with self._context_lock:
            self._user_context = UserContext(
                id=user.get("id"),
                email=user.get("email"),
                username=user.get("username"),
                ip=user.get("ip"),
                extra={k: v for k, v in user.items() 
                      if k not in ["id", "email", "username", "ip"]}
            )
    
    def add_breadcrumb(
        self,
        message: str,
        category: str = "custom",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a breadcrumb.
        
        Args:
            message: Breadcrumb message
            category: Category of the breadcrumb
            level: Level (debug, info, warning, error)
            data: Additional data
        """
        self.breadcrumb_manager.add_breadcrumb(message, category, level, data)
    
    def capture_exception(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Any] = None
    ) -> None:
        """Capture an exception with advanced processing.
        
        Args:
            exception: The exception to capture
            context: Additional context data
            request: HTTP request object (Django/Flask)
        """
        if not self.config.enabled:
            return
        
        start_time = time.time()
        
        try:
            # Add exception breadcrumb
            self.breadcrumb_manager.add_exception_context(exception)
            
            # Format error data
            error_data = self._format_error(exception, context, request)
            
            # Security validation
            url_valid, url_reason = self.security_validator.validate_api_url(self.config.webhook_url)
            if not url_valid:
                if self.config.debug:
                    print(f"Error Explorer: Security validation failed: {url_reason}")
                return
            
            # Sanitize error data
            error_data = self.security_validator.sanitize_error_data(error_data)
            
            # Payload size validation
            size_valid, size_reason, size_mb = self.security_validator.validate_payload_size(error_data)
            if not size_valid:
                if self.config.debug:
                    print(f"Error Explorer: {size_reason}")
                return
            
            # Rate limiting check
            if self.rate_limiter:
                rate_allowed, rate_reason = self.rate_limiter.should_allow_request(error_data)
                if not rate_allowed:
                    if self.config.debug:
                        print(f"Error Explorer: {rate_reason}")
                    return
            
            # Quota check
            if self.quota_manager:
                quota_ok, quota_reason, quota_info = self.quota_manager.check_quota(error_data)
                if not quota_ok:
                    if self.config.debug:
                        print(f"Error Explorer: {quota_reason}")
                    return
            
            # Apply before_send hook
            if self.config.before_send:
                processed_data = self.config.before_send(error_data)
                if not processed_data:
                    return
                error_data = processed_data
            
            # Try to send error
            self._send_error_with_services(error_data)
            
        except Exception as e:
            if self.config.debug:
                print(f"Error Explorer: Failed to capture exception: {e}")
        finally:
            # Record performance metrics
            if self.sdk_monitor:
                duration_ms = (time.time() - start_time) * 1000
                self.sdk_monitor.record_request(duration_ms, True)
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Capture a message.
        
        Args:
            message: The message to capture
            level: Message level (debug, info, warning, error)
            context: Additional context data
        """
        exception = Exception(message)
        exception.__class__.__name__ = "CapturedMessage"
        context = context or {}
        context["level"] = level
        self.capture_exception(exception, context)
    
    def _format_error(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Any] = None
    ) -> ErrorData:
        """Format exception data for sending.
        
        Args:
            exception: The exception to format
            context: Additional context data
            request: HTTP request object
            
        Returns:
            ErrorData: Formatted error data
        """
        # Get traceback information
        tb = traceback.extract_tb(exception.__traceback__)
        stack_trace = "".join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        # Get file and line information
        if tb:
            frame = tb[-1]
            file_path = frame.filename
            line_number = frame.lineno
        else:
            file_path = "unknown"
            line_number = 0
        
        error_data = ErrorData(
            message=str(exception),
            exception_class=exception.__class__.__name__,
            stack_trace=stack_trace,
            file=file_path,
            line=line_number,
            project=self.config.project_name,
            environment=self.config.environment,
            commitHash=self.commit_hash,
            timestamp=datetime.utcnow().isoformat() + "Z",
            server=self._get_server_data(),
            breadcrumbs=self.breadcrumb_manager.get_breadcrumbs(),
            context=context
        )
        
        # Add user context if available
        with self._context_lock:
            if self._user_context:
                error_data.user = self._user_context
        
        # Add request data if available
        if request:
            error_data.request = self._format_request(request)
            # Try to get HTTP status from various framework request objects
            if hasattr(request, "status_code"):
                error_data.http_status = request.status_code
            elif hasattr(request, "response") and hasattr(request.response, "status_code"):
                error_data.http_status = request.response.status_code
        
        return error_data
    
    def _detect_commit_hash(self) -> Optional[str]:
        """Detect the current git commit hash."""
        try:
            command = ["git", "rev-parse", "HEAD"]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _format_request(self, request: Any) -> RequestData:
        """Format request data from various frameworks.
        
        Args:
            request: Request object from Django/Flask/etc
            
        Returns:
            RequestData: Formatted request data
        """
        request_data = RequestData()
        
        # Handle Django request
        if hasattr(request, "build_absolute_uri"):
            request_data.url = request.build_absolute_uri()
            request_data.method = request.method
            request_data.headers = dict(request.headers) if hasattr(request, "headers") else {}
            request_data.query = dict(request.GET) if hasattr(request, "GET") else {}
            
            # Get POST data
            if hasattr(request, "POST") and request.method == "POST":
                request_data.body = dict(request.POST)
            
            # Get user IP
            request_data.ip = self._get_client_ip(request)
            request_data.user_agent = request.META.get("HTTP_USER_AGENT") if hasattr(request, "META") else None
        
        # Handle Flask request
        elif hasattr(request, "url"):
            request_data.url = request.url
            request_data.method = request.method
            request_data.headers = dict(request.headers) if hasattr(request, "headers") else {}
            request_data.query = dict(request.args) if hasattr(request, "args") else {}
            
            # Get form data or JSON
            if hasattr(request, "form") and request.method == "POST":
                request_data.body = dict(request.form)
            elif hasattr(request, "get_json"):
                try:
                    request_data.body = request.get_json(silent=True)
                except:
                    pass
            
            request_data.ip = self._get_client_ip(request)
            request_data.user_agent = request.headers.get("User-Agent") if hasattr(request, "headers") else None
        
        # Sanitize sensitive data
        self._sanitize_request_data(request_data)
        
        return request_data
    
    def _get_client_ip(self, request: Any) -> Optional[str]:
        """Get client IP from request.
        
        Args:
            request: Request object
            
        Returns:
            Client IP address or None
        """
        # Django
        if hasattr(request, "META"):
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                return x_forwarded_for.split(",")[0].strip()
            return request.META.get("REMOTE_ADDR")
        
        # Flask
        if hasattr(request, "environ"):
            return request.environ.get("REMOTE_ADDR")
        
        # Try common attributes
        if hasattr(request, "remote_addr"):
            return request.remote_addr
        
        return None
    
    def _sanitize_request_data(self, request_data: RequestData) -> None:
        """Remove sensitive data from request.
        
        Args:
            request_data: Request data to sanitize
        """
        sensitive_fields = [
            "password", "token", "secret", "key", "auth", "authorization",
            "csrf", "session", "cookie", "api_key", "access_token"
        ]
        
        # Sanitize headers
        if request_data.headers:
            for key in list(request_data.headers.keys()):
                if any(field in key.lower() for field in sensitive_fields):
                    request_data.headers[key] = "[FILTERED]"
        
        # Sanitize body
        if isinstance(request_data.body, dict):
            self._sanitize_dict(request_data.body, sensitive_fields)
        
        # Sanitize query parameters
        if isinstance(request_data.query, dict):
            self._sanitize_dict(request_data.query, sensitive_fields)
    
    def _sanitize_dict(self, data: Dict[str, Any], sensitive_fields: List[str]) -> None:
        """Sanitize dictionary data.
        
        Args:
            data: Dictionary to sanitize
            sensitive_fields: List of sensitive field names
        """
        for key in list(data.keys()):
            if any(field in key.lower() for field in sensitive_fields):
                data[key] = "[FILTERED]"
            elif isinstance(data[key], dict):
                self._sanitize_dict(data[key], sensitive_fields)
    
    def _get_server_data(self) -> ServerData:
        """Get server information.
        
        Returns:
            ServerData: Server information
        """
        try:
            import psutil
            memory_usage = psutil.Process().memory_info().rss
        except ImportError:
            memory_usage = 0
        
        return ServerData(
            python_version=sys.version,
            platform=platform.platform(),
            hostname=platform.node(),
            memory_usage=memory_usage,
            pid=os.getpid(),
            thread_id=threading.get_ident()
        )
    
    def _send_error(self, error_data: ErrorData) -> None:
        """Send error data to Error Explorer.
        
        Args:
            error_data: Error data to send
        """
        # Convert dataclass to dict
        data = self._dataclass_to_dict(error_data)
        
        for attempt in range(self.config.retries):
            try:
                response = requests.post(
                    self.config.webhook_url,
                    json=data,
                    timeout=self.config.timeout,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": f"ErrorExplorer-Python/{sys.version_info.major}.{sys.version_info.minor}"
                    }
                )
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == self.config.retries - 1:
                    if self.config.debug:
                        print(f"Error Explorer: Failed to send error after {self.config.retries} attempts: {e}")
                else:
                    # Wait before retry
                    time.sleep(2 ** attempt)
    
    def _send_error_with_services(self, error_data: ErrorData) -> None:
        """Send error data using advanced services.
        
        Args:
            error_data: Error data to send
        """
        def send_operation() -> Any:
            return self._send_error_direct(error_data)
        
        # Use retry manager if available
        if self.retry_manager:
            success, result, retry_attempts = self.retry_manager.execute_with_retry(
                send_operation, 
                context="error_reporting"
            )
            
            # Record metrics
            if self.sdk_monitor:
                self.sdk_monitor.record_request(
                    duration_ms=100,  # Placeholder - actual duration tracked elsewhere
                    success=success,
                    error_type=type(result).__name__ if not success else None,
                    retry_count=len(retry_attempts)
                )
            
            # If send failed and offline queue is enabled, queue for later
            if not success and self.offline_manager:
                self.offline_manager.queue_error(error_data)
                if self.config.debug:
                    print(f"Error Explorer: Queued error for offline processing")
        else:
            # Fallback to simple send
            self._send_error_direct(error_data)
    
    def _send_error_direct(self, error_data: ErrorData) -> bool:
        """Send error data directly to Error Explorer.
        
        Args:
            error_data: Error data to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert dataclass to dict
            data = self._dataclass_to_dict(error_data)
            
            response = requests.post(
                self.config.webhook_url,
                json=data,
                timeout=self.config.timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"ErrorExplorer-Python/{sys.version_info.major}.{sys.version_info.minor}"
                }
            )
            response.raise_for_status()
            
            # Add success breadcrumb
            self.breadcrumb_manager.add_system_event(
                "Error sent successfully",
                {"status_code": response.status_code}
            )
            
            return True
            
        except Exception as e:
            # Add failure breadcrumb
            self.breadcrumb_manager.add_system_event(
                f"Error send failed: {str(e)}",
                level="error"
            )
            
            if self.config.debug:
                print(f"Error Explorer: Failed to send error: {e}")
            
            return False
    
    def _dataclass_to_dict(self, obj: Any) -> Any:
        """Convert dataclass to dictionary recursively.
        
        Args:
            obj: Object to convert
            
        Returns:
            Dictionary representation
        """
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for field_name, field_value in obj.__dict__.items():
                if field_value is not None:
                    result[field_name] = self._dataclass_to_dict(field_value)
            return result
        elif isinstance(obj, list):
            return [self._dataclass_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._dataclass_to_dict(value) for key, value in obj.items()}
        else:
            return obj
    
    # Advanced features API
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get SDK health status and metrics."""
        health_info = {"sdk_enabled": self.config.enabled}
        
        if self.sdk_monitor:
            health_info.update(self.sdk_monitor.get_health_summary())
        
        if self.rate_limiter:
            health_info["rate_limiter"] = self.rate_limiter.get_stats()
        
        if self.quota_manager:
            health_info["quota"] = self.quota_manager.get_quota_status()
        
        if self.offline_manager:
            health_info["offline_queue"] = self.offline_manager.get_queue_status()
        
        health_info["breadcrumbs"] = self.breadcrumb_manager.get_stats()
        
        return health_info
    
    def process_offline_queue(self) -> Dict[str, int]:
        """Process any queued offline errors."""
        if self.offline_manager:
            return self.offline_manager.process_queue(force=True)
        return {"processed": 0, "failed": 0, "remaining": 0}
    
    def clear_offline_queue(self) -> int:
        """Clear all queued offline errors."""
        if self.offline_manager:
            return self.offline_manager.clear_queue()
        return 0
    
    def get_security_report(self, sample_error: Optional[ErrorData] = None) -> Dict[str, Any]:
        """Get security validation report."""
        if sample_error is None:
            # Create sample error for testing
            sample_error = ErrorData(
                message="Sample error",
                exception_class="TestException",
                stack_trace="Sample stack trace",
                file="test.py",
                line=1,
                project=self.config.project_name,
                environment=self.config.environment,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
        
        return self.security_validator.get_security_report(sample_error, self.config.webhook_url)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Error Explorer API."""
        test_start = time.time()
        
        try:
            # Create a test error
            test_error = ErrorData(
                message="SDK Connection Test",
                exception_class="ConnectionTest",
                stack_trace="Test stack trace",
                file="test.py",
                line=1,
                project=self.config.project_name,
                environment=self.config.environment,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            # Test security validation
            url_valid, url_reason = self.security_validator.validate_api_url(self.config.webhook_url)
            if not url_valid:
                return {
                    "success": False,
                    "error": f"URL validation failed: {url_reason}",
                    "duration_ms": (time.time() - test_start) * 1000
                }
            
            # Test payload validation
            size_valid, size_reason, size_mb = self.security_validator.validate_payload_size(test_error)
            if not size_valid:
                return {
                    "success": False,
                    "error": f"Payload validation failed: {size_reason}",
                    "duration_ms": (time.time() - test_start) * 1000
                }
            
            # Attempt actual connection
            success = self._send_error_direct(test_error)
            
            return {
                "success": success,
                "url": self.config.webhook_url,
                "payload_size_mb": size_mb,
                "duration_ms": (time.time() - test_start) * 1000,
                "message": "Connection successful" if success else "Connection failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_ms": (time.time() - test_start) * 1000
            }
    
    def reset_stats(self) -> None:
        """Reset all statistics and counters."""
        if self.rate_limiter:
            self.rate_limiter.reset_stats()
        
        if self.sdk_monitor:
            self.sdk_monitor.reset_metrics()
        
        if self.retry_manager:
            self.retry_manager.reset_stats()
        
        if self.quota_manager:
            # Reset only for testing - be careful in production
            if self.config.debug:
                self.quota_manager.reset_all_quotas()
    
    def enable_auto_breadcrumbs(self) -> None:
        """Enable automatic breadcrumb collection for HTTP requests, etc."""
        # This would integrate with requests library, logging, etc.
        # Implementation depends on specific requirements
        pass
    
    def configure_performance_monitoring(
        self, 
        slow_threshold_seconds: float = 5.0,
        enable_memory_tracking: bool = True
    ) -> None:
        """Configure performance monitoring settings."""
        if self.sdk_monitor:
            self.sdk_monitor.config.slow_request_threshold_seconds = slow_threshold_seconds
            self.sdk_monitor.config.memory_check_enabled = enable_memory_tracking