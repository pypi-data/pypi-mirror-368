"""AWS Simple Email Service (SES) API package.

This package provides a high-level interface for AWS SES operations including
email sending, template management, and bulk operations.

Example:
    ```python
    from chainsaws.aws.ses import SESAPI, EmailFormat, EmailAddress

    # Initialize API
    ses = SESAPI()

    # Send single email
    ses.send_email(
        recipients="user@example.com",
        subject="Welcome!",
        body="<h1>Welcome to our service!</h1>",
        format=EmailFormat.HTML
    )

    # Send bulk emails with template
    ses.send_bulk_emails(
        recipients=[
            {
                "email": "user1@example.com",
                "template_data": {"name": "User 1"}
            },
            {
                "email": "user2@example.com",
                "template_data": {"name": "User 2"}
            }
        ],
        template_name="welcome_template"
    )
    ```

"""

from chainsaws.aws.ses.ses import SESAPI
from chainsaws.aws.ses.ses_models import (
    BulkEmailConfig,
    BulkEmailRecipient,
    EmailAddress,
    EmailContent,
    EmailFormat,
    EmailPriority,
    EmailQuota,
    SendEmailConfig,
    SendTemplateConfig,
    SESAPIConfig,
    TemplateContent,
)
from chainsaws.aws.ses.response import (
    SendEmailResponse,
    SendTemplatedEmailResponse,
    GetSendQuotaResponse,
    TemplateMetadata,
    Template,
    GetTemplateResponse,
    ListTemplatesResponse,
)

__all__ = [
    "SESAPI",
    "BulkEmailConfig",
    "BulkEmailRecipient",
    "EmailAddress",
    "EmailContent",
    "EmailFormat",
    "EmailPriority",
    "EmailQuota",
    "SESAPIConfig",
    "SendEmailConfig",
    "SendTemplateConfig",
    "TemplateContent",
    "SendEmailResponse",
    "SendTemplatedEmailResponse",
    "GetSendQuotaResponse",
    "TemplateMetadata",
    "Template",
    "GetTemplateResponse",
    "ListTemplatesResponse",
]
