"""API Gateway event resolvers for Lambda functions.

Provides REST and HTTP API Gateway event handling with routing capabilities.
"""

import re
import logging
import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Generic, get_type_hints, Type
from enum import Enum
from http import HTTPStatus
from dataclasses import dataclass, is_dataclass, fields
from collections import defaultdict

from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse, LambdaEvent
from chainsaws.aws.lambda_client.types.events.api_gateway_proxy import (
    APIGatewayProxyV1Event,
    APIGatewayProxyV2Event,
)
from chainsaws.aws.lambda_client.event_handler.middleware import MiddlewareManager, Middleware
from chainsaws.aws.lambda_client.event_handler.openapi_generator import (
    ResponseSchemaRegistry,
    create_schema_from_type,
    IS_BUILD_TIME
)
from chainsaws.aws.lambda_client.event_handler.dependency_injection import inject

T = TypeVar("T", APIGatewayProxyV1Event, APIGatewayProxyV2Event)
RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


class HttpMethod(str, Enum):
    """HTTP methods supported by API Gateway."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass(slots=True)
class ResolverContext:
    """Context class for API Gateway request handling.

    Attributes:
        event: API Gateway event object
        context: Lambda context object
        path_parameters: URL path parameters (e.g., id value in /users/{id})
        query_parameters: URL query parameters (e.g., ?name=value)
        headers: HTTP request headers
        body: HTTP request body (parsed JSON data)
    """
    event: LambdaEvent
    context: Any
    path_parameters: Dict[str, str]
    query_parameters: Optional[Dict[str, str]]
    headers: Dict[str, str]
    body: Any


class Route:
    """API Gateway route definition."""

    __slots__ = ('path', 'method', 'handler', 'cors',
                 '_pattern', 'is_static', 'openapi_metadata')

    def __init__(
        self,
        path: str,
        method: HttpMethod,
        handler: Callable[..., Any],
        cors: bool = True,
        openapi_metadata: Optional[dict] = None
    ):
        """Initialize route with immediate pattern compilation."""
        self.path = path
        self.method = method
        # Wrap handler with dependency injection
        self.handler = inject(handler)
        self.cors = cors
        self.openapi_metadata = openapi_metadata or {}
        # Skip pattern compilation for static paths
        self.is_static = '{' not in path
        self._pattern = None if self.is_static else self._compile_pattern(path)

    @staticmethod
    def _compile_pattern(path: str) -> re.Pattern:
        """Compile route pattern."""
        pattern = re.sub(r'{([^:}]+)(?::([^}]+))?}',
                         r'(?P<\1>[^/]+)', path)
        return re.compile(f'^{pattern}$')

    def match(self, path: str) -> Optional[re.Match]:
        """Match a path against this route's pattern."""
        if self.is_static:
            if path == self.path:
                pattern = re.compile(f"^{re.escape(path)}$")
                return pattern.match(path)

            return None

        return self._pattern.match(path)


class BaseResolver(Generic[T]):
    """Base resolver for API Gateway events."""

    def __init__(self, base_path: str = ""):
        """Initialize resolver with optimized route storage."""
        self.base_path = self._normalize_base_path(base_path)
        self._route_map: Dict[str, List[Route]] = defaultdict(list)
        self.middleware_manager: MiddlewareManager[T] = MiddlewareManager()
        self.routers: list["Router"] = []

    def _normalize_base_path(self, path: str) -> str:
        """Normalize base path to always start with / and never end with /."""
        if not path:
            return ""
        return "/" + path.strip("/")

    def _normalize_path(self, path: str) -> str:
        """Normalize path with base path."""
        path = "/" + path.strip("/")
        if not self.base_path:
            return path
        return self.base_path + path

    def include_router(
        self,
        router: "Router",
        tags: list[str] | None = None
    ) -> None:
        """Include a router with optional tags.

        Args:
            router: Router instance to include
            tags: Additional tags to apply to all routes in the router
        """
        if tags:
            router.tags.extend(tags)

        router.parent = self
        self.routers.append(router)

        # Add router's routes to resolver
        for route in router.routes:
            full_path = router._get_full_path(route.path)
            new_route = Route(
                path=full_path,
                method=route.method,
                handler=route.handler,
                cors=route.cors,
                openapi_metadata=route.openapi_metadata
            )
            self._route_map[route.method.value].append(new_route)

        # Add router's middleware
        for middleware in router.middleware_manager.middleware:
            self.add_middleware(middleware)

    def add_middleware(self, middleware: Middleware) -> None:
        """Add a middleware to the resolver."""
        self.middleware_manager.add_middleware(middleware)

    def middleware(self, middleware_func: Middleware) -> Middleware:
        """Decorator to add a middleware."""
        self.add_middleware(middleware_func)
        return middleware_func

    def get_response_schema(self, handler: Callable) -> dict:
        """핸들러의 반환 타입에서 응답 스키마를 자동으로 생성"""
        hints = get_type_hints(handler)
        return_type = hints.get('return')

        if not return_type:
            return {}

        def type_to_schema(typ: type) -> dict:
            if is_dataclass(typ):
                properties = {}
                for field in fields(typ):
                    properties[field.name] = type_to_schema(field.type)
                return {
                    "type": "object",
                    "properties": properties
                }
            elif hasattr(typ, '__origin__'):
                if typ.__origin__ is list:
                    item_schema = self._create_schema_from_type(
                        typ.__args__[0])
                    if item_schema:
                        return {
                            "type": "array",
                            "items": item_schema
                        }
                elif typ.__origin__ is dict:
                    value_schema = self._create_schema_from_type(
                        typ.__args__[1])
                    if value_schema:
                        return {
                            "type": "object",
                            "additionalProperties": value_schema
                        }
            elif isinstance(typ, type):
                if issubclass(typ, str):
                    return {"type": "string"}
                elif issubclass(typ, int):
                    return {"type": "integer"}
                elif issubclass(typ, float):
                    return {"type": "number"}
                elif issubclass(typ, bool):
                    return {"type": "boolean"}
            return {}

        return type_to_schema(return_type)

    def add_route(
        self,
        path: str,
        method: Union[str, HttpMethod],
        cors: bool = True,
        status_code: Union[int, HTTPStatus] = HTTPStatus.OK,
        summary: str = "",
        description: str = "",
        tags: List[str] = None,
        responses: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type] = None,
        response_description: str = ""
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator to add a route handler."""
        if isinstance(method, str):
            method = HttpMethod(method.upper())

        status_code_value = status_code.value if isinstance(
            status_code, HTTPStatus) else status_code
        normalized_path = self._normalize_path(path)

        # Build time only: Generate response schema
        route_responses = None
        if IS_BUILD_TIME and response_model:
            if hasattr(response_model, '__response_schema__'):
                model_schema = getattr(response_model, '__response_schema__')
            else:
                model_schema = create_schema_from_type(response_model)
                if model_schema:
                    setattr(response_model, '__response_schema__', model_schema)

            if model_schema:
                route_responses = {
                    str(status_code_value): {
                        "description": response_description or "Successful response",
                        "content": {
                            "application/json": {
                                "schema": model_schema
                            }
                        }
                    }
                }
        # Runtime: Use stored schema
        elif not IS_BUILD_TIME and response_model:
            schemas = ResponseSchemaRegistry.load_schemas()
            model_name = f"{response_model.__module__}.{
                response_model.__name__}"
            if model_name in schemas:
                route_responses = {
                    str(status_code_value): {
                        "description": response_description or "Successful response",
                        "content": {
                            "application/json": {
                                "schema": schemas[model_name]
                            }
                        }
                    }
                }

        def decorator(handler: RouteHandler) -> RouteHandler:
            # Response schema priority:
            # 1. Explicitly passed responses
            # 2. Response decorator schema
            # 3. route_responses (generated from response_model)
            # 4. Default empty schema
            handler_responses = None
            if IS_BUILD_TIME:
                handler_responses = getattr(
                    handler, '__response_schema__', None)
            else:
                schemas = ResponseSchemaRegistry.load_schemas()
                handler_name = f"{handler.__module__}.{handler.__name__}"
                handler_responses = schemas.get(handler_name)

            openapi_metadata = {
                "summary": summary or handler.__doc__ or "",
                "description": description,
                "tags": tags or [],
                "responses": responses or handler_responses or route_responses or {
                    str(status_code_value): {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {}
                            }
                        }
                    }
                }
            }

            def wrapped_handler(*args, **kwargs):
                sig = inspect.signature(handler)
                params = sig.parameters

                # Filter out only required parameters
                filtered_kwargs = {}
                for name, param in params.items():
                    if name in kwargs:
                        filtered_kwargs[name] = kwargs[name]
                    elif param.default is not inspect.Parameter.empty:
                        filtered_kwargs[name] = param.default

                result = handler(*args, **filtered_kwargs)
                if not isinstance(result, dict) or "statusCode" not in result:
                    return LambdaResponse.create(result, status_code=status_code_value)

                return result

            wrapped_handler.__name__ = handler.__name__
            wrapped_handler.__doc__ = handler.__doc__
            wrapped_handler.__module__ = handler.__module__
            if hasattr(handler, '__annotations__'):
                wrapped_handler.__annotations__ = handler.__annotations__

            route = Route(
                path=normalized_path,
                method=method,
                handler=wrapped_handler,
                cors=cors,
                openapi_metadata=openapi_metadata
            )
            self._route_map[method.value].append(route)
            return wrapped_handler  # wrapped_handler를 반환
        return decorator

    def _create_schema_from_type(self, typ: Type) -> Optional[dict]:
        """타입에서 OpenAPI 스키마 생성"""
        if is_dataclass(typ):
            properties = {}
            required = []
            for field in fields(typ):
                field_schema = self._create_schema_from_type(field.type)
                if field_schema:
                    properties[field.name] = field_schema
                    if field.default == field.default_factory:
                        required.append(field.name)
            schema = {
                "type": "object",
                "properties": properties
            }
            if required:
                schema["required"] = required
            return schema
        elif hasattr(typ, '__origin__'):
            if typ.__origin__ is list:
                item_schema = self._create_schema_from_type(typ.__args__[0])
                if item_schema:
                    return {
                        "type": "array",
                        "items": item_schema
                    }
            elif typ.__origin__ is dict:
                value_schema = self._create_schema_from_type(typ.__args__[1])
                if value_schema:
                    return {
                        "type": "object",
                        "additionalProperties": value_schema
                    }
        elif isinstance(typ, type):
            if issubclass(typ, str):
                return {"type": "string"}
            elif issubclass(typ, int):
                return {"type": "integer"}
            elif issubclass(typ, float):
                return {"type": "number"}
            elif issubclass(typ, bool):
                return {"type": "boolean"}
        return None

    def get(
        self,
        path: str,
        cors: bool = True,
        status_code: Union[int, HTTPStatus] = HTTPStatus.OK,
        summary: str = "",
        description: str = "",
        tags: List[str] = None,
        responses: Dict[str, Any] = None,
        response_model: Optional[Type] = None,
        response_description: str = ""
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for GET method routes."""
        return self.add_route(
            path,
            HttpMethod.GET,
            cors,
            status_code,
            summary=summary,
            description=description,
            tags=tags,
            responses=responses,
            response_model=response_model,
            response_description=response_description
        )

    def post(
        self,
        path: str,
        cors: bool = True,
        status_code: Union[int, HTTPStatus] = HTTPStatus.CREATED,
        summary: str = "",
        description: str = "",
        tags: List[str] = None,
        responses: Dict[str, Any] = None,
        response_model: Optional[Type] = None,
        response_description: str = ""
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for POST method routes."""
        return self.add_route(
            path,
            HttpMethod.POST,
            cors,
            status_code,
            summary=summary,
            description=description,
            tags=tags,
            responses=responses,
            response_model=response_model,
            response_description=response_description
        )

    def put(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.OK) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PUT method routes."""
        return self.add_route(path, HttpMethod.PUT, cors, status_code)

    def delete(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.NO_CONTENT) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for DELETE method routes."""
        return self.add_route(path, HttpMethod.DELETE, cors, status_code)

    def patch(self, path: str, cors: bool = True, status_code: Union[int, HTTPStatus] = HTTPStatus.OK) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for PATCH method routes."""
        return self.add_route(path, HttpMethod.PATCH, cors, status_code)

    def head(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for HEAD method routes."""
        return self.add_route(path, HttpMethod.HEAD, cors)

    def options(self, path: str, cors: bool = True) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for OPTIONS method routes."""
        return self.add_route(path, HttpMethod.OPTIONS, cors)

    def _find_route(self, path: str, method: str) -> Optional[Route]:
        """Find matching route for path and method."""
        method = method.upper()
        for route in self._route_map[method]:
            match = route.match(path)
            if match:
                return route
        return None


class APIGatewayRestResolver(BaseResolver[APIGatewayProxyV1Event]):
    """Resolver for REST API Gateway events."""

    def resolve(self, event: APIGatewayProxyV1Event, context: Any = None) -> dict[str, Any]:
        """Resolve REST API Gateway event to handler response."""
        try:
            # Validate event structure
            if event.get('version', '1.0') != '1.0':
                return LambdaResponse.create(
                    {"message":
                        "Invalid API Gateway version. Expected REST API (v1)"},
                    status_code=400
                )

            lambda_event = LambdaEvent.from_dict(event)
            path = event.get('path', '')
            method = event.get('httpMethod', '')

            route = self._find_route(path, method)
            if not route:
                return LambdaResponse.create(
                    {"message": "Not Found"},
                    status_code=404
                )

            # Extract path parameters
            match = route.match(path)
            path_params = match.groupdict() if match else {}

            # Create resolver context
            resolver_ctx = ResolverContext(
                event=lambda_event,
                context=context,
                path_parameters=path_params,
                query_parameters=event.get('queryStringParameters'),
                headers=event.get('headers', {}),
                body=lambda_event.get_json_body()
            )

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    event=e,
                    context=c,
                    path_parameters=resolver_ctx.path_parameters,
                    query_parameters=resolver_ctx.query_parameters,
                    headers=resolver_ctx.headers,
                    body=resolver_ctx.body
                )
            )
            result = handler(event, context)

            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )


class APIGatewayHttpResolver(BaseResolver[APIGatewayProxyV2Event]):
    """Resolver for HTTP API Gateway events."""

    # Define frequently used constants
    _REQUEST_CONTEXT = 'requestContext'
    _HTTP = 'http'
    _PATH = 'path'
    _METHOD = 'method'
    _HEADERS = 'headers'
    _QUERY_PARAMS = 'queryStringParameters'
    _NOT_FOUND_RESPONSE = {"message": "Not Found"}
    _ERROR_RESPONSE_PREFIX = "Error handling request: "

    def __init__(self, base_path: str = ""):
        """Initialize resolver with base path.

        Args:
            base_path: Base path for all routes (e.g. "/api/v1")
        """
        super().__init__(base_path=base_path)

    def resolve(self, event: APIGatewayProxyV2Event, context: Any = None) -> dict[str, Any]:
        """Resolve HTTP API Gateway event to handler response."""
        try:
            # Minimize dictionary access
            request_context = event.get(self._REQUEST_CONTEXT, {})
            http_context = request_context.get(self._HTTP, {})
            path = http_context.get(self._PATH, '')
            method = http_context.get(self._METHOD, '')

            route = self._find_route(path, method)
            if not route:
                return LambdaResponse.create(
                    self._NOT_FOUND_RESPONSE,
                    status_code=404
                )

            # Extract path parameters
            match = route.match(path)
            path_params = match.groupdict() if match else {}

            # Convert event and parse body only once
            lambda_event = LambdaEvent.from_dict(event)
            parsed_body = lambda_event.get_json_body()

            # Create resolver context with minimized dictionary access
            resolver_ctx = ResolverContext(
                event=lambda_event,
                context=context,
                path_parameters=path_params,
                query_parameters=event.get(self._QUERY_PARAMS),
                headers=event.get(self._HEADERS, {}),
                body=parsed_body
            )

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(
                    event=e,
                    context=c,
                    path_parameters=resolver_ctx.path_parameters,
                    query_parameters=resolver_ctx.query_parameters,
                    headers=resolver_ctx.headers,
                    body=resolver_ctx.body
                )
            )
            result = handler(event, context)

            if isinstance(result, dict) and "statusCode" in result:
                return result

            return LambdaResponse.create(result)

        except Exception as e:
            logger.error(f"{self._ERROR_RESPONSE_PREFIX}{e}")
            return LambdaResponse.create(
                {"message": str(e)},
                status_code=500
            )


class Router(BaseResolver[T]):
    """Router for modular route handling."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None):
        """Initialize router."""
        super().__init__(base_path=prefix)
        self.tags = tags or []
        self.parent: Optional[BaseResolver] = None

    @property
    def routes(self) -> list[Route]:
        """Get all routes from the route map."""
        return [route for routes in self._route_map.values() for route in routes]

    def _get_full_path(self, path: str) -> str:
        """Get full path including all parent base paths."""
        full_path = self._normalize_path(path)
        if self.parent and self.parent.base_path:
            full_path = self.parent.base_path + full_path
        return full_path
