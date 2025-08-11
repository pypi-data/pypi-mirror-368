"""Gremlin query builder for Neptune.

This package provides a fluent interface for building Gremlin queries.
"""

from typing import Dict, List, Any, TypeVar

from chainsaws.aws.neptune.gremlin.gremlin_query import GremlinQuery
from chainsaws.aws.neptune.neptune_models import Vertex, Edge

# Type aliases for common query result types
R = TypeVar('R')
VertexQuery = GremlinQuery[Vertex]
EdgeQuery = GremlinQuery[Edge]
CountQuery = GremlinQuery[int]
MapQuery = GremlinQuery[Dict[str, Any]]
ListQuery = GremlinQuery[List[Any]]

__all__ = [
    "GremlinQuery",
    "VertexQuery",
    "EdgeQuery",
    "CountQuery",
    "MapQuery",
    "ListQuery",
] 