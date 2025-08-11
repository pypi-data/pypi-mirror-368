from typing import TypedDict


class OriginEndpointPolicyResponse(TypedDict):
    ChannelGroupName: str
    ChannelName: str
    OriginEndpointName: str
    Policy: str


GetOriginEndpointPolicyResponse = OriginEndpointPolicyResponse