"""AWS IAM client module for managing IAM roles and policies."""

from chainsaws.aws.iam.iam import IAMAPI
from chainsaws.aws.iam.iam_models import IAMAPIConfig, RoleConfig, RolePolicyConfig

__all__ = [
    "IAMAPI",
    "IAMAPIConfig",
    "RoleConfig",
    "RolePolicyConfig",
]
