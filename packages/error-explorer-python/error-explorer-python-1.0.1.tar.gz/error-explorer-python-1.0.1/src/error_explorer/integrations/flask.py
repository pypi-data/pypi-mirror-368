"""Flask integration for Error Explorer Python SDK."""

import logging
from functools import wraps
from typing import Any, Callable, Optional

try:
    from flask import Flask, request, g, has_request_context
    from werkzeug.exceptions import HTTPException
except ImportError:
    Flask = None
    request = None
    g = None
    has_request_context = None
    HTTPException = None

from ..client import ErrorExplorer


class FlaskIntegration:
    """Flask integration for Error Explorer."""
    
    def __init__(self, app: Optional[Flask] = None, client: Optional[ErrorExplorer] = None):
        """Initialize Flask integration.
        
        Args:
            app: Flask application instance
            client: Error Explorer client instance
        """
        self.client = client
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize Flask application.
        
        Args:
            app: Flask application instance
        """
        if not self.client:
            from .. import get_client
            self.client = get_client()
        
        if not self.client:
            # Initialize from Flask config
            config = app.config.get('ERROR_EXPLORER', {})
            if config.get('WEBHOOK_URL'):
                from .. import init
                self.client = init(
                    webhook_url=config['WEBHOOK_URL'],
                    project_name=config.get('PROJECT_NAME', app.name),
                    environment=config.get('ENVIRONMENT', 'production'),
                    **{k.lower(): v for k, v in config.items() 
                       if k not in ['WEBHOOK_URL', 'PROJECT_NAME', 'ENVIRONMENT']}
                )
        
        if not self.client:
            return
        
        # Set up error handlers
        app.errorhandler(Exception)(self._handle_exception)
        
        # Set up request hooks
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Store client reference in app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['error_explorer'] = self
    
    def _before_request(self) -> None:
        """Handle before request."""
        if not self.client or not has_request_context():
            return
        
        # Add request breadcrumb
        self.client.add_breadcrumb(
            f"{request.method} {request.path}",
            category="http",
            level="info",
            data={
                "method": request.method,
                "path": request.path,
                "query_string": request.query_string.decode('utf-8') if request.query_string else ''
            }
        )
        
        # Set user context if available (assuming user is stored in g)
        if hasattr(g, 'user') and g.user:
            user_data = {}
            if hasattr(g.user, 'id'):
                user_data['id'] = g.user.id
            if hasattr(g.user, 'email'):
                user_data['email'] = g.user.email
            if hasattr(g.user, 'username'):
                user_data['username'] = g.user.username
            
            if user_data:
                self.client.set_user(user_data)
    
    def _after_request(self, response) -> Any:
        """Handle after request.
        
        Args:
            response: Flask response object
            
        Returns:
            Flask response object
        """
        if not self.client or not has_request_context():
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
    
    def _handle_exception(self, exception: Exception) -> Any:
        """Handle exceptions.
        
        Args:
            exception: Exception that occurred
            
        Returns:
            None to let Flask handle the exception normally
        """
        if not self.client:
            return None
        
        # Skip HTTP exceptions (they're handled by after_request)
        if HTTPException and isinstance(exception, HTTPException):
            return None
        
        context = {}
        if has_request_context():
            # Get view function info
            endpoint = request.endpoint
            if endpoint:
                context['endpoint'] = endpoint
            
            # Get view args
            if request.view_args:
                context['view_args'] = request.view_args
        
        self.client.capture_exception(
            exception, 
            context=context, 
            request=request if has_request_context() else None
        )
        
        # Let Flask handle the exception normally
        return None


def capture_exceptions(app: Flask, client: Optional[ErrorExplorer] = None) -> Flask:
    """Decorator to set up Error Explorer for a Flask app.
    
    Args:
        app: Flask application instance
        client: Error Explorer client instance
        
    Returns:
        Flask application instance
    """
    FlaskIntegration(app, client)
    return app


def capture_exception_route(func: Callable) -> Callable:
    """Decorator to capture exceptions in Flask routes.
    
    Args:
        func: Route function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from .. import get_client
            client = get_client()
            if client:
                context = {
                    "route_function": func.__name__,
                    "route_args": args,
                    "route_kwargs": kwargs
                }
                client.capture_exception(
                    e,
                    context=context,
                    request=request if has_request_context() else None
                )
            raise
    return wrapper


# Logging handler
class FlaskErrorExplorerHandler(logging.Handler):
    """Flask-specific logging handler for Error Explorer."""
    
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
        
        # Add Flask request context if available
        if has_request_context():
            context.update({
                "request_method": request.method,
                "request_path": request.path,
                "request_endpoint": request.endpoint
            })
        
        if record.exc_info:
            # Handle exception
            exception = record.exc_info[1]
            if exception:
                self.client.capture_exception(
                    exception,
                    context=context,
                    request=request if has_request_context() else None
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
                context=context
            )