import json
import logging

import boto3
from botocore.exceptions import ClientError

from chainsaws.aws.ses.ses_models import (
    SendEmailConfig,
    SendTemplateConfig,
    SESAPIConfig,
    TemplateContent,
)
from chainsaws.aws.ses.response import (
    SendEmailResponse,
    SendTemplatedEmailResponse,
    GetSendQuotaResponse,
    GetTemplateResponse,
    ListTemplatesResponse,
)

logger = logging.getLogger(__name__)


class SESError(Exception):
    """Base exception for SES operations."""


class SES:
    """Internal SES operations."""

    def __init__(
        self,
        boto3_session: boto3.Session,
        config: SESAPIConfig | None = None,
    ) -> None:
        """Initialize SES client."""
        self.config = config or SESAPIConfig()
        self.client = boto3_session.client(
            "ses", region_name=self.config.region)

    def send_email(self, config: SendEmailConfig) -> SendEmailResponse:
        """Send email."""
        try:
            params = {
                "Source": str(config["sender"]),
                "Destination": {
                    "ToAddresses": [str(r) for r in config["recipients"]],
                },
                "Message": {
                    "Subject": {
                        "Data": config["content"]["subject"],
                        "Charset": config["content"].get("charset", "UTF-8"),
                    },
                },
            }

            # Add message body
            message_body = {}
            if config["content"].get("body_text"):
                message_body["Text"] = {
                    "Data": config["content"]["body_text"],
                    "Charset": config["content"].get("charset", "UTF-8"),
                }
            if config["content"].get("body_html"):
                message_body["Html"] = {
                    "Data": config["content"]["body_html"],
                    "Charset": config["content"].get("charset", "UTF-8"),
                }
            params["Message"]["Body"] = message_body

            # Add optional parameters
            if config.get("cc"):
                params["Destination"]["CcAddresses"] = [
                    str(cc) for cc in config["cc"]]
            if config.get("bcc"):
                params["Destination"]["BccAddresses"] = [
                    str(bcc) for bcc in config["bcc"]]
            if config.get("reply_to"):
                params["ReplyToAddresses"] = [str(r) for r in config["reply_to"]]
            if config.get("tags"):
                params["Tags"] = [
                    {"Name": k, "Value": v} for k, v in config["tags"].items()
                ]

            return self.client.send_email(**params)

        except ClientError as e:
            logger.exception("[SES.send_email] Failed to send email")
            msg = "Failed to send email"
            raise SESError(msg) from e

    def create_template(
        self,
        template_name: str,
        content: TemplateContent,
    ) -> None:
        """Create email template."""
        try:
            template = {
                "TemplateName": template_name,
                "SubjectPart": content["subject"],
            }
            if content.get("text"):
                template["TextPart"] = content["text"]
            if content.get("html"):
                template["HtmlPart"] = content["html"]

            self.client.create_template(Template=template)

        except ClientError as e:
            logger.exception(
                "[SES.create_template] Failed to create template")
            msg = "Failed to create template"
            raise SESError(msg) from e

    def delete_template(self, template_name: str) -> None:
        """Delete email template."""
        try:
            self.client.delete_template(TemplateName=template_name)
        except ClientError as e:
            logger.exception(
                "[SES.delete_template] Failed to delete template")
            msg = "Failed to delete template"
            raise SESError(msg) from e

    def get_template(self, template_name: str) -> GetTemplateResponse:
        """Get email template."""
        try:
            return self.client.get_template(TemplateName=template_name)
        except ClientError as e:
            logger.exception(
                "[SES.get_template] Failed to get template")
            msg = "Failed to get template"
            raise SESError(msg) from e

    def list_templates(self) -> ListTemplatesResponse:
        """List email templates."""
        try:
            return self.client.list_templates()
        except ClientError as e:
            logger.exception(
                "[SES.list_templates] Failed to list templates")
            msg = "Failed to list templates"
            raise SESError(msg) from e

    def send_templated_email(self, config: SendTemplateConfig) -> SendTemplatedEmailResponse:
        """Send templated email."""
        try:
            params = {
                "Source": str(config["sender"]),
                "Destination": {
                    "ToAddresses": [str(r) for r in config["recipients"]],
                },
                "Template": config["template_name"],
                "TemplateData": json.dumps(config["template_data"]),
            }

            if config.get("cc"):
                params["Destination"]["CcAddresses"] = [str(cc) for cc in config["cc"]]
            if config.get("bcc"):
                params["Destination"]["BccAddresses"] = [str(bcc) for bcc in config["bcc"]]
            if config.get("tags"):
                params["Tags"] = [{"Name": k, "Value": v} for k, v in config["tags"].items()]

            return self.client.send_templated_email(**params)

        except ClientError as e:
            logger.exception(
                "[SES.send_templated_email] Failed to send email")
            msg = "Failed to send templated email"
            raise SESError(msg) from e

    def get_send_quota(self) -> GetSendQuotaResponse:
        """Get sending quota."""
        try:
            return self.client.get_send_quota()
        except ClientError as e:
            logger.exception(
                "[SES.get_send_quota] Failed to get quota")
            msg = "Failed to get sending quota"
            raise SESError(msg) from e

    def verify_email_identity(self, email: str) -> None:
        """Verify email identity."""
        try:
            self.client.verify_email_identity(EmailAddress=email)
        except ClientError as e:
            logger.exception(
                "[SES.verify_email_identity] Failed to verify email")
            msg = "Failed to verify email identity"
            raise SESError(msg) from e

    def list_identities(self) -> list[str]:
        """List verified identities."""
        try:
            return self.client.list_identities()["Identities"]
        except ClientError as e:
            logger.exception(
                "[SES.list_identities] Failed to list identities")
            msg = "Failed to list identities"
            raise SESError(msg) from e
