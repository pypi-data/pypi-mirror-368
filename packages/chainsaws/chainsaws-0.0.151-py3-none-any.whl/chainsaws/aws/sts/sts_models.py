"""Models for AWS STS operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Literal

from chainsaws.aws.shared.config import APIConfig

# Supported OAuth 2.0 identity providers
OAuthProviderId = Literal["www.amazon.com", "graph.facebook.com"]


@dataclass
class STSAPIConfig(APIConfig):
    """Configuration for STS API."""

    credentials: Optional[Dict[str, str]] = None
    region: Optional[str] = None
    profile_name: Optional[str] = None


@dataclass
class Credentials:
    """AWS credentials."""

    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'Credentials':
        """Create credentials from API response."""
        return cls(
            access_key_id=response['AccessKeyId'],
            secret_access_key=response['SecretAccessKey'],
            session_token=response['SessionToken'],
            expiration=response['Expiration'],
        )


@dataclass
class AssumedRoleCredentials:
    """Credentials for assumed role."""

    credentials: Credentials
    assumed_role_id: str
    arn: str

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'AssumedRoleCredentials':
        """Create credentials from API response."""
        return cls(
            credentials=Credentials.from_response(response['Credentials']),
            assumed_role_id=response['AssumedRoleId'],
            arn=response['Arn'],
        )


@dataclass
class AssumeRoleConfig:
    """Configuration for role assumption."""

    role_arn: str
    role_session_name: str
    duration_seconds: int = 3600
    external_id: Optional[str] = None
    policy: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class AssumeRoleWithWebIdentityConfig:
    """Configuration for role assumption with web identity.

    Args:
        role_arn: ARN of the role to assume
        role_session_name: Identifier for the assumed role session
        web_identity_token: OAuth 2.0 access token or OpenID Connect ID token
        provider_id: Optional identifier for the OAuth 2.0 identity provider.
                    Required only for OAuth 2.0 access tokens.
                    Must be either 'www.amazon.com' or 'graph.facebook.com'.
                    Do not specify for OpenID Connect ID tokens.
        duration_seconds: Duration of the session (900-43200 seconds)
        policy: Optional IAM policy to further restrict the assumed role
        tags: Optional session tags
    """

    role_arn: str
    role_session_name: str
    web_identity_token: str
    provider_id: Optional[OAuthProviderId] = None
    duration_seconds: int = 3600
    policy: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class AssumeRoleWithWebIdentityResponse:
    """Response from assume_role_with_web_identity."""

    credentials: Credentials
    assumed_role_id: str
    arn: str
    subject_from_web_identity_token: str
    audience: str
    source_identity: Optional[str] = None

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'AssumeRoleWithWebIdentityResponse':
        """Create response from API response."""
        return cls(
            credentials=Credentials.from_response(response['Credentials']),
            assumed_role_id=response['AssumedRoleId'],
            arn=response['Arn'],
            subject_from_web_identity_token=response['SubjectFromWebIdentityToken'],
            audience=response['Audience'],
            source_identity=response.get('SourceIdentity'),
        )


@dataclass
class GetCallerIdentityResponse:
    """Response from get_caller_identity."""

    user_id: str
    account: str
    arn: str

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'GetCallerIdentityResponse':
        """Create response from API response."""
        return cls(
            user_id=response['UserId'],
            account=response['Account'],
            arn=response['Arn'],
        )


@dataclass
class GetFederationTokenConfig:
    """Configuration for federation token."""

    name: str
    duration_seconds: int = 43200
    policy: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class FederationTokenCredentials:
    """Credentials for federated user."""

    credentials: Credentials
    federated_user_id: str
    arn: str

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'FederationTokenCredentials':
        """Create credentials from API response."""
        return cls(
            credentials=Credentials.from_response(response['Credentials']),
            federated_user_id=response['FederatedUserId'],
            arn=response['Arn'],
        )


@dataclass
class GetSessionTokenResponse:
    """Response from get_session_token."""

    credentials: Credentials

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'GetSessionTokenResponse':
        """Create response from API response."""
        return cls(
            credentials=Credentials.from_response(response['Credentials']),
        )


@dataclass
class GetSessionTokenConfig:
    """Configuration for session token."""

    duration_seconds: int = 43200
    serial_number: Optional[str] = None
    token_code: Optional[str] = None


@dataclass
class DecodeAuthorizationMessageResponse:
    """Response from decode_authorization_message."""

    decoded_message: Dict[str, Any]

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'DecodeAuthorizationMessageResponse':
        """Create response from API response."""
        return cls(
            decoded_message=response['DecodedMessage'],
        )


@dataclass
class DecodeAuthorizationMessageConfig:
    """Configuration for authorization message decoding."""

    encoded_message: str


@dataclass
class GetAccessKeyLastUsedResponse:
    """Response from get_access_key_last_used."""

    access_key_id: str
    last_used_date: datetime
    service_name: str
    region: str

    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> 'GetAccessKeyLastUsedResponse':
        """Create response from API response."""
        return cls(
            access_key_id=response['AccessKeyId'],
            last_used_date=response['LastUsedDate'],
            service_name=response['ServiceName'],
            region=response['Region'],
        )


@dataclass
class GetAccessKeyLastUsedConfig:
    """Configuration for access key info."""

    access_key_id: str
