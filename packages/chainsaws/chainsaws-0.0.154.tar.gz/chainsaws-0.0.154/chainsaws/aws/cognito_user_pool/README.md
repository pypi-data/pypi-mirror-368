# Cognito User Pool (chainsaws)

High-level, DX-focused API for Amazon Cognito User Pools. All dict returns are normalized as TypedDict, and low-level calls are routed through the thin wrapper `_cognito_user_pool_internal.py`.

- High-level module: `cognito_user_pool.py`
- Models (Requests/Responses/Config): `cognito_user_pool_models.py`
- Exceptions: `cognito_user_pool_exception.py`
- Low-level wrapper: `_cognito_user_pool_internal.py`

Reference: `CognitoIdentityProvider` in Boto3. See: [boto3 CognitoIdentityProvider](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html)

## Install / Import

```python
from chainsaws.aws.cognito_user_pool import CognitoUserPoolAPI
from chainsaws.aws.cognito_user_pool.cognito_user_pool_models import (
    SignUpRequest, SignInWithPasswordRequest,
)
from chainsaws.aws.cognito_user_pool.cognito_user_pool_exception import (
    CognitoUserPoolException, NotAuthorizedException,
)
```

## Quick Start

1. Sign up → Confirm

```python
api = CognitoUserPoolAPI()

# Sign up
signup_req: SignUpRequest = {
    "ClientId": "your_client_id",
    "Username": "user@example.com",
    "Password": "YourStrong!Passw0rd",
    "UserAttributes": [{"Name": "email", "Value": "user@example.com"}],
}
signup_res = api.sign_up(signup_req)

# Confirm code from email/SMS
api.confirm_sign_up({
    "ClientId": "your_client_id",
    "Username": "user@example.com",
    "ConfirmationCode": "123456",
})
```

2. Sign in (USER_PASSWORD_AUTH)

```python
try:
    signin_res = api.sign_in_with_password({
        "ClientId": "your_client_id",
        "Username": "user@example.com",
        "Password": "YourStrong!Passw0rd",
    })
    if "AuthenticationResult" in signin_res:
        tokens = signin_res["AuthenticationResult"]
        access_token = tokens.get("AccessToken")
        id_token = tokens.get("IdToken")
        refresh_token = tokens.get("RefreshToken")
    elif signin_res.get("ChallengeName"):
        # Handle MFA, NEW_PASSWORD_REQUIRED, etc.
        pass
except NotAuthorizedException:
    # Wrong password or user not confirmed
    ...
```

3. Forgot / Confirm forgot password

```python
# Send code
res = api.forgot_password({
    "ClientId": "your_client_id",
    "Username": "user@example.com",
})

# Confirm code + set new password
api.confirm_forgot_password({
    "ClientId": "your_client_id",
    "Username": "user@example.com",
    "ConfirmationCode": "123456",
    "Password": "NewStrong!Passw0rd",
})
```

4. Refresh / Revoke tokens

```python
refresh = api.refresh_tokens({
    "ClientId": "your_client_id",
    "RefreshToken": refresh_token,
})
api.revoke_token({
    "ClientId": "your_client_id",
    "Token": refresh_token,
})
```

5. Get user / Global sign-out

```python
me = api.get_user({"AccessToken": access_token})
api.global_sign_out({"AccessToken": access_token})
```

## Manage User Pool / Client / Domain

```python
# Create a user pool
pool = api.create_user_pool({"PoolName": "my-pool"})

# Create an App Client
client = api.create_user_pool_client({
    "UserPoolId": pool["UserPool"]["Id"],
    "ClientName": "web",
    "GenerateSecret": False,
})

# Configure Cognito Hosted UI domain
api.set_domain({
    "UserPoolId": pool["UserPool"]["Id"],
    "Domain": "my-brand-domain",
})

# Describe / Delete
summary = api.get_user_pool(pool["UserPool"]["Id"])  # Id / Arn / Name / Status
api.delete_user_pool(pool["UserPool"]["Id"])        # delete
```

## Exceptions

`botocore.exceptions.ClientError` is mapped to service-specific exceptions.

```python
from chainsaws.aws.cognito_user_pool.cognito_user_pool_exception import (
    CognitoUserPoolException,
    NotAuthorizedException, InvalidParameterException,
    UsernameExistsException, AliasExistsException,
)

try:
    api.sign_up({...})
except UsernameExistsException:
    ...
except NotAuthorizedException:
    ...
except CognitoUserPoolException as e:
    ...
```

## Models (TypedDict)

- All requests/responses/configs are `TypedDict` for better IDE support
- File: `cognito_user_pool_models.py`

## Notes

- Password-based sign-in uses `USER_PASSWORD_AUTH`. You can extend to `USER_SRP_AUTH` (SRP) or MFA flows with the same pattern.

## End-to-end: API Gateway ↔ Lambda (FastAPI) ↔ DynamoDB with org_id

Two production patterns are common. Both work with this SDK and your current DynamoDB API.

### A) JWT mode (Bearer in browser)

- API Gateway HTTP API (v2) with JWT Authorizer linked to your User Pool
- Browser sends `Authorization: Bearer <AccessToken>`
- Lambda (FastAPI) extracts claims and queries DynamoDB by `org_id`

Browser call:

```javascript
await fetch("https://api.example.com/items", {
  headers: { Authorization: `Bearer ${accessToken}` },
});
```

FastAPI: get org_id from HTTP API v2 claims

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

- Public routes (no authorizer): `/auth/signin`, `/auth/refresh`, `/auth/signout`, `/auth/respond-challenge`
- Protected routes: `/api/**` with Lambda Authorizer (HTTP API v2)
- Sign-in sets `access_token`(short) and `refresh_token`(long) as httpOnly cookies

Sign-in route (public) sets cookies

```python
from fastapi import FastAPI, Request, Response, HTTPException
from chainsaws.aws.cognito_user_pool import CognitoUserPoolAPI

app = FastAPI()
up = CognitoUserPoolAPI()

@app.post("/auth/signin")
async def signin(req: Request):
    body = await req.json()
    res = up.sign_in_with_password({
        "ClientId": "your_client_id",
        "Username": body["username"],
        "Password": body["password"],
    })
    auth = res.get("AuthenticationResult")
    if not auth:
        return {"challenge": res.get("ChallengeName"), "session": res.get("Session")}
    resp = Response(status_code=204)
    resp.set_cookie("access_token", auth.get("AccessToken"), max_age=900, httponly=True, secure=True, samesite="lax", path="/api")
    resp.set_cookie("refresh_token", auth.get("RefreshToken"), max_age=2592000, httponly=True, secure=True, samesite="strict", path="/auth")
    return resp
```

Lambda Authorizer (HTTP API v2) returns `{ isAuthorized, context }`

```python
# authorizer.py (HTTP API v2)
from typing import Any, Dict
import time, requests
from jose import jwt

REGION = "ap-northeast-2"
USER_POOL_ID = "<user_pool_id>"
APP_CLIENT_ID = "<app_client_id>"
ISS = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"{ISS}/.well-known/jwks.json"
_JWKS, _TS = None, 0

def _jwks():
    global _JWKS, _TS
    now = int(time.time())
    if _JWKS and now - _TS < 3600: return _JWKS
    _JWKS = requests.get(JWKS_URL, timeout=3).json(); _TS = now; return _JWKS

def _cookies(cookies: list[str] | None) -> Dict[str,str]:
    jar = {}
    for c in (cookies or []):
        if "=" in c:
            k,v = c.split("=",1); jar[k.strip()] = v.strip()
    return jar

def handler(event: dict, context: Any) -> Dict[str, Any]:
    jar = _cookies(event.get("cookies"))
    token = jar.get("access_token")
    if not token:
        return {"isAuthorized": False}
    try:
        claims = jwt.decode(token, _jwks(), algorithms=["RS256"], audience=APP_CLIENT_ID, issuer=ISS, options={"verify_at_hash": False})
    except Exception:
        return {"isAuthorized": False}
    org_id = claims.get("org_id")
    if not org_id:
        return {"isAuthorized": False}
    return {"isAuthorized": True, "context": {"org_id": org_id, "sub": claims.get("sub")}}
```

FastAPI (protected) reads authorizer context

```python
from fastapi import Request

def get_org_id(req: Request) -> str:
    ev = req.scope.get("aws.event") or {}
    lambdactx = ((ev.get("requestContext") or {}).get("authorizer") or {}).get("lambda") or {}
    return lambdactx.get("org_id")
```

### Adding org_id to tokens

Use a Pre Token Generation Lambda trigger in User Pool to append `org_id` (and any other tenant data) to Id/Access tokens. API Gateway/JWT Authorizer will pass it through to your Lambda.
