"""Gremlin query builder for Neptune.

This module provides a fluent interface for building Gremlin queries.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic, cast

from chainsaws.aws.neptune.neptune import NeptuneAPI
from chainsaws.aws.neptune.neptune_models import Vertex, Edge

T = TypeVar('T')
R = TypeVar('R')


class GremlinQuery(Generic[R]):
    """Builder for Gremlin queries with type safety."""
    
    def __init__(self, neptune_api: Optional['NeptuneAPI'] = None):
        """Initialize Gremlin query builder.
        
        Args:
            neptune_api: Optional Neptune API instance for query execution
        """
        self.neptune_api = neptune_api
        self.query_parts: List[str] = []
        self._parameters: Dict[str, Any] = {}
    
    def V(self, vertex_id: Optional[str] = None) -> 'GremlinQuery[R]':
        """Start a query with vertex selection.
        
        Args:
            vertex_id: Optional vertex ID to select
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if vertex_id:
            self.query_parts.append(f'g.V("{vertex_id}")')
        else:
            self.query_parts.append('g.V()')
        return self
    
    def E(self, edge_id: Optional[str] = None) -> 'GremlinQuery[R]':
        """Start a query with edge selection.
        
        Args:
            edge_id: Optional edge ID to select
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if edge_id:
            self.query_parts.append(f'g.E("{edge_id}")')
        else:
            self.query_parts.append('g.E()')
        return self
    
    def has(self, key: str, value: Any) -> 'GremlinQuery[R]':
        """Filter elements by property.
        
        Args:
            key: Property key
            value: Property value
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if isinstance(value, str):
            self.query_parts.append(f'.has("{key}", "{value}")')
        else:
            self.query_parts.append(f'.has("{key}", {value})')
        return self
    
    def hasLabel(self, label: str) -> 'GremlinQuery[R]':
        """Filter elements by label.
        
        Args:
            label: Label to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.hasLabel("{label}")')
        return self
    
    def hasId(self, id_value: str) -> 'GremlinQuery[R]':
        """Filter elements by ID.
        
        Args:
            id_value: ID to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.hasId("{id_value}")')
        return self
    
    def out(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to outgoing adjacent vertices.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.out({label_str})')
        else:
            self.query_parts.append('.out()')
        return self
    
    def in_(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to incoming adjacent vertices.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.in({label_str})')
        else:
            self.query_parts.append('.in()')
        return self
    
    def both(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to both incoming and outgoing adjacent vertices.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.both({label_str})')
        else:
            self.query_parts.append('.both()')
        return self
    
    def outE(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to outgoing edges.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.outE({label_str})')
        else:
            self.query_parts.append('.outE()')
        return self
    
    def inE(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to incoming edges.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.inE({label_str})')
        else:
            self.query_parts.append('.inE()')
        return self
    
    def bothE(self, *labels: str) -> 'GremlinQuery[R]':
        """Navigate to both incoming and outgoing edges.
        
        Args:
            *labels: Optional edge labels to filter by
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if labels:
            label_str = ', '.join([f'"{label}"' for label in labels])
            self.query_parts.append(f'.bothE({label_str})')
        else:
            self.query_parts.append('.bothE()')
        return self
    
    def values(self, *properties: str) -> 'GremlinQuery[R]':
        """Extract property values.
        
        Args:
            *properties: Property names to extract
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if properties:
            prop_str = ', '.join([f'"{prop}"' for prop in properties])
            self.query_parts.append(f'.values({prop_str})')
        else:
            self.query_parts.append('.values()')
        return self
    
    def valueMap(self, include_tokens: bool = False) -> 'GremlinQuery[R]':
        """Extract property values as a map.
        
        Args:
            include_tokens: Whether to include tokens (id, label)
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if include_tokens:
            self.query_parts.append('.valueMap(true)')
        else:
            self.query_parts.append('.valueMap()')
        return self
    
    def properties(self, *property_keys: str) -> 'GremlinQuery[R]':
        """Get element properties.
        
        Args:
            *property_keys: Property keys to get
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if property_keys:
            keys_str = ', '.join([f'"{key}"' for key in property_keys])
            self.query_parts.append(f'.properties({keys_str})')
        else:
            self.query_parts.append('.properties()')
        return self
    
    def property(self, key: str, value: Any) -> 'GremlinQuery[R]':
        """Add or update a property.
        
        Args:
            key: Property key
            value: Property value
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if isinstance(value, str):
            self.query_parts.append(f'.property("{key}", "{value}")')
        else:
            self.query_parts.append(f'.property("{key}", {value})')
        return self
    
    def limit(self, count: int) -> 'GremlinQuery[R]':
        """Limit the number of results.
        
        Args:
            count: Maximum number of results
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.limit({count})')
        return self
    
    def order(self) -> 'GremlinQuery[R]':
        """Order the results.
        
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append('.order()')
        return self
    
    def by(self, property_name: str, desc: bool = False) -> 'GremlinQuery[R]':
        """Specify ordering criteria.
        
        Args:
            property_name: Property to order by
            desc: Whether to order in descending order
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if desc:
            self.query_parts.append(f'.by("{property_name}", desc)')
        else:
            self.query_parts.append(f'.by("{property_name}")')
        return self
    
    def path(self) -> 'GremlinQuery[R]':
        """Get the path of the traversal.
        
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append('.path()')
        return self
    
    def count(self) -> 'GremlinQuery[int]':
        """Count the number of results.
        
        Returns:
            GremlinQuery: Query builder instance with int result type
        """
        self.query_parts.append('.count()')
        return cast('GremlinQuery[int]', self)
    
    def group(self) -> 'GremlinQuery[Dict[str, List[Any]]]':
        """Group the results.
        
        Returns:
            GremlinQuery: Query builder instance with grouped result type
        """
        self.query_parts.append('.group()')
        return cast('GremlinQuery[Dict[str, List[Any]]]', self)
    
    def unfold(self) -> 'GremlinQuery[R]':
        """Unfold a list into individual elements.
        
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append('.unfold()')
        return self
    
    def fold(self) -> 'GremlinQuery[List[R]]':
        """Fold individual elements into a list.
        
        Returns:
            GremlinQuery: Query builder instance with list result type
        """
        self.query_parts.append('.fold()')
        return cast('GremlinQuery[List[R]]', self)
    
    def project(self, *projections: str) -> 'GremlinQuery[Dict[str, Any]]':
        """Project properties into a map.
        
        Args:
            *projections: Property names to project
            
        Returns:
            GremlinQuery: Query builder instance with dict result type
        """
        if projections:
            proj_str = ', '.join([f'"{proj}"' for proj in projections])
            self.query_parts.append(f'.project({proj_str})')
        return cast('GremlinQuery[Dict[str, Any]]', self)
    
    def select(self, *selections: str) -> 'GremlinQuery[R]':
        """Select labeled steps.
        
        Args:
            *selections: Step labels to select
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if selections:
            sel_str = ', '.join([f'"{sel}"' for sel in selections])
            self.query_parts.append(f'.select({sel_str})')
        else:
            self.query_parts.append('.select()')
        return self
    
    def as_(self, label: str) -> 'GremlinQuery[R]':
        """Label a step.
        
        Args:
            label: Label for the step
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.as("{label}")')
        return self
    
    def where(self, predicate: str) -> 'GremlinQuery[R]':
        """Filter with a predicate.
        
        Args:
            predicate: Predicate expression
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.where({predicate})')
        return self
    
    def and_(self, *predicates: str) -> 'GremlinQuery[R]':
        """Combine predicates with AND.
        
        Args:
            *predicates: Predicates to combine
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if predicates:
            pred_str = ', '.join(predicates)
            self.query_parts.append(f'.and({pred_str})')
        else:
            self.query_parts.append('.and()')
        return self
    
    def or_(self, *predicates: str) -> 'GremlinQuery[R]':
        """Combine predicates with OR.
        
        Args:
            *predicates: Predicates to combine
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if predicates:
            pred_str = ', '.join(predicates)
            self.query_parts.append(f'.or({pred_str})')
        else:
            self.query_parts.append('.or()')
        return self
    
    def not_(self, predicate: str) -> 'GremlinQuery[R]':
        """Negate a predicate.
        
        Args:
            predicate: Predicate to negate
            
        Returns:
            GremlinQuery: Query builder instance
        """
        if predicate:
            self.query_parts.append(f'.not({predicate})')
        else:
            self.query_parts.append('.not()')
        return self
    
    def drop(self) -> 'GremlinQuery[None]':
        """Drop elements.
        
        Returns:
            GremlinQuery: Query builder instance with None result type
        """
        self.query_parts.append('.drop()')
        return cast('GremlinQuery[None]', self)
    
    def addV(self, label: str) -> 'GremlinQuery[R]':
        """Add a vertex.
        
        Args:
            label: Label for the new vertex
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.addV("{label}")')
        return self
    
    def addE(self, label: str) -> 'GremlinQuery[R]':
        """Add an edge.
        
        Args:
            label: Label for the new edge
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.addE("{label}")')
        return self
    
    def from_(self, vertex_ref: str) -> 'GremlinQuery[R]':
        """Set the from vertex for an edge.
        
        Args:
            vertex_ref: Vertex reference
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.from({vertex_ref})')
        return self
    
    def to(self, vertex_ref: str) -> 'GremlinQuery[R]':
        """Set the to vertex for an edge.
        
        Args:
            vertex_ref: Vertex reference
            
        Returns:
            GremlinQuery: Query builder instance
        """
        self.query_parts.append(f'.to({vertex_ref})')
        return self
    
    def id(self) -> 'GremlinQuery[str]':
        """Get the ID of elements.
        
        Returns:
            GremlinQuery: Query builder instance with string result type
        """
        self.query_parts.append('.id()')
        return cast('GremlinQuery[str]', self)
    
    def label(self) -> 'GremlinQuery[str]':
        """Get the label of elements.
        
        Returns:
            GremlinQuery: Query builder instance with string result type
        """
        self.query_parts.append('.label()')
        return cast('GremlinQuery[str]', self)
    
    def build(self) -> str:
        """Build the final Gremlin query string.
        
        Returns:
            str: Gremlin query string
        """
        return ''.join(self.query_parts)
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query and return results.
        
        Returns:
            List[Dict[str, Any]]: Query results
        """
        if not self.neptune_api:
            raise ValueError("Neptune API instance is required for query execution")
        
        query = self.build()
        return self.neptune_api.query(query)
    
    def execute_vertices(self) -> List['Vertex']:
        """Execute the query and return vertices.
        
        Returns:
            List[Vertex]: List of vertices
        """
        if not self.neptune_api:
            raise ValueError("Neptune API instance is required for query execution")
        
        query = self.build()
        return self.neptune_api.query_vertices(query)
    
    def execute_edges(self) -> List['Edge']:
        """Execute the query and return edges.
        
        Returns:
            List[Edge]: List of edges
        """
        if not self.neptune_api:
            raise ValueError("Neptune API instance is required for query execution")
        
        query = self.build()
        return self.neptune_api.query_edges(query) 