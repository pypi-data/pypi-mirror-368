from dataclasses import dataclass, field
from typing import Optional

from chainsaws.aws.shared.session import AWSCredentials


@dataclass
class APIConfig:
    """Configuration for AWS Configs.
    Used as a parent class for AWS service config classes.
    """

    credentials: Optional[AWSCredentials] = None  # AWS credentials dictionary
    region: Optional[str] = field(default="ap-northeast-2")  # AWS region
