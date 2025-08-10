"""Neptune API wrapper for graph database operations with ORM-like features.

This module provides a high-level interface for AWS Neptune graph database operations:
- Simplified vertex and edge operations
- ORM-like model definitions for graph entities
- Type-safe query builders for Gremlin and SPARQL
- Transaction support and connection management
- Comprehensive error handling
"""

from chainsaws.aws.neptune.neptune import NeptuneAPI
from chainsaws.aws.neptune.neptune_models import (
    NeptuneAPIConfig,
    GraphModel,
    Vertex,
    Edge,
    VertexProperty,
    EdgeProperty,
    GraphQuery,
    QueryResult,
)
from chainsaws.aws.neptune.neptune_exception import (
    NeptuneError,
    NeptuneConnectionError,
    NeptuneQueryError,
    NeptuneModelError,
    NeptuneTransactionError,
    NeptuneValidationError,
    NeptuneSerializationError,
    NeptuneTimeoutError,
    NeptuneResourceNotFoundError,
)
from chainsaws.aws.neptune.gremlin.gremlin_query import GremlinQuery
from chainsaws.aws.neptune.gremlin import (
    VertexQuery,
    EdgeQuery,
    CountQuery,
    MapQuery,
    ListQuery,
)

__all__ = [
    # Main API
    "NeptuneAPI",
    # Models
    "NeptuneAPIConfig",
    "GraphModel",
    "Vertex",
    "Edge",
    "VertexProperty",
    "EdgeProperty",
    "GraphQuery",
    "QueryResult",
    # Query builders
    "GremlinQuery",
    "VertexQuery",
    "EdgeQuery",
    "CountQuery",
    "MapQuery",
    "ListQuery",
    # Exceptions
    "NeptuneError",
    "NeptuneConnectionError",
    "NeptuneQueryError",
    "NeptuneModelError",
    "NeptuneTransactionError",
    "NeptuneValidationError",
    "NeptuneSerializationError",
    "NeptuneTimeoutError",
    "NeptuneResourceNotFoundError",
] 