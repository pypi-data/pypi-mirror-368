# Cognito Identity (chainsaws)

High-level, DX-focused API for Amazon Cognito Identity Pools. All dict returns are normalized as TypedDict, and low-level calls are routed through the thin wrapper `_cognito_identity_internal.py`.

- High-level module: `cognito_identity.py`
- Models (Requests/Responses/Config): `cognito_identity_models.py` + `request/`, `response/`
- Exceptions: `cognito_identity_exception.py`
- Low-level wrapper: `_cognito_identity_internal.py`

Reference: `CognitoIdentity` in Boto3. See: [boto3 CognitoIdentity](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-identity.html)

## Install / Import

```python
from chainsaws.aws.cognito_identity import CognitoIdentityAPI
from chainsaws.aws.cognito_identity.request.GetIdRequest import GetIdRequest
from chainsaws.aws.cognito_identity.request.GetCredentialsForIdentityRequest import GetCredentialsForIdentityRequest
from chainsaws.aws.cognito_identity.cognito_identity_exception import (
    CognitoIdentityException, CognitoIdentityNotAuthorizedException,
)
```

## Quick Start

1. Get IdentityId and temporary credentials

```python
api = CognitoIdentityAPI()

get_id_req: GetIdRequest = {
    "IdentityPoolId": "ap-northeast-2:xxxx-xxxx",
    # Optional: federation with a user pool IdToken
    # "Logins": {"cognito-idp.<region>.amazonaws.com/<userPoolId>": id_token}
}
identity = api.get_id(get_id_req)

creds_req: GetCredentialsForIdentityRequest = {
    "IdentityId": identity["IdentityId"],
    # If you federated, keep the same Logins map here
}
creds = api.get_credentials_for_identity(creds_req)
```

2. Developer identity (optional)

```python
# Link / merge / lookup / unlink developer users
from chainsaws.aws.cognito_identity.request.LookupDeveloperIdentityRequest import LookupDeveloperIdentityRequest
from chainsaws.aws.cognito_identity.request.MergeDeveloperIdentitiesRequest import MergeDeveloperIdentitiesRequest
from chainsaws.aws.cognito_identity.request.UnlinkDeveloperIdentityRequest import UnlinkDeveloperIdentityRequest

api.lookup_developer_identity({
    "IdentityPoolId": "ap-northeast-2:xxxx-xxxx",
    "DeveloperUserIdentifier": "dev-user-1",
})

api.merge_developer_identities({
    "IdentityPoolId": "ap-northeast-2:xxxx-xxxx",
    "DeveloperProviderName": "your-developer-provider",
    "SourceUserIdentifier": "dev-user-1",
    "DestinationUserIdentifier": "dev-user-2",
})

api.unlink_developer_identity({
    "IdentityPoolId": "ap-northeast-2:xxxx-xxxx",
    "IdentityId": identity["IdentityId"],
    "DeveloperProviderName": "your-developer-provider",
    "DeveloperUserIdentifier": "dev-user-1",
})
```

## Manage Identity Pools

```python
# Create
pool = api.create_identity_pool({
    "IdentityPoolName": "my-identity-pool",
    "AllowUnauthenticatedIdentities": False,
})

# Set roles
api.set_identity_pool_roles({
    "IdentityPoolId": pool["IdentityPoolId"],
    "Roles": {
        "authenticated": "arn:aws:iam::123456789012:role/CognitoAuthRole",
        "unauthenticated": "arn:aws:iam::123456789012:role/CognitoUnauthRole",
    },
})

# Describe / Delete
summary = api.get_identity_pool(pool["IdentityPoolId"])  # summary
api.delete_identity_pool(pool["IdentityPoolId"])        # delete
```

## Exceptions

`botocore.exceptions.ClientError` is mapped to service-specific exceptions.

```python
from chainsaws.aws.cognito_identity.cognito_identity_exception import (
    CognitoIdentityException,
    CognitoIdentityNotAuthorizedException,
    CognitoIdentityInvalidParameterException,
)

try:
    creds = api.get_credentials_for_identity({...})
except CognitoIdentityNotAuthorizedException:
    ...
except CognitoIdentityInvalidParameterException:
    ...
except CognitoIdentityException as e:
    ...
```

## Models (TypedDict)

- All requests/responses/configs are `TypedDict` for better IDE support
- Files: `cognito_identity_models.py`; details in `request/`, `response/`

## Notes

- Tagging APIs are intentionally excluded for now. They can be added later with the same pattern (`tag_resource` / `untag_resource` / `list_tags_for_resource`).

## End-to-end patterns with API Gateway HTTP API (v2)

Two common integration modes depending on how the browser carries credentials.

### A) JWT mode (Bearer in browser)

- API Gateway JWT Authorizer validates the token (issuer/audience) from the User Pool
- Lambda reads claims at `requestContext.authorizer.jwt.claims`
- `org_id` from the token is used to scope DynamoDB queries

Reading claims in FastAPI:

```python
from fastapi import Request

def get_org_id_from_claims(req: Request) -> str:
    ev = req.scope.get("aws.event") or {}
    claims = (((ev.get("requestContext") or {}).get("authorizer") or {}).get("jwt") or {}).get("claims", {})
    org_id = claims.get("org_id")
    if not org_id:
        raise ValueError("org_id missing")
    return org_id
```

### B) Cookie mode (httpOnly) with Lambda Authorizer

- Public routes manage sign-in/refresh/signout and set httpOnly cookies
- Protected routes are backed by a Lambda Authorizer that decodes the cookie `access_token`
- Authorizer returns `{ isAuthorized, context }`, e.g., `{ context: { org_id } }`

Authorizer response (HTTP API v2):

```json
{
  "isAuthorized": true,
  "context": { "org_id": "org_123", "sub": "user_sub" }
}
```

The protected Lambda can read `requestContext.authorizer.lambda.org_id` and use it for DynamoDB partitioning.
