import logging
from typing import Optional

from chainsaws.aws.shared import session
from chainsaws.aws.cognito_user_pool._cognito_user_pool_internal import CognitoUserPool
from chainsaws.aws.cognito_user_pool.cognito_user_pool_models import (
    CognitoUserPoolAPIConfig,
    CreateUserPoolConfig,
    CreateUserPoolResult,
    CreateUserPoolClientConfig,
    CreateUserPoolClientResult,
    SetDomainConfig,
    SetDomainResult,
    GetUserPoolResult,
    SignUpRequest,
    SignUpResult,
    ConfirmSignUpRequest,
    ConfirmSignUpResult,
    ResendConfirmationCodeRequest,
    ResendConfirmationCodeResult,
    SignInWithPasswordRequest,
    SignInResult,
    RespondToAuthChallengeRequest,
    ForgotPasswordRequest,
    ForgotPasswordResult,
    ConfirmForgotPasswordRequest,
    ConfirmForgotPasswordResult,
    ChangePasswordRequest,
    ChangePasswordResult,
    GetUserRequest,
    GetUserResult,
    GlobalSignOutRequest,
    GlobalSignOutResult,
    RefreshTokensRequest,
    RefreshTokensResult,
    RevokeTokenRequest,
    RevokeTokenResult,
)

logger = logging.getLogger(__name__)


class CognitoUserPoolAPI:
    def __init__(self, config: Optional[CognitoUserPoolAPIConfig] = None) -> None:
        self.config = config or CognitoUserPoolAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.user_pool = CognitoUserPool(self.boto3_session, config=self.config)


    def create_user_pool(self, cfg: CreateUserPoolConfig) -> CreateUserPoolResult:
        resp = self.user_pool.create_user_pool(cfg)
        return CreateUserPoolResult(UserPool=resp.get("UserPool", {}))


    def create_user_pool_client(self, cfg: CreateUserPoolClientConfig) -> CreateUserPoolClientResult:
        resp = self.user_pool.create_user_pool_client(cfg)
        return CreateUserPoolClientResult(UserPoolClient=resp.get("UserPoolClient", {}))


    def set_domain(self, cfg: SetDomainConfig) -> SetDomainResult:
        resp = self.user_pool.create_user_pool_domain(cfg)
        result: SetDomainResult = {}
        if "CloudFrontDomain" in resp:
            result["CloudFrontDomain"] = resp["CloudFrontDomain"]
        return result


    def get_user_pool(self, user_pool_id: str) -> GetUserPoolResult:
        resp = self.user_pool.describe_user_pool(user_pool_id)
        pool = resp.get("UserPool", {})
        result: GetUserPoolResult = {
            "Id": pool.get("Id", ""),
            "Arn": pool.get("Arn", ""),
            "Name": pool.get("Name", ""),
        }

        if pool.get("Status"):
            result["Status"] = pool["Status"]

        return result


    def delete_user_pool(self, user_pool_id: str) -> None:
        self.user_pool.delete_user_pool(user_pool_id)


    # ===== High-level auth wrappers =====
    def sign_up(self, req: SignUpRequest) -> SignUpResult:
        resp = self.user_pool.sign_up(req)
        result: SignUpResult = {
            "UserConfirmed": resp.get("UserConfirmed", False),
            "UserSub": resp.get("UserSub", ""),
        }
        if "CodeDeliveryDetails" in resp:
            result["CodeDeliveryDetails"] = resp["CodeDeliveryDetails"]
        return result

    def confirm_sign_up(self, req: ConfirmSignUpRequest) -> ConfirmSignUpResult:
        self.user_pool.confirm_sign_up(req)
        return {"Success": True}

    def resend_confirmation_code(self, req: ResendConfirmationCodeRequest) -> ResendConfirmationCodeResult:
        resp = self.user_pool.resend_confirmation_code(req)
        return {"CodeDeliveryDetails": resp.get("CodeDeliveryDetails", {})}

    def sign_in_with_password(self, req: SignInWithPasswordRequest) -> SignInResult:
        resp = self.user_pool.initiate_auth_with_password(req)
        result: SignInResult = {}
        if "AuthenticationResult" in resp:
            result["AuthenticationResult"] = resp["AuthenticationResult"]
        if "ChallengeName" in resp:
            result["ChallengeName"] = resp["ChallengeName"]
        if "ChallengeParameters" in resp:
            result["ChallengeParameters"] = resp["ChallengeParameters"]
        if "Session" in resp:
            result["Session"] = resp["Session"]
        return result

    def respond_to_auth_challenge(self, req: RespondToAuthChallengeRequest) -> SignInResult:
        resp = self.user_pool.respond_to_auth_challenge(req)
        result: SignInResult = {}
        if "AuthenticationResult" in resp:
            result["AuthenticationResult"] = resp["AuthenticationResult"]
        if "ChallengeName" in resp:
            result["ChallengeName"] = resp["ChallengeName"]
        if "ChallengeParameters" in resp:
            result["ChallengeParameters"] = resp["ChallengeParameters"]
        if "Session" in resp:
            result["Session"] = resp["Session"]
        return result

    def forgot_password(self, req: ForgotPasswordRequest) -> ForgotPasswordResult:
        resp = self.user_pool.forgot_password(req)
        return {"CodeDeliveryDetails": resp.get("CodeDeliveryDetails", {})}

    def confirm_forgot_password(self, req: ConfirmForgotPasswordRequest) -> ConfirmForgotPasswordResult:
        self.user_pool.confirm_forgot_password(req)
        return {"Success": True}

    def change_password(self, req: ChangePasswordRequest) -> ChangePasswordResult:
        self.user_pool.change_password(req)
        return {"Success": True}

    def get_user(self, req: GetUserRequest) -> GetUserResult:
        resp = self.user_pool.get_user(req)
        return {
            "Username": resp.get("Username", ""),
            "UserAttributes": resp.get("UserAttributes", []),
        }

    def global_sign_out(self, req: GlobalSignOutRequest) -> GlobalSignOutResult:
        self.user_pool.global_sign_out(req)
        return {"Success": True}

    def refresh_tokens(self, req: RefreshTokensRequest) -> RefreshTokensResult:
        resp = self.user_pool.refresh_tokens(req)
        auth = resp.get("AuthenticationResult", {})
        return {
            "AccessToken": auth.get("AccessToken"),
            "IdToken": auth.get("IdToken"),
            "ExpiresIn": auth.get("ExpiresIn"),
            "TokenType": auth.get("TokenType"),
        }

    def revoke_token(self, req: RevokeTokenRequest) -> RevokeTokenResult:
        self.user_pool.revoke_token(req)
        return {"Success": True}

