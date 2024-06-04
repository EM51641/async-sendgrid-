| | |
| --- | --- |
| Python| ![Python](https://img.shields.io/pypi/pyversions/sendgrid-async) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/sendgrid-async.svg)](https://pypi.org/project/sendgrid-async/) [![PyPI Downloads](https://img.shields.io/pypi/dm/sendgrid-async.svg?label=PyPI%20downloads)](https://pypi.org/project/sendgrid-async/) |
| Meta | [![License - MIT](https://img.shields.io/pypi/l/async_sendgrid.svg)](https://github.com/sensodevices/async_sendgrid/blob/main/LICENSE)|

# Async-Sendgrid

Sendgrid simple asynchronous client based on the httpx libarary.

# Installation

It is possible to install sendgrid-async with pip:

```shell
pip install sendgrid-async
```

# Usage
This is a small script showing how to send an email with async-sendgrid:

First, you need to import the ```SendgridAPI``` from the ```async_sendgrid``` package. Then, you need to create a ```SendgridAPI``` object with your API key.

```python
from async_sendgrid import SendgridAPI
import os

API_KEY = os.environ.get('API_KEY')
sendgrid = SendgridAPI(API_KEY)
```

Thereafter, you can create an email with the original ```sendgrid``` package such:

```python
from sendgrid.helpers.mail import Content, Email, Mail, To

from_email = Email("test@example.com")
to_email = To("test@example.com")
subject = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
content = Content("text/plain", "Sed varius ligula ac urna vehicula ultrices. Nunc ut dolor sem.")

mail = Mail(
    from_email=from_email,
    to_email=to_email,
    subject=subject,
    content=content
    )

```

Finally you can send the email with the ```send``` method of the ```SendgridAPI``` instance:

```python
async with sendgrid as client:
    response = await client.send(data)
```
