# Error Explorer Python SDK

Python SDK for Error Explorer - Capture and report errors automatically from your Python applications.

## Installation

```bash
pip install error-explorer-python
# or
poetry add error-explorer-python
```

## Quick Start

### Basic Setup

```python
import error_explorer

# Initialize Error Explorer
error_explorer.init(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-python-app",
    environment="production"
)

# Capture exceptions
try:
    risky_operation()
except Exception as e:
    error_explorer.capture_exception(e)

# Capture messages
error_explorer.capture_message("Something happened", "info")
```

### Django Integration

1. **Add to installed apps** (`settings.py`):

```python
INSTALLED_APPS = [
    # ... your other apps
    'error_explorer.integrations.django',
]
```

2. **Add middleware** (`settings.py`):

```python
MIDDLEWARE = [
    'error_explorer.integrations.django.ErrorExplorerMiddleware',
    # ... your other middleware
]
```

3. **Configure Error Explorer** (`settings.py`):

```python
ERROR_EXPLORER = {
    'WEBHOOK_URL': 'https://error-explorer.com/webhook/project-token',
    'PROJECT_NAME': 'my-django-app',
    'ENVIRONMENT': 'production',
    'ENABLED': True,
}

# Optional: Add logging handler
LOGGING = {
    'version': 1,
    'handlers': {
        'error_explorer': {
            'class': 'error_explorer.integrations.django.ErrorExplorerHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error_explorer'],
            'level': 'ERROR',
        },
    },
}
```

4. **Initialize in your Django app** (`apps.py` or `__init__.py`):

```python
import error_explorer
from django.conf import settings

if hasattr(settings, 'ERROR_EXPLORER'):
    config = settings.ERROR_EXPLORER
    error_explorer.init(
        webhook_url=config['WEBHOOK_URL'],
        project_name=config['PROJECT_NAME'],
        environment=config.get('ENVIRONMENT', 'production'),
        enabled=config.get('ENABLED', True)
    )
```

### Flask Integration

```python
from flask import Flask
import error_explorer
from error_explorer.integrations.flask import capture_exceptions

app = Flask(__name__)

# Initialize Error Explorer
error_explorer.init(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-flask-app",
    environment="production"
)

# Set up automatic error capture
capture_exceptions(app)

# Or use the integration class
from error_explorer.integrations.flask import FlaskIntegration
FlaskIntegration(app)

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

### FastAPI Integration

```python
from fastapi import FastAPI
import error_explorer
from error_explorer.integrations.fastapi import setup_error_explorer

app = FastAPI()

# Initialize Error Explorer
error_explorer.init(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-fastapi-app",
    environment="production"
)

# Set up automatic error capture
setup_error_explorer(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Configuration

### Required Options

- `webhook_url`: Your Error Explorer webhook URL
- `project_name`: Name of your project

### Optional Options

```python
error_explorer.init(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-python-app",
    environment="production",        # Default: "production"
    enabled=True,                    # Default: True
    user_id="user123",              # Optional: Default user ID
    user_email="user@example.com",  # Optional: Default user email
    max_breadcrumbs=50,              # Default: 50
    timeout=5,                       # Default: 5 seconds
    retries=3,                       # Default: 3
    debug=False,                     # Default: False
    before_send=lambda data: data    # Optional: Filter/modify data
)
```

## API Reference

### error_explorer.init(\*\*config)

Initializes the Error Explorer client.

### error_explorer.capture_exception(exception, context=None)

Captures an exception with optional context.

```python
try:
    risky_operation()
except Exception as e:
    error_explorer.capture_exception(e, {
        "user_id": 123,
        "operation": "risky_operation"
    })
```

### error_explorer.capture_message(message, level="info", context=None)

Captures a custom message.

```python
error_explorer.capture_message("User logged in", "info", {
    "user_id": 123
})
```

### error_explorer.add_breadcrumb(message, category="custom", level="info", data=None)

Adds a breadcrumb for debugging context.

```python
error_explorer.add_breadcrumb("User clicked button", "ui", "info", {
    "button_id": "submit-btn"
})
```

### error_explorer.set_user(user)

Sets user context for all future error reports.

```python
error_explorer.set_user({
    "id": 123,
    "email": "user@example.com",
    "username": "john_doe"
})
```

## Advanced Usage

### Custom Error Context

```python
from error_explorer import ErrorExplorer

client = ErrorExplorer(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-app"
)

# Add breadcrumbs for context
client.add_breadcrumb("User started checkout", "user_action")
client.add_breadcrumb("Payment method selected", "user_action")

try:
    process_payment()
except Exception as e:
    client.capture_exception(e, {
        "payment_method": "credit_card",
        "amount": 99.99,
        "currency": "USD"
    })
```

### Database Query Monitoring

```python
import time

def execute_query(sql, params=None):
    start_time = time.time()
    
    error_explorer.add_breadcrumb(f"Executing query: {sql[:50]}...", "database")
    
    try:
        result = database.execute(sql, params)
        duration = time.time() - start_time
        
        error_explorer.add_breadcrumb(
            f"Query completed in {duration:.3f}s", 
            "database", 
            "info",
            {"duration": duration, "rows": len(result)}
        )
        
        return result
    except Exception as e:
        duration = time.time() - start_time
        error_explorer.capture_exception(e, {
            "query": sql,
            "params": params,
            "duration": duration
        })
        raise
```

### Before Send Hook

```python
def filter_sensitive_data(data):
    """Filter out sensitive information before sending."""
    if data.context and 'password' in data.context:
        data.context['password'] = '[FILTERED]'
    
    # Don't send errors from development environment
    if data.environment == 'development':
        return None
    
    return data

error_explorer.init(
    webhook_url="https://error-explorer.com/webhook/project-token",
    project_name="my-app",
    before_send=filter_sensitive_data
)
```

## CLI Usage

The package includes a CLI tool for testing:

```bash
# Test connection
error-explorer test https://error-explorer.com/webhook/project-token my-project

# Show version
error-explorer version
```

## Environment Variables

You can use environment variables for configuration:

```bash
ERROR_EXPLORER_WEBHOOK_URL=https://error-explorer.com/webhook/project-token
ERROR_EXPLORER_PROJECT_NAME=my-python-app
ERROR_EXPLORER_ENVIRONMENT=production
```

```python
import os
import error_explorer

error_explorer.init(
    webhook_url=os.environ['ERROR_EXPLORER_WEBHOOK_URL'],
    project_name=os.environ['ERROR_EXPLORER_PROJECT_NAME'],
    environment=os.environ.get('ERROR_EXPLORER_ENVIRONMENT', 'production')
)
```

## Framework-Specific Examples

### Django with Custom User Context

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
import error_explorer

class UserContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            error_explorer.set_user({
                "id": request.user.id,
                "email": request.user.email,
                "username": request.user.username,
                "is_staff": request.user.is_staff
            })
```

### Flask with Request Context

```python
from flask import Flask, request, g
import error_explorer

app = Flask(__name__)

@app.before_request
def before_request():
    error_explorer.add_breadcrumb(
        f"{request.method} {request.path}",
        "http"
    )
    
    if hasattr(g, 'user'):
        error_explorer.set_user({
            "id": g.user.id,
            "email": g.user.email
        })
```

## Troubleshooting

### Errors not appearing in dashboard
1. Check that the webhook URL is correct
2. Verify that Error Explorer is running and accessible
3. Enable debug mode: `error_explorer.init(..., debug=True)`
4. Check the console for any Error Explorer related messages

### Performance considerations
1. Error Explorer sends data asynchronously by default
2. Adjust `timeout` and `retries` based on your needs
3. Use `before_send` to filter out unnecessary errors
4. Consider rate limiting in high-traffic applications

## Requirements

- Python 3.7+
- requests
- Optional: Django 3.0+, Flask 1.0+, FastAPI 0.65.0+

## License

MIT