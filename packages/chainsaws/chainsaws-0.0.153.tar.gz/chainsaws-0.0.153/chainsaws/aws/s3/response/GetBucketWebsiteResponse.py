from typing import TypedDict, Optional, List


class RedirectAllRequestsTo(TypedDict, total=False):
    """Redirect all requests configuration."""
    HostName: str
    Protocol: Optional[str]


class Condition(TypedDict, total=False):
    """Redirect condition."""
    HttpErrorCodeReturnedEquals: Optional[str]
    KeyPrefixEquals: Optional[str]


class Redirect(TypedDict, total=False):
    """Redirect configuration."""
    HostName: Optional[str]
    HttpRedirectCode: Optional[str]
    Protocol: Optional[str]
    ReplaceKeyPrefixWith: Optional[str]
    ReplaceKeyWith: Optional[str]


class RoutingRule(TypedDict, total=False):
    """Website routing rule."""
    Condition: Optional[Condition]
    Redirect: Redirect


class IndexDocument(TypedDict):
    """Index document configuration."""
    Suffix: str


class ErrorDocument(TypedDict):
    """Error document configuration."""
    Key: str


class GetBucketWebsiteResponse(TypedDict, total=False):
    """Response from S3 GetBucketWebsite operation."""
    RedirectAllRequestsTo: Optional[RedirectAllRequestsTo]
    IndexDocument: Optional[IndexDocument]
    ErrorDocument: Optional[ErrorDocument]
    RoutingRules: Optional[List[RoutingRule]] 