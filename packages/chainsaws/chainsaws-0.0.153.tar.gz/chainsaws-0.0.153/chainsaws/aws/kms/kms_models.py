from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, TypedDict, Literal

from chainsaws.aws.shared.config import APIConfig


# Key usage types for KMS keys
KeyUsage = Literal[
    'SIGN_VERIFY',
    'ENCRYPT_DECRYPT',
    'GENERATE_VERIFY_MAC',
    'KEY_AGREEMENT'
]

# Customer master key specifications and key specs
KeySpec = Literal[
    'RSA_2048',
    'RSA_3072',
    'RSA_4096',
    'ECC_NIST_P256',
    'ECC_NIST_P384',
    'ECC_NIST_P521',
    'ECC_SECG_P256K1',
    'SYMMETRIC_DEFAULT',
    'HMAC_224',
    'HMAC_256',
    'HMAC_384',
    'HMAC_512',
    'SM2'
]

CustomerMasterKeySpec = KeySpec

# KMS key states
KeyState = Literal[
    'Creating',
    'Enabled',
    'Disabled',
    'PendingDeletion',
    'PendingImport',
    'PendingReplicaDeletion',
    'Unavailable',
    'Updating'
]

# Key manager types
KeyManager = Literal['AWS', 'CUSTOMER']

# Key origin types
OriginType = Literal[
    'AWS_KMS',
    'EXTERNAL',
    'AWS_CLOUDHSM',
    'EXTERNAL_KEY_STORE'
]

# Expiration model types
ExpirationModel = Literal[
    'KEY_MATERIAL_EXPIRES',
    'KEY_MATERIAL_DOES_NOT_EXPIRE'
]

# Encryption algorithm types
EncryptionAlgorithm = Literal[
    'SYMMETRIC_DEFAULT',
    'RSAES_OAEP_SHA_1',
    'RSAES_OAEP_SHA_256',
    'SM2PKE'
]

# Signing algorithm types
SigningAlgorithm = Literal[
    'RSASSA_PSS_SHA_256',
    'RSASSA_PSS_SHA_384',
    'RSASSA_PSS_SHA_512',
    'RSASSA_PKCS1_V1_5_SHA_256',
    'RSASSA_PKCS1_V1_5_SHA_384',
    'RSASSA_PKCS1_V1_5_SHA_512',
    'ECDSA_SHA_256',
    'ECDSA_SHA_384',
    'ECDSA_SHA_512',
    'SM2DSA'
]

# Key agreement algorithm types
KeyAgreementAlgorithm = Literal['ECDH']

# MAC algorithm types
MacAlgorithm = Literal[
    'HMAC_SHA_224',
    'HMAC_SHA_256',
    'HMAC_SHA_384',
    'HMAC_SHA_512'
]


@dataclass
class KMSAPIConfig(APIConfig):
    """KMS API configuration."""
    pass


class EncryptResponse(TypedDict):
    """Response type for encrypt operation."""
    CiphertextBlob: bytes
    KeyId: str
    EncryptionAlgorithm: EncryptionAlgorithm


class DecryptResponse(TypedDict):
    """Response type for decrypt operation."""
    Plaintext: bytes
    KeyId: str
    EncryptionAlgorithm: str


class KeyListEntry(TypedDict):
    """KMS key list entry"""
    KeyId: str
    KeyArn: str


class ListKeysResponse(TypedDict):
    """Response type for list_keys operation"""
    Keys: List[KeyListEntry]
    NextMarker: Optional[str]
    Truncated: bool


class GenerateDataKeyResponse(TypedDict):
    """Response type for generate_data_key operation."""
    Plaintext: bytes
    CiphertextBlob: bytes
    KeyId: str
    EncryptionAlgorithm: str


class GenerateRandomResponse(TypedDict):
    """Response type for generate_random operation."""
    Plaintext: bytes
    EncryptionAlgorithm: str


class MultiRegionKey(TypedDict):
    """Multi-region key configuration"""
    Arn: str
    Region: str


class MultiRegionConfiguration(TypedDict):
    """Multi-region configuration"""
    MultiRegionKeyType: Literal['PRIMARY', 'REPLICA']
    PrimaryKey: MultiRegionKey
    ReplicaKeys: List[MultiRegionKey]


class XksKeyConfiguration(TypedDict):
    """External key store key configuration"""
    Id: str


class KMSKeyMetadata(TypedDict, total=False):
    """KMS key metadata

    Required fields:
    - AWSAccountId: 12-digit AWS account ID
    - KeyId: Globally unique identifier
    - Arn: Amazon Resource Name
    - CreationDate: Creation date and time
    - Enabled: Whether the key is enabled
    - KeyUsage: Cryptographic operations allowed
    - KeyState: Current key status
    - Origin: Source of the key material
    - KeyManager: AWS or customer managed
    - KeySpec: Type of key material

    Optional fields (depending on key configuration):
    - Description: Key description
    - DeletionDate: Scheduled deletion date (when KeyState is PendingDeletion)
    - ValidTo: Expiration time for imported key material
    - CustomKeyStoreId: Custom key store identifier
    - CloudHsmClusterId: CloudHSM cluster ID
    - ExpirationModel: Key material expiration model
    - CustomerMasterKeySpec: Deprecated, use KeySpec instead
    - EncryptionAlgorithms: Supported encryption algorithms
    - SigningAlgorithms: Supported signing algorithms
    - KeyAgreementAlgorithms: Key agreement algorithms
    - MultiRegion: Whether it's a multi-region key
    - MultiRegionConfiguration: Multi-region key configuration
    - PendingDeletionWindowInDays: Waiting period for primary key deletion
    - MacAlgorithms: Supported MAC algorithms
    - XksKeyConfiguration: External key store configuration
    """
    # Required fields
    AWSAccountId: str
    KeyId: str
    Arn: str
    CreationDate: datetime
    Enabled: bool
    KeyUsage: KeyUsage
    KeyState: KeyState
    Origin: OriginType
    KeyManager: KeyManager
    KeySpec: KeySpec

    # Optional fields
    Description: Optional[str]
    DeletionDate: Optional[datetime]  # Present only when KeyState is PendingDeletion
    ValidTo: Optional[datetime]  # Present only when Origin is EXTERNAL and ExpirationModel is KEY_MATERIAL_EXPIRES
    CustomKeyStoreId: Optional[str]  # Present only for custom key store
    CloudHsmClusterId: Optional[str]  # Present only for CloudHSM key store
    ExpirationModel: Optional[ExpirationModel]  # Present only when Origin is EXTERNAL
    CustomerMasterKeySpec: Optional[CustomerMasterKeySpec]  # Deprecated, use KeySpec instead
    EncryptionAlgorithms: Optional[List[EncryptionAlgorithm]]  # Present only when KeyUsage is ENCRYPT_DECRYPT
    SigningAlgorithms: Optional[List[SigningAlgorithm]]  # Present only when KeyUsage is SIGN_VERIFY
    KeyAgreementAlgorithms: Optional[List[KeyAgreementAlgorithm]]
    MultiRegion: Optional[bool]
    MultiRegionConfiguration: Optional[MultiRegionConfiguration]  # Present only when MultiRegion is True
    PendingDeletionWindowInDays: Optional[int]  # Present only when KeyState is PendingReplicaDeletion
    MacAlgorithms: Optional[List[MacAlgorithm]]  # Present only when KeyUsage is GENERATE_VERIFY_MAC
    XksKeyConfiguration: Optional[XksKeyConfiguration]  # Present only for external key store


class DescribeKeyResponse(KMSKeyMetadata):
    """Response type for describe_key operation"""
    pass


@dataclass
class EncryptionContext:
    """Encryption context for KMS operations."""
    context: Dict[str, str]

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the encryption context
        """
        return self.context


@dataclass
class GrantConstraints:
    """Constraints for KMS grants."""
    encryption_context_subset: Optional[Dict[str, str]] = None
    encryption_context_equals: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the grant constraints
        """
        constraints = {}
        if self.encryption_context_subset:
            constraints['EncryptionContextSubset'] = self.encryption_context_subset
        if self.encryption_context_equals:
            constraints['EncryptionContextEquals'] = self.encryption_context_equals
        return constraints


@dataclass
class Tag:
    """Tag for KMS resources."""
    key: str
    value: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the tag
        """
        return {
            'TagKey': self.key,
            'TagValue': self.value
        }


class CreateKeyRequest(TypedDict, total=False):
    """Request type for create_key operation"""
    Policy: str
    Description: str
    KeyUsage: KeyUsage
    CustomerMasterKeySpec: CustomerMasterKeySpec
    KeySpec: KeySpec
    Origin: OriginType
    CustomKeyStoreId: str
    BypassPolicyLockoutSafetyCheck: bool
    Tags: List[Dict[str, str]]
    MultiRegion: bool
    XksKeyId: str


class CreateKeyResponse(KMSKeyMetadata):
    """Response type for create_key operation"""
    pass