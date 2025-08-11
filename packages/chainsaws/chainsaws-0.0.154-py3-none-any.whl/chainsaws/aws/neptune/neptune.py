"""Neptune API for graph database operations.

This module provides a high-level interface for AWS Neptune graph database operations.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union, TypeVar, Iterator, Type, cast

from chainsaws.aws.neptune._neptune_internal import Neptune
from chainsaws.aws.neptune.neptune_models import (
    NeptuneAPIConfig,
    GraphModel,
    Vertex,
    Edge,
    GraphQuery,
    TransactionConfig,
)
from chainsaws.aws.neptune.neptune_exception import (
    NeptuneModelError,
    NeptuneTransactionError
)
from chainsaws.aws.shared import session

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=GraphModel)
V = TypeVar('V', bound=Vertex)
E = TypeVar('E', bound=Edge)


class NeptuneAPI:
    """High-level Neptune API for graph database operations."""

    def __init__(
        self,
        endpoint: str,
        config: Optional[NeptuneAPIConfig] = None,
    ) -> None:
        """Initialize Neptune client.

        Args:
            endpoint: Neptune cluster endpoint
            config: Optional Neptune configuration
        """
        self.endpoint = endpoint
        self.config = config or NeptuneAPIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.neptune = Neptune(
            boto3_session=self.boto3_session,
            endpoint=endpoint,
            config=config,
        )

    def connect(self) -> None:
        """Establish connection to Neptune cluster."""
        self.neptune.connect()

    # Vertex operations
    def create_vertex(self, vertex: Vertex) -> str:
        """Create a new vertex in the graph.

        Args:
            vertex: Vertex model to create

        Returns:
            str: ID of the created vertex
        """
        return self.neptune.create_vertex(vertex)

    def get_vertex(self, vertex_id: str) -> Optional[Vertex]:
        """Get a vertex by ID.

        Args:
            vertex_id: ID of the vertex to retrieve

        Returns:
            Optional[Vertex]: The vertex if found, None otherwise
        """
        return self.neptune.get_vertex(vertex_id)

    def update_vertex(self, vertex: Vertex) -> None:
        """Update a vertex.

        Args:
            vertex: Vertex model to update
        """
        self.neptune.update_vertex(vertex)

    def delete_vertex(self, vertex_id: str) -> None:
        """Delete a vertex.

        Args:
            vertex_id: ID of the vertex to delete
        """
        self.neptune.delete_vertex(vertex_id)

    def get_vertices_by_label(self, label: str, limit: int = 100) -> List[Vertex]:
        """Get vertices by label.

        Args:
            label: Label to filter vertices
            limit: Maximum number of vertices to return

        Returns:
            List[Vertex]: List of vertices with the specified label
        """
        return self.neptune.get_vertices_by_label(label, limit)

    # Edge operations
    def create_edge(self, edge: Edge) -> str:
        """Create a new edge between vertices.

        Args:
            edge: Edge model to create

        Returns:
            str: ID of the created edge
        """
        return self.neptune.create_edge(edge)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID.

        Args:
            edge_id: ID of the edge to retrieve

        Returns:
            Optional[Edge]: The edge if found, None otherwise
        """
        return self.neptune.get_edge(edge_id)

    def update_edge(self, edge: Edge) -> None:
        """Update an edge.

        Args:
            edge: Edge model to update
        """
        self.neptune.update_edge(edge)

    def delete_edge(self, edge_id: str) -> None:
        """Delete an edge.

        Args:
            edge_id: ID of the edge to delete
        """
        self.neptune.delete_edge(edge_id)

    def get_edges_by_label(self, label: str, limit: int = 100) -> List[Edge]:
        """Get edges by label.

        Args:
            label: Label to filter edges
            limit: Maximum number of edges to return

        Returns:
            List[Edge]: List of edges with the specified label
        """
        return self.neptune.get_edges_by_label(label, limit)

    # Query operations
    def query(self, query: Union[str, GraphQuery]) -> List[Dict[str, Any]]:
        """Execute a raw Gremlin query.

        Args:
            query: Gremlin query string or GraphQuery object

        Returns:
            List[Dict[str, Any]]: Query results
        """
        return self.neptune.execute_query(query)

    def query_vertices(self, query: Union[str, GraphQuery]) -> List[Vertex]:
        """Execute a Gremlin query and return vertices.

        Args:
            query: Gremlin query string or GraphQuery object

        Returns:
            List[Vertex]: List of vertices
        """
        result = self.neptune.execute_query(query)
        vertices: List[Vertex] = []

        for vertex_data in result:
            # Check if result is a vertex
            if 'label' in vertex_data and 'id' in vertex_data:
                # Extract properties
                properties = {}
                for key, value in vertex_data.items():
                    if key not in ['id', 'label']:
                        properties[key] = value

                # Create Vertex object
                vertex = Vertex(
                    id=vertex_data.get('id'),
                    label=vertex_data.get('label', ''),
                    properties=properties
                )
                vertices.append(vertex)

        return vertices

    def query_edges(self, query: Union[str, GraphQuery]) -> List[Edge]:
        """Execute a Gremlin query and return edges.

        Args:
            query: Gremlin query string or GraphQuery object

        Returns:
            List[Edge]: List of edges
        """
        result = self.neptune.execute_query(query)
        edges: List[Edge] = []

        for edge_data in result:
            # Check if result is an edge
            if 'label' in edge_data and 'id' in edge_data and 'from' in edge_data and 'to' in edge_data:
                # Create Edge object
                edge = Edge(
                    id=edge_data.get('id'),
                    label=edge_data.get('label', ''),
                    properties=edge_data.get('properties', {}),
                    from_vertex=edge_data.get('from'),
                    to_vertex=edge_data.get('to')
                )
                edges.append(edge)

        return edges

    # Transaction operations
    @contextmanager
    def transaction(self, config: Optional[TransactionConfig] = None) -> Iterator[None]:
        """Create a transaction context.
        
        Note:
            This is currently a placeholder implementation. Neptune doesn't support
            explicit transactions in Gremlin in the same way as traditional databases.
            This context manager provides a logical grouping for operations but does
            not guarantee ACID properties. Operations are executed immediately and
            cannot be rolled back if an error occurs.
            
            For true transactional behavior, consider using Neptune's SPARQL interface
            or wait for future Neptune versions with enhanced transaction support.

        Args:
            config: Optional transaction configuration

        Yields:
            None
        """
        try:
            yield
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise NeptuneTransactionError(f"Transaction failed: {str(e)}")

    # Batch operations
    def batch_create_vertices(self, vertices: List[Vertex]) -> List[str]:
        """Create multiple vertices in a batch.

        Args:
            vertices: List of vertices to create

        Returns:
            List[str]: List of created vertex IDs
        """
        vertex_ids: List[str] = []
        for vertex in vertices:
            try:
                vertex_id = self.create_vertex(vertex)
                if vertex_id:
                    vertex_ids.append(vertex_id)
            except Exception as e:
                logger.error(f"Failed to create vertex in batch: {str(e)}")
                # Continue with the rest of the batch
                continue
        return vertex_ids

    def batch_create_edges(self, edges: List[Edge]) -> List[str]:
        """Create multiple edges in a batch.

        Args:
            edges: List of edges to create

        Returns:
            List[str]: List of created edge IDs
        """
        edge_ids: List[str] = []
        for edge in edges:
            try:
                edge_id = self.create_edge(edge)
                if edge_id:
                    edge_ids.append(edge_id)
            except Exception as e:
                logger.error(f"Failed to create edge in batch: {str(e)}")
                # Continue with the rest of the batch
                continue
        return edge_ids

    # Graph traversal operations
    def get_neighbors(self, vertex_id: str, direction: str = "both", labels: Optional[List[str]] = None) -> List[Vertex]:
        """Get neighbors of a vertex.

        Args:
            vertex_id: ID of the vertex
            direction: Direction of edges ("out", "in", or "both")
            labels: Optional list of edge labels to filter

        Returns:
            List[Vertex]: List of neighboring vertices
        """
        try:
            # Build query based on direction
            if direction == "out":
                query = f'g.V("{vertex_id}").out('
            elif direction == "in":
                query = f'g.V("{vertex_id}").in('
            else:  # both
                query = f'g.V("{vertex_id}").both('

            # Add labels if provided
            if labels:
                label_str = ', '.join([f'"{label}"' for label in labels])
                query += label_str + ')'
            else:
                query += ')'

            # Add valueMap to get properties
            query += '.valueMap(true).with(WithOptions.tokens)'

            # Execute query
            result = self.neptune.execute_query(query)

            vertices: List[Vertex] = []
            for vertex_data in result:
                # Extract ID and label
                vertex_id = vertex_data.get('id')
                vertex_label = vertex_data.get('label', '')

                # Extract properties
                properties = {}
                for key, value in vertex_data.items():
                    if key not in ['id', 'label']:
                        # Handle multi-value properties
                        if isinstance(value, list) and len(value) == 1:
                            properties[key] = value[0]
                        else:
                            properties[key] = value

                # Create Vertex object
                vertices.append(Vertex(
                    id=vertex_id,
                    label=vertex_label,
                    properties=properties
                ))

            return vertices
        except Exception as e:
            logger.error(f"Failed to get neighbors: {str(e)}")
            raise

    def get_path(self, from_vertex_id: str, to_vertex_id: str, max_depth: int = 5) -> List[List[Union[Vertex, Edge]]]:
        """Find paths between two vertices.

        Args:
            from_vertex_id: ID of the source vertex
            to_vertex_id: ID of the target vertex
            max_depth: Maximum path depth

        Returns:
            List[List[Union[Vertex, Edge]]]: List of paths, each containing vertices and edges
        """
        try:
            # Build query to find paths
            query = f'g.V("{from_vertex_id}").repeat(both().simplePath()).until(hasId("{to_vertex_id}").or().loops().is(gt({max_depth}))).hasId("{to_vertex_id}").path().limit(5)'
            result = self.neptune.execute_query(query)

            paths: List[List[Union[Vertex, Edge]]] = []
            for path_data in result:
                path: List[Union[Vertex, Edge]] = []
                for i, element in enumerate(path_data.get('objects', [])):
                    if i % 2 == 0:  # Vertex
                        vertex = Vertex(
                            id=element.get('id'),
                            label=element.get('label', ''),
                            properties=element.get('properties', {})
                        )
                        path.append(vertex)
                    else:  # Edge
                        edge = Edge(
                            id=element.get('id'),
                            label=element.get('label', ''),
                            properties=element.get('properties', {}),
                            from_vertex=path_data.get('objects', [])[i-1].get('id'),
                            to_vertex=path_data.get('objects', [])[i+1].get('id')
                        )
                        path.append(edge)
                paths.append(path)

            return paths
        except Exception as e:
            logger.error(f"Failed to get path: {str(e)}")
            raise

    # ORM-like operations
    def save(self, model: T) -> T:
        """Save a graph model (create or update).

        Args:
            model: Graph model to save

        Returns:
            T: Saved graph model
        """
        if isinstance(model, Vertex):
            if model.id and self.get_vertex(model.id):
                self.update_vertex(model)
            else:
                model_id = self.create_vertex(model)
                if model_id:
                    model.id = model_id
        elif isinstance(model, Edge):
            if model.id and self.get_edge(model.id):
                self.update_edge(model)
            else:
                model_id = self.create_edge(model)
                if model_id:
                    model.id = model_id
        else:
            raise NeptuneModelError(f"Unsupported model type: {type(model)}")

        return model

    def delete(self, model: T) -> None:
        """Delete a graph model.

        Args:
            model: Graph model to delete
        """
        if isinstance(model, Vertex):
            self.delete_vertex(model.id)
        elif isinstance(model, Edge):
            self.delete_edge(model.id)
        else:
            raise NeptuneModelError(f"Unsupported model type: {type(model)}")

    def find_by_id(self, model_type: Type[T], model_id: str) -> Optional[T]:
        """Find a graph model by ID.

        Args:
            model_type: Type of the model to find
            model_id: ID of the model to find

        Returns:
            Optional[T]: Found model or None
        """
        if model_type == Vertex or issubclass(model_type, Vertex):
            return cast(T, self.get_vertex(model_id))
        elif model_type == Edge or issubclass(model_type, Edge):
            return cast(T, self.get_edge(model_id))
        else:
            raise NeptuneModelError(f"Unsupported model type: {model_type}")

    def find_by_property(self, model_type: Type[T], property_name: str, property_value: Any, limit: int = 100) -> List[T]:
        """Find graph models by property.

        Args:
            model_type: Type of the model to find
            property_name: Name of the property to filter by
            property_value: Value of the property to filter by
            limit: Maximum number of models to return

        Returns:
            List[T]: List of found models
        """
        try:
            if model_type == Vertex or issubclass(model_type, Vertex):
                if isinstance(property_value, str):
                    query = f'g.V().has("{property_name}", "{property_value}").limit({limit}).valueMap(true).with(WithOptions.tokens)'
                else:
                    query = f'g.V().has("{property_name}", {property_value}).limit({limit}).valueMap(true).with(WithOptions.tokens)'
                return cast(List[T], self.query_vertices(query))
            elif model_type == Edge or issubclass(model_type, Edge):
                if isinstance(property_value, str):
                    query = f'g.E().has("{property_name}", "{property_value}").limit({limit}).as("e")' + \
                            '.project("id", "label", "properties", "from", "to")' + \
                            '.by(id).by(label).by(valueMap()).by(outV().id()).by(inV().id())'
                else:
                    query = f'g.E().has("{property_name}", {property_value}).limit({limit}).as("e")' + \
                            '.project("id", "label", "properties", "from", "to")' + \
                            '.by(id).by(label).by(valueMap()).by(outV().id()).by(inV().id())'
                return cast(List[T], self.query_edges(query))
            else:
                raise NeptuneModelError(f"Unsupported model type: {model_type}")
        except Exception as e:
            logger.error(f"Failed to find by property: {str(e)}")
            raise

    def find_vertices_by_property(self, property_name: str, property_value: Any, limit: int = 100) -> List[Vertex]:
        """Find vertices by property.

        Args:
            property_name: Name of the property to filter by
            property_value: Value of the property to filter by
            limit: Maximum number of vertices to return

        Returns:
            List[Vertex]: List of found vertices
        """
        return self.find_by_property(Vertex, property_name, property_value, limit)

    def find_edges_by_property(self, property_name: str, property_value: Any, limit: int = 100) -> List[Edge]:
        """Find edges by property.

        Args:
            property_name: Name of the property to filter by
            property_value: Value of the property to filter by
            limit: Maximum number of edges to return

        Returns:
            List[Edge]: List of found edges
        """
        return self.find_by_property(Edge, property_name, property_value, limit) 