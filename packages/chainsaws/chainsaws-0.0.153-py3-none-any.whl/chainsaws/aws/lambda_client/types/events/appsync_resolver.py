"""AppSync resolver event types for AWS Lambda."""

from typing import Any, Dict, List, TypedDict, Union


class AppSyncInfo(TypedDict):
    """Information about the GraphQL operation.

    Args:
        selectionSetList (List[str]): List of selected fields.
        selectionSetGraphQL (str): GraphQL selection set.
        parentTypeName (str): Name of the parent type.
        fieldName (str): Name of the field being resolved.
        variables (Dict[str, Any]): GraphQL variables.
    """
    selectionSetList: List[str]
    selectionSetGraphQL: str
    parentTypeName: str
    fieldName: str
    variables: Dict[str, Any]


class AppSyncPrev(TypedDict):
    """Result from a previous pipeline resolver.

    Args:
        result (Dict[str, Any]): The result data.
    """
    result: Dict[str, Any]


class AppSyncRequest(TypedDict):
    """HTTP request information.

    Args:
        headers (Dict[str, str]): Request headers.
    """
    headers: Dict[str, str]


class AppSyncIdentityIAM(TypedDict):
    """IAM identity information.

    Args:
        accountId (str): AWS account ID.
        cognitoIdentityPoolId (str): Cognito identity pool ID.
        cognitoIdentityId (str): Cognito identity ID.
        sourceIp (List[str]): Source IP addresses.
        username (str): IAM username.
        userArn (str): IAM user ARN.
        cognitoIdentityAuthType (str): Cognito authentication type.
        cognitoIdentityAuthProvider (str): Cognito authentication provider.
    """
    accountId: str
    cognitoIdentityPoolId: str
    cognitoIdentityId: str
    sourceIp: List[str]
    username: str
    userArn: str
    cognitoIdentityAuthType: str
    cognitoIdentityAuthProvider: str


class AppSyncIdentityCognito(TypedDict, total=False):
    """Cognito user pool identity information.

    Args:
        sub (str): Subject identifier.
        issuer (str): Token issuer.
        username (str): Cognito username.
        claims (Dict): JWT claims.
        sourceIp (List[str]): Source IP addresses.
        defaultAuthStrategy (str): Default authentication strategy.
        groups (List[str] | None): User groups.
    """
    sub: str
    issuer: str
    username: str
    claims: Dict
    sourceIp: List[str]
    defaultAuthStrategy: str
    groups: List[str]


class AppSyncIdentityOIDC(TypedDict):
    """OpenID Connect identity information.

    Args:
        claims (Any): OIDC claims.
        issuer (str): Token issuer.
        sub (str): Subject identifier.
    """
    claims: Any
    issuer: str
    sub: str


class AppSyncIdentityLambda(TypedDict):
    """Lambda authorizer identity information.

    Args:
        resolverContext (Any): Custom resolver context.
    """
    resolverContext: Any


class AppSyncResolverEvent(TypedDict, total=False):
    """AppSync resolver event for AWS Lambda.

    Args:
        arguments (Dict): GraphQL arguments.
        identity (Union[AppSyncIdentityIAM, AppSyncIdentityCognito, AppSyncIdentityOIDC, AppSyncIdentityLambda]):
            Identity information based on authorization type.
        source (Dict | None): Source data from parent field.
        stash (Dict[str, Any]): Shared data between resolvers.
        request (AppSyncRequest): Request information.
        prev (AppSyncPrev | None): Previous resolver result.
        info (AppSyncInfo): GraphQL operation information.

    Reference:
        https://docs.aws.amazon.com/appsync/latest/devguide/resolver-context-reference.html
    """
    arguments: Dict
    identity: Union[
        AppSyncIdentityIAM,
        AppSyncIdentityCognito,
        AppSyncIdentityOIDC,
        AppSyncIdentityLambda,
    ]
    source: Dict
    stash: Dict[str, Any]
    request: AppSyncRequest
    prev: AppSyncPrev
    info: AppSyncInfo
