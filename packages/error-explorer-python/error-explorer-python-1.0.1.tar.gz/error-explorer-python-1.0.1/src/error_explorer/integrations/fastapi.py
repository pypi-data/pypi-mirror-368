"""FastAPI integration for Error Explorer Python SDK."""

import logging
from typing import Awaitable, Callable, Optional

try:
    from fastapi import FastAPI, Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.base import RequestResponseEndpoint
except ImportError:
    FastAPI = None
    Request = None
    Response = None
    BaseHTTPMiddleware = None
    RequestResponseEndpoint = None

from ..client import ErrorExplorer


class ErrorExplorerMiddleware(BaseHTTPMiddleware if BaseHTTPMiddleware else object):
    """FastAPI middleware for Error Explorer."""
    
    def __init__(self, app, client: Optional[ErrorExplorer] = None):
        """Initialize middleware.
        
        Args:
            app: FastAPI application instance
            client: Error Explorer client instance
        """
        if BaseHTTPMiddleware:
            super().__init__(app)
        self.client = client
        if not self.client:
            from .. import get_client
            self.client = get_client()
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and response.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint
            
        Returns:
            FastAPI response object
        """
        if not self.client:
            return await call_next(request)
        
        # Add request breadcrumb
        self.client.add_breadcrumb(
            f"{request.method} {request.url.path}",
            category="http",
            level="info",
            data={
                "method": request.method,
                "path": request.url.path,
                "query_string": str(request.url.query) if request.url.query else ''
            }
        )
        
        # Set user context if available
        if hasattr(request.state, 'user') and request.state.user:
            user_data = {}
            if hasattr(request.state.user, 'id'):
                user_data['id'] = request.state.user.id
            if hasattr(request.state.user, 'email'):
                user_data['email'] = request.state.user.email
            if hasattr(request.state.user, 'username'):
                user_data['username'] = request.state.user.username
            
            if user_data:
                self.client.set_user(user_data)
        
        try:
            response = await call_next(request)
            
            # Add response breadcrumb
            self.client.add_breadcrumb(
                f"{request.method} {request.url.path} → {response.status_code}",
                category="http",
                level="error" if response.status_code >= 400 else "info",
                data={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code
                }
            )
            
            # Capture 4xx and 5xx responses as errors
            if response.status_code >= 400:
                error_message = f"HTTP {response.status_code}: {request.method} {request.url.path}"
                self.client.capture_message(
                    error_message,
                    level="error",
                    context={
                        "http_status": response.status_code,
                        "request_method": request.method,
                        "request_path": request.url.path
                    }
                )
            
            return response
            
        except Exception as exception:
            # Capture exception
            context = {
                "endpoint": request.url.path,
                "method": request.method
            }
            
            # Get path params if available
            if hasattr(request, 'path_params') and request.path_params:
                context['path_params'] = dict(request.path_params)
            
            self.client.capture_exception(exception, context=context, request=request)
            raise


class FastAPIIntegration:
    """FastAPI integration for Error Explorer."""
    
    def __init__(self, app: Optional[FastAPI] = None, client: Optional[ErrorExplorer] = None):
        """Initialize FastAPI integration.
        
        Args:
            app: FastAPI application instance
            client: Error Explorer client instance
        """
        self.client = client
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: FastAPI) -> None:
        """Initialize FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        if not self.client:
            from .. import get_client
            self.client = get_client()
        
        # Add middleware
        app.add_middleware(ErrorExplorerMiddleware, client=self.client)
        
        # Add exception handler
        @app.exception_handler(Exception)
        async def error_explorer_exception_handler(request: Request, exc: Exception):
            """Global exception handler.
            
            Args:
                request: FastAPI request object
                exc: Exception that occurred
                
            Returns:
                None to let FastAPI handle the exception normally
            """
            if self.client:
                context = {
                    "endpoint": request.url.path,
                    "method": request.method
                }
                
                if hasattr(request, 'path_params') and request.path_params:
                    context['path_params'] = dict(request.path_params)
                
                self.client.capture_exception(exc, context=context, request=request)
            
            # Re-raise to let FastAPI handle it
            raise exc


def setup_error_explorer(app: FastAPI, client: Optional[ErrorExplorer] = None) -> FastAPI:
    """Set up Error Explorer for a FastAPI app.
    
    Args:
        app: FastAPI application instance
        client: Error Explorer client instance
        
    Returns:
        FastAPI application instance
    """
    FastAPIIntegration(app, client)
    return app


# Logging handler
class FastAPIErrorExplorerHandler(logging.Handler):
    """FastAPI-specific logging handler for Error Explorer."""
    
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
        
        context = {
            "logger": record.name,
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            # Handle exception
            exception = record.exc_info[1]
            if exception:
                self.client.capture_exception(exception, context=context)
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
                context=context
            )