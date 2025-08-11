# Django Async Logger

A reusable Django app that provides asynchronous logging functionality using a separate thread to avoid blocking the main application.

## Features

- **Asynchronous Logging**: All log operations run in a separate thread
- **Thread-Safe**: Uses a queue system for thread-safe logging
- **Rich Metadata**: Captures module, function, line number, user ID, request ID, and extra data
- **Admin Interface**: Django admin interface for viewing and managing logs
- **API Endpoints**: REST API for external logging
- **Middleware**: Automatic request logging with unique request IDs
- **Decorators**: Utility decorators for function logging and performance monitoring
- **Context Managers**: Easy-to-use context managers for operation logging
- **Configurable**: Customizable queue size, flush intervals, and cleanup policies
- **Extendible**: Easily add your own custom handlers to process logs in different ways.

  **Useful built-in and example handlers include:**
  - **Console Handler**: Output logs to the console
  - You can implement your own handler by subclassing the provided base handler class.

## Installation

1. Add the app to your Django project:
```python
INSTALLED_APPS = [
    # ...
    'logq',
]
```

2. Add the middleware to your settings:
```python
MIDDLEWARE = [
    # ...
    'logq.middleware.AsyncLoggingMiddleware',
]
```

3. Run migrations:
```bash
python manage.py makemigrations logq
python manage.py migrate
```

4. (Optional) Configure logging settings:
```python
ASYNC_LOGGING_CONFIG = {
    'MAX_QUEUE_SIZE': 1000,
    'FLUSH_INTERVAL': 1.0,  # seconds
    'AUTO_CLEANUP_INTERVAL': 3600,  # seconds
    'ENABLE_REQUEST_LOGGING': True,
    'IGNORE_PATHS': ['/admin/'],  # paths to ignore for request logging
    'DEFAULT_HANDLERS': [],  # list of handler class paths, e.g. ['logq.handlers.FileHandler'],
    # CLEANUP_POLICIES defines how long to keep logs of each level before automatic deletion.
    # Each policy is a dictionary with:
    #   - "days": Number of days to retain logs at this level
    #   - "level": Log level to which this policy applies (e.g., "INFO", "WARNING", "ERROR")
    #   - "enabled": Whether this cleanup policy is active
    'CLEANUP_POLICIES': [
        {"days": 10, "level": "INFO", "enabled": True},     # Keep INFO logs for 10 days
        {"days": 10, "level": "WARNING", "enabled": True},  # Keep WARNING logs for 10 days
        {"days": 15, "level": "ERROR", "enabled": True},    # Keep ERROR logs for 15 days
    ]
}
```

## Usage

### Basic Logging

```python
from logq.async_logger import get_async_logger

logger = get_async_logger()

# Different log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# With extra data
logger.info("User action", extra_data={'action': 'login', 'ip': '192.168.1.1'})

# Log exceptions
try:
    # some code that might fail
    pass
except Exception as e:
    logger.exception("An error occurred", exc_info=str(e))
```

### Function Decorators

```python
from logq.utils import log_function_call, log_performance

@log_function_call
def my_function():
    return "result"

@log_function_call(level='DEBUG')
def debug_function():
    return "debug result"

@log_performance(threshold_seconds=0.5)
def slow_function():
    time.sleep(1)
    return "slow result"
```

### Context Managers

```python
from logq.utils import LogContext

with LogContext("Processing data", level='INFO'):
    # do some work
    time.sleep(0.1)
    # automatically logs start and completion with timing
```

### API Logging

```python
import requests
import json

# Log via API
data = {
    'level': 'INFO',
    'message': 'External log message',
    'extra_data': {'source': 'external_service'}
}

response = requests.post(
    'http://your-domain/logq/api/log/',
    data=json.dumps(data),
    headers={'Content-Type': 'application/json'}
)

# Retrieve logs via API
response = requests.get('http://your-domain/logq/api/logs/?limit=10')
logs = response.json()['logs']
```

### CUSTOM HANDLERS
You can define custom log handlers by subclassing `LogHandler` and passing them to `AsyncLogger` or define them in the `DEFAULT_HANDLERS` section of the config. This allows you to process or forward log entries in any way you need (e.g., send to an external service, write to a file, etc).



### Admin Interface

Access the admin interface at `/admin/` to view and manage logs. Features include:

- Filter by level, module, timestamp, user ID
- Search by message, module, function, request ID


### Management Commands

Clean old logs:
```bash
# Delete logs older than 30 days
python manage.py clean_logs

# Delete logs older than 7 days
python manage.py clean_logs --days 7

# Delete only DEBUG and INFO logs older than 30 days
python manage.py clean_logs --level INFO

# Dry run to see what would be deleted
python manage.py clean_logs --dry-run
```

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_QUEUE_SIZE` | 1000 | Maximum number of log entries in the queue |
| `FLUSH_INTERVAL` | 1.0 | How often to flush logs to database (seconds) |
| `ENABLE_REQUEST_LOGGING` | True | Whether to log all HTTP requests |

## Model Fields

The `LogEntry` model includes:

- `timestamp`: When the log was created
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: The log message
- `module`: Python module where the log originated
- `function`: Function name where the log originated
- `line_number`: Line number where the log originated
- `user_id`: ID of the user (if authenticated)
- `request_id`: Unique request identifier
- `extra_data`: Additional JSON data
- `created_at`: When the entry was saved to database

## Performance Considerations

- The logger runs in a separate thread and won't block your main application
- Log entries are batched and written to the database periodically
- If the queue is full, new entries are dropped (with console fallback)
- Consider setting up database indexes for better query performance
- Use the cleanup command regularly to prevent database bloat

## Thread Safety

The logger is completely thread-safe:
- Uses a thread-safe queue for communication
- Database operations are wrapped in transactions
- Multiple threads can safely call the logger simultaneously

## Customization

You can extend the logger by:

1. Creating custom log levels
2. Adding new fields to the LogEntry model
3. Customizing the admin interface
4. Adding new API endpoints
5. Creating custom middleware

## Troubleshooting

### Logs not appearing
- Check that the async logger thread is running
- Verify database migrations are applied
- Check for any database connection issues

### Performance issues
- Reduce `FLUSH_INTERVAL` for more frequent writes
- Increase `MAX_QUEUE_SIZE` for higher throughput
- Add database indexes for frequently queried fields

### Memory usage
- Reduce `MAX_QUEUE_SIZE` if memory is a concern
- Run cleanup commands more frequently
- Monitor database size and clean old logs

## License

This project is open source and available under the MIT License. 