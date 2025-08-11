from dataclasses import dataclass, field
from chainsaws.aws.shared.config import APIConfig

@dataclass
class APIGatewayManagementAPIConfig(APIConfig):
    """Configuration for APIGatewayManagement."""
    endpoint_url: str = field(kw_only=True)