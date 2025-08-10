import copy
import json
import logging
import time
from collections.abc import Callable, Generator
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from functools import wraps
from typing import (
    Any,
    Optional,
    ParamSpec,
    TypeVar,
    Final,
    overload,
)

from chainsaws.aws.dynamodb._dynamodb_config import (
    DELIMITER,
    PARTITION_KEY_META_INFO,
    SORT_KEY_LENGTH,
)
from chainsaws.aws.dynamodb._dynamodb_internal import DynamoDB
from chainsaws.aws.dynamodb._dynamodb_utils import (
    convert_int_to_custom_base64,
    decode_dict,
    encode_dict,
    find_proper_index,
    format_value,
    merge_pk_sk,
    pop_system_keys,
    split_pk_sk,
    unsigned_number,
)
from chainsaws.aws.dynamodb.dynamodb_exception import (
    BatchOperationError,
    DynamoDBError,
    DynamoDBPartitionError,
    PartitionNotFoundError,
)
from chainsaws.aws.dynamodb.dynamodb_models import (
    DynamoDBAPIConfig,
    DynamoModel,
    FilterCondition,
    FilterDict,
    RecursiveFilterNode,
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DynamoModel)
R = TypeVar("R")
P = ParamSpec("P")


def validate_partition_keys(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to validate partition key fields."""
    @wraps(func)
    def wrapper(self: "DynamoDBAPI", *args: P.args, **kwargs: P.kwargs) -> R:
        partition = kwargs.get("partition")
        pk_field = kwargs.get("pk_field")
        sk_field = kwargs.get("sk_field")

        if not partition:
            msg = "Partition name is required"
            raise DynamoDBError(msg)

        # Get partition configuration
        partition_obj = self.get_partition(partition)
        if not partition_obj:
            raise PartitionNotFoundError(partition)

        # Collect all valid key fields
        valid_pk_fields: set[str] = {
            "_ptn", partition_obj.get("_pk_field", "")}
        valid_sk_fields: set[str] = {partition_obj.get("_sk_field", "")}

        for index in partition_obj.get("indexes", []):
            valid_pk_fields.add(index.get("_pk_field", ""))
            valid_sk_fields.add(index.get("_sk_field", ""))

        valid_pk_fields.discard("")
        valid_sk_fields.discard("")

        if pk_field and pk_field not in valid_pk_fields:
            msg = (
                f"Invalid partition key field '{
                    pk_field}' for partition '{partition}'.\n"
                f"Valid partition key fields:\n"
                f"- Primary: {partition_obj.get('_pk_field')}\n"
                f"- Indexes: {sorted(valid_pk_fields - {'_ptn',
                                     partition_obj.get('_pk_field', '')})}\n"
                f"- Special: '_ptn'"
            )
            raise DynamoDBError(
                msg,
            )

        # Validate sort key field
        if sk_field and sk_field not in valid_sk_fields:
            msg = (
                f"Invalid sort key field '{
                    sk_field}' for partition '{partition}'.\n"
                f"Valid sort key fields:\n"
                f"- Primary: {partition_obj.get('_sk_field')}\n"
                f"- Indexes: {sorted(valid_sk_fields -
                                     {partition_obj.get('_sk_field', '')})}"
            )
            raise DynamoDBError(
                msg,
            )

        return func(self, *args, **kwargs)
    return wrapper


class DynamoDBAPI:
    """High-level DynamoDB API with partition and index management."""

    def __init__(
        self,
        table_name: str,
        config: Optional[DynamoDBAPIConfig] = None,
    ) -> None:
        self.config = config or DynamoDBAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.table_name = table_name
        self.dynamo_db = DynamoDB(
            boto3_session=self.boto3_session,
            table_name=table_name,
            config=self.config,
        )
        self.cache: dict[str, Any] = {}

    def init_db_table(self) -> None:
        """Initialize DynamoDB table."""
        self.dynamo_db.init_db_table()

    def get_item(
        self,
        item_id: str,
        consistent_read: bool = True,
    ) -> dict[str, Any] | None:
        """Get single item by ID.

        Args:
            item_id: The ID of the item to retrieve, in format 'partition_key|sort_key'
            consistent_read: Whether to use strongly consistent reads

        Returns:
            The item data with system keys removed and values encoded, or None if not found

        Raises:
            Exception: If the provided item_id is invalid

        """
        # Split the item_id into partition key and sort key components
        pair = split_pk_sk(item_id)
        if not pair:
            msg = f'Invalid item_id: "{item_id}"'
            raise DynamoDBError(msg)

        _pk, _sk = pair

        # Retrieve the item from DynamoDB
        item = self.dynamo_db.get_item(_pk, _sk, consistent_read)

        if not item:
            return None

        item["_id"] = merge_pk_sk(
            partition_key=item["_pk"], sort_key=item["_sk"])

        # Remove system keys and encode values before returning
        return pop_system_keys(encode_dict(item))

    def get_items(
        self,
        item_ids: list[str],
        consistent_read: bool = False,
    ) -> list[dict[str, Any]]:
        """Batch query items by their IDs.

        Args:
            item_ids: List of item IDs to retrieve
            consistent_read: Whether to use strongly consistent reads

        Returns:
            List of items with system keys removed and values properly encoded

        """
        items = self.dynamo_db.get_items(
            pk_sk_pairs=[split_pk_sk(item_id) for item_id in item_ids],
            consistent_read=consistent_read,
        )

        for item in items:
            if item:
                item["_id"] = merge_pk_sk(item["_pk"], item["_sk"])
        # Cast values like Decimal to int/float
        return [pop_system_keys(encode_dict(item)) for item in items]

    @overload
    def put_item(
        self,
        partition: str,
        item: T,
        can_overwrite: bool = True,
    ) -> T: ...

    @overload
    def put_item(
        self,
        partition: str,
        item: dict[str, Any],
        can_overwrite: bool = True,
    ) -> dict[str, Any]: ...

    def put_item(
        self,
        partition: str,
        item: T | dict[str, Any],
        can_overwrite: bool = True
    ) -> T | dict[str, Any]:
        """Put a single item into DynamoDB

        Args:
            partition: Partition name to store the item in
            item: Item data to store
            can_overwrite: Whether existing items can be overwritten

        Returns:
            Dict[str, Any]: The stored item with system keys removed
        """
        # Check if the input is an instance of DynamoModel
        is_model = isinstance(item, DynamoModel)

        # Save the original model class
        model_class = item.__class__ if is_model else None

        # Convert to dictionary if it's a model
        item_dict = item.to_dict() if is_model else item
        processed_item = self.process_item_with_partition(item_dict, partition)
        _id = processed_item.get('_id', None)

        # Temporary remove _id to avoid conflict with DynamoDB primary key
        if '_id' in processed_item:
            processed_item.pop('_id')

        self.dynamo_db.put_item(item=processed_item,
                                can_overwrite=can_overwrite)

        # Restore _id after storing the item
        if _id:
            processed_item['_id'] = _id

        result = encode_dict(pop_system_keys(processed_item))

        # Convert back to model instance if input was a model
        if is_model and model_class:
            return model_class.from_dict(result)

        return result

    @overload
    def put_items(
        self,
        partition: str,
        items: list[T],
        can_overwrite: bool = True,
    ) -> list[T]: ...

    @overload
    def put_items(
        self,
        partition: str,
        items: list[dict[str, Any]],
        can_overwrite: bool = True,
    ) -> list[dict[str, Any]]: ...

    def put_items(
        self,
        partition: str,
        items: list[T] | list[dict[str, Any]],
        can_overwrite: bool = True,
    ) -> list[T] | list[dict[str, Any]]:
        """Put multiple items using batch operation.

        Args:
            partition: Partition name to store items in
            items: List of items to store (either all DynamoModel instances or all dictionaries)
            can_overwrite: Whether existing items can be overwritten

        Returns:
            List of processed items (same type as input)

        Raises:
            PartitionNotFoundError: If partition does not exist
            BatchOperationError: If batch operation fails

        """
        if not items:
            return []

        partition_obj = self.get_partition(partition)
        if not partition_obj:
            raise PartitionNotFoundError(partition)

        # Check if the first item is an instance of DynamoModel
        is_model = isinstance(items[0], DynamoModel)
        processed_items = []

        try:
            # Process each item with partition info
            items_to_put = []
            for item in items:
                # Convert to dictionary if it's a model
                item_dict = item.to_dict() if is_model else item

                processed_item = self.process_item_with_partition(
                    item_dict,
                    partition,
                )

                # Temporarily remove _id to avoid conflicts
                if "_id" in processed_item:
                    processed_item.pop("_id")

                items_to_put.append(processed_item)

            # Perform batch put operation
            success = self.dynamo_db.batch_put(
                items=items_to_put,
                can_overwrite=can_overwrite,
            )

            if not success:
                msg = "Failed to put items in batch"
                raise BatchOperationError(
                    message=msg,
                    succeeded_items=[],
                    failed_items=items,
                )

            # Process results
            for original_item, processed_item in zip(items, items_to_put, strict=False):
                if "_id" in original_item:
                    processed_item["_id"] = original_item["_id"]

                result = encode_dict(pop_system_keys(processed_item))

                if is_model:
                    # Use original item's class for conversion
                    result = original_item.__class__.from_dict(result)

                processed_items.append(result)

            return processed_items

        except Exception as e:
            logger.exception(f"Batch put operation failed: {e!s}")
            raise BatchOperationError(
                message=f"Failed to put items: {e!s}",
                failed_items=items,
            ) from e

    def _check_keys_cannot_update(self, partition_name: str) -> set[str]:
        """Return list of fields that cannot be updated (primary key and unique key fields).

        This method checks which fields in a partition cannot be updated by:
        1. Getting the partition configuration
        2. Identifying primary key fields (partition key and sort key)
        3. Identifying any unique key fields
        4. Combining them into a set of protected fields

        Args:
            partition_name: Name of the partition to check

        Returns:
            Set[str]: Set of field names that cannot be updated

        Raises:
            PartitionNotFoundError: If the specified partition does not exist

        """
        # Initialize empty set to store protected field names
        keys_cannot_update = set()

        # Get partition configuration, which contains key field definitions
        partition = self.get_partition(partition_name)

        # Validate partition exists
        if not partition:
            msg = f"No such partition: {partition_name}"
            raise PartitionNotFoundError(
                msg)

        pk_field = partition["_pk_field"]  # Partition key field (hash key)
        sk_field = partition["_sk_field"]  # Sort key field (range key)
        # List of unique key fields for indexes
        uk_fields = partition["_uk_fields"]

        # Add primary key fields to protected set
        # These fields form the table's primary key and cannot be modified
        keys_cannot_update.add(pk_field)
        keys_cannot_update.add(sk_field)

        # Add any unique key fields to protected set
        # Unique keys are used in GSIs and must remain immutable
        if uk_fields:
            for uk_field in uk_fields:
                keys_cannot_update.add(uk_field)

        return keys_cannot_update

    @overload
    def update_item(
        self,
        partition: str,
        item_id: str,
        item: T,
        consistent_read: bool = False,
    ) -> T: ...

    @overload
    def update_item(
        self,
        partition: str,
        item_id: str,
        item: dict[str, Any],
        consistent_read: bool = False,
    ) -> dict[str, Any]: ...

    def update_item(
        self,
        partition: str,
        item_id: str,
        item: T | dict[str, Any],
        consistent_read: bool = False,
    ) -> T | dict[str, Any]:
        """Update a single item in DynamoDB.

        Args:
            partition: Partition name where the item exists
            item_id: ID of the item to update
            item: Model instance or dictionary containing fields to update
            consistent_read: Use strong consistent read if True

        Returns:
            The updated item with system keys removed, same type as input

        Notes:
            1. Cannot update partition key (pk) and sort key (sk) fields
            2. Will validate that key fields are not being modified

        """
        # Check if the input is an instance of DynamoModel
        is_model = isinstance(item, DynamoModel)
        model_class = item.__class__ if is_model else None
        item_dict = item.to_dict() if is_model else item

        # Check if item exists in partition
        target_item = self.get_item(
            item_id=item_id, consistent_read=consistent_read)

        if not target_item:
            msg = f"No such item: {item_id}"
            raise DynamoDBError(msg)

        if target_item["_ptn"] != partition:
            msg = (
                f'Partition not match: {
                    partition} != {target_item["_ptn"]}'
            )
            raise DynamoDBError(msg)

        # Extract pk and sk from item_id
        origin_pk, origin_sk = split_pk_sk(merged_id=item_id)

        # Get list of fields that cannot be updated (keys)
        key_fields = self._check_keys_cannot_update(partition_name=partition)

        # Create copy to avoid modifying original
        item_to_insert = copy.deepcopy(item_dict)

        # Remove any key fields from update
        for key_field in key_fields:
            if key_field in item_to_insert:
                item_to_insert.pop(key_field)
                logger.warning(f"Cannot update key fields: {key_field}")

        # Process item and update indexes
        item_to_insert = self.process_item_with_partition(
            item_to_insert, partition, for_creation=False)

        # Remove system fields that cannot be updated
        ban_keys = ["_pk", "_sk", "_id", "_crt", "_ptn"]
        for ban_key in ban_keys:
            if ban_key in item_to_insert:
                item_to_insert.pop(ban_key)

        # Perform update
        response = self.dynamo_db.update_item(
            pk=origin_pk, sk=origin_sk, item=item_to_insert)

        attributes = response.get("Attributes", {})

        # Add item_id to response if successful
        if attributes:
            attributes["_id"] = item_id

        result = pop_system_keys(encode_dict(attributes))

        # Convert back to model instance if input was a model
        if is_model and model_class:
            return model_class.from_dict(result)

        return result

    @overload
    def update_items(
        self,
        partition: str,
        item_updates: dict[str, T],
        max_workers: int = 32,
    ) -> list[T]: ...

    @overload
    def update_items(
        self,
        partition: str,
        item_updates: dict[str, dict[str, Any]],
        max_workers: int = 32,
    ) -> list[dict[str, Any]]: ...

    def update_items(
        self,
        partition: str,
        item_updates: dict[str, T] | dict[str, dict[str, Any]],
        max_workers: int = 32,
    ) -> list[T] | list[dict[str, Any]]:
        """Update multiple items in parallel.

        Args:
            partition: Partition name where items exist
            item_updates: Dictionary mapping item_ids to update data
                        (either all model instances or all dictionaries)
            max_workers: Maximum number of parallel workers

        Returns:
            List of updated items (same type as input)

        Raises:
            BatchOperationError: If any update operation fails

        Example:
            # Using model instances
            updates = {
                "user#123": User(name="Updated Name"),
                "user#456": User(email="new@email.com")
            }
            updated_users = db.update_items(
                "user", updates)  # Returns List[User]

            # Using dictionaries
            updates = {
                "user#123": {"name": "Updated Name"},
                "user#456": {"email": "new@email.com"}
            }
            updated_items = db.update_items(
                "user", updates)  # Returns List[Dict]

        """
        if not item_updates:
            return []

        updated_items: list[T | dict[str, Any]] = []
        failed_updates: list[tuple[str, T | dict[str, Any]]] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for item_id, item in item_updates.items():
                futures.append(
                    executor.submit(
                        self.update_item,
                        partition=partition,
                        item_id=item_id,
                        item=item,
                    ),
                )

            for future, (item_id, original_item) in zip(futures, item_updates.items(), strict=False):
                try:
                    result = future.result()
                    updated_items.append(result)
                except Exception as e:
                    logger.exception(f"Failed to update item {item_id}: {e!s}")
                    failed_updates.append((item_id, original_item))

            if failed_updates:
                failed_ids = [item_id for item_id, _ in failed_updates]
                msg = "Failed to update items"
                raise BatchOperationError(
                    msg,
                    updated_items,
                    failed_ids,
                )

        return updated_items

    def delete_item(
        self,
        item_id: str,
    ) -> dict[str, Any]:
        """Delete single item by ID.

        Args:
            item_id: ID of the item to delete in format 'partition_key&sort_key'

        Returns:
            Dict containing the deleted item attributes

        Raises:
            DynamoDBError: If the item ID is invalid or the item does not exist
        """
        try:
            pk, sk = split_pk_sk(merged_id=item_id)
        except ValueError as e:
            raise e

        try:
            response = self.dynamo_db.delete_item(pk=pk, sk=sk)
            return encode_dict(response.get("Attributes", {}))
        except Exception as ex:
            msg = f"Failed to delete item {item_id}: {ex!s}"
            raise DynamoDBError(msg) from ex

    def delete_items(
        self,
        item_ids: list[str],
    ) -> None:
        """Delete multiple items by IDs in parallel.

        This method deletes multiple items from DynamoDB in a batch operation.
        It splits each item ID into partition key and sort key pairs before deletion.

        Args:
            item_ids: List of item IDs to delete. Each ID should be in the format
                     'partition_key|sort_key'

        Returns:
            None

        Raises:
            DynamoDBError: If any item ID is invalid

        Note:
            Uses DynamoDB batch delete operation which has a limit of 25 items per batch.
            For larger deletes, the underlying batch_delete method handles batching.

        """
        # Validate all item IDs first
        pk_sk_pairs = []
        invalid_ids = []

        for item_id in item_ids:
            pk, sk = split_pk_sk(merged_id=item_id)
            if not pk or not sk:
                invalid_ids.append(item_id)
            else:
                pk_sk_pairs.append((pk, sk))

        # Raise error if any invalid IDs found
        if invalid_ids:
            raise DynamoDBError(
                "Invalid item IDs found:\n" +
                "\n".join(f"- {item_id}" for item_id in invalid_ids),
            )

        # Proceed with batch delete if all IDs are valid
        return self.dynamo_db.batch_delete(pk_sk_pairs=pk_sk_pairs)

    @validate_partition_keys
    def query_items(
        self,
        partition: str,
        pk_field: Optional[str] = None,
        sk_field: Optional[str] = None,
        pk_value: Optional[Any] = None,
        sk_condition: Optional[FilterCondition] = None,
        sk_value: Optional[Any] = None,
        sk_second_value: Optional[Any] = None,
        start_key: Optional[str | dict[str, Any]] = None,
        limit: int = 100,
        max_scan_rep: int = 100,
        filters: Optional[list[FilterDict]] = None,
        recursive_filters: Optional[RecursiveFilterNode] = None,
        reverse: bool = False,
        consistent_read: bool = False,
        projection_fields: Optional[list[str]] = None,
    ) -> tuple[list[dict[str, Any]], Optional[str]]:
        """Query items with complex filtering.

        Args:
            partition: Partition name
            pk_field: Partition key field name
            sk_field: Sort key field name
            pk_value: Partition key value
            sk_condition: Sort key operation condition
            sk_value: Sort key value
            sk_second_value: Second sort key value for between operations
            filters: List of filter conditions. Example:
                [
                    {
                        'field': 'name',           # Field to filter on
                        'value': 'John',           # Value to compare against
                        # One of: eq|neq|lte|lt|gte|gt|btw|stw|is_in|contains|exist|not_exist
                        'condition': 'eq'
                    }
                ]
            recursive_filters: Nested filter conditions with AND/OR operations. Example:
                {
                    'left': {
                        'field': 'age',
                        'value': 25,
                        'condition': 'gte'
                    },
                    'operation': 'and',
                    'right': {
                        'left': {
                            'field': 'city',
                            'value': 'Seoul',
                            'condition': 'eq'
                        },
                        'operation': 'or',
                        'right': {
                            'field': 'status',
                            'value': 'active',
                            'condition': 'eq'
                        }
                    }
                }
            max_scan_rep: Maximum number of scan repetitions
            start_key: Start key for pagination
            limit: Maximum number of items to return
            reverse: Sort in descending order if True
            consistent_read: Use strong consistent read if True

        Returns:
            Tuple of (items, last_evaluated_key)

        """
        if not pk_field or not pk_value:
            pk_field, pk_value = "_ptn", partition

        if sk_value is not None and sk_field is None:
            msg = "sk_field is required when sk_value is provided"
            raise DynamoDBError(
                msg)
        if sk_value is not None and sk_condition is None:
            msg = "sk_condition is required when sk_value is provided"
            raise DynamoDBError(
                msg)
        if sk_second_value is not None and sk_value is None:
            msg = "sk_value is required when sk_second_value is provided"
            raise DynamoDBError(
                msg)

        # Get partition configuration
        partition_obj = self.get_partition(partition)
        if not partition_obj:
            raise PartitionNotFoundError(partition)

        # Initialize filter lists
        filters = filters or []
        recursive_filters = recursive_filters or {}

        # Find appropriate index
        index_name, pk_name, sk_name = find_proper_index(
            partition_object=partition_obj,
            pk_field=pk_field,
            sk_field=sk_field,
        )

        # Handle start_key
        if isinstance(start_key, str):
            start_key = json.loads(start_key)
            # One more check for string
            # NOTE: sometimes start_key need another json.loads
            if isinstance(start_key, str):
                start_key = json.loads(start_key)

        # Query items with pagination
        items = []
        end_key = start_key
        scan_count = 0

        while scan_count < max_scan_rep:
            batch_items, end_key = self._query_items_batch(
                pk_field=pk_field,
                pk_value=pk_value,
                sort_condition=sk_condition,
                partition=partition,
                sk_field=sk_field,
                sk_value=sk_value,
                sk_second_value=sk_second_value,
                start_key=end_key,
                filters=filters,
                limit=limit,
                reverse=reverse,
                consistent_read=consistent_read,
                index_name=index_name,
                pk_name=pk_name,
                sk_name=sk_name,
                recursive_filters=recursive_filters,
                projection_fields=projection_fields,
            )

            scan_count += 1
            items.extend(batch_items)

            if len(items) >= limit or not end_key:
                break

        # Filter and process items
        filtered_items = [
            encode_dict(obj=pop_system_keys(item))
            for item in items
            if item.get("_id") and item.get("_ptn")
        ]

        if end_key:
            end_key = json.dumps(obj=end_key)

        return filtered_items, end_key

    def _query_items_batch(
        self,
        pk_field: str,
        pk_value: Any,
        sort_condition: str | None = None,
        partition: str = "",
        sk_field: str = "",
        sk_value: Any | None = None,
        sk_second_value: Any | None = None,
        filters: list[dict[str, Any]] | None = None,
        start_key: dict[str, Any] | None = None,
        limit: int = 100,
        reverse: bool = False,
        consistent_read: bool = False,
        index_name: str | None = None,
        pk_name: str = "_pk",
        sk_name: str = "_sk",
        recursive_filters: dict[str, Any] | None = None,
        projection_fields: list[str] | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Execute a low-level optimized NoSQL query operation.

        Partition key fields are required for queries, while sort key fields help with
        sequential item querying. Sort key values can only be used when partition is provided,
        as sk_field is determined through the partition.

        Args:
            pk_field: Partition key field name
            pk_value: Partition key value
            sort_condition: Sort key condition
            partition: Partition name
            sk_field: Sort key field name
            sk_value: Sort key value
            sk_second_value: Second sort key value for between operations
            filters: List of filter conditions. Example:
                [
                    {
                        'field': '<FIELD>',
                        'value': '<VALUE>',
                        'second_value': '<SECOND_VALUE>' | None,  # For between operations
                        'condition': 'eq|neq|lte|lt|gte|gt|btw|stw|is_in|contains|exist|not_exist'
                    }
                ]
            start_key: Start key for pagination
            limit: Maximum number of items to return
            reverse: Sort in descending order if True
            consistent_read: Use strongly consistent reads if True
            index_name: Index name for querying (uses default parameters if None)
            pk_name: Partition key name in table/index
            sk_name: Sort key name in table/index
            recursive_filters: Nested filter conditions. Example:
                {
                    'left': {
                        'field': '<FIELD>',
                        'value': '<VALUE>',
                        'second_value': '<SECOND_VALUE>' | None,
                        'condition': 'eq|neq|lte|lt|gte|gt|btw|stw|is_in|contains|exist|not_exist'
                    },
                    'operation': 'and|or',
                    'right': {
                        'left': {...},
                        'operation': 'and|or',
                        'right': {...}
                    }
                }

        Returns:
            Tuple of (items, last_evaluated_key)

        """
        # Validate partition exists
        if partition is not None:
            partitions = self.get_partitions(use_cache=True)
            partitions_by_name = {
                p.get("_partition_name", None): p for p in partitions
            }
            partition_obj = partitions_by_name.get(partition)
            if not partition_obj:
                msg = f"No such partition: {partition}"
                raise DynamoDBError(msg)

        sk_digit_fit = SORT_KEY_LENGTH

        # Handle sort key value formatting
        if sk_value is not None:
            if isinstance(sk_value, int | float | Decimal):
                # Convert numeric sort key to base64 representation
                sk_value = convert_int_to_custom_base64(
                    number=unsigned_number(sk_value))
                sk_value = "D" + sk_value.rjust(sk_digit_fit)
                # For numeric equality, use starts_with condition
                if sort_condition == "eq":
                    sort_condition = "stw"
            else:
                # Handle string sort key
                sk_value = str(sk_value)
                if sort_condition == "eq":
                    # Add delimiter for exact matching using starts_with
                    sk_value = sk_value + DELIMITER
                    sort_condition = "stw"
                sk_value = "S" + sk_value
        else:
            sk_value = ""

        # Handle second sort key value for between operations
        if sk_second_value is not None:
            if isinstance(sk_second_value, int | float | Decimal):
                sk_second_value = convert_int_to_custom_base64(
                    number=unsigned_number(sk_second_value))
                sk_second_value = "D" + sk_second_value.rjust(sk_digit_fit)
            else:
                sk_second_value = str(sk_second_value)
                sk_second_value = "S" + sk_second_value
        else:
            sk_second_value = ""

        # Construct partition key
        if pk_field == "_ptn":
            # Optimize storage by using shorter representation for partition
            pk = f"{partition}"
        else:
            pk = f"{partition}#{pk_field}#{pk_value}"

        # Ensure minimum sort key field length
        if not sk_field:
            # Insert space character as minimum sort key prefix
            sk_field = " "

        # Construct sort key
        sk = f"{sk_field}"

        # Handle high range for between operations
        sk_high = ""
        if sk_second_value:
            sk_high = sk + f"#{sk_second_value}"
        if sk_value:
            sk += f"#{sk_value}"
            # Handle edge cases for GT and LTE conditions
            if sort_condition == "gt":
                # Prevent EQ condition overlap by adding highest possible value
                sk += "A"
            elif sort_condition == "lte":
                # Adjust postfix to be greater than '#'
                sk += "A"

        # Execute query
        response = self.dynamo_db.query_items(
            partition_key_name=pk_name, partition_key_value=pk,
            sort_condition=sort_condition, sort_key_name=sk_name, sort_key_value=sk,
            sort_key_second_value=sk_high,
            filters=filters,
            start_key=start_key,
            reverse=reverse,
            limit=limit,
            consistent_read=consistent_read,
            index_name=index_name,
            recursive_filters=recursive_filters,
            projection_fields=projection_fields,
        )

        end_key = response.get("LastEvaluatedKey", None)
        items = response.get("Items", [])

        # Generate unique IDs for items
        for item in items:
            if item:
                item["_id"] = merge_pk_sk(
                    partition_key=item["_pk"],
                    sort_key=item["_sk"],
                )

        return items, end_key

    def get_partitions(self, use_cache=False) -> list[dict[str, Any]]:
        """Get list of all partitions in the DynamoDB table.

        Args:
            use_cache: If True, returns cached partition list if available.
                      Cache is valid for 100 seconds.

        Returns:
            List of partition configuration dictionaries containing metadata
            like partition name, key fields, and indexes.

        """
        # Check cache first - cache key changes every 3600 seconds
        cache_key = "partitions" + str(int(time.time() // 3600))
        if use_cache and cache_key in self.cache:
            return [it.copy() for it in self.cache[cache_key]]

        # Query all partition metadata items using pagination
        items = []
        start_key = None
        while True:
            response = self.dynamo_db.query_items(
                partition_key_name="_pk", partition_key_value=PARTITION_KEY_META_INFO,
                sort_condition="gte", sort_key_name="_sk", sort_key_value=" ",
                limit=1000, consistent_read=True, start_key=start_key,
            )

            _items = response.get("Items", [])
            start_key = response.get("LastEvaluatedKey", None)
            items.extend(_items)

            # Break if no more pages
            if not start_key:
                break

        # Clean up internal DynamoDB keys that aren't needed
        for item in items:
            item.pop("_pk")
            item.pop("_sk")

        # Encode and cache the partition configurations
        items = [encode_dict(item) for item in items]
        items = [it.copy() for it in items]
        self.cache[cache_key] = items
        return items

    def get_partition(self, partition: str, use_cache: bool = True) -> dict[str, Any] | None:
        """Get configuration for a specific partition.

        Args:
            partition: Name of the partition to retrieve
            use_cache: If True, uses cached partition list if available

        Returns:
            Partition configuration dictionary if found, False otherwise

        """
        pts = self.get_partitions(use_cache=use_cache)
        for pt in pts:
            if pt["_partition_name"] == partition:
                return pt

        return False

    def process_item_with_partition(self, item: dict | DynamoModel, partition: str, for_creation=True) -> dict | DynamoModel:
        """Process item according to partition configuration before inserting into DB.

        Args:
            item: Item to process
            partition: Partition name
            for_creation: If False, prevents key duplication during updates

        Returns:
            Processed item with partition keys and indexes

        """
        partitions = self.get_partitions(use_cache=True)
        partitions_by_name = {
            p.get("_partition_name", None): p for p in partitions
        }
        partition_obj = partitions_by_name.get(partition)
        if not partition_obj:
            msg = f"No such partition: {partition}"
            raise DynamoDBError(msg)

        pk_field = partition_obj["_pk_field"]
        sk_field = partition_obj["_sk_field"]
        uk_fields = partition_obj.get("_uk_fields", [])

        # Get index information
        indexes = partition_obj.get("indexes", [])
        if for_creation:
            # Don't update timestamp during updates
            item["_crt"] = int(time.time())
        item["_ptn"] = partition
        item = decode_dict(item)

        pk_value = ""
        # Only validate pk/sk during creation
        if for_creation:
            if pk_field not in item:
                msg = f'pk_field:["{pk_field}"] should in item'
                raise DynamoDBError(msg)
            if sk_field and sk_field not in item:
                msg = f'sk_field:["{sk_field}"] should in item'
                raise DynamoDBError(msg)
            pk_value = item[pk_field]

        # Generate sort key value
        sk_value = item[sk_field] if sk_field and sk_field in item else ""

        # Format value - right justify numbers, left justify strings
        sk_value = format_value(sk_value)

        if sk_field is None:
            # Prevent None from being inserted directly
            sk_field = ""
        # pk = f'{pk_group}#{pk_field}#{pk_value}'
        # sk = f'{sk_group}#{partition}#{sk_field}#{sk_value}'
        if pk_field == "_ptn":
            # Optimize storage by reducing redundancy when pk_field is partition
            pk = f"{partition}"
        else:
            pk = f"{partition}#{pk_field}#{pk_value}"
        sk = f"{sk_field}#{sk_value}"

        if uk_fields:
            for uk_field in uk_fields:
                uk_value = item.get(uk_field, "")
                # Format value for consistent length
                uk_value = format_value(uk_value)
                sk += f"#{uk_field}#{uk_value}"

        item["_pk"] = pk
        item["_sk"] = sk

        # Map index fields
        for index in indexes:
            pk_name = index["pk_name"]  # e.g. _pk2
            sk_name = index["sk_name"]  # e.g. _sk2
            pk_field = index["_pk_field"]
            sk_field = index["_sk_field"]
            has_pk = pk_field in item
            has_sk = sk_field in item

            pk_value = item.get(pk_field, None)

            sk_value = item.get(sk_field, "") if sk_field else ""

            # Format value - right justify numbers, left justify strings
            sk_value = format_value(sk_value)

            if sk_field is None:
                # Prevent None from being inserted directly
                sk_field = ""

            # Generate index pk/sk values
            # _pk_v = f'{pk_group}#{pk_field}#{pk_value}'
            # _sk_v = f'{sk_group}#{partition}#{sk_field}#{sk_value}'
            if pk_field == "_ptn":
                # Optimize storage by reducing redundancy when pk_field is partition
                _pk_v = f"{partition}"
            else:
                _pk_v = f"{partition}#{pk_field}#{pk_value}"
            _sk_v = f"{sk_field}#{sk_value}"

            if for_creation:
                # Always insert index keys for new items
                item[pk_name] = _pk_v
                item[sk_name] = _sk_v
            else:
                # For updates, only insert index keys if explicitly updated
                if has_pk:
                    item[pk_name] = _pk_v
                if has_sk:
                    item[sk_name] = _sk_v

        item["_id"] = merge_pk_sk(partition_key=pk, sort_key=sk)
        return item

    @validate_partition_keys
    def generate_items(
        self,
        partition: str,
        pk_field: str | None = None,
        sk_field: str | None = None,
        pk_value: str | None = None,
        sk_condition: FilterCondition | None = None,
        sk_value: str | None = None,
        sk_second_value: str | None = None,
        filters: list[FilterDict] | None = None,
        recursive_filters: RecursiveFilterNode | None = None,
        reverse: bool = False,
        consistent_read: bool = False,
        limit: int = 500,
        max_scan_rep: int = 100,
    ) -> Generator[dict[str, Any], None, None]:
        """Generate all items from the query API in a convenient generator format.

        Args:
            partition: Partition to query
            pk_field: Partition key field name
            sk_field: Sort key field name
            pk_value: Partition key value to match
            sk_condition: Sort key condition operator
            sk_value: Sort key value to compare
            sk_second_value: Second sort key value for between conditions
            filters: List of filter conditions to apply
            recursive_filters: Recursive filter conditions
            reverse: Whether to return items in reverse order
            consistent_read: Whether to use strongly consistent reads
            limit: Maximum number of items per page
            max_scan_rep: Maximum number of scan repetitions

        Returns:
            Generator yielding items from the query results

        """
        start_key = None

        while True:
            items, end_key = self.query_items(
                partition=partition,
                pk_field=pk_field,
                sk_field=sk_field,
                pk_value=pk_value,
                sk_condition=sk_condition,
                sk_value=sk_value,
                sk_second_value=sk_second_value,
                filters=filters,
                recursive_filters=recursive_filters,
                max_scan_rep=max_scan_rep,
                start_key=start_key,
                limit=limit,
                reverse=reverse,
                consistent_read=consistent_read,
            )

            start_key = end_key
            yield from items

            if not end_key:
                break

    def copy_partition(
        self,
        source_partition: str,
        target_partition: str,
        transform_func: Callable[[dict[str, Any]],
                                 dict[str, Any]] | None = None,
        batch_size: int = 1000,
        max_workers: int = 10,
    ) -> None:
        """Copy items from one partition to another."""
        try:
            # Validate partitions exist
            if not self.get_partition(source_partition):
                raise PartitionNotFoundError(source_partition)
            if not self.get_partition(target_partition):
                raise PartitionNotFoundError(target_partition)

            items = self.generate_items(source_partition)

            if transform_func:
                items = [transform_func(item) for item in items]

            failed_batches = []
            processed_count = 0

            for batch in [items[i:i + batch_size] for i in range(0, len(items), batch_size)]:
                try:
                    self.put_items(target_partition, batch,
                                   max_workers=max_workers)
                    processed_count += len(batch)
                    logger.info(
                        f"Copied {len(batch)} items from {
                            source_partition} to {target_partition} "
                        f"(total: {processed_count})",
                    )
                except Exception as ex:
                    logger.exception(f"Failed to copy batch to {
                        target_partition}: {ex!s}")
                    failed_batches.append(batch)

            if failed_batches:
                msg = (
                    f"Failed to copy {sum(len(b)
                                          for b in failed_batches)} items"
                )
                raise BatchOperationError(
                    msg,
                    succeeded_items=[
                        item for batch in items if batch not in failed_batches
                        for item in batch
                    ],
                    failed_items=[
                        item for batch in failed_batches
                        for item in batch
                    ],
                )

        except Exception as ex:
            msg = (
                f"Failed to copy partition from '{
                    source_partition}' to '{target_partition}': {ex!s}"
            )
            raise DynamoDBPartitionError(
                msg,
            ) from ex

    def scan_items(
        self,
        filters: list[FilterDict] | None = None,
        recursive_filters: RecursiveFilterNode | None = None,
        start_key: dict[str, Any] | None = None,
        limit: int = 1000,
    ):
        """Generate scanned items (memory efficient)."""
        while True:
            items, last_key = self.dynamo_db.scan_table(
                filters=filters,
                recursive_filters=recursive_filters,
                start_key=start_key,
                limit=limit,
            )

            yield from items

            if not last_key:
                break

            start_key = json.loads(last_key)

    def get_partition_names(self) -> list[str]:
        """Get all partition names."""
        response = self.dynamo_db.query_items(
            table_name=self.table_name,
            partition_key_name="_pk",
            partition_key_value=PARTITION_KEY_META_INFO,
        )

        return [
            item["_sk"]
            for item in response.get("Items", [])
            if item.get("_sk")
        ]

    def delete_partition(self, partition: str) -> None:
        """Delete a partition and all its items."""
        try:
            # Delete partition configuration
            self.dynamo_db.delete_item(
                PARTITION_KEY_META_INFO,
                partition,
            )

            # Delete all items in partition
            items = self.generate_items(partition)
            item_ids = [item["_id"] for item in items]
            self.delete_items(partition, item_ids)

            # Clear cache
            cache_key = f"partition_{partition}"
            if cache_key in self.cache:
                del self.cache[cache_key]

            logger.info(f"Deleted partition: {partition}")

        except Exception as ex:
            logger.exception(f"Failed to delete partition {partition}: {ex!s}")
            msg = f"Failed to delete partition {partition}: {ex!s}"
            raise DynamoDBPartitionError(
                msg,
            ) from ex

    def apply_partition_map(
        self,
        partition_map: dict[str, dict[str, Any]],
    ) -> None:
        """Apply partition map configuration to DynamoDB table.

        Args:
            partition_map: Configuration dictionary in format:
                {
                    "<partition_name>": {
                        "pk": "_ptn",  # Primary partition key
                        "sk": "_crt",  # Primary sort key
                        "uks": None,   # Unique keys
                        "indexes": [    # GSI configurations
                            {
                                "pk": "_ptn",
                                "sk": "_crt"
                            },
                            {
                                "pk": "_ptn",
                                "sk": "phone"
                            }
                        ]
                    }
                }

        Raises:
            ValueError: If partition map configuration is invalid

        """
        self._validate_partition_map(partition_map)

        # Get existing partitions
        existing_partitions = self.get_partitions(use_cache=False)
        existing_partition_names = {
            partition["_partition_name"] for partition in existing_partitions
        }

        # Apply partition configurations
        for partition_name, config in partition_map.items():
            self._apply_partition_config(
                partition_name=partition_name,
                config=config,
                exists=partition_name in existing_partition_names,
            )

    def _validate_partition_map(
        self,
        partition_map: dict[str, dict[str, Any]],
    ) -> None:
        """Validate partition map structure and content.

        Args:
            partition_map: Partition configuration dictionary

        Raises:
            ValueError: If validation fails

        """
        for partition_name, config in partition_map.items():
            # Validate partition name
            if not isinstance(partition_name, str):
                msg = (
                    f"Partition name '{
                        partition_name}' must be a string"
                )
                raise DynamoDBPartitionError(msg)

            # Validate partition config
            if not isinstance(config, dict):
                msg = (
                    f"Config for partition '{
                        partition_name}' must be a dictionary"
                )
                raise DynamoDBPartitionError(msg)

            # Validate required fields
            if "pk" not in config or "sk" not in config:
                msg = (
                    f"Both 'pk' and 'sk' are required in config for partition '{
                        partition_name}'"
                )
                raise DynamoDBPartitionError(
                    msg,
                )

            # Validate indexes if present
            if "indexes" in config:
                if not isinstance(config["indexes"], list):
                    msg = (
                        f"'indexes' for partition '{
                            partition_name}' must be a list"
                    )
                    raise DynamoDBPartitionError(
                        msg,
                    )

                for index in config["indexes"]:
                    if not isinstance(index, dict):
                        msg = (
                            f"Each index in partition '{
                                partition_name}' must be a dictionary"
                        )
                        raise DynamoDBPartitionError(
                            msg,
                        )
                    if "pk" not in index or "sk" not in index:
                        msg = (
                            f"Both 'pk' and 'sk' are required in each index for partition '{
                                partition_name}'"
                        )
                        raise DynamoDBPartitionError(
                            msg,
                        )

    def _apply_partition_config(
        self,
        partition_name: str,
        config: dict[str, Any],
        exists: bool,
    ) -> None:
        """Apply configuration for a single partition.

        Args:
            partition_name: Name of the partition
            config: Partition configuration
            exists: Whether partition already exists

        """
        # Update or create partition
        if exists:
            self.update_partition(
                partition=partition_name,
                pk_field=config["pk"],
                sk_field=config["sk"],
                uk_fields=config.get("uks", []),
            )

            logger.info(f"Updated partition: {partition_name}")
        else:
            self.create_partition(
                partition=partition_name,
                pk_field=config["pk"],
                sk_field=config["sk"],
                uk_fields=config.get("uks", []),
                create_default_index=True,
            )

            logger.info(f"Created partition: {partition_name}")

        # Apply index configurations
        for index in config.get("indexes", []):
            try:
                response = self.append_index(
                    partition_name=partition_name,
                    pk_field=index["pk"],
                    sk_field=index["sk"],
                )
                logger.info(f"Added index: {response}")
            except Exception as ex:
                logger.info(f"Index already exists: {ex!s}")

    def apply_model_partitions(self, *models: type[DynamoModel]) -> None:
        """Apply partition configurations from model classes.

        Args:
            *models: Model classes that inherit from DynamoModel

        Raises:
            TypeError: If any model is not a valid DynamoModel subclass
            ValueError: If partition key, sort key or index fields don't exist in model
        """
        if not models:
            raise DynamoDBError("No models to apply partition configuration")

        invalid_models = [
            model.__name__ for model in models
            if not DynamoModel.is_dynamo_model(model)
        ]

        if invalid_models:
            msg = (
                f"All models must be DynamoModel subclasses with required attributes. The required attributes are: _partition, _pk, _sk\nInvalid models: {
                    ', '.join(invalid_models)}"
            )
            raise DynamoDBError(msg)

        default_keys = ['_ptn', '_crt']

        for model in models:
            model_fields = model.__annotations__.keys()

            # Check partition and sort keys
            if model._pk not in model_fields and model._pk not in default_keys:
                raise DynamoDBPartitionError(message=f"Partition key '{
                    model._pk}' not found in model {model.__name__}")
            if model._sk not in model_fields and model._sk not in default_keys:
                raise DynamoDBPartitionError(message=f"Sort key '{model._sk}' not found in model {
                    model.__name__}")

            # Check index fields
            for idx in model._indexes:
                if idx.pk not in model_fields and idx.pk != "_ptn":
                    raise DynamoDBPartitionError(message=f"Index partition key '{
                        idx.pk}' not found in model {model.__name__}")
                if idx.sk not in model_fields and idx.sk != "_crt":
                    raise DynamoDBPartitionError(message=f"Index sort key '{
                        idx.sk}' not found in model {model.__name__}")

        partition_map = {}
        for model in models:
            config = model.get_partition_config()
            partition_map[config.partition] = {
                "pk": config.pk_field,
                "sk": config.sk_field,
                "indexes": [
                    {"pk": idx.pk, "sk": idx.sk}
                    for idx in config.indexes
                ],
            }

        self.apply_partition_map(partition_map)

    def create_partition(
        self,
        partition: str,
        pk_field: str,
        sk_field: str | None = None,
        uk_fields: list[str] | None = None,
        create_default_index: bool = True,
    ) -> dict[str, Any]:
        """Create or declare a partition in DynamoDB.

        This method creates a partition configuration. If the partition already exists,
        it will be updated. Note that deleting a partition does not delete its internal data.

        Args:
            partition: Partition name (e.g., 'order')
            pk_field: Partition key field (e.g., 'user_id'). Used for parallel processing
                    and debugging. The actual DB pk field will contain '<pk_field>#<pk.value>'
            sk_field: Sort key field (e.g., 'created_at'). Useful for date-based sorting
            uk_fields: Additional fields appended to sort key. Useful for preventing duplicate data
            create_default_index: If True, creates default index with '_ptn' and '_crt'

        Returns:
            Dict containing the created partition attributes

        """
        self._remove_partition_cache()

        response = self.dynamo_db.put_item(item={
            "_pk": PARTITION_KEY_META_INFO,
            "_sk": partition,
            "_partition_name": partition,
            "_pk_field": pk_field,
            "_sk_field": sk_field,
            "_uk_fields": uk_fields,
            "_crt": int(time.time()),
        }, can_overwrite=False)

        result_item = response.get("Attributes", {})

        if create_default_index:
            self.append_index(
                partition_name=partition,
                pk_field="_ptn",
                sk_field="_crt",
            )

        return result_item

    def update_partition(
        self,
        partition: str,
        pk_field: str,
        sk_field: str | None = None,
        uk_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing partition in DynamoDB.

        Updates partition configuration. Note that modifying a partition
        does not affect its existing data.

        Args:
            partition: Partition name (e.g., 'order')
            pk_field: Partition key field (e.g., 'user_id'). Used for parallel processing
                    and debugging. The actual DB pk field will contain '<pk_field>#<pk.value>'
            sk_field: Sort key field (e.g., 'created_at'). Useful for date-based sorting
            uk_fields: Additional fields appended to sort key. Useful for preventing duplicate data

        Returns:
            Dict containing the updated partition attributes

        """
        self._remove_partition_cache()

        response = self.dynamo_db.update_item(
            pk=PARTITION_KEY_META_INFO,
            sk=partition,
            item={
                "_pk_field": pk_field,
                "_sk_field": sk_field,
                "_uk_fields": uk_fields,
                "_crt": int(time.time()),
            })
        return response.get("Attributes", {})

    def append_index(
        self,
        partition_name: str,
        pk_field: str,
        sk_field: str,
    ) -> dict[str, Any]:
        """Appends a new index to a partition.

        Args:
            partition_name: Name of the partition to add index to.
            pk_field: Partition key field for the index.
            sk_field: Sort key field for the index.

        Returns:
            Dict containing the updated partition attributes.

        Raises:
            DynamoDBPartitionError: If partition not found or index already exists.
        """
        partitions = self.get_partitions()
        partitions = [p for p in partitions if p.get(
            '_partition_name', '') == partition_name]

        if not partitions:
            raise DynamoDBPartitionError(
                f'No such partition: {partition_name}')

        partition = partitions[0]
        indexes = partition.get('indexes', [])

        MAX_GSI_LIMIT: Final[int] = 20

        # Find lowest available index number
        index_number = None
        for idx_num in range(1, MAX_GSI_LIMIT):
            has_number = False
            for index in indexes:
                if index['index_number'] == idx_num:
                    has_number = True
            if not has_number:
                index_number = idx_num
                break

        if not index_number:
            raise DynamoDBPartitionError(
                message='Maximum number of allowed indexes exceeded')

        pk_name = f"_pk{index_number}"
        sk_name = f"_sk{index_number}"
        index_name = f'{pk_name}-{sk_name}'

        try:
            # Create physical index in DynamoDB if it doesn't exist
            self.dynamo_db.create_db_partition_index(
                index_name=index_name,
                pk_name=pk_name,
                sk_name=sk_name,
            )
        except Exception as ex:
            logger.info("Index creation error: %s", str(ex))
            pass

        for index in indexes:
            if index['_pk_field'] == pk_field and index['_sk_field'] == sk_field:
                raise DynamoDBPartitionError(
                    message='<_pk_field> & <_sk_field>  already exist in index')

        index_item = {
            '_pk_field': pk_field,
            '_sk_field': sk_field,
            'pk_name': pk_name,
            'sk_name': sk_name,
            'index_number': index_number,
            'index_name': index_name
        }

        indexes.append(index_item)
        partition['indexes'] = indexes

        return self.dynamo_db.update_item(
            pk=PARTITION_KEY_META_INFO,
            sk=partition_name,
            item={
                'indexes': indexes
            }
        )

    def detach_index(self, partition_name: str, index_name: str) -> dict[str, Any]:
        """Detach an index from a partition.

        Args:
            partition_name: Name of the partition
            index_name: Name of the index to detach

        Returns:
            Updated partition configuration

        Raises:
            DynamoDBError: If partition does not exist

        """
        # Get partition configuration
        partition = next(
            (p for p in self.get_partitions() if p.get(
                "_partition_name") == partition_name),
            None,
        )
        if not partition:
            msg = f"No such partition: {partition_name}"
            raise DynamoDBError(msg)

        # Remove index from configuration
        indexes = [
            index for index in partition.get("indexes", [])
            if index.get("index_name") != index_name
        ]

        # Update partition configuration
        return self.dynamo_db.update_item(
            pk=PARTITION_KEY_META_INFO,
            sk=partition_name,
            item={"indexes": indexes},
        )

    def _remove_partition_cache(self) -> None:
        """Remove cache, needed when adding a new partition."""
        keys_to_delete = [k for k in list(self.cache.keys()) if k.startswith("partitions")]
        for k in keys_to_delete:
            self.cache.pop(k, None)
