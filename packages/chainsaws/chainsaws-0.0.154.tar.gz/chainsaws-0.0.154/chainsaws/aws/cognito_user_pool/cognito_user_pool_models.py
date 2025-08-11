from dataclasses import dataclass
from typing import TypedDict, Literal, NotRequired

from chainsaws.aws.shared.config import APIConfig


@dataclass
class CognitoUserPoolAPIConfig(APIConfig):
    """Config for Cognito User Pool API."""
    pass


class PasswordPolicyDict(TypedDict, total=False):
    MinimumLength: int
    RequireUppercase: bool
    RequireLowercase: bool
    RequireNumbers: bool
    RequireSymbols: bool
    TemporaryPasswordValidityDays: int


class EmailConfigurationDict(TypedDict, total=False):
    EmailSendingAccount: Literal["COGNITO_DEFAULT", "DEVELOPER"]
    SourceArn: str
    From: str
    ReplyToEmailAddress: str
    ConfigurationSet: str


class LambdaConfigDict(TypedDict, total=False):
    PreSignUp: str
    CustomMessage: str
    PostConfirmation: str
    PreAuthentication: str
    PostAuthentication: str
    DefineAuthChallenge: str
    CreateAuthChallenge: str
    VerifyAuthChallengeResponse: str
    PreTokenGeneration: str
    UserMigration: str
    CustomSMSSender: dict
    CustomEmailSender: dict
    KMSKeyID: str


class SchemaAttributeDict(TypedDict, total=False):
    Name: str
    AttributeDataType: Literal["String", "Number", "DateTime", "Boolean"]
    Mutable: bool
    Required: bool
    StringAttributeConstraints: dict
    NumberAttributeConstraints: dict


class CreateUserPoolConfig(TypedDict, total=False):
    PoolName: str
    Policies: dict
    LambdaConfig: LambdaConfigDict
    AutoVerifiedAttributes: list[str]
    AliasAttributes: list[str]
    UsernameAttributes: list[str]
    SmsVerificationMessage: str
    EmailVerificationMessage: str
    EmailVerificationSubject: str
    VerificationMessageTemplate: dict
    SmsAuthenticationMessage: str
    MfaConfiguration: Literal["OFF", "ON", "OPTIONAL"]
    DeviceConfiguration: dict
    EmailConfiguration: EmailConfigurationDict
    SmsConfiguration: dict
    UserPoolTags: dict[str, str]
    AdminCreateUserConfig: dict
    Schema: list[SchemaAttributeDict]
    UserPoolAddOns: dict
    AccountRecoverySetting: dict


class CreateUserPoolResult(TypedDict, total=False):
    UserPool: dict


class CreateUserPoolClientConfig(TypedDict, total=False):
    UserPoolId: str
    ClientName: str
    GenerateSecret: bool
    ReadAttributes: list[str]
    WriteAttributes: list[str]
    ExplicitAuthFlows: list[str]
    SupportedIdentityProviders: list[str]
    CallbackURLs: list[str]
    LogoutURLs: list[str]
    DefaultRedirectURI: str
    AllowedOAuthFlows: list[str]
    AllowedOAuthScopes: list[str]
    AllowedOAuthFlowsUserPoolClient: bool
    PreventUserExistenceErrors: Literal["LEGACY", "ENABLED"]
    EnableTokenRevocation: bool
    EnablePropagateAdditionalUserContextData: bool
    AccessTokenValidity: int
    IdTokenValidity: int
    RefreshTokenValidity: int
    TokenValidityUnits: dict


class CreateUserPoolClientResult(TypedDict, total=False):
    UserPoolClient: dict


class SetDomainConfig(TypedDict):
    UserPoolId: str
    Domain: str
    CustomDomainConfig: NotRequired[dict]


class SetDomainResult(TypedDict, total=False):
    CloudFrontDomain: str


class GetUserPoolResult(TypedDict, total=False):
    Id: str
    Arn: str
    Name: str
    Status: NotRequired[str]


class DeleteUserPoolResult(TypedDict, total=False):
    Success: bool



# ===== SignUp / SignIn / Password / Tokens =====

class CodeDeliveryDetailsDict(TypedDict, total=False):
    Destination: str
    DeliveryMedium: Literal["SMS", "EMAIL"]
    AttributeName: NotRequired[str]


class UserAttributeDict(TypedDict):
    Name: str
    Value: str


class SignUpRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    Password: str
    UserAttributes: NotRequired[list[UserAttributeDict]]
    ValidationData: NotRequired[list[UserAttributeDict]]
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]
    UserContextData: NotRequired[dict]
    AnalyticsMetadata: NotRequired[dict]


class SignUpResult(TypedDict, total=False):
    UserConfirmed: bool
    UserSub: str
    CodeDeliveryDetails: NotRequired[CodeDeliveryDetailsDict]


class ConfirmSignUpRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    ConfirmationCode: str
    ForceAliasCreation: NotRequired[bool]
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class ConfirmSignUpResult(TypedDict, total=False):
    Success: bool


class ResendConfirmationCodeRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class ResendConfirmationCodeResult(TypedDict, total=False):
    CodeDeliveryDetails: CodeDeliveryDetailsDict


class AuthenticationResultDict(TypedDict, total=False):
    AccessToken: NotRequired[str]
    IdToken: NotRequired[str]
    RefreshToken: NotRequired[str]
    ExpiresIn: NotRequired[int]
    TokenType: NotRequired[str]


class SignInWithPasswordRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    Password: str
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class SignInResult(TypedDict, total=False):
    AuthenticationResult: NotRequired[AuthenticationResultDict]
    ChallengeName: NotRequired[str]
    ChallengeParameters: NotRequired[dict]
    Session: NotRequired[str]


class RespondToAuthChallengeRequest(TypedDict, total=False):
    ClientId: str
    ChallengeName: str
    ChallengeResponses: dict
    Session: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class ForgotPasswordRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class ForgotPasswordResult(TypedDict, total=False):
    CodeDeliveryDetails: CodeDeliveryDetailsDict


class ConfirmForgotPasswordRequest(TypedDict, total=False):
    ClientId: str
    Username: str
    ConfirmationCode: str
    Password: str
    SecretHash: NotRequired[str]
    ClientMetadata: NotRequired[dict]


class ConfirmForgotPasswordResult(TypedDict, total=False):
    Success: bool


class ChangePasswordRequest(TypedDict):
    PreviousPassword: str
    ProposedPassword: str
    AccessToken: str


class ChangePasswordResult(TypedDict, total=False):
    Success: bool


class GetUserRequest(TypedDict):
    AccessToken: str


class GetUserResult(TypedDict, total=False):
    Username: str
    UserAttributes: list[UserAttributeDict]


class GlobalSignOutRequest(TypedDict):
    AccessToken: str


class GlobalSignOutResult(TypedDict, total=False):
    Success: bool


class RefreshTokensRequest(TypedDict, total=False):
    ClientId: str
    RefreshToken: str
    Scope: NotRequired[str]


class RefreshTokensResult(TypedDict, total=False):
    AccessToken: NotRequired[str]
    IdToken: NotRequired[str]
    ExpiresIn: NotRequired[int]
    TokenType: NotRequired[str]


class RevokeTokenRequest(TypedDict):
    ClientId: str
    Token: str
    ClientSecret: NotRequired[str]


class RevokeTokenResult(TypedDict, total=False):
    Success: bool

