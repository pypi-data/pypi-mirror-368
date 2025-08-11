"""Neptune data models and type definitions.

This module defines the data models and type definitions for Neptune graph entities.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Type

# Type definitions
PropertyValue = Union[str, int, float, bool, datetime, List[Any], Dict[str, Any]]
PropertyDict = Dict[str, PropertyValue]
VertexId = str
EdgeId = str
T = TypeVar('T')


class GraphDataType(str, Enum):
    """Supported data types for graph properties."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    LIST = "list"
    MAP = "map"


@dataclass
class NeptuneAPIConfig:
    """Configuration for Neptune API."""
    port: int = 8182
    use_ssl: bool = True
    credentials: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3
    connection_pool_size: int = 10
    enable_iam_auth: bool = False
    region: Optional[str] = None
    use_websockets: bool = True


@dataclass
class GraphProperty:
    """Base class for graph properties."""
    name: str
    value: PropertyValue
    data_type: Optional[GraphDataType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "data_type": self.data_type.value if self.data_type else None
        }


@dataclass
class VertexProperty(GraphProperty):
    """Property of a vertex."""
    cardinality: str = "single"  # single, set, list


@dataclass
class EdgeProperty(GraphProperty):
    """Property of an edge."""
    pass


@dataclass
class GraphModel:
    """Base class for graph models."""
    id: Optional[str] = None
    label: str = ""
    properties: PropertyDict = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Initialize model after creation."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls: Type['GraphModel'], data: Dict[str, Any]) -> 'GraphModel':
        """Create model from dictionary."""
        properties = data.get("properties", {})
        
        # Handle datetime conversion
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id"),
            label=data.get("label", ""),
            properties=properties,
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class Vertex(GraphModel):
    """Vertex model representing a node in the graph."""
    incoming_edges: List[EdgeId] = field(default_factory=list)
    outgoing_edges: List[EdgeId] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vertex to dictionary."""
        result = super().to_dict()
        result.update({
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges,
        })
        return result
    
    @classmethod
    def from_dict(cls: Type['Vertex'], data: Dict[str, Any]) -> 'Vertex':
        """Create vertex from dictionary."""
        base = super(Vertex, cls).from_dict(data)
        return cls(
            id=base.id,
            label=base.label,
            properties=base.properties,
            created_at=base.created_at,
            updated_at=base.updated_at,
            incoming_edges=data.get("incoming_edges", []),
            outgoing_edges=data.get("outgoing_edges", []),
        )


@dataclass
class Edge(GraphModel):
    """Edge model representing a relationship between vertices."""
    from_vertex: VertexId = ""
    to_vertex: VertexId = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        result = super().to_dict()
        result.update({
            "from_vertex": self.from_vertex,
            "to_vertex": self.to_vertex,
        })
        return result
    
    @classmethod
    def from_dict(cls: Type['Edge'], data: Dict[str, Any]) -> 'Edge':
        """Create edge from dictionary."""
        base = super(Edge, cls).from_dict(data)
        return cls(
            id=base.id,
            label=base.label,
            properties=base.properties,
            created_at=base.created_at,
            updated_at=base.updated_at,
            from_vertex=data.get("from_vertex", ""),
            to_vertex=data.get("to_vertex", ""),
        )


@dataclass
class GraphQuery:
    """Base class for graph queries."""
    query_string: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "query_string": self.query_string,
            "parameters": self.parameters,
            "timeout": self.timeout,
        }


@dataclass
class QueryResult(Generic[T]):
    """Result of a graph query."""
    data: List[T] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query result to dictionary."""
        return {
            "data": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data],
            "metadata": self.metadata,
            "execution_time": self.execution_time,
        }


@dataclass
class TransactionConfig:
    """Configuration for Neptune transactions."""
    read_only: bool = False
    timeout: int = 30
    max_retries: int = 3 