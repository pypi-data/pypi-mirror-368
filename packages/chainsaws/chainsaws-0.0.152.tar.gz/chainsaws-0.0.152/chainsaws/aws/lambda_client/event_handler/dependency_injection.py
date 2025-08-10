"""Dependency injection container for Lambda handlers."""

from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints, Union
import inspect
from functools import wraps

T = TypeVar('T')


class Depends:
    """FastAPI-style dependency marker."""

    def __init__(self, dependency: Optional[Callable[..., Any]] = None):
        self.dependency = dependency
        self.cache: Dict[str, Any] = {}

    def __call__(self) -> Any:
        return self.dependency


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        self._instances: Dict[Any, Any] = {}
        self._dependency_cache: Dict[Callable, Any] = {}

    def resolve_sync(self, dependency: Union[Type[T], Depends]) -> T:
        """Resolve a dependency synchronously."""
        # Handle Depends instances
        if isinstance(dependency, Depends):
            dependency_fn = dependency.dependency
            if dependency_fn is None:
                return self._instances.get(dependency, None)

            if dependency_fn in self._dependency_cache:
                return self._dependency_cache[dependency_fn]

            # Resolve dependencies for the dependency function
            sig = inspect.signature(dependency_fn)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                annotation = param.annotation
                if annotation != inspect.Parameter.empty:
                    kwargs[param_name] = self.resolve_sync(annotation)

            # Call the dependency function
            result = dependency_fn(**kwargs)
            self._dependency_cache[dependency_fn] = result
            return result

        # Handle class dependencies (FastAPI style)
        if inspect.isclass(dependency):
            if dependency in self._instances:
                return self._instances[dependency]

            sig = inspect.signature(dependency.__init__)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                annotation = param.annotation
                if annotation != inspect.Parameter.empty:
                    kwargs[param_name] = self.resolve_sync(annotation)

            instance = dependency(**kwargs)
            self._instances[dependency] = instance
            return instance

        return dependency

    async def resolve(self, dependency: Union[Type[T], Depends]) -> T:
        """Resolve a dependency asynchronously."""
        # Handle Depends instances
        if isinstance(dependency, Depends):
            dependency_fn = dependency.dependency
            if dependency_fn is None:
                return self._instances.get(dependency, None)

            if dependency_fn in self._dependency_cache:
                return self._dependency_cache[dependency_fn]

            # Resolve dependencies for the dependency function
            sig = inspect.signature(dependency_fn)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                annotation = param.annotation
                if annotation != inspect.Parameter.empty:
                    kwargs[param_name] = await self.resolve(annotation)

            # Call the dependency function
            if inspect.iscoroutinefunction(dependency_fn):
                result = await dependency_fn(**kwargs)
            else:
                result = dependency_fn(**kwargs)

            self._dependency_cache[dependency_fn] = result
            return result

        # Handle class dependencies (FastAPI style)
        if inspect.isclass(dependency):
            if dependency in self._instances:
                return self._instances[dependency]

            sig = inspect.signature(dependency.__init__)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                annotation = param.annotation
                if annotation != inspect.Parameter.empty:
                    kwargs[param_name] = await self.resolve(annotation)

            instance = dependency(**kwargs)
            self._instances[dependency] = instance
            return instance

        return dependency

    def clear_cache(self) -> None:
        """Clear dependency cache."""
        self._dependency_cache.clear()


class Inject:
    """Decorator for injecting dependencies into handler methods."""

    def __init__(self, container: Container):
        self.container = container

    def __call__(self, handler: Callable) -> Callable:
        sig = inspect.signature(handler)
        type_hints = get_type_hints(handler)

        is_async = inspect.iscoroutinefunction(handler)

        if is_async:
            @wraps(handler)
            async def async_wrapper(*args, **kwargs):
                self.container.clear_cache()

                for param_name, param in sig.parameters.items():
                    if param_name in kwargs:
                        continue

                    if param_name in type_hints:
                        service_type = type_hints[param_name]
                        try:
                            kwargs[param_name] = await self.container.resolve(service_type)
                        except KeyError:
                            pass

                return await handler(*args, **kwargs)

            return async_wrapper
        else:
            @wraps(handler)
            def sync_wrapper(*args, **kwargs):
                self.container.clear_cache()

                for param_name, param in sig.parameters.items():
                    if param_name in kwargs:
                        continue

                    if param_name in type_hints:
                        service_type = type_hints[param_name]
                        try:
                            kwargs[param_name] = self.container.resolve_sync(
                                service_type)
                        except KeyError:
                            pass

                return handler(*args, **kwargs)

            return sync_wrapper


# Global container instance
container = Container()


def inject(handler: Callable) -> Callable:
    """Convenience decorator for dependency injection."""
    return Inject(container)(handler)
