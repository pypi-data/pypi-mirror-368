from typing import Literal
from chainsaws.aws.shared.config import APIConfig
from dataclasses import dataclass

@dataclass
class KVSAPIConfig(APIConfig):
    """Configuration for KVS."""
    pass


KVSDataEndpointAPI = Literal[
    'PUT_MEDIA',
    'GET_MEDIA',
    'LIST_FRAGMENTS',
    'GET_MEDIA_FOR_FRAGMENT_LIST',
    'GET_HLS_STREAMING_SESSION_URL',
    'GET_DASH_STREAMING_SESSION_URL',
    'GET_CLIP',
    'GET_IMAGES'
]