# Async SendGrid

[![Python](https://img.shields.io/pypi/pyversions/sendgrid-async)](https://pypi.org/project/sendgrid-async/)
[![PyPI Latest Release](https://img.shields.io/pypi/v/sendgrid-async.svg)](https://pypi.org/project/sendgrid-async/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/sendgrid-async.svg?label=PyPI%20downloads)](https://pypi.org/project/sendgrid-async/)
[![License - MIT](https://img.shields.io/pypi/l/async_sendgrid.svg)](https://github.com/sensodevices/async_sendgrid/blob/main/LICENSE)

A modern, asynchronous SendGrid client built on top of `httpx`. This library provides a simple and efficient way to send emails using SendGrid's API with Python's async/await syntax.

## Features

- 🚀 Asynchronous API client for SendGrid
- 🔄 Connection pooling for better performance
- 📊 OpenTelemetry integration for monitoring
- 🔍 Detailed error tracking and tracing
- 🛠️ Customizable configuration
- 📝 Comprehensive documentation

## Installation

Install the package using pip:

```bash
pip install sendgrid-async
```

## Quick Start

```python
from async_sendgrid import SendgridAPI
from sendgrid.helpers.mail import Mail

# Initialize the client
sendgrid = SendgridAPI(api_key="YOUR_API_KEY")

# Create and send an email
email = Mail(
    from_email="from@example.com",
    to_emails="to@example.com",
    subject="Hello World",
    plain_text_content="Hello World!",
)

response = await sendgrid.send(email)
```

## Advanced Features

### Connection Pooling

Optimize performance with connection pooling:

```python
from async_sendgrid import SendgridAPI
from async_sendgrid.pool import ConnectionPool

pool = ConnectionPool(
    max_connections=20,
    max_keepalive_connections=10,
    keepalive_expiry=10.0,
)

sendgrid = SendgridAPI(
    api_key="YOUR_API_KEY",
    pool=pool,
)
```

### Retry Configuration

By default, requests are automatically retried up to 5 times with exponential backoff and jitter on transient failures (429 Too Many Requests, 5xx server errors, and timeouts).

The delay between retries is calculated as:

```
delay = backoff_factor * (2 ** attempt) * random(0, 1)
```

With the default `backoff_factor=0.5`, this gives approximate max delays of 0.5s, 1s, 2s, 4s, 8s across retries. The random jitter prevents thundering herd problems when multiple requests retry simultaneously.

Customize the retry behavior through the connection pool:

```python
from async_sendgrid import SendgridAPI
from async_sendgrid.pool import ConnectionPool

pool = ConnectionPool(
    total=3,            # Maximum retry attempts (default: 5)
    backoff_factor=1.0, # Backoff multiplier in seconds (default: 0.5)
)

sendgrid = SendgridAPI(
    api_key="YOUR_API_KEY",
    pool=pool,
)
```

To disable retries entirely, set `total=0`:

```python
pool = ConnectionPool(total=0)
```

### Send emails on behalf of another user

Send emails on behalf of subusers:

```python
sendgrid = SendgridAPI(
    api_key="YOUR_API_KEY",
    on_behalf_of="John Smith",
)
```

### Custom Endpoints

Use custom API endpoints:

```python
sendgrid = SendgridAPI(
    api_key="YOUR_API_KEY",
    endpoint="https://custom.endpoint.com/v3/mail/send",
)
```

## Telemetry Integration

Monitor and trace your SendGrid operations with OpenTelemetry:

### Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure OpenTelemetry
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Add your exporter
otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
```

### Available Metrics

The library automatically tracks:

#### HTTP Metrics
- Status codes
- Response sizes
- URLs
- Methods

#### SendGrid Metrics
- Number of recipients
- Attachment presence
- Email content type

### Configuration

Control telemetry behavior with environment variables:

```bash
# Disable telemetry
SENDGRID_TELEMETRY_IS_ENABLED=false

# Custom span name
SENDGRID_TELEMETRY_SPAN_NAME=custom.span.name
```

## Error Handling

Robust error handling for API operations:

```python
try:
    response = await sendgrid.send(email)
except Exception as e:
    # Handle the error
    print(f"Error sending email: {e}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/async-sendgrid.git
cd async-sendgrid

# Install development dependencies
pip install -e ".[test]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=async_sendgrid
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.