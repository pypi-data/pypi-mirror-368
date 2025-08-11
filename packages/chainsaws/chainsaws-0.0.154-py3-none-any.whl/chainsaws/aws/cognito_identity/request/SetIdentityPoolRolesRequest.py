from typing import TypedDict, NotRequired, Literal


class SetIdentityPoolRolesRequest(TypedDict, total=False):
    IdentityPoolId: str
    Roles: dict[str, str]
    RoleMappings: NotRequired[dict[str, "RoleMapping"]]


class RulesConfigurationType(TypedDict):
    Rules: list["MappingRule"]


class MappingRule(TypedDict):
    Claim: str
    MatchType: Literal["Equals", "Contains", "StartsWith", "NotEqual"]
    Value: str
    RoleARN: str


class RoleMapping(TypedDict, total=False):
    Type: Literal["Token", "Rules"]
    AmbiguousRoleResolution: NotRequired[Literal["AuthenticatedRole", "Deny"]]
    RulesConfiguration: NotRequired[RulesConfigurationType]


