from typing import Optional, Dict, List, Union
import base64
import os

from chainsaws.aws.kms._kms_internal import KMS
from chainsaws.aws.shared import session
from chainsaws.aws.kms.kms_models import (
    KMSAPIConfig, EncryptResponse, DecryptResponse, ListKeysResponse,
    KeyUsage, CustomerMasterKeySpec, OriginType, EncryptionContext,EncryptionAlgorithm,
    GrantConstraints, Tag, GenerateDataKeyResponse, GenerateRandomResponse, DescribeKeyResponse,
    KeySpec, CreateKeyRequest, CreateKeyResponse
)
from chainsaws.aws.kms.kms_exception import (
    KMSException, KMSValidationError, KMSKeyNotFoundError, KMSInvalidKeyStateError,
    KMSInvalidGrantTokenError, KMSMalformedPolicyDocumentError, KMSUnsupportedOperationError, KMSDisabledError,
    KMSUnsupportedKeySpecError
)


class KMSAPI:
    """High-level interface for AWS KMS service"""

    def __init__(self, config: Optional[KMSAPIConfig] = None) -> None:
        """Initialize KMS API client

        Args:
            config: KMS API configuration (optional)
        """
        self.config = config or KMSAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.kms = KMS(boto3_session=self.boto3_session, config=self.config)

    def create_key(
        self,
        description: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
        key_usage: KeyUsage = 'ENCRYPT_DECRYPT',
        key_spec: Optional[KeySpec] = None,
        customer_master_key_spec: Optional[CustomerMasterKeySpec] = None,
        policy: Optional[str] = None,
        bypass_policy_lockout_safety_check: bool = False,
        origin: OriginType = 'AWS_KMS',
        custom_key_store_id: Optional[str] = None,
        multi_region: Optional[bool] = None,
        xks_key_id: Optional[str] = None
    ) -> CreateKeyResponse:
        """Create a new KMS key.

        Args:
            description: Description for the key (optional)
            tags: List of tags to apply to the key (optional)
            key_usage: Key usage purpose (default: ENCRYPT_DECRYPT)
            key_spec: Key specification (optional)
            customer_master_key_spec: Customer master key specification (optional)
            policy: Key policy (optional)
            bypass_policy_lockout_safety_check: Whether to bypass policy lockout safety check
            origin: Key origin (default: AWS_KMS)
            custom_key_store_id: Custom key store ID (optional)
            multi_region: Whether to create a multi-region key (optional)
            xks_key_id: External key store key ID (optional)

        Returns:
            CreateKeyResponse: Response containing the key metadata

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
        """
        request: CreateKeyRequest = {}

        if description is not None:
            request['Description'] = description
        if tags:
            request['Tags'] = [tag.to_dict() for tag in tags]
        if key_usage:
            request['KeyUsage'] = key_usage
        if key_spec:
            request['KeySpec'] = key_spec
        if customer_master_key_spec:
            request['CustomerMasterKeySpec'] = customer_master_key_spec
        if policy:
            request['Policy'] = policy
        if bypass_policy_lockout_safety_check:
            request['BypassPolicyLockoutSafetyCheck'] = bypass_policy_lockout_safety_check
        if origin:
            request['Origin'] = origin
        if custom_key_store_id:
            request['CustomKeyStoreId'] = custom_key_store_id
        if multi_region is not None:
            request['MultiRegion'] = multi_region
        if xks_key_id:
            request['XksKeyId'] = xks_key_id

        response = self.kms.create_key(**request)
        return response['KeyMetadata']

    def encrypt(
        self,
        key_id: str,
        plaintext: Union[str, bytes],
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        encryption_context: Optional[EncryptionContext] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> EncryptResponse:
        """Encrypt data using a KMS key.

        Args:
            key_id: KMS key ID or ARN
            plaintext: Data to encrypt
            encryption_algorithm: Encryption algorithm (optional)
            encryption_context: Encryption context (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            EncryptResponse: {
                'CiphertextBlob': Encrypted data,
                'KeyId': Key ID used for encryption,
                'EncryptionAlgorithm': Algorithm used for encryption
            }

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
            KMSDisabledError: If key is disabled
            KMSInvalidKeyStateError: If key is in an invalid state
            KMSInvalidGrantTokenError: If grant token is invalid
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        try:
            response = self.kms.encrypt(
                key_id=key_id,
                plaintext=plaintext,
                encryption_algorithm=encryption_algorithm,
                encryption_context=encryption_context,
                grant_tokens=grant_tokens
            )
            return {
                'CiphertextBlob': response['CiphertextBlob'],
                'KeyId': response['KeyId'],
                'EncryptionAlgorithm': response['EncryptionAlgorithm']
            }
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")
        except self.kms.client.exceptions.DisabledException:
            raise KMSDisabledError(f"Key is disabled: {key_id}")
        except self.kms.client.exceptions.InvalidKeyUsageException:
            raise KMSInvalidKeyStateError(
                f"Key is in an invalid state: {key_id}")
        except self.kms.client.exceptions.InvalidGrantTokenException:
            raise KMSInvalidGrantTokenError("Invalid grant token")

    def decrypt(
        self,
        ciphertext: Union[str, bytes],
        encryption_context: Optional[EncryptionContext] = None,
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        grant_tokens: Optional[List[str]] = None,
        key_id: Optional[str] = None
    ) -> DecryptResponse:
        """Decrypt data using a KMS key.

        Args:
            ciphertext: Encrypted data to decrypt
            encryption_context: Encryption context (optional)
            encryption_algorithm: Encryption algorithm (optional)
            grant_tokens: Grant tokens (optional)
            key_id: KMS key ID or ARN (optional)

        Returns:
            DecryptResponse: {
                'Plaintext': Decrypted data as bytes,
                'KeyId': Key ID used for decryption,
                'EncryptionAlgorithm': Algorithm used for decryption
            }

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
            KMSDisabledError: If key is disabled
            KMSInvalidKeyStateError: If key is in an invalid state
            KMSInvalidGrantTokenError: If grant token is invalid
        """
        if not ciphertext:
            raise KMSValidationError("ciphertext is required")

        try:
            response = self.kms.decrypt(
                ciphertext_blob=ciphertext,
                encryption_context=encryption_context,
                encryption_algorithm=encryption_algorithm,
                grant_tokens=grant_tokens,
                key_id=key_id
            )
            return {
                'Plaintext': response['Plaintext'],
                'KeyId': response['KeyId'],
                'EncryptionAlgorithm': response['EncryptionAlgorithm']
            }
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")
        except self.kms.client.exceptions.DisabledException:
            raise KMSDisabledError(f"Key is disabled: {key_id}")
        except self.kms.client.exceptions.InvalidKeyUsageException:
            raise KMSInvalidKeyStateError(f"Key is in an invalid state: {key_id}")
        except self.kms.client.exceptions.InvalidGrantTokenException:
            raise KMSInvalidGrantTokenError("Invalid grant token")

    def describe_key(
        self,
        key_id: str,
        grant_tokens: Optional[List[str]] = None
    ) -> DescribeKeyResponse:
        """Get detailed information about a KMS key.

        Args:
            key_id: KMS key ID or ARN
            grant_tokens: Grant tokens (optional)

        Returns:
            DescribeKeyResponse: Detailed information about the KMS key including:
                - KeyMetadata: Key metadata including ID, ARN, state, usage, etc.

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.describe_key(
                key_id=key_id,
                grant_tokens=grant_tokens
            )
            return response['KeyMetadata']
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def list_keys(
        self,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> ListKeysResponse:
        """List KMS keys in the account.

        Args:
            limit: Maximum number of keys to return (optional)
            marker: Pagination marker (optional)

        Returns:
            ListKeysResponse: {
                'Keys': List of KMS keys with their IDs and ARNs,
                'NextMarker': Pagination token for the next page,
                'Truncated': Whether there are more keys to list
            }
        """
        response = self.kms.list_keys(limit=limit, marker=marker)
        return ListKeysResponse(
            Keys=response['Keys'],
            NextMarker=response.get('NextMarker'),
            Truncated=response.get('Truncated', False)
        )

    def enable_key(self, key_id: str) -> None:
        """Enable a KMS key.

        Args:
            key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.enable_key(key_id=key_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def disable_key(self, key_id: str) -> None:
        """Disable a KMS key.

        Args:
            key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.disable_key(key_id=key_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def schedule_key_deletion(
        self,
        key_id: str,
        pending_window_in_days: int = 30
    ) -> None:
        """Schedule key deletion.

        Args:
            key_id: KMS key ID or ARN
            pending_window_in_days: Number of days before deletion (default: 30)

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.schedule_key_deletion(
                key_id=key_id,
                pending_window_in_days=pending_window_in_days
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def cancel_key_deletion(self, key_id: str) -> None:
        """Cancel scheduled key deletion.

        Args:
            key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.cancel_key_deletion(key_id=key_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def create_alias(
        self,
        alias_name: str,
        target_key_id: str
    ) -> None:
        """Create a key alias.

        Args:
            alias_name: Name for the alias
            target_key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not alias_name or not target_key_id:
            raise KMSValidationError(
                "alias_name and target_key_id are required")

        try:
            self.kms.create_alias(
                alias_name=alias_name,
                target_key_id=target_key_id
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {target_key_id}")

    def delete_alias(self, alias_name: str) -> None:
        """Delete a key alias.

        Args:
            alias_name: Name of the alias to delete

        Raises:
            KMSValidationError: If alias_name is invalid
        """
        if not alias_name:
            raise KMSValidationError("alias_name is required")

        self.kms.delete_alias(alias_name=alias_name)

    def list_aliases(
        self,
        key_id: Optional[str] = None,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List key aliases.

        Args:
            key_id: KMS key ID or ARN (optional)
            limit: Maximum number of aliases to return (optional)
            marker: Pagination marker (optional)

        Returns:
            Dict: List of aliases and next page marker
        """
        response = self.kms.list_aliases(
            key_id=key_id,
            limit=limit,
            marker=marker
        )
        return {
            'Aliases': response['Aliases'],
            'NextMarker': response.get('NextMarker')
        }

    def generate_data_key(
        self,
        key_id: str,
        key_spec: KeySpec = 'AES_256',
        encryption_context: Optional[EncryptionContext] = None,
        number_of_bytes: Optional[int] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> GenerateDataKeyResponse:
        """Generate a data key.

        Args:
            key_id: KMS key ID or ARN
            key_spec: Key specification (default: AES_256)
            encryption_context: Encryption context (optional)
            number_of_bytes: Number of bytes to generate (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            GenerateDataKeyResponse: Generated data key and metadata

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
            KMSDisabledError: If key is disabled
            KMSInvalidKeyStateError: If key is in an invalid state
            KMSInvalidGrantTokenError: If grant token is invalid
            KMSUnsupportedKeySpecError: If key specification is not supported
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.generate_data_key(
                key_id=key_id,
                key_spec=key_spec,
                encryption_context=encryption_context,
                number_of_bytes=number_of_bytes,
                grant_tokens=grant_tokens
            )
            return {
                'Plaintext': response['Plaintext'],
                'CiphertextBlob': response['CiphertextBlob'],
                'KeyId': response['KeyId'],
                'EncryptionAlgorithm': response['EncryptionAlgorithm']
            }
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")
        except self.kms.client.exceptions.DisabledException:
            raise KMSDisabledError(f"Key is disabled: {key_id}")
        except self.kms.client.exceptions.InvalidKeyUsageException:
            raise KMSInvalidKeyStateError(
                f"Key is in an invalid state: {key_id}")
        except self.kms.client.exceptions.InvalidGrantTokenException:
            raise KMSInvalidGrantTokenError("Invalid grant token")
        except self.kms.client.exceptions.UnsupportedKeySpecException:
            raise KMSUnsupportedKeySpecError(
                f"Unsupported key specification: {key_spec}")

    def generate_data_key_without_plaintext(
        self,
        key_id: str,
        key_spec: str = 'AES_256',
        encryption_context: Optional[EncryptionContext] = None,
        number_of_bytes: Optional[int] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> GenerateDataKeyResponse:
        """Generate an encrypted data key without plaintext.

        Args:
            key_id: KMS key ID or ARN
            key_spec: Key specification (default: AES_256)
            encryption_context: Encryption context (optional)
            number_of_bytes: Number of bytes to generate (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            GenerateDataKeyResponse: Generated encrypted data key and metadata

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.generate_data_key_without_plaintext(
                key_id=key_id,
                key_spec=key_spec,
                encryption_context=encryption_context,
                number_of_bytes=number_of_bytes,
                grant_tokens=grant_tokens
            )
            return {
                'Plaintext': b'',  # Empty bytes for without_plaintext
                'CiphertextBlob': response['CiphertextBlob'],
                'KeyId': response['KeyId'],
                'EncryptionAlgorithm': response.get('EncryptionAlgorithm', 'SYMMETRIC_DEFAULT')
            }
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def enable_key_rotation(self, key_id: str) -> None:
        """Enable automatic key rotation.

        Args:
            key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.enable_key_rotation(key_id=key_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def disable_key_rotation(self, key_id: str) -> None:
        """Disable automatic key rotation.

        Args:
            key_id: KMS key ID or ARN

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.disable_key_rotation(key_id=key_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def get_key_rotation_status(self, key_id: str) -> bool:
        """Get key rotation status.

        Args:
            key_id: KMS key ID or ARN

        Returns:
            bool: True if key rotation is enabled, False otherwise

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.get_key_rotation_status(key_id=key_id)
            return response['KeyRotationEnabled']
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def list_resource_tags(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List resource tags.

        Args:
            key_id: KMS key ID or ARN
            limit: Maximum number of tags to return (optional)
            marker: Pagination marker (optional)

        Returns:
            Dict: List of tags and next page marker

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.list_resource_tags(
                key_id=key_id,
                limit=limit,
                marker=marker
            )
            return {
                'Tags': response['Tags'],
                'NextMarker': response.get('NextMarker')
            }
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def tag_resource(
        self,
        key_id: str,
        tags: List[Tag]
    ) -> None:
        """Add tags to a resource.

        Args:
            key_id: KMS key ID or ARN
            tags: List of tags to add

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.tag_resource(key_id=key_id, tags=tags)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def untag_resource(
        self,
        key_id: str,
        tag_keys: List[str]
    ) -> None:
        """Remove tags from a resource.

        Args:
            key_id: KMS key ID or ARN
            tag_keys: List of tag keys to remove

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.untag_resource(key_id=key_id, tag_keys=tag_keys)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

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
        """Create a grant.

        Args:
            key_id: KMS key ID or ARN
            grantee_principal: Principal to grant permissions to
            operations: List of operations to grant
            retiring_principal: Principal that can retire the grant (optional)
            constraints: Grant constraints (optional)
            grant_tokens: Grant tokens (optional)
            name: Name for the grant (optional)

        Returns:
            Dict: Created grant information

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            return self.kms.create_grant(
                key_id=key_id,
                grantee_principal=grantee_principal,
                operations=operations,
                retiring_principal=retiring_principal,
                constraints=constraints,
                grant_tokens=grant_tokens,
                name=name
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def list_grants(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None,
        grant_id: Optional[str] = None,
        grantee_principal: Optional[str] = None
    ) -> Dict:
        """List grants.

        Args:
            key_id: KMS key ID or ARN
            limit: Maximum number of grants to return (optional)
            marker: Pagination marker (optional)
            grant_id: Grant ID to filter by (optional)
            grantee_principal: Principal to filter by (optional)

        Returns:
            Dict: List of grants and next page marker

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            return self.kms.list_grants(
                key_id=key_id,
                limit=limit,
                marker=marker,
                grant_id=grant_id,
                grantee_principal=grantee_principal
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def revoke_grant(
        self,
        key_id: str,
        grant_id: str
    ) -> None:
        """Revoke a grant.

        Args:
            key_id: KMS key ID or ARN
            grant_id: ID of the grant to revoke

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.revoke_grant(key_id=key_id, grant_id=grant_id)
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def retire_grant(
        self,
        grant_token: str,
        key_id: Optional[str] = None,
        grant_id: Optional[str] = None
    ) -> None:
        """Retire a grant.

        Args:
            grant_token: Token of the grant to retire
            key_id: KMS key ID or ARN (optional)
            grant_id: ID of the grant to retire (optional)

        Raises:
            KMSValidationError: If grant_token is invalid
        """
        if not grant_token:
            raise KMSValidationError("grant_token is required")

        self.kms.retire_grant(
            grant_token=grant_token,
            key_id=key_id,
            grant_id=grant_id
        )

    def get_key_policy(
        self,
        key_id: str,
        policy_name: str = 'default'
    ) -> str:
        """Get key policy.

        Args:
            key_id: KMS key ID or ARN
            policy_name: Name of the policy (default: default)

        Returns:
            str: Key policy

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            response = self.kms.get_key_policy(
                key_id=key_id,
                policy_name=policy_name
            )
            return response['Policy']
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def put_key_policy(
        self,
        key_id: str,
        policy: str,
        policy_name: str = 'default',
        bypass_policy_lockout_safety_check: bool = False
    ) -> None:
        """Set key policy.

        Args:
            key_id: KMS key ID or ARN
            policy: Key policy
            policy_name: Name of the policy (default: default)
            bypass_policy_lockout_safety_check: Whether to bypass policy lockout safety check

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
            KMSMalformedPolicyDocumentError: If policy document is malformed
            KMSUnsupportedOperationError: If operation is not supported
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            self.kms.put_key_policy(
                key_id=key_id,
                policy=policy,
                policy_name=policy_name,
                bypass_policy_lockout_safety_check=bypass_policy_lockout_safety_check
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")
        except self.kms.client.exceptions.MalformedPolicyDocumentException:
            raise KMSMalformedPolicyDocumentError("Malformed policy document")
        except self.kms.client.exceptions.UnsupportedOperationException:
            raise KMSUnsupportedOperationError("Operation not supported")

    def list_key_policies(
        self,
        key_id: str,
        limit: Optional[int] = None,
        marker: Optional[str] = None
    ) -> Dict:
        """List key policies.

        Args:
            key_id: KMS key ID or ARN
            limit: Maximum number of policies to return (optional)
            marker: Pagination marker (optional)

        Returns:
            Dict: List of policy names and next page marker

        Raises:
            KMSValidationError: If key_id is invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        try:
            return self.kms.list_key_policies(
                key_id=key_id,
                limit=limit,
                marker=marker
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {key_id}")

    def re_encrypt(
        self,
        ciphertext: Union[str, bytes],
        destination_key_id: str,
        source_encryption_context: Optional[EncryptionContext] = None,
        destination_encryption_context: Optional[EncryptionContext] = None,
        source_key_id: Optional[str] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> Dict:
        """Re-encrypt data using a different key.

        Args:
            ciphertext: Encrypted data to re-encrypt
            destination_key_id: KMS key ID or ARN to re-encrypt with
            source_encryption_context: Source encryption context (optional)
            destination_encryption_context: Destination encryption context (optional)
            source_key_id: Source KMS key ID or ARN (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            Dict: Re-encrypted data and metadata

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
        """
        if not ciphertext or not destination_key_id:
            raise KMSValidationError(
                "ciphertext and destination_key_id are required")

        try:
            return self.kms.re_encrypt(
                ciphertext_blob=ciphertext,
                destination_key_id=destination_key_id,
                source_encryption_context=source_encryption_context,
                destination_encryption_context=destination_encryption_context,
                source_key_id=source_key_id,
                grant_tokens=grant_tokens
            )
        except self.kms.client.exceptions.NotFoundException:
            raise KMSKeyNotFoundError(f"Key not found: {destination_key_id}")

    def generate_random(
        self,
        number_of_bytes: Optional[int] = None,
        custom_key_store_id: Optional[str] = None
    ) -> GenerateRandomResponse:
        """Generate cryptographically secure random data.

        Args:
            number_of_bytes: Number of bytes to generate (optional)
            custom_key_store_id: Custom key store ID (optional)

        Returns:
            GenerateRandomResponse: Generated random data
        """
        response = self.kms.generate_random(
            number_of_bytes=number_of_bytes,
            custom_key_store_id=custom_key_store_id
        )
        return {
            'Plaintext': response['Plaintext'],
            'EncryptionAlgorithm': response.get('EncryptionAlgorithm', 'SYMMETRIC_DEFAULT')
        }

    def encrypt_string(
        self,
        key_id: str,
        text: str,
        encryption_context: Optional[EncryptionContext] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> str:
        """Encrypt a string and return the result as base64 encoded string.

        Args:
            key_id: KMS key ID or ARN
            text: String to encrypt
            encryption_context: Encryption context (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            str: Base64 encoded ciphertext

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
        """
        response = self.encrypt(key_id, text.encode(
            'utf-8'), encryption_context, grant_tokens)
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')

    def decrypt_string(
        self,
        ciphertext: str,
        encryption_context: Optional[EncryptionContext] = None,
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        grant_tokens: Optional[List[str]] = None,
        key_id: Optional[str] = None
    ) -> str:
        """Decrypt a base64 encoded ciphertext and return the result as string.

        Args:
            ciphertext: Base64 encoded ciphertext
            encryption_context: Encryption context (optional)
            encryption_algorithm: Encryption algorithm (optional)
            grant_tokens: Grant tokens (optional)
            key_id: KMS key ID or ARN (optional)

        Returns:
            str: Decrypted string

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
            KMSDisabledError: If key is disabled
            KMSInvalidKeyStateError: If key is in an invalid state
            KMSInvalidGrantTokenError: If grant token is invalid
        """
        try:
            ciphertext_blob = base64.b64decode(ciphertext)
            response = self.decrypt(
                ciphertext=ciphertext_blob,
                encryption_context=encryption_context,
                encryption_algorithm=encryption_algorithm,
                grant_tokens=grant_tokens,
                key_id=key_id
            )

            return response['Plaintext'].decode('utf-8')
        except base64.binascii.Error:
            raise KMSValidationError("Invalid base64 encoded ciphertext")
        except KMSException:
            raise
        except Exception as e:
            raise KMSValidationError(f"Failed to decrypt string: {str(e)}")

    def encrypt_file(
        self,
        key_id: str,
        input_file: Union[str, bytes, os.PathLike],
        output_file: Optional[Union[str, bytes, os.PathLike]] = None,
        encryption_context: Optional[EncryptionContext] = None,
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        grant_tokens: Optional[List[str]] = None
    ) -> str:
        """Encrypt a file using KMS.

        Args:
            key_id: KMS key ID or ARN
            input_file: Path to the file to encrypt
            output_file: Path where to save the encrypted file (optional)
            encryption_context: Encryption context (optional)
            encryption_algorithm: Encryption algorithm (optional)
            grant_tokens: Grant tokens (optional)

        Returns:
            str: Path to the encrypted file

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
            FileNotFoundError: If input file does not exist
            PermissionError: If cannot read input file or write output file
        """
        if not key_id:
            raise KMSValidationError("key_id is required")

        if not input_file:
            raise KMSValidationError("input_file is required")

    
        if output_file is None:
            output_file = str(input_file) + '.encrypted'

        try:
            with open(input_file, 'rb') as f:
                plaintext = f.read()

            response = self.encrypt(
                key_id=key_id,
                plaintext=plaintext,
                encryption_algorithm=encryption_algorithm,
                encryption_context=encryption_context,
                grant_tokens=grant_tokens
            )

            with open(output_file, 'wb') as f:
                f.write(response['CiphertextBlob'])

            return str(output_file)

        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {input_file}")
        except PermissionError:
            raise PermissionError(f"Permission denied accessing file: {input_file}")
        except Exception as e:
            raise KMSValidationError(f"Failed to encrypt file: {str(e)}")

    def decrypt_file(
        self,
        input_file: Union[str, bytes, os.PathLike],
        output_file: Optional[Union[str, bytes, os.PathLike]] = None,
        encryption_context: Optional[EncryptionContext] = None,
        encryption_algorithm: Optional[EncryptionAlgorithm] = None,
        grant_tokens: Optional[List[str]] = None,
        key_id: Optional[str] = None
    ) -> str:
        """Decrypt a file that was encrypted using KMS.

        Args:
            input_file: Path to the encrypted file
            output_file: Path where to save the decrypted file (optional)
            encryption_context: Encryption context (optional)
            encryption_algorithm: Encryption algorithm (optional)
            grant_tokens: Grant tokens (optional)
            key_id: KMS key ID or ARN (optional)

        Returns:
            str: Path to the decrypted file

        Raises:
            KMSValidationError: If input values are invalid
            KMSKeyNotFoundError: If key is not found
            FileNotFoundError: If input file does not exist
            PermissionError: If cannot read input file or write output file
        """
        if not input_file:
            raise KMSValidationError("input_file is required")

        if output_file is None:
            base_name = str(input_file)
            if base_name.endswith('.encrypted'):
                base_name = base_name[:-10]
            output_file = base_name + '.decrypted'

        try:
            # Read the encrypted file
            with open(input_file, 'rb') as f:
                ciphertext = f.read()

            # Decrypt the file contents
            response = self.decrypt(
                ciphertext=ciphertext,
                encryption_context=encryption_context,
                encryption_algorithm=encryption_algorithm,
                grant_tokens=grant_tokens,
                key_id=key_id
            )

            # Write the decrypted data
            with open(output_file, 'wb') as f:
                f.write(response['Plaintext'])

            return str(output_file)

        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {input_file}")
        except PermissionError:
            raise PermissionError(f"Permission denied accessing file: {input_file}")
        except Exception as e:
            raise KMSValidationError(f"Failed to decrypt file: {str(e)}")
