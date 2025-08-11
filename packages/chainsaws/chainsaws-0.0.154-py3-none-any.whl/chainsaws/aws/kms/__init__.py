"""AWS KMS (Key Management Service) module.

This module provides a high-level interface for interacting with AWS KMS.
It includes functionality for key management, encryption, decryption, and more.
"""

from chainsaws.aws.kms.kms import KMSAPI
from chainsaws.aws.kms.kms_models import (
    KMSAPIConfig,
    KeyUsage,
    CustomerMasterKeySpec,
    KeyState,
    KeyManager,
    OriginType,
    EncryptionContext,
    GrantConstraints,
    Tag,
    EncryptResponse,
    DecryptResponse,
    ListKeysResponse,
    GenerateDataKeyResponse,
    GenerateRandomResponse
)
from chainsaws.aws.kms.kms_exception import KMSValidationError, KMSKeyNotFoundError

__all__ = [
    # Main API class
    'KMSAPI',

    # Configuration and models
    'KMSAPIConfig',
    'EncryptionContext',
    'GrantConstraints',
    'Tag',

    # Enums and types
    'KeyUsage',
    'CustomerMasterKeySpec',
    'KeyState',
    'KeyManager',
    'OriginType',

    # Response types
    'EncryptResponse',
    'DecryptResponse',
    'ListKeysResponse',
    'GenerateDataKeyResponse',
    'GenerateRandomResponse',

    # Exceptions
    'KMSValidationError',
    'KMSKeyNotFoundError'
]
