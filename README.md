# Async-Sendgrid

[![Python](https://img.shields.io/pypi/pyversions/sendgrid-async)](https://pypi.org/project/sendgrid-async/)
[![PyPI Latest Release](https://img.shields.io/pypi/v/sendgrid-async.svg)](https://pypi.org/project/sendgrid-async/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/sendgrid-async.svg?label=PyPI%20downloads)](https://pypi.org/project/sendgrid-async/)
[![License - MIT](https://img.shields.io/pypi/l/async_sendgrid.svg)](https://github.com/sensodevices/async_sendgrid/blob/main/LICENSE)

A modern, asynchronous SendGrid client built on top of `httpx`. This library provides a simple and efficient way to send emails using SendGrid's API with Python's async/await syntax.

## Features

- 🚀 Asynchronous email sending using `httpx`
- 🔒 Type-safe with comprehensive type hints
- ⚡️ Efficient connection pooling and session management
- 🛠️ Compatible with SendGrid's official Python library
- 📦 Easy installation and simple API

## Requirements

- Python 3.10 or higher
- SendGrid API key

## Installation

Install the package using pip:

```bash
pip install sendgrid-async
```

Or using Poetry:

```bash
poetry add sendgrid-async
```

## Quick Start

Here's a simple example of how to send an email:

```python
import os
from async_sendgrid import SendgridAPI
from sendgrid.helpers.mail import Content, Email, Mail, To

# Initialize the client
api_key = os.environ.get('SENDGRID_API_KEY')
sendgrid = SendgridAPI(api_key)

# Create email content
from_email = Email("sender@example.com")
to_email = To("recipient@example.com")
subject = "Hello from Async-Sendgrid!"
content = Content("text/plain", "This is a test email sent using Async-Sendgrid.")

# Create mail object
mail = Mail(from_email, to_email, subject, content)

# Send the email
async with sendgrid as client:
    response = await client.send(mail)
```

## Advanced Usage

### Custom Endpoint

For testing or development purposes, you can specify a custom endpoint:

```python
sendgrid = SendgridAPI(
    api_key="YOUR_API_KEY",
    endpoint="https://localhost:3000/v3/mail/send"
)
```

### Error Handling

The library provides proper error handling for API responses:

```python
from async_sendgrid.exceptions import SendgridError

try:
    async with sendgrid as client:
        response = await client.send(mail)
except SendgridError as e:
    print(f"Failed to send email: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.