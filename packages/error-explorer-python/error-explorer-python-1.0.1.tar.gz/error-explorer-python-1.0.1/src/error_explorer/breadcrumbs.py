"""Breadcrumb management for Error Explorer Python SDK."""

import threading
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .types import Breadcrumb


class BreadcrumbManager:
    """
    Advanced thread-safe breadcrumb manager.
    
    Features:
    - Multiple breadcrumb types (HTTP, database, user actions, navigation, console, performance, system)
    - Framework-specific breadcrumbs (Django, Flask, FastAPI)
    - Automatic breadcrumb rotation with configurable limits
    - Performance tracking breadcrumbs
    - System event tracking
    """
    
    def __init__(self, max_breadcrumbs: int = 50):
        """Initialize breadcrumb manager.
        
        Args:
            max_breadcrumbs: Maximum number of breadcrumbs to keep
        """
        self.max_breadcrumbs = max_breadcrumbs
        self._breadcrumbs: List[Breadcrumb] = []
        self._lock = threading.Lock()
        
        # Track breadcrumb statistics
        self.stats = {
            "total_added": 0,
            "by_category": {},
            "by_level": {}
        }
    
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
        breadcrumb = Breadcrumb(
            message=message,
            category=category,
            level=level,
            timestamp=datetime.utcnow().isoformat() + "Z",
            data=data
        )
        
        with self._lock:
            self._breadcrumbs.append(breadcrumb)
            if len(self._breadcrumbs) > self.max_breadcrumbs:
                self._breadcrumbs.pop(0)
            
            # Update statistics
            self.stats["total_added"] += 1
            self.stats["by_category"][category] = self.stats["by_category"].get(category, 0) + 1
            self.stats["by_level"][level] = self.stats["by_level"].get(level, 0) + 1
    
    def get_breadcrumbs(self) -> List[Breadcrumb]:
        """Get all breadcrumbs.
        
        Returns:
            List of breadcrumbs (copy)
        """
        with self._lock:
            return self._breadcrumbs.copy()
    
    def clear(self) -> None:
        """Clear all breadcrumbs."""
        with self._lock:
            self._breadcrumbs.clear()
    
    def add_http_request(
        self, 
        method: str, 
        url: str, 
        status_code: Optional[int] = None
    ) -> None:
        """Add HTTP request breadcrumb.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
        """
        message = f"{method} {url}"
        if status_code:
            message += f" → {status_code}"
        
        level = "error" if status_code and status_code >= 400 else "info"
        
        self.add_breadcrumb(
            message=message,
            category="http",
            level=level,
            data={
                "method": method,
                "url": url,
                "status_code": status_code
            }
        )
    
    def add_database_query(
        self, 
        query: str, 
        duration: Optional[float] = None,
        params: Optional[Any] = None
    ) -> None:
        """Add database query breadcrumb.
        
        Args:
            query: SQL query or description
            duration: Query duration in seconds
            params: Query parameters
        """
        # Truncate long queries
        display_query = query[:100] + "..." if len(query) > 100 else query
        
        message = f"Query: {display_query}"
        if duration:
            message += f" ({duration:.3f}s)"
        
        self.add_breadcrumb(
            message=message,
            category="query",
            level="info",
            data={
                "query": query,
                "duration": duration,
                "params": params
            }
        )
    
    def add_user_action(
        self, 
        action: str, 
        target: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add user action breadcrumb.
        
        Args:
            action: Action performed
            target: Target of the action
            data: Additional action data
        """
        message = f"User {action}"
        if target:
            message += f" {target}"
        
        self.add_breadcrumb(
            message=message,
            category="user",
            level="info",
            data=data or {"action": action, "target": target}
        )
    
    def add_navigation(
        self, 
        from_url: str, 
        to_url: str
    ) -> None:
        """Add navigation breadcrumb.
        
        Args:
            from_url: Source URL
            to_url: Destination URL
        """
        self.add_breadcrumb(
            message=f"Navigation: {from_url} → {to_url}",
            category="navigation",
            level="info",
            data={
                "from": from_url,
                "to": to_url
            }
        )
    
    def add_console_log(
        self, 
        level: str, 
        message: str, 
        data: Optional[Any] = None
    ) -> None:
        """Add console log breadcrumb.
        
        Args:
            level: Log level
            message: Log message
            data: Additional log data
        """
        self.add_breadcrumb(
            message=message,
            category="console",
            level=level,
            data={"data": data} if data else None
        )
    
    def add_performance(
        self,
        operation: str,
        duration_ms: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add performance breadcrumb.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            details: Additional performance details
        """
        level = "warning" if duration_ms > 1000 else "info"  # Warn for operations > 1s
        
        self.add_breadcrumb(
            message=f"Performance: {operation} ({duration_ms:.1f}ms)",
            category="performance",
            level=level,
            data={
                "operation": operation,
                "duration_ms": duration_ms,
                "details": details
            }
        )
    
    def add_system_event(
        self,
        event: str,
        details: Optional[Dict[str, Any]] = None,
        level: str = "info"
    ) -> None:
        """Add system event breadcrumb.
        
        Args:
            event: System event description
            details: Event details
            level: Event level
        """
        self.add_breadcrumb(
            message=f"System: {event}",
            category="system",
            level=level,
            data=details
        )
    
    def add_lifecycle_event(
        self,
        stage: str,
        component: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add application lifecycle event breadcrumb.
        
        Args:
            stage: Lifecycle stage (init, startup, shutdown, etc.)
            component: Component name
            details: Additional details
        """
        message = f"Lifecycle: {stage}"
        if component:
            message += f" ({component})"
        
        self.add_breadcrumb(
            message=message,
            category="lifecycle",
            level="info",
            data=details
        )
    
    def add_security_event(
        self,
        event: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add security event breadcrumb.
        
        Args:
            event: Security event description
            severity: Event severity (info, warning, error)
            details: Event details
        """
        self.add_breadcrumb(
            message=f"Security: {event}",
            category="security",
            level=severity,
            data=details
        )
    
    def add_cache_operation(
        self,
        operation: str,
        key: str,
        hit: Optional[bool] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """Add cache operation breadcrumb.
        
        Args:
            operation: Cache operation (get, set, delete, clear)
            key: Cache key
            hit: Whether operation was a cache hit
            duration_ms: Operation duration
        """
        message = f"Cache {operation}: {key}"
        if hit is not None:
            message += f" ({'HIT' if hit else 'MISS'})"
        if duration_ms:
            message += f" ({duration_ms:.1f}ms)"
        
        self.add_breadcrumb(
            message=message,
            category="cache",
            level="info",
            data={
                "operation": operation,
                "key": key,
                "hit": hit,
                "duration_ms": duration_ms
            }
        )
    
    def add_file_operation(
        self,
        operation: str,
        path: str,
        size_bytes: Optional[int] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """Add file system operation breadcrumb.
        
        Args:
            operation: File operation (read, write, delete, create)
            path: File path
            size_bytes: File size in bytes
            duration_ms: Operation duration
        """
        message = f"File {operation}: {path}"
        if size_bytes:
            message += f" ({size_bytes} bytes)"
        if duration_ms:
            message += f" ({duration_ms:.1f}ms)"
        
        self.add_breadcrumb(
            message=message,
            category="file",
            level="info",
            data={
                "operation": operation,
                "path": path,
                "size_bytes": size_bytes,
                "duration_ms": duration_ms
            }
        )
    
    # Framework-specific breadcrumbs
    
    def add_django_event(
        self,
        event_type: str,
        request_path: Optional[str] = None,
        view_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add Django-specific event breadcrumb.
        
        Args:
            event_type: Type of Django event (request, response, middleware, etc.)
            request_path: Request path
            view_name: View function name
            details: Additional details
        """
        message = f"Django {event_type}"
        if view_name:
            message += f": {view_name}"
        if request_path:
            message += f" ({request_path})"
        
        self.add_breadcrumb(
            message=message,
            category="django",
            level="info",
            data={
                "event_type": event_type,
                "request_path": request_path,
                "view_name": view_name,
                "details": details
            }
        )
    
    def add_flask_event(
        self,
        event_type: str,
        endpoint: Optional[str] = None,
        route: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add Flask-specific event breadcrumb.
        
        Args:
            event_type: Type of Flask event
            endpoint: Flask endpoint name
            route: Route pattern
            details: Additional details
        """
        message = f"Flask {event_type}"
        if endpoint:
            message += f": {endpoint}"
        if route:
            message += f" ({route})"
        
        self.add_breadcrumb(
            message=message,
            category="flask",
            level="info",
            data={
                "event_type": event_type,
                "endpoint": endpoint,
                "route": route,
                "details": details
            }
        )
    
    def add_fastapi_event(
        self,
        event_type: str,
        path: Optional[str] = None,
        operation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add FastAPI-specific event breadcrumb.
        
        Args:
            event_type: Type of FastAPI event
            path: API path
            operation_id: Operation ID
            details: Additional details
        """
        message = f"FastAPI {event_type}"
        if operation_id:
            message += f": {operation_id}"
        if path:
            message += f" ({path})"
        
        self.add_breadcrumb(
            message=message,
            category="fastapi",
            level="info",
            data={
                "event_type": event_type,
                "path": path,
                "operation_id": operation_id,
                "details": details
            }
        )
    
    def add_exception_context(
        self,
        exception: Exception,
        context: Optional[str] = None
    ) -> None:
        """Add exception context breadcrumb.
        
        Args:
            exception: Exception that occurred
            context: Additional context about where exception occurred
        """
        message = f"Exception: {exception.__class__.__name__}: {str(exception)}"
        if context:
            message = f"{context} - {message}"
        
        # Get stack trace
        stack_trace = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        
        self.add_breadcrumb(
            message=message,
            category="exception",
            level="error",
            data={
                "exception_type": exception.__class__.__name__,
                "exception_message": str(exception),
                "context": context,
                "stack_trace": "".join(stack_trace)
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get breadcrumb statistics."""
        with self._lock:
            return {
                "total_breadcrumbs": len(self._breadcrumbs),
                "max_breadcrumbs": self.max_breadcrumbs,
                "stats": self.stats.copy()
            }
    
    def get_breadcrumbs_by_category(self, category: str) -> List[Breadcrumb]:
        """Get breadcrumbs filtered by category."""
        with self._lock:
            return [bc for bc in self._breadcrumbs if bc.category == category]
    
    def get_breadcrumbs_by_level(self, level: str) -> List[Breadcrumb]:
        """Get breadcrumbs filtered by level."""
        with self._lock:
            return [bc for bc in self._breadcrumbs if bc.level == level]
    
    def get_recent_breadcrumbs(self, count: int = 10) -> List[Breadcrumb]:
        """Get most recent breadcrumbs."""
        with self._lock:
            return self._breadcrumbs[-count:] if count <= len(self._breadcrumbs) else self._breadcrumbs.copy()