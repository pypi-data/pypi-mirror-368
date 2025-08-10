"""Internal Neptune client implementation.

This module provides the internal implementation for Neptune operations.
It handles the low-level communication with the Neptune database.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from gremlin_python.driver.client import Client
from gremlin_python.driver.serializer import GraphSONSerializersV3d0
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import T

from chainsaws.aws.neptune.neptune_models import (
    NeptuneAPIConfig,
    Vertex,
    Edge,
    GraphQuery,
)
from chainsaws.aws.neptune.neptune_exception import (
    NeptuneConnectionError,
    NeptuneQueryError,
    NeptuneTimeoutError,
    NeptuneResourceNotFoundError,
)

logger = logging.getLogger(__name__)


class Neptune:
    """Internal Neptune client implementation."""

    def __init__(
        self,
        boto3_session,
        endpoint: str,
        config: Optional[NeptuneAPIConfig] = None,
    ):
        """Initialize Neptune client.

        Args:
            boto3_session: Boto3 session
            endpoint: Neptune cluster endpoint
            config: Optional Neptune configuration
        """
        self.boto3_session = boto3_session
        self.endpoint = endpoint
        self.config = config or NeptuneAPIConfig()
        self.client = None
        self.g = None
        self._connection_pool = []
        self._connection_time = 0

    def connect(self) -> None:
        """Establish connection to Neptune cluster."""
        try:
            protocol = "wss" if self.config.use_ssl else "ws"
            connection_string = f"{protocol}://{self.endpoint}:{self.config.port}"

            # Add IAM authentication if enabled
            request_headers = {}
            if self.config.enable_iam_auth and self.config.region:
                request_headers = self._get_iam_auth_headers(connection_string)

            # Create client
            self.client = Client(
                connection_string,
                'g',
                message_serializer=GraphSONSerializersV3d0(),
                headers=request_headers,
            )

            # Test connection
            self.client.submit('g.V().limit(1)').all().result()
            logger.info(f"Connected to Neptune cluster at {self.endpoint}")

            # Initialize traversal source
            self.g = traversal().withRemote(self.client)

            # Initialize connection pool if needed
            if self.config.connection_pool_size > 1:
                self._init_connection_pool()

            self._connection_time = time.time()

        except Exception as e:
            logger.error(f"Failed to connect to Neptune: {str(e)}")
            raise NeptuneConnectionError(
                f"Failed to connect to Neptune: {str(e)}")

    def _init_connection_pool(self) -> None:
        """Initialize connection pool."""
        protocol = "wss" if self.config.use_ssl else "ws"
        connection_string = f"{protocol}://{self.endpoint}:{self.config.port}/gremlin"
        request_headers = {}

        if self.config.enable_iam_auth and self.config.region:
            request_headers = self._get_iam_auth_headers(connection_string)

        # Create connection pool
        for _ in range(self.config.connection_pool_size):
            try:
                client = Client(
                    connection_string,
                    'g',
                    message_serializer=GraphSONSerializersV3d0(),
                    headers=request_headers,
                )
                # Test connection
                client.submit('g.V().limit(1)').all().result()
                self._connection_pool.append(client)
            except Exception as e:
                logger.warning(f"Failed to add connection to pool: {str(e)}")

        logger.info(
            f"Initialized connection pool with {len(self._connection_pool)} connections")

    def _get_iam_auth_headers(self, connection_string: str) -> Dict[str, str]:
        """Get IAM authentication headers for Neptune.

        Args:
            connection_string: Neptune connection string

        Returns:
            Dict[str, str]: IAM authentication headers
        """
        try:
            credentials = self.boto3_session.get_credentials()
            region = self.config.region

            # Create a request to sign
            request = AWSRequest(
                method='GET',
                url=connection_string,
                data=''
            )

            # Sign the request
            SigV4Auth(credentials, 'neptune-db', region).add_auth(request)

            # Extract the signed headers
            return dict(request.headers)
        except Exception as e:
            logger.error(f"Failed to generate IAM auth headers: {str(e)}")
            return {}

    def _get_client(self) -> Client:
        """Get a client from the connection pool or create a new one.

        Returns:
            Client: Gremlin client
        """
        # Check if connection is stale (older than 1 hour)
        if time.time() - self._connection_time > 3600:
            logger.info("Connection is stale, reconnecting...")
            self.connect()

        # If connection pool is enabled, use it
        if self._connection_pool:
            return self._connection_pool[int(time.time()) % len(self._connection_pool)]

        # Otherwise, use the main client
        if not self.client:
            self.connect()

        return self.client

    def execute_query(self, query: Union[str, GraphQuery]) -> List[Dict[str, Any]]:
        """Execute a Gremlin query.

        Args:
            query: Gremlin query string or GraphQuery object

        Returns:
            List[Dict[str, Any]]: Query results
        """
        client = self._get_client()

        try:
            query_str = query if isinstance(query, str) else query.query_string
            parameters = {} if isinstance(query, str) else query.parameters
            timeout = self.config.timeout

            if not isinstance(query, str) and query.timeout:
                timeout = query.timeout

            start_time = time.time()
            result_set = client.submit(query_str, parameters).all()
            result = result_set.result(timeout=timeout)
            execution_time = time.time() - start_time

            logger.debug(
                f"Query executed in {execution_time:.2f}s: {query_str}")

            return result
        except TimeoutError:
            logger.error(
                f"Query execution timed out after {self.config.timeout}s")
            raise NeptuneTimeoutError(
                f"Query execution timed out after {self.config.timeout}s")
        except Exception as e:
            query_str = query if isinstance(query, str) else query.query_string
            logger.error(f"Query execution failed: {str(e)}")
            raise NeptuneQueryError(
                f"Query execution failed: {str(e)}", query=query_str)

    def create_vertex(self, vertex: Vertex) -> str:
        """Create a new vertex.

        Args:
            vertex: Vertex model to create

        Returns:
            str: ID of the created vertex
        """
        try:
            # Build property string for query
            properties = []
            for key, value in vertex.properties.items():
                if isinstance(value, str):
                    properties.append(f'.property("{key}", "{value}")')
                elif isinstance(value, (int, float, bool)):
                    properties.append(f'.property("{key}", {value})')
                elif value is None:
                    continue
                else:
                    # Convert complex types to JSON
                    json_value = json.dumps(value)
                    properties.append(f'.property("{key}", {json_value})')

            property_string = ''.join(properties)

            # Create vertex
            query = f'g.addV("{vertex.label}")' + property_string

            # If ID is provided, use it
            if vertex.id:
                query += f'.property(T.id, "{vertex.id}")'

            # Execute query
            result = self.execute_query(query + '.id()')

            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to create vertex: {str(e)}")
            raise

    def get_vertex(self, vertex_id: str) -> Optional[Vertex]:
        """Get a vertex by ID.

        Args:
            vertex_id: ID of the vertex to retrieve

        Returns:
            Optional[Vertex]: The vertex if found, None otherwise
        """
        try:
            # Query vertex
            query = f'g.V("{vertex_id}").valueMap(true).with(WithOptions.tokens)'
            result = self.execute_query(query)

            if not result:
                return None

            # Convert result to Vertex model
            vertex_data = result[0]

            # Extract label and properties
            label = vertex_data.get('label', '')
            properties = {}

            # Process properties
            for key, value in vertex_data.items():
                if key not in ['id', 'label', T.id, T.label]:
                    # Handle multi-value properties
                    if isinstance(value, list) and len(value) == 1:
                        properties[key] = value[0]
                    else:
                        properties[key] = value

            # Create Vertex object
            return Vertex(
                id=vertex_id,
                label=label,
                properties=properties
            )
        except Exception as e:
            logger.error(f"Failed to get vertex: {str(e)}")
            if "ResourceNotFoundException" in str(e):
                raise NeptuneResourceNotFoundError(
                    f"Vertex with ID {vertex_id} not found")
            raise

    def update_vertex(self, vertex: Vertex) -> None:
        """Update a vertex.

        Args:
            vertex: Vertex model to update
        """
        try:
            # Check if vertex exists
            existing = self.get_vertex(vertex.id)
            if not existing:
                raise NeptuneResourceNotFoundError(
                    f"Vertex with ID {vertex.id} not found")

            # Build property updates
            updates = []
            for key, value in vertex.properties.items():
                if isinstance(value, str):
                    updates.append(f'.property(single, "{key}", "{value}")')
                elif isinstance(value, (int, float, bool)):
                    updates.append(f'.property(single, "{key}", {value})')
                elif value is None:
                    # Remove property
                    updates.append(f'.properties("{key}").drop()')
                else:
                    # Convert complex types to JSON
                    json_value = json.dumps(value)
                    updates.append(f'.property(single, "{key}", {json_value})')

            update_string = ''.join(updates)

            # Update vertex
            query = f'g.V("{vertex.id}")' + update_string
            self.execute_query(query)
        except NeptuneResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update vertex: {str(e)}")
            raise

    def delete_vertex(self, vertex_id: str) -> None:
        """Delete a vertex.

        Args:
            vertex_id: ID of the vertex to delete
        """
        try:
            # Delete vertex
            query = f'g.V("{vertex_id}").drop()'
            self.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to delete vertex: {str(e)}")
            raise

    def create_edge(self, edge: Edge) -> str:
        """Create a new edge between vertices.

        Args:
            edge: Edge model to create

        Returns:
            str: ID of the created edge
        """
        try:
            # Build property string for query
            properties = []
            for key, value in edge.properties.items():
                if isinstance(value, str):
                    properties.append(f'.property("{key}", "{value}")')
                elif isinstance(value, (int, float, bool)):
                    properties.append(f'.property("{key}", {value})')
                elif value is None:
                    continue
                else:
                    # Convert complex types to JSON
                    json_value = json.dumps(value)
                    properties.append(f'.property("{key}", {json_value})')

            property_string = ''.join(properties)

            # Create edge
            query = f'g.V("{edge.from_vertex}").addE("{edge.label}").to(g.V("{edge.to_vertex}"))' + property_string

            # If ID is provided, use it
            if edge.id:
                query += f'.property(T.id, "{edge.id}")'

            # Execute query
            result = self.execute_query(query + '.id()')

            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to create edge: {str(e)}")
            raise

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID.

        Args:
            edge_id: ID of the edge to retrieve

        Returns:
            Optional[Edge]: The edge if found, None otherwise
        """
        try:
            # Query edge
            query = f'g.E("{edge_id}").as("e").project("id", "label", "properties", "from", "to")' + \
                '.by(id).by(label).by(valueMap()).by(outV().id()).by(inV().id())'
            result = self.execute_query(query)

            if not result:
                return None

            # Convert result to Edge model
            edge_data = result[0]

            # Extract properties
            properties = {}
            if 'properties' in edge_data and edge_data['properties']:
                for key, value in edge_data['properties'].items():
                    # Handle multi-value properties consistently with vertex properties
                    if isinstance(value, list) and len(value) == 1:
                        properties[key] = value[0]
                    else:
                        properties[key] = value

            # Create Edge object
            return Edge(
                id=edge_data.get('id'),
                label=edge_data.get('label', ''),
                properties=properties,
                from_vertex=edge_data.get('from'),
                to_vertex=edge_data.get('to')
            )
        except Exception as e:
            logger.error(f"Failed to get edge: {str(e)}")
            if "ResourceNotFoundException" in str(e):
                raise NeptuneResourceNotFoundError(
                    f"Edge with ID {edge_id} not found")
            raise

    def update_edge(self, edge: Edge) -> None:
        """Update an edge.

        Args:
            edge: Edge model to update
        """
        try:
            # Check if edge exists
            existing = self.get_edge(edge.id)
            if not existing:
                raise NeptuneResourceNotFoundError(
                    f"Edge with ID {edge.id} not found")

            # Build property updates
            updates = []
            for key, value in edge.properties.items():
                if isinstance(value, str):
                    updates.append(f'.property("{key}", "{value}")')
                elif isinstance(value, (int, float, bool)):
                    updates.append(f'.property("{key}", {value})')
                elif value is None:
                    # Remove property
                    updates.append(f'.properties("{key}").drop()')
                else:
                    # Convert complex types to JSON
                    json_value = json.dumps(value)
                    updates.append(f'.property("{key}", {json_value})')

            update_string = ''.join(updates)

            # Update edge
            query = f'g.E("{edge.id}")' + update_string
            self.execute_query(query)
        except NeptuneResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update edge: {str(e)}")
            raise

    def delete_edge(self, edge_id: str) -> None:
        """Delete an edge.

        Args:
            edge_id: ID of the edge to delete
        """
        try:
            # Delete edge
            query = f'g.E("{edge_id}").drop()'
            self.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to delete edge: {str(e)}")
            raise

    def get_vertices_by_label(self, label: str, limit: int = 100) -> List[Vertex]:
        """Get vertices by label.

        Args:
            label: Label to filter vertices
            limit: Maximum number of vertices to return

        Returns:
            List[Vertex]: List of vertices with the specified label
        """
        try:
            # Query vertices
            query = f'g.V().hasLabel("{label}").limit({limit}).valueMap(true).with(WithOptions.tokens)'
            result = self.execute_query(query)

            vertices = []
            for vertex_data in result:
                # Extract ID and label
                vertex_id = vertex_data.get('id')
                vertex_label = vertex_data.get('label', '')

                # Extract properties
                properties = {}
                for key, value in vertex_data.items():
                    if key not in ['id', 'label', T.id, T.label]:
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
            logger.error(f"Failed to get vertices by label: {str(e)}")
            raise

    def get_edges_by_label(self, label: str, limit: int = 100) -> List[Edge]:
        """Get edges by label.

        Args:
            label: Label to filter edges
            limit: Maximum number of edges to return

        Returns:
            List[Edge]: List of edges with the specified label
        """
        try:
            # Query edges
            query = f'g.E().hasLabel("{label}").limit({limit}).as("e")' + \
                '.project("id", "label", "properties", "from", "to")' + \
                '.by(id).by(label).by(valueMap()).by(outV().id()).by(inV().id())'
            result = self.execute_query(query)

            edges = []
            for edge_data in result:
                # Create Edge object
                edges.append(Edge(
                    id=edge_data.get('id'),
                    label=edge_data.get('label', ''),
                    properties=edge_data.get('properties', {}),
                    from_vertex=edge_data.get('from'),
                    to_vertex=edge_data.get('to')
                ))

            return edges
        except Exception as e:
            logger.error(f"Failed to get edges by label: {str(e)}")
            raise
