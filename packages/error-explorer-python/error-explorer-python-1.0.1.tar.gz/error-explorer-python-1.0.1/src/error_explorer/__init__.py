"""Error Explorer Python SDK

A comprehensive error monitoring and reporting library for Python applications.
Supports Django, Flask, FastAPI, and standalone Python applications.
"""

from .client import ErrorExplorer
from .breadcrumbs import BreadcrumbManager
from .types import (
    ErrorData,
    RequestData,
    ServerData,
    UserContext,
    Breadcrumb,
    ErrorExplorerConfig,
)

# Global instance
_global_client: ErrorExplorer | None = None


def init(
    webhook_url: str,
    project_name: str,
    environment: str = "production",
    **kwargs
) -> ErrorExplorer:
    """Initialize the global Error Explorer client.
    
    Args:
        webhook_url: The webhook URL for your Error Explorer project
        project_name: Name of your project
        environment: Environment (development, staging, production)
        **kwargs: Additional configuration options
        
    Returns:
        ErrorExplorer: The initialized client instance
    """
    global _global_client
    _global_client = ErrorExplorer(
        webhook_url=webhook_url,
        project_name=project_name,
        environment=environment,
        **kwargs
    )
    return _global_client


def get_client() -> ErrorExplorer | None:
    """Get the global Error Explorer client.
    
    Returns:
        ErrorExplorer | None: The global client instance or None if not initialized
    """
    return _global_client


def capture_exception(exception: Exception, context: dict | None = None) -> None:
    """Capture an exception using the global client.
    
    Args:
        exception: The exception to capture
        context: Additional context data
    """
    if _global_client:
        _global_client.capture_exception(exception, context)
    else:
        raise RuntimeError("Error Explorer not initialized. Call init() first.")


def capture_message(
    message: str, 
    level: str = "info", 
    context: dict | None = None
) -> None:
    """Capture a message using the global client.
    
    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error)
        context: Additional context data
    """
    if _global_client:
        _global_client.capture_message(message, level, context)
    else:
        raise RuntimeError("Error Explorer not initialized. Call init() first.")


def add_breadcrumb(
    message: str,
    category: str = "custom",
    level: str = "info",
    data: dict | None = None
) -> None:
    """Add a breadcrumb using the global client.
    
    Args:
        message: Breadcrumb message
        category: Category of the breadcrumb
        level: Level (debug, info, warning, error)
        data: Additional data
    """
    if _global_client:
        _global_client.add_breadcrumb(message, category, level, data)
    else:
        raise RuntimeError("Error Explorer not initialized. Call init() first.")


def set_user(user: dict) -> None:
    """Set user context using the global client.
    
    Args:
        user: User context data
    """
    if _global_client:
        _global_client.set_user(user)
    else:
        raise RuntimeError("Error Explorer not initialized. Call init() first.")


__version__ = "1.0.0"
__all__ = [
    "ErrorExplorer",
    "BreadcrumbManager",
    "ErrorData",
    "RequestData",
    "ServerData",
    "UserContext",
    "Breadcrumb",
    "ErrorExplorerConfig",
    "init",
    "get_client",
    "capture_exception",
    "capture_message",
    "add_breadcrumb",
    "set_user",
]