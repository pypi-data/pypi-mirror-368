"""WebSocket event resolvers for Lambda functions.

Provides WebSocket API Gateway event handling with routing capabilities.
"""

from typing import Any, Callable, Dict, TypeVar
from enum import Enum

from chainsaws.aws.lambda_client.event_handler.handler_models import LambdaResponse, LambdaEvent
from chainsaws.aws.lambda_client.types.events.api_gateway_websocket import (
    WebSocketConnectEvent,
    WebSocketRouteEvent,
)
from chainsaws.aws.lambda_client.event_handler.middleware import MiddlewareManager, Middleware


RouteHandler = TypeVar("RouteHandler", bound=Callable[..., Any])


class WebSocketEventType(str, Enum):
    """WebSocket event types supported by API Gateway."""
    CONNECT = "$connect"
    DISCONNECT = "$disconnect"
    DEFAULT = "$default"


class WebSocketRoute:
    """WebSocket route definition."""

    __slots__ = ('route_key', 'handler')

    def __init__(
        self,
        route_key: str,
        handler: Callable[..., Any],
    ):
        """Initialize WebSocket route.

        Args:
            route_key: The route key to match against
            handler: The handler function to execute
        """
        self.route_key = route_key
        self.handler = handler


class WebSocketResolver:
    """Resolver for WebSocket API Gateway events."""

    def __init__(self):
        """Initialize resolver."""
        self.routes: Dict[str, WebSocketRoute] = {}
        self.middleware_manager: MiddlewareManager = MiddlewareManager()

    def add_middleware(self, middleware: Middleware) -> None:
        """Add a middleware to the resolver."""
        self.middleware_manager.add_middleware(middleware)

    def middleware(self, middleware_func: Middleware) -> Middleware:
        """Decorator to add a middleware."""
        self.add_middleware(middleware_func)
        return middleware_func

    def add_route(
        self,
        route_key: str,
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator to add a route handler."""
        def decorator(handler: RouteHandler) -> RouteHandler:
            async def wrapped_handler(*args, **kwargs):
                result = await handler(*args, **kwargs) if hasattr(handler, '__await__') else handler(*args, **kwargs)
                if not isinstance(result, dict) or "statusCode" not in result:
                    return LambdaResponse.create(result)
                return result

            route = WebSocketRoute(
                route_key=route_key,
                handler=wrapped_handler,
            )
            self.routes[route_key] = route
            return handler
        return decorator

    def on_connect(self) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for $connect route."""
        return self.add_route(WebSocketEventType.CONNECT)

    def on_disconnect(self) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for $disconnect route."""
        return self.add_route(WebSocketEventType.DISCONNECT)

    def on_default(self) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for $default route."""
        return self.add_route(WebSocketEventType.DEFAULT)

    def on_message(self, route_key: str) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator for custom message routes."""
        return self.add_route(route_key)

    def resolve(self, event: WebSocketConnectEvent | WebSocketRouteEvent, context: Any = None) -> dict[str, Any]:
        """Resolve WebSocket API Gateway event to handler response.

        Args:
            event: The WebSocket event from API Gateway
            context: The Lambda context

        Returns:
            The handler response
        """
        lambda_event = LambdaEvent.from_dict(event)
        route_key = event["requestContext"]["routeKey"]

        route = self.routes.get(route_key)
        if not route:
            return LambdaResponse.create(
                {"message": "No handler found for route"},
                status_code=404
            )

        try:
            # Prepare kwargs for handler
            kwargs = {
                "event": lambda_event,
                "context": context,
                "connection_id": event["requestContext"]["connectionId"],
                "body": lambda_event.get_json_body() if "body" in event else None,
            }

            # Apply middleware chain to the handler
            handler = self.middleware_manager.apply(
                lambda e, c: route.handler(**{**kwargs, "event": e, "context": c})
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