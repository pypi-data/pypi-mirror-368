from datetime import datetime
from typing import TypedDict

class ConnectionIdentity(TypedDict):
    SourceIp: str
    UserAgent: str

class GetConnectionResponse(TypedDict):
    ConnectedAt: datetime
    Identity: ConnectionIdentity
    LastActiveAt: datetime