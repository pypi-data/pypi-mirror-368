import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from chainsaws.aws.ses._ses_internal import SES
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
    ListTemplatesResponse,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)


class SESAPI:
    """High-level SES API."""

    def __init__(self, config: SESAPIConfig | None = None) -> None:
        """Initialize SES API.

        Args:
            config: Optional API configuration

        Example:
            ```python
            ses = SESAPI(
                config=SESAPIConfig(
                    region="ap-northeast-2",
                    default_sender=EmailAddress(
                        email="noreply@example.com",
                        name="My Service"
                    )
                )
            )
            ```

        """
        self.config = config or SESAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.ses = SES(self.boto3_session, config=self.config)

    def send_email(
        self,
        recipients: str | list[str] | EmailAddress | list[EmailAddress],
        subject: str,
        body: str,
        email_format: EmailFormat | None = None,
        sender: str | EmailAddress | None = None,
        cc: list[str] | list[EmailAddress] | None = None,
        bcc: list[str] | list[EmailAddress] | None = None,
        reply_to: list[str] | list[EmailAddress] | None = None,
        priority: EmailPriority = EmailPriority.NORMAL,
        tags: dict[str, str] | None = None,
    ) -> SendEmailResponse:
        """Send email.

        Args:
            recipients: Recipient email address(es)
            subject: Email subject
            body: Email body content
            email_format: Optional content format
            sender: Optional sender address
            cc: Optional CC addresses
            bcc: Optional BCC addresses
            reply_to: Optional reply-to addresses
            priority: Email priority
            tags: Optional email tags

        Returns:
            SendEmailResponse including message ID

        Example:
            ```python
            result = ses.send_email(
                recipients=["user@example.com"],
                subject="Welcome!",
                body="<h1>Welcome to our service!</h1>",
                email_format=EmailFormat.HTML,
                tags={"category": "welcome"}
            )
            print(f"Message ID: {result['MessageId']}")
            ```

        """
        # Convert string addresses to EmailAddress objects
        def to_email_addresses(
            addresses: str | list[str] | EmailAddress | list[EmailAddress] | None,
        ) -> list[EmailAddress] | None:
            if not addresses:
                return None
            if isinstance(addresses, str | EmailAddress):
                addresses = [addresses]
            return [
                addr if isinstance(addr, EmailAddress)
                else EmailAddress(email=addr)
                for addr in addresses
            ]

        # Prepare email content
        email_format = email_format or self.config.default_format
        content: EmailContent = {
            "subject": subject,
            "body_html": body if email_format in [
                EmailFormat.HTML, EmailFormat.BOTH
            ]
            else None,
            "body_text": body if email_format in [
                EmailFormat.TEXT, EmailFormat.BOTH
            ]
            else None,
            "charset": "UTF-8",
        }

        # Prepare configuration
        config: SendEmailConfig = {
            "sender": (
                sender
                if isinstance(sender, EmailAddress)
                else EmailAddress(email=sender)
                if sender
                else self.config.default_sender
            ),
            "recipients": to_email_addresses(recipients) or [],
            "cc": to_email_addresses(cc),
            "bcc": to_email_addresses(bcc),
            "reply_to": to_email_addresses(reply_to),
            "content": content,
            "priority": priority,
            "tags": tags or {},
        }

        return self.ses.send_email(config)

    def create_template(
        self,
        name: str,
        subject: str,
        text_content: str | None = None,
        html_content: str | None = None,
    ) -> None:
        """Create email template.

        Args:
            name: Template name
            subject: Template subject
            text_content: Optional text version
            html_content: Optional HTML version

        Example:
            ```python
            ses.create_template(
                name="welcome_template",
                subject="Welcome {{name}}!",
                html_content="<h1>Welcome {{name}}!</h1>"
            )
            ```

        """
        content = TemplateContent(
            subject=subject,
            text=text_content,
            html=html_content,
        )
        self.ses.create_template(name, content)

    def send_template(
        self,
        template_name: str,
        recipients: str | list[str] | EmailAddress | list[EmailAddress],
        template_data: dict[str, Any],
        sender: str | EmailAddress | None = None,
        cc: list[str] | list[EmailAddress] | None = None,
        bcc: list[str] | list[EmailAddress] | None = None,
        tags: dict[str, str] | None = None,
    ) -> SendTemplatedEmailResponse:
        """Send templated email.

        Args:
            template_name: Name of template to use
            recipients: Recipient email address(es)
            template_data: Template variables
            sender: Optional sender address
            cc: Optional CC addresses
            bcc: Optional BCC addresses
            tags: Optional email tags

        Returns:
            SendTemplatedEmailResponse including message ID

        Example:
            ```python
            result = ses.send_template(
                template_name="welcome_template",
                recipients=["user@example.com"],
                template_data={"name": "John Doe"},
                tags={"category": "welcome"}
            )
            ```

        """
        # Convert addresses
        def to_email_addresses(
            addresses: str | list[str] | EmailAddress | list[EmailAddress] | None,
        ) -> list[EmailAddress] | None:
            if not addresses:
                return None
            if isinstance(addresses, str | EmailAddress):
                addresses = [addresses]
            return [
                addr if isinstance(addr, EmailAddress)
                else EmailAddress(email=addr)
                for addr in addresses
            ]

        config: SendTemplateConfig = {
            "template_name": template_name,
            "sender": (
                sender
                if isinstance(sender, EmailAddress)
                else EmailAddress(email=sender)
                if sender
                else self.config.default_sender
            ),
            "recipients": to_email_addresses(recipients) or [],
            "template_data": template_data,
            "cc": to_email_addresses(cc),
            "bcc": to_email_addresses(bcc),
            "tags": tags or {},
        }

        return self.ses.send_templated_email(config)

    def get_quota(self) -> EmailQuota:
        """Get sending quota information.

        Returns:
            EmailQuota object containing quota details

        Example:
            ```python
            quota = ses.get_quota()
            print(f"Sent in last 24h: {quota.sent_last_24_hours}")
            ```

        """
        quota = self.ses.get_send_quota()
        return {
            "max_24_hour_send": int(quota["Max24HourSend"]),
            "max_send_rate": float(quota["MaxSendRate"]),
            "sent_last_24_hours": int(quota["SentLast24Hours"]),
        }

    def verify_email(self, email: str) -> None:
        """Verify email identity.

        Args:
            email: Email address to verify

        Example:
            ```python
            ses.verify_email("sender@example.com")
            ```

        """
        self.ses.verify_email_identity(email)

    def list_verified_emails(self) -> list[str]:
        """List verified email identities.

        Returns:
            List of verified email addresses

        Example:
            ```python
            emails = ses.list_verified_emails()
            for email in emails:
                print(f"Verified: {email}")
            ```

        """
        return self.ses.list_identities()

    def list_templates(self) -> ListTemplatesResponse:
        """List email templates.

        Returns:
            ListTemplatesResponse containing template metadata

        Example:
            ```python
            templates = ses.list_templates()
            for template in templates:
                print(f"Template: {template['Name']}")
            ```

        """
        return self.ses.list_templates()

    def delete_template(self, name: str) -> None:
        """Delete email template.

        Args:
            name: Template name to delete

        Example:
            ```python
            ses.delete_template("welcome_template")
            ```

        """
        self.ses.delete_template(name)

    def send_bulk_emails(
        self,
        recipients: list[str | dict[str, Any] | BulkEmailRecipient],
        subject: str | None = None,
        body: str | None = None,
        template_name: str | None = None,
        email_format: EmailFormat | None = None,
        sender: str | EmailAddress | None = None,
        batch_size: int = 50,
        max_workers: int | None = None,
    ) -> list[dict[str, Any]]:
        """Send bulk emails using template or direct content with parallel processing."""
        # Convert to BulkEmailConfig
        sender_address = (
            sender if isinstance(sender, EmailAddress)
            else EmailAddress(email=sender) if sender
            else self.config.default_sender
        )

        # Convert recipients to BulkEmailRecipient objects
        bulk_recipients: list[BulkEmailRecipient] = []
        for recipient in recipients:
            if isinstance(recipient, BulkEmailRecipient):
                bulk_recipients.append(recipient)
            elif isinstance(recipient, dict):
                bulk_recipients.append(
                    {
                        "email": EmailAddress(email=recipient["email"]),
                        "template_data": recipient.get("template_data", {}),
                        "tags": recipient.get("tags", {}),
                    }
                )
            else:
                bulk_recipients.append({"email": EmailAddress(email=str(recipient))})

        # Create content if not using template
        content = None
        if not template_name and (subject or body):
            content = {
                "subject": subject,
                "body_text": body if email_format in [
                    EmailFormat.TEXT,
                    EmailFormat.BOTH,
                ]
                else None,
                "body_html": body if email_format in [
                    EmailFormat.HTML,
                    EmailFormat.BOTH,
                ]
                else None,
                "charset": "UTF-8",
            }

        config: BulkEmailConfig = {
            "sender": sender_address,
            "recipients": bulk_recipients,
            "template_name": template_name,
            "content": content,
            "batch_size": batch_size,
            "max_workers": max_workers,
            "email_format": email_format or self.config.default_format,
        }

        return self._send_bulk_emails(config)

    def _send_bulk_emails(self, config: BulkEmailConfig) -> list[dict[str, Any]]:
        """Internal method to send bulk emails using configuration."""
        results = []

        def send_template_email(recipient: BulkEmailRecipient) -> dict[str, Any]:
            try:
                result = self.send_template(
                    template_name=config.get("template_name"),
                    recipients=recipient["email"],
                    template_data=recipient.get("template_data", {}),
                    sender=config["sender"],
                    tags=recipient.get("tags", {}),
                )
                return {
                    "email": str(recipient["email"]),
                    "status": "success",
                    "message_id": result.get("MessageId"),
                    "error": None,
                }
            except Exception as e:
                return {
                    "email": str(recipient["email"]),
                    "status": "error",
                    "message_id": None,
                    "error": str(e),
                }

        def send_direct_email(recipient: BulkEmailRecipient) -> dict[str, Any]:
            try:
                result = self.send_email(
                    recipients=recipient["email"],
                    subject=config["content"]["subject"],
                    body=config["content"].get("body_html")
                    or config["content"].get("body_text"),
                    email_format=config.get("email_format"),
                    sender=config["sender"],
                    tags=recipient.get("tags", {}),
                )
                return {
                    "email": str(recipient["email"]),
                    "status": "success",
                    "message_id": result.get("MessageId"),
                    "error": None,
                }
            except Exception as e:
                return {
                    "email": str(recipient["email"]),
                    "status": "error",
                    "message_id": None,
                    "error": str(e),
                }

        for i in range(0, len(config.recipients), config.batch_size):
            batch = config.recipients[i:i + config.batch_size]
            workers = min(config.max_workers or 16, len(batch))

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = []
                for recipient in batch:
                    if config.template_name:
                        future = executor.submit(
                            send_template_email, recipient)
                    else:
                        future = executor.submit(send_direct_email, recipient)
                    futures.append(future)

                for future in as_completed(futures):
                    results.append(future.result())

        return results
