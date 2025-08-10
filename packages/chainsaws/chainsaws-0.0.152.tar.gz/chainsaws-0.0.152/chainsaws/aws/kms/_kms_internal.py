from typing import Dict, Optional, List, Union, Any
from boto3 import Session, client

from chainsaws.aws.kms.kms_models import (
    KMSAPIConfig, KeyUsage, CustomerMasterKeySpec, KeyManager, OriginType, EncryptionContext, GrantConstraints, Tag, EncryptionAlgorithm
)


class KMS:
    """Internal class responsible for direct communication with AWS KMS service"""

    def __init__(self, boto3_session: Session, config: KMSAPIConfig) -> None:
        """Initialize KMS client

        Args:
            boto3_session: Boto3 session object
            config: KMS API configuration
        """
        self.boto3_session = boto3_session
        self.config = config or KMSAPIConfig()
        self.client: client = boto3_session.client(
            service_name="kms",
            region_name=self.config.region if self.config.region else None,
        )

    def create_key(
        self,
        description: str,
        tags: Optional[List[Tag]] = None,
        key_usage: KeyUsage = 'ENCRYPT_DECRYPT',
        customer_master_key_spec: CustomerMasterKeySpec = 'SYMMETRIC_DEFAULT',
        policy: Optional[str] = None,
        bypass_policy_lockout_safety_check: bool = False,
        origin: OriginType = 'AWS_KMS',
        custom_key_store_id: Optional[str] = None,
        valid_to: Optional[Any] = None,
        key_manager: KeyManager = 'CUSTOMER'
    ) -> Dict:
        """Create a new KMS key.

        Args:
            description: Description for the key
            tags: List of tags to apply to the key (optional)
            key_usage: Key usage purpose (default: ENCRYPT_DECRYPT)
            customer_master_key_spec: Key specification (default: SYMMETRIC_DEFAULT)
            policy: Key policy (optional)
            bypass_policy_lockout_safety_check: Whether to bypass policy lockout safety check
            origin: Key origin (default: AWS_KMS)
            custom_key_store_id: Custom key store ID (optional)
            valid_to: Key validity period (optional)
            key_manager: Key manager type (default: CUSTOMER)

        Returns:
            Dict: Response from AWS KMS API
        """
        params = {
            'Description': description,
            'KeyUsage': key_usage,
            'CustomerMasterKeySpec': customer_master_key_spec,
            'Origin': origin,
            'KeyManager': key_manager
        }

        if tags:
            params['Tags'] = [tag.to_dict() for tag in tags]
        if policy:
            params['Policy'] = policy
        if bypass_policy_lockout_safety_check:
            params['BypassPolicyLockoutSafetyCheck'] = True
        if custom_key_store_id:
            params['CustomKeyStoreId'] = custom_key_store_id
        if valid_to:
            params['ValidTo'] = valid_to

        return self.client.create_key(**params)

    def encrypt(
        self,
        key_id: str,
        plaintext: Union[str, bytes],
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        encryption_context: Optional[EncryptionContext] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Encrypt data"""
        params = {
            'KeyId': key_id,
            'Plaintext': plaintext
        }

        if encryption_algorithm:
            params['EncryptionAlgorithm'] = encryption_algorithm
        if encryption_context:
            params['EncryptionContext'] = encryption_context.to_dict()
        if grant_tokens:
            params['GrantTokens'] = grant_tokens

        return self.client.encrypt(**params)

    def decrypt(
        self,
        ciphertext_blob: Union[str, bytes],
        encryption_context: Optional[EncryptionContext] = None,
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        grant_tokens: Optional[List[str]] = None,
        key_id: Optional[str] = None
    ) -> Dict:
        """Decrypt data"""
        params = {
            'CiphertextBlob': ciphertext_blob
        }

        if encryption_algorithm:
            params['EncryptionAlgorithm'] = encryption_algorithm
        if encryption_context:
            params['EncryptionContext'] = encryption_context.to_dict()
        if grant_tokens:
            params['GrantTokens'] = grant_tokens
        if key_id:
            params['KeyId'] = key_id

        return self.client.decrypt(**params)

    def describe_key(
        self,
        key_id: str,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Get key details"""
        params = {'KeyId': key_id}
        if grant_tokens:
            params['GrantTokens'] = grant_tokens
        return self.client.describe_key(**params)

    def list_keys(
        self,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List KMS keys"""
        params = {}
        if limit:
            params['Limit'] = limit
        if marker:
            params['Marker'] = marker
        return self.client.list_keys(**params)

    def enable_key(self, key_id: str) -> Dict:
        """Enable a KMS key"""
        return self.client.enable_key(KeyId=key_id)

    def disable_key(self, key_id: str) -> Dict:
        """Disable a KMS key"""
        return self.client.disable_key(KeyId=key_id)

    def schedule_key_deletion(
        self,
        key_id: str,
        pending_window_in_days: int = 30
    ) -> Dict:
        """Schedule key deletion"""
        return self.client.schedule_key_deletion(
            KeyId=key_id,
            PendingWindowInDays=pending_window_in_days
        )

    def cancel_key_deletion(self, key_id: str) -> Dict:
        """Cancel scheduled key deletion"""
        return self.client.cancel_key_deletion(KeyId=key_id)

    def create_alias(
        self,
        alias_name: str,
        target_key_id: str
    ) -> Dict:
        """Create a key alias"""
        return self.client.create_alias(
            AliasName=alias_name,
            TargetKeyId=target_key_id
        )

    def delete_alias(self, alias_name: str) -> Dict:
        """Delete a key alias"""
        return self.client.delete_alias(AliasName=alias_name)

    def list_aliases(
        self,
        key_id: Optional[str] = None,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List key aliases"""
        params = {}
        if key_id:
            params['KeyId'] = key_id
        if limit:
            params['Limit'] = limit
        if marker:
            params['Marker'] = marker
        return self.client.list_aliases(**params)

    def generate_data_key(
        self,
        key_id: str,
        key_spec: str = 'AES_256',
        encryption_context: Optional[EncryptionContext] = None,
        number_of_bytes: Optional[int] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Generate a data key"""
        params = {
            'KeyId': key_id,
            'KeySpec': key_spec
        }

        if encryption_context:
            params['EncryptionContext'] = encryption_context.to_dict()
        if number_of_bytes:
            params['NumberOfBytes'] = number_of_bytes
        if grant_tokens:
            params['GrantTokens'] = grant_tokens

        return self.client.generate_data_key(**params)

    def generate_data_key_without_plaintext(
        self,
        key_id: str,
        key_spec: str = 'AES_256',
        encryption_context: Optional[EncryptionContext] = None,
        number_of_bytes: Optional[int] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Generate an encrypted data key without plaintext"""
        params = {
            'KeyId': key_id,
            'KeySpec': key_spec
        }

        if encryption_context:
            params['EncryptionContext'] = encryption_context.to_dict()
        if number_of_bytes:
            params['NumberOfBytes'] = number_of_bytes
        if grant_tokens:
            params['GrantTokens'] = grant_tokens

        return self.client.generate_data_key_without_plaintext(**params)

    def enable_key_rotation(self, key_id: str) -> Dict:
        """Enable automatic key rotation"""
        return self.client.enable_key_rotation(KeyId=key_id)

    def disable_key_rotation(self, key_id: str) -> Dict:
        """Disable automatic key rotation"""
        return self.client.disable_key_rotation(KeyId=key_id)

    def get_key_rotation_status(self, key_id: str) -> Dict:
        """Get key rotation status"""
        return self.client.get_key_rotation_status(KeyId=key_id)

    def list_resource_tags(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List resource tags"""
        params = {'KeyId': key_id}
        if limit:
            params['Limit'] = limit
        if marker:
            params['Marker'] = marker
        return self.client.list_resource_tags(**params)

    def tag_resource(
        self,
        key_id: str,
        tags: List[Tag]
    ) -> Dict:
        """Add tags to a resource"""
        return self.client.tag_resource(
            KeyId=key_id,
            Tags=[tag.to_dict() for tag in tags]
        )

    def untag_resource(
        self,
        key_id: str,
        tag_keys: List[str]
    ) -> Dict:
        """Remove tags from a resource"""
        return self.client.untag_resource(
            KeyId=key_id,
            TagKeys=tag_keys
        )

    def create_grant(
        self,
        key_id: str,
        grantee_principal: str,
        operations: List[str],
        retiring_principal: Optional[str] = None,
        constraints: Optional[GrantConstraints] = None,
        grant_tokens: Optional[List[str]] = None,
        name: Optional[str] = None
    ) -> Dict:
        """Create a grant"""
        params = {
            'KeyId': key_id,
            'GranteePrincipal': grantee_principal,
            'Operations': operations
        }

        if retiring_principal:
            params['RetiringPrincipal'] = retiring_principal
        if constraints:
            params['Constraints'] = constraints.to_dict()
        if grant_tokens:
            params['GrantTokens'] = grant_tokens
        if name:
            params['Name'] = name

        return self.client.create_grant(**params)

    def list_grants(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None,
        grant_id: Optional[str] = None,
        grantee_principal: Optional[str] = None
    ) -> Dict:
        """List grants"""
        params = {'KeyId': key_id}
        if limit:
            params['Limit'] = limit
        if marker:
            params['Marker'] = marker
        if grant_id:
            params['GrantId'] = grant_id
        if grantee_principal:
            params['GranteePrincipal'] = grantee_principal
        return self.client.list_grants(**params)

    def revoke_grant(
        self,
        key_id: str,
        grant_id: str
    ) -> Dict:
        """Revoke a grant"""
        return self.client.revoke_grant(
            KeyId=key_id,
            GrantId=grant_id
        )

    def retire_grant(
        self,
        grant_token: str,
        key_id: Optional[str] = None,
        grant_id: Optional[str] = None
    ) -> Dict:
        """Retire a grant"""
        params = {'GrantToken': grant_token}
        if key_id:
            params['KeyId'] = key_id
        if grant_id:
            params['GrantId'] = grant_id
        return self.client.retire_grant(**params)

    def get_key_policy(
        self,
        key_id: str,
        policy_name: str = 'default'
    ) -> Dict:
        """Get key policy"""
        return self.client.get_key_policy(
            KeyId=key_id,
            PolicyName=policy_name
        )

    def put_key_policy(
        self,
        key_id: str,
        policy: str,
        policy_name: str = 'default',
        bypass_policy_lockout_safety_check: bool = False
    ) -> Dict:
        """Set key policy"""
        return self.client.put_key_policy(
            KeyId=key_id,
            Policy=policy,
            PolicyName=policy_name,
            BypassPolicyLockoutSafetyCheck=bypass_policy_lockout_safety_check
        )

    def list_key_policies(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List key policies"""
        params = {'KeyId': key_id}
        if limit:
            params['Limit'] = limit
        if marker:
            params['Marker'] = marker
        return self.client.list_key_policies(**params)

    def re_encrypt(
        self,
        ciphertext_blob: Union[str, bytes],
        destination_key_id: str,
        source_encryption_context: Optional[EncryptionContext] = None,
        destination_encryption_context: Optional[EncryptionContext] = None,
        source_key_id: Optional[str] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Re-encrypt data"""
        params = {
            'CiphertextBlob': ciphertext_blob,
            'DestinationKeyId': destination_key_id
        }

        if source_encryption_context:
            params['SourceEncryptionContext'] = source_encryption_context.to_dict()
        if destination_encryption_context:
            params['DestinationEncryptionContext'] = destination_encryption_context.to_dict()
        if source_key_id:
            params['SourceKeyId'] = source_key_id
        if grant_tokens:
            params['GrantTokens'] = grant_tokens

        return self.client.re_encrypt(**params)

    def generate_random(
        self,
        number_of_bytes: Optional[int] = None,
        custom_key_store_id: Optional[str] = None
    ) -> Dict:
        """Generate cryptographically secure random data"""
        params = {}
        if number_of_bytes:
            params['NumberOfBytes'] = number_of_bytes
        if custom_key_store_id:
            params['CustomKeyStoreId'] = custom_key_store_id
        return self.client.generate_random(**params)
