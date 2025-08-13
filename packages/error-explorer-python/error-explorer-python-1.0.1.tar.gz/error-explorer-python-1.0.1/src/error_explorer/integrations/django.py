"""Django integration for Error Explorer Python SDK."""

import logging
from typing import Any, Dict, Optional

try:
    from django.conf import settings
    from django.core.signals import got_request_exception
    from django.http import HttpRequest, HttpResponse
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    settings = None
    got_request_exception = None
    HttpRequest = None
    HttpResponse = None
    MiddlewareMixin = object

from ..client import ErrorExplorer


class DjangoIntegration:
    """Django integration for Error Explorer."""
    
    def __init__(self, client: ErrorExplorer):
        """Initialize Django integration.
        
        Args:
            client: Error Explorer client instance
        """
        self.client = client
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Set up Django signal handlers."""
        if got_request_exception:
            got_request_exception.connect(self._handle_exception)
    
    def _handle_exception(self, sender: Any, request: HttpRequest, **kwargs) -> None:
        """Handle Django exceptions.
        
        Args:
            sender: Signal sender
            request: Django request object
            **kwargs: Additional signal data
        """
        import sys
        exc_info = sys.exc_info()
        if exc_info[1]:
            self.client.capture_exception(exc_info[1], request=request)


class ErrorExplorerMiddleware(MiddlewareMixin):
    """Django middleware for Error Explorer."""
    
    def __init__(self, get_response=None):
        """Initialize middleware.
        
        Args:
            get_response: Django get_response callable
        """
        super().__init__(get_response)
        self.client: Optional[ErrorExplorer] = None
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Set up Error Explorer client from Django settings."""
        if not settings:
            return
        
        error_explorer_config = getattr(settings, 'ERROR_EXPLORER', {})
        
        if not error_explorer_config.get('WEBHOOK_URL'):
            return
        
        from .. import get_client
        self.client = get_client()
        
        if not self.client:
            # Initialize if not already done
            from .. import init
            self.client = init(
                webhook_url=error_explorer_config['WEBHOOK_URL'],
                project_name=error_explorer_config.get('PROJECT_NAME', 'django-app'),
                environment=error_explorer_config.get('ENVIRONMENT', 'production'),
                **{k.lower(): v for k, v in error_explorer_config.items() 
                   if k not in ['WEBHOOK_URL', 'PROJECT_NAME', 'ENVIRONMENT']}
            )
    
    def process_request(self, request: HttpRequest) -> None:
        """Process incoming request.
        
        Args:
            request: Django request object
        """
        if not self.client:
            return
        
        # Add request breadcrumb
        self.client.add_breadcrumb(
            f"{request.method} {request.path}",
            category="http",
            level="info",
            data={
                "method": request.method,
                "path": request.path,
                "query_string": request.META.get('QUERY_STRING', '')
            }
        )
        
        # Set user context if available
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.client.set_user({
                "id": request.user.pk,
                "email": getattr(request.user, 'email', ''),
                "username": getattr(request.user, 'username', '')
            })
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response.
        
        Args:
            request: Django request object
            response: Django response object
            
        Returns:
            Django response object
        """
        if not self.client:
            return response
        
        # Add response breadcrumb
        self.client.add_breadcrumb(
            f"{request.method} {request.path} → {response.status_code}",
            category="http",
            level="error" if response.status_code >= 400 else "info",
            data={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code
            }
        )
        
        # Capture 4xx and 5xx responses as errors
        if response.status_code >= 400:
            error_message = f"HTTP {response.status_code}: {request.method} {request.path}"
            self.client.capture_message(
                error_message,
                level="error",
                context={
                    "http_status": response.status_code,
                    "request_method": request.method,
                    "request_path": request.path
                }
            )
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Process exception.
        
        Args:
            request: Django request object
            exception: Exception that occurred
        """
        if not self.client:
            return
        
        context = {
            "view": getattr(request.resolver_match, 'view_name', None) if hasattr(request, 'resolver_match') else None,
            "url_name": getattr(request.resolver_match, 'url_name', None) if hasattr(request, 'resolver_match') else None
        }
        
        self.client.capture_exception(exception, context=context, request=request)


# Django app configuration
if settings:
    class ErrorExplorerConfig:
        """Django app config for Error Explorer."""
        name = "error_explorer.django"
        verbose_name = "Error Explorer"
        
        def ready(self):
            """App ready hook."""
            from .. import get_client
            client = get_client()
            if client:
                DjangoIntegration(client)


# Logging handler
class ErrorExplorerHandler(logging.Handler):
    """Logging handler for Error Explorer."""
    
    def __init__(self, client: Optional[ErrorExplorer] = None):
        """Initialize handler.
        
        Args:
            client: Error Explorer client instance
        """
        super().__init__()
        self.client = client
        if not self.client:
            from .. import get_client
            self.client = get_client()
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record.
        
        Args:
            record: Log record to emit
        """
        if not self.client:
            return
        
        if record.exc_info:
            # Handle exception
            exception = record.exc_info[1]
            if exception:
                self.client.capture_exception(
                    exception,
                    context={
                        "logger": record.name,
                        "level": record.levelname,
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno
                    }
                )
        else:
            # Handle message
            level_map = {
                logging.DEBUG: "debug",
                logging.INFO: "info",
                logging.WARNING: "warning",
                logging.ERROR: "error",
                logging.CRITICAL: "error"
            }
            
            self.client.capture_message(
                record.getMessage(),
                level=level_map.get(record.levelno, "info"),
                context={
                    "logger": record.name,
                    "level": record.levelname,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
            )