from dataclasses import dataclass, field, fields, Field
from typing import (
    Any,
    ClassVar,
    Literal,
    Self,
    TypedDict,
    TypeGuard,
    Union,
    Optional,
    Set,
    Type,
)
import json

from chainsaws.aws.shared.config import APIConfig


@dataclass(slots=True)
class KeySchemaElement:
    """DynamoDB key schema element."""

    attribute_name: str  # Name of the key attribute
    key_type: Literal["HASH", "RANGE"]  # Type of the key


@dataclass(slots=True)
class AttributeDefinitionElement:
    """DynamoDB attribute definition element."""

    attribute_name: str  # Name of the attribute
    attribute_type: Literal["S", "N", "B"]  # Type of the attribute


@dataclass(slots=True)
class StreamSpecificationElement:
    """DynamoDB stream specification."""

    stream_enabled: bool = True  # Enable/disable DynamoDB Streams
    stream_view_type: Literal["NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES",
                              "KEYS_ONLY"] = "NEW_AND_OLD_IMAGES"  # Type of information captured in the stream


@dataclass(kw_only=True)
class PartitionIndex:
    """Configuration for a partition index."""

    pk: str  # Primary key field for the index
    sk: str  # Sort key field for the index


@dataclass
class PartitionMapConfig:
    """Configuration for a single partition in the partition map."""

    pk: str  # Primary key field
    sk: str  # Sort key field
    uks: Optional[list[str]] = field(
        default_factory=list)  # List of unique key fields
    indexes: Optional[list[PartitionIndex]] = field(
        default_factory=list)  # List of secondary indexes


@dataclass
class PartitionMap:
    """Complete partition map configuration."""

    # Mapping of partition names to their configurations
    partitions: dict[str, PartitionMapConfig]


@dataclass
class DynamoDBConfig:
    """DynamoDB configuration settings."""

    region: str = "ap-northeast-2"  # AWS region for the DynamoDB table
    # Maximum number of connections in the connection pool
    max_pool_connections: int = 100

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.max_pool_connections <= 1000:
            raise ValueError("max_pool_connections must be between 1 and 1000")


@dataclass
class DynamoDBAPIConfig(APIConfig):
    """DynamoDB API configuration."""

    # Maximum number of connections in the connection pool
    max_pool_connections: int = 100
    endpoint_url: Optional[str] = None  # Endpoint URL for the DynamoDB API

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not 1 <= self.max_pool_connections <= 1000:
            raise ValueError("max_pool_connections must be between 1 and 1000")


# Filter condition types
FilterCondition = Literal[
    "eq", "neq", "lte", "lt", "gte", "gt", "btw",
    "stw", "is_in", "contains", "exist", "not_exist",
    "not_btw", "not_stw", "is_not_in", "not_contains",
]


class FilterDict(TypedDict):
    """Single filter condition."""

    field: str
    value: Any
    condition: FilterCondition


class RecursiveFilterBase(TypedDict):
    """Base for recursive filter operations."""

    field: str
    value: Any
    condition: FilterCondition


class RecursiveFilterNode(TypedDict):
    """Node in recursive filter tree."""

    left: Union["RecursiveFilterNode", RecursiveFilterBase]
    operation: Literal["and", "or"]
    right: Union["RecursiveFilterNode", RecursiveFilterBase]


@dataclass(kw_only=True, slots=True)
class DynamoIndex:
    """Index configuration for DynamoDB models."""

    pk: str
    sk: str


@dataclass(kw_only=True, slots=True)
class DynamoDBPartitionConfig:
    """Partition configuration for DynamoDB models."""

    partition: str
    pk_field: str
    sk_field: str
    indexes: list[DynamoIndex] = field(default_factory=list)


@dataclass(kw_only=True)
class DynamoModel:
    """Base model for DynamoDB models with partition configuration."""

    # System fields with aliases
    _id: Optional[str] = field(default=None, metadata={"exclude": True})
    _crt: Optional[int] = field(default=None, metadata={"exclude": True})
    _ptn: Optional[str] = field(default=None, metadata={"exclude": True})

    # Class variables for configuration
    _partition: ClassVar[str]
    _pk: ClassVar[str]
    _sk: ClassVar[str]
    _indexes: ClassVar[list[DynamoIndex]] = []

    # TTL field
    _ttl: ClassVar[Optional[float]] = None

    @classmethod
    def get_partition_config(cls) -> DynamoDBPartitionConfig:
        """Get partition configuration for this model."""
        return DynamoDBPartitionConfig(
            partition=cls._partition,
            pk_field=cls._pk,
            sk_field=cls._sk,
            indexes=cls._indexes,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_json(self) -> str:
        """Convert the model to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a model instance from a dictionary."""
        # Filter out unknown fields
        known_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

    @staticmethod
    def is_dynamo_model(model: type[Any]) -> TypeGuard[type["DynamoModel"]]:
        """Check if a type is a DynamoModel."""
        return (
            isinstance(model, type)
            and issubclass(model, DynamoModel)
            and hasattr(model, "_partition")
            and hasattr(model, "_pk")
            and hasattr(model, "_sk")
        )


class PKDescriptor:
    """Descriptor for partition key field."""

    def __init__(self, f: Field):
        self.field = f

    def __get__(self, obj, objtype=None):
        return self.field

    def __set_name__(self, owner, name):
        if hasattr(owner, '_pk'):
            raise ValueError(f"Multiple PK fields defined in {owner.__name__}")
        owner._pk = name


class SKDescriptor:
    """Descriptor for sort key field."""

    def __init__(self, f: Field):
        self.field = f

    def __get__(self, obj, objtype=None):
        return self.field

    def __set_name__(self, owner, name):
        if hasattr(owner, '_sk'):
            raise ValueError(f"Multiple SK fields defined in {owner.__name__}")
        owner._sk = name


def PK(*,
       default: Any = None,
       default_factory: Any = None,
       init: bool = True,
       repr: bool = True,
       hash: Optional[bool] = None,
       compare: bool = True,
       metadata: Optional[dict[Any, Any]] = None,
       kw_only: Optional[bool] = None,
       ) -> Any:
    """Decorator function for marking a field as the partition key.

    Args:
        default: Default value for the field if not provided
        default_factory: Function that returns the default value
        init: Whether to include the field in __init__
        repr: Whether to include the field in __repr__
        hash: Whether to include the field in __hash__
        compare: Whether to include the field in comparison methods
        metadata: Additional metadata for the field
        kw_only: Whether the field should be keyword-only in __init__
    """
    if default is not None and default_factory is not None:
        raise ValueError('cannot specify both default and default_factory')

    kwargs = {}
    if default is not None:
        kwargs['default'] = default
    if default_factory is not None:
        kwargs['default_factory'] = default_factory
    if init is not None:
        kwargs['init'] = init
    if repr is not None:
        kwargs['repr'] = repr
    if hash is not None:
        kwargs['hash'] = hash
    if compare is not None:
        kwargs['compare'] = compare
    if metadata is not None:
        kwargs['metadata'] = metadata
    if kw_only is not None:
        kwargs['kw_only'] = kw_only

    f = field(**kwargs)
    return PKDescriptor(f)


def SK(*,
       default: Any = None,
       default_factory: Any = None,
       init: bool = True,
       repr: bool = True,
       hash: Optional[bool] = None,
       compare: bool = True,
       metadata: Optional[dict[Any, Any]] = None,
       kw_only: Optional[bool] = None,
       ) -> Any:
    """Decorator function for marking a field as the sort key.

    Args:
        default: Default value for the field if not provided
        default_factory: Function that returns the default value
        init: Whether to include the field in __init__
        repr: Whether to include the field in __repr__
        hash: Whether to include the field in __hash__
        compare: Whether to include the field in comparison methods
        metadata: Additional metadata for the field
        kw_only: Whether the field should be keyword-only in __init__
    """
    if default is not None and default_factory is not None:
        raise ValueError('cannot specify both default and default_factory')

    kwargs = {}
    if default is not None:
        kwargs['default'] = default
    if default_factory is not None:
        kwargs['default_factory'] = default_factory
    if init is not None:
        kwargs['init'] = init
    if repr is not None:
        kwargs['repr'] = repr
    if hash is not None:
        kwargs['hash'] = hash
    if compare is not None:
        kwargs['compare'] = compare
    if metadata is not None:
        kwargs['metadata'] = metadata
    if kw_only is not None:
        kwargs['kw_only'] = kw_only

    f = field(**kwargs)
    return SKDescriptor(f)


_models_to_sync: Set[Type[DynamoModel]] = set()

def sync(cls: Type[DynamoModel]) -> Type[DynamoModel]:
    """
    Decorator to collect models that need partition synchronization
    """
    _models_to_sync.add(cls)
    return cls

def sync_all_models() -> None:
    """
    Batch synchronize all collected models at once
    """
    if _models_to_sync:
        from chainsaws.aws.dynamodb.dynamodb import DynamoDBAPI
        DynamoDBAPI.apply_model_partitions(*_models_to_sync)

    _models_to_sync.clear()
