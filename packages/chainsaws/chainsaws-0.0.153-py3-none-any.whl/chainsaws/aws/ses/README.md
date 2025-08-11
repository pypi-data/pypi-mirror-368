# AWS SES (Simple Email Service) API

A high-level Python interface for AWS Simple Email Service (SES) that provides an easy-to-use API for sending emails, managing templates, and handling bulk email operations.

## Features

- ✉️ Single and bulk email sending
- 📝 Template management
- 🚀 Parallel processing for bulk emails
- 📊 Quota monitoring
- ✅ Email verification
- 🎨 HTML and plain text support
- 🏷️ Email tagging
- 🔒 Type-safe with dataclasses

## Installation

```bash
pip install chainsaws
```

## Quick Start

```python
from chainsaws.aws.ses import SESAPI, EmailAddress, EmailFormat

# Initialize the API
ses = SESAPI()

# Send a simple email
ses.send_email(
    recipients="user@example.com",
    subject="Welcome!",
    body="<h1>Welcome to our service!</h1>",
    format=EmailFormat.HTML
)
```

## Email Sending

### Single Email

```python
# Basic email
ses.send_email(
    recipients=["user@example.com"],
    subject="Hello!",
    body="Welcome to our service!",
    format=EmailFormat.TEXT
)

# HTML email with custom sender
ses.send_email(
    sender=EmailAddress(
        email="noreply@company.com",
        name="Company Name"
    ),
    recipients=["user@example.com"],
    subject="Welcome!",
    body="<h1>Welcome!</h1><p>Thanks for joining.</p>",
    format=EmailFormat.HTML,
    tags={"category": "welcome"}
)

# With CC and BCC
ses.send_email(
    recipients=["primary@example.com"],
    cc=["manager@example.com"],
    bcc=["archive@example.com"],
    subject="Project Update",
    body="Latest project status...",
    reply_to=["support@example.com"]
)
```

### Template Management

```python
# Create template
ses.create_template(
    name="welcome_template",
    subject="Welcome {{name}}!",
    html_content="""
    <h1>Welcome {{name}}!</h1>
    <p>Thanks for choosing {{company}}.</p>
    """
)

# Send templated email
ses.send_template(
    template_name="welcome_template",
    recipients="user@example.com",
    template_data={
        "name": "John Doe",
        "company": "ACME Inc"
    }
)

# List templates
templates = ses.list_templates()
```

### Bulk Email Sending

```python
# Simple bulk send
results = ses.send_bulk_emails(
    recipients=[
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ],
    subject="Important Update",
    body="Service maintenance scheduled...",
    batch_size=100
)

# Templated bulk send with custom data
results = ses.send_bulk_emails(
    recipients=[
        {
            "email": "user1@example.com",
            "template_data": {"name": "User 1", "plan": "Premium"},
            "tags": {"type": "premium"}
        },
        {
            "email": "user2@example.com",
            "template_data": {"name": "User 2", "plan": "Basic"},
            "tags": {"type": "basic"}
        }
    ],
    template_name="welcome_template",
    batch_size=50,
    max_workers=10
)

# Process results
for result in results:
    if result['status'] == 'success':
        print(f"Sent to {result['email']}: {result['message_id']}")
    else:
        print(f"Failed to send to {result['email']}: {result['error']}")
```

### Email Verification

```python
# Verify sender email
ses.verify_email("sender@company.com")

# List verified emails
verified = ses.list_verified_emails()
```

### Quota Management

```python
# Check sending quota
quota = ses.get_quota()
print(f"Sent in last 24h: {quota.sent_last_24_hours}")
print(f"Maximum sends per 24h: {quota.max_24_hour_send}")
print(f"Send rate: {quota.max_send_rate} emails/second")
```

## Advanced Configuration

```python
from chainsaws.aws.ses import SESAPI, SESAPIConfig, EmailAddress

ses = SESAPI(
    config=SESAPIConfig(
        region="ap-northeast-2",
        default_sender=EmailAddress(
            email="noreply@company.com",
            name="Company Name"
        ),
        default_format=EmailFormat.BOTH,
        credentials={
            "aws_access_key_id": "YOUR_ACCESS_KEY",
            "aws_secret_access_key": "YOUR_SECRET_KEY"
        }
    )
)
```

## Best Practices

1. **Batch Processing**: Use `send_bulk_emails` for sending to multiple recipients
2. **Template Usage**: Create reusable templates for consistent emails
3. **Error Handling**: Always check bulk send results for failures
4. **Quota Monitoring**: Monitor your sending quota to avoid limits
5. **Verification**: Verify sender emails before sending
6. **Tags**: Use tags to categorize and track emails

## Error Handling

```python
try:
    ses.send_email(
        recipients="user@example.com",
        subject="Test",
        body="Test message"
    )
except Exception as e:
    logger.error(f"Failed to send email: {str(e)}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
