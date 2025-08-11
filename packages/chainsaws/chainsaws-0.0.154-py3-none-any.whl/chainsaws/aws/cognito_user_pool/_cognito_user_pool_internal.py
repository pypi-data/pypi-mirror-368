import logging
from typing import Optional

from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError

from chainsaws.aws.cognito_user_pool.cognito_user_pool_models import (
    CognitoUserPoolAPIConfig,
    CreateUserPoolConfig,
    CreateUserPoolClientConfig,
    SetDomainConfig,
    SignUpRequest,
    ConfirmSignUpRequest,
    ResendConfirmationCodeRequest,
    SignInWithPasswordRequest,
    RespondToAuthChallengeRequest,
    ForgotPasswordRequest,
    ConfirmForgotPasswordRequest,
    ChangePasswordRequest,
    GetUserRequest,
    GlobalSignOutRequest,
    RefreshTokensRequest,
    RevokeTokenRequest,
)
from chainsaws.aws.cognito_user_pool.cognito_user_pool_exception import (
    CognitoUserPoolException,
    InvalidParameterException,
    NotAuthorizedException,
    TooManyRequestsException,
    ResourceInUseException,
    LimitExceededException,
    UsernameExistsException,
    AliasExistsException,
    UserPoolNotFoundException,
)

logger = logging.getLogger(__name__)


class CognitoUserPool:
    """Low-level thin wrapper over boto3 cognito-idp client."""

    def __init__(self, boto3_session: Session, config: Optional[CognitoUserPoolAPIConfig] = None) -> None:
        self.config = config or CognitoUserPoolAPIConfig()
        client_config = Config(region_name=self.config.region)
        self.client = boto3_session.client("cognito-idp", config=client_config, region_name=self.config.region)

    def create_user_pool(self, cfg: CreateUserPoolConfig) -> dict:
        try:
            return self.client.create_user_pool(**cfg)  # type: ignore[arg-type]
        except ClientError as e:
            raise self._map_client_error(e)

    def create_user_pool_client(self, cfg: CreateUserPoolClientConfig) -> dict:
        try:
            return self.client.create_user_pool_client(**cfg)  # type: ignore[arg-type]
        except ClientError as e:
            raise self._map_client_error(e)

    def create_user_pool_domain(self, cfg: SetDomainConfig) -> dict:
        try:
            return self.client.create_user_pool_domain(**cfg)  # type: ignore[arg-type]
        except ClientError as e:
            raise self._map_client_error(e)

    def describe_user_pool(self, user_pool_id: str) -> dict:
        try:
            return self.client.describe_user_pool(UserPoolId=user_pool_id)
        except ClientError as e:
            raise self._map_client_error(e)

    def delete_user_pool(self, user_pool_id: str) -> None:
        try:
            self.client.delete_user_pool(UserPoolId=user_pool_id)
        except ClientError as e:
            raise self._map_client_error(e)

    # ===== Low-level auth flows =====
    def sign_up(self, req: SignUpRequest) -> dict:
        try:
            return self.client.sign_up(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def confirm_sign_up(self, req: ConfirmSignUpRequest) -> dict:
        try:
            return self.client.confirm_sign_up(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def resend_confirmation_code(self, req: ResendConfirmationCodeRequest) -> dict:
        try:
            return self.client.resend_confirmation_code(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def initiate_auth_with_password(self, req: SignInWithPasswordRequest) -> dict:
        try:
            return self.client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    k: v
                    for k, v in {
                        "USERNAME": req.get("Username", ""),
                        "PASSWORD": req.get("Password", ""),
                        "SECRET_HASH": req.get("SecretHash"),
                    }.items()
                    if v is not None
                },
                ClientId=req.get("ClientId", ""),
                ClientMetadata=req.get("ClientMetadata"),
            )
        except ClientError as e:
            raise self._map_client_error(e)

    def respond_to_auth_challenge(self, req: RespondToAuthChallengeRequest) -> dict:
        try:
            return self.client.respond_to_auth_challenge(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def forgot_password(self, req: ForgotPasswordRequest) -> dict:
        try:
            return self.client.forgot_password(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def confirm_forgot_password(self, req: ConfirmForgotPasswordRequest) -> dict:
        try:
            return self.client.confirm_forgot_password(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def change_password(self, req: ChangePasswordRequest) -> dict:
        try:
            return self.client.change_password(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def get_user(self, req: GetUserRequest) -> dict:
        try:
            return self.client.get_user(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def global_sign_out(self, req: GlobalSignOutRequest) -> dict:
        try:
            return self.client.global_sign_out(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    def refresh_tokens(self, req: RefreshTokensRequest) -> dict:
        try:
            return self.client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    k: v
                    for k, v in {
                        "REFRESH_TOKEN": req.get("RefreshToken", ""),
                        "SCOPE": req.get("Scope"),
                    }.items()
                    if v is not None
                },
                ClientId=req.get("ClientId", ""),
            )
        except ClientError as e:
            raise self._map_client_error(e)

    def revoke_token(self, req: RevokeTokenRequest) -> dict:
        try:
            return self.client.revoke_token(**req)
        except ClientError as e:
            raise self._map_client_error(e)

    # --- error mapping ---
    def _map_client_error(self, err: ClientError) -> CognitoUserPoolException:
        code = err.response.get("Error", {}).get("Code", "")
        mapping: dict[str, type[CognitoUserPoolException]] = {
            "InvalidParameterException": InvalidParameterException,
            "NotAuthorizedException": NotAuthorizedException,
            "TooManyRequestsException": TooManyRequestsException,
            "ResourceInUseException": ResourceInUseException,
            "LimitExceededException": LimitExceededException,
            "UsernameExistsException": UsernameExistsException,
            "AliasExistsException": AliasExistsException,
            "ResourceNotFoundException": UserPoolNotFoundException,
        }
        exc_cls = mapping.get(code, CognitoUserPoolException)
        return exc_cls(str(err))

