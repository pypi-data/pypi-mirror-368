from typing import TypeVar, List

T = TypeVar("T")


def listify(value: T) -> List[T]:
    """Convert a value to a list if it's not already a list."""
    if isinstance(value, list):
        return value
    return [value]
