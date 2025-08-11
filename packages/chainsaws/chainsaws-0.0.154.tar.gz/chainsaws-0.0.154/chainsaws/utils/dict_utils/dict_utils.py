"""Dictionary utility functions."""

from __future__ import annotations

from decimal import Decimal
from typing import TypeVar, Any
from datetime import datetime
from json import JSONEncoder, JSONDecoder
from enum import Enum
from collections.abc import Iterator

T = TypeVar("T")


class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder for handling various Python built-in types.

    Handles the following types:
    - datetime: ISO format string
    - Decimal: float
    - Enum: value
    - set: list
    - bytes: UTF-8 decoded string
    - type: class name
    - complex: dict with real and imag parts
    - range: list
    - frozenset: list
    - memoryview: list of integers
    - bytearray: list of integers
    - PathLike objects: string path
    - object with __dict__: dictionary of attributes
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (set, frozenset, tuple)):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        if isinstance(obj, type):
            return obj.__name__
        if isinstance(obj, complex):
            return {"real": obj.real, "imag": obj.imag}
        if isinstance(obj, range):
            return list(obj)
        if isinstance(obj, memoryview):
            return list(obj.tobytes())
        if isinstance(obj, bytearray):
            return list(obj)
        if hasattr(obj, "__fspath__"):  # PathLike objects
            return str(obj)
        if hasattr(obj, "__dict__"):  # Custom objects
            return obj.__dict__

        return super().default(obj)


class CustomJSONDecoder(JSONDecoder):
    """Custom JSON decoder for handling encoded Python built-in types.

    Handles the following types:
    - ISO format string: datetime
    - float: Decimal (if specified in context)
    - dict with real/imag: complex
    - encoded PathLike: Path object
    """

    def __init__(self, *args, convert_decimal: bool = False, **kwargs):
        """Initialize the decoder.

        Args:
            convert_decimal: If True, converts float values to Decimal
            *args: Additional positional arguments for JSONDecoder
            **kwargs: Additional keyword arguments for JSONDecoder
        """
        self.convert_decimal = convert_decimal
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: dict) -> Any:
        """Convert JSON objects back to Python types.

        Args:
            obj: Dictionary to be converted

        Returns:
            Converted Python object
        """
        # Try to parse datetime strings
        if isinstance(obj, str):
            try:
                return datetime.fromisoformat(obj)
            except ValueError:
                pass

        # Handle complex numbers
        if len(obj) == 2 and "real" in obj and "imag" in obj:
            return complex(obj["real"], obj["imag"])

        # Convert float to Decimal if specified
        if self.convert_decimal:
            return {
                k: (Decimal(str(v)) if isinstance(v, float) else v)
                for k, v in obj.items()
            }

        return obj


def divide_chunks(
    data: list[T] | dict[str, T],
    chunk_size: int,
) -> Iterator[list[T] | dict[str, T]]:
    """Split a list or dictionary into chunks of specified size.

    Args:
        data: Input list or dictionary to be chunked
        chunk_size: Size of each chunk

    Returns:
        Iterator yielding chunks of the input data

    Raises:
        ValueError: If chunk_size is less than 1

    Examples:
        >>> list(divide_chunks([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]

        >>> list(divide_chunks({'a': 1, 'b': 2, 'c': 3}, 2))
        [{'a': 1, 'b': 2}, {'c': 3}]

    """
    if chunk_size < 1:
        msg = "Chunk size must be at least 1"

        raise ValueError(msg)

    if isinstance(data, list):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    elif isinstance(data, dict):
        items = list(data.items())
        for i in range(0, len(items), chunk_size):
            yield dict(items[i:i + chunk_size])


def convert_number_to_decimal(dict_detail: dict) -> dict:
    """Convert all float values in a nested dictionary to Decimal.

    Args:
        dict_detail: Dictionary containing float values to be converted

    Returns:
        dict: The input dictionary with float values converted to Decimal

    """
    for key, value in dict_detail.items():
        if isinstance(value, float):
            dict_detail[key] = Decimal(str(value))
        elif isinstance(dict_detail[key], dict):
            convert_number_to_decimal(dict_detail[key])
        elif isinstance(dict_detail[key], list):
            for item in dict_detail[key]:
                if isinstance(item, dict):
                    convert_number_to_decimal(item)
    return dict_detail


def convert_decimal_to_number(dict_detail: dict) -> dict:
    """Convert all Decimal values in a nested dictionary to int or float.

    Args:
        dict_detail: Dictionary containing Decimal values to be converted

    Returns:
        dict: The input dictionary with Decimal values converted to int/float

    """
    for key, value in dict_detail.items():
        if isinstance(value, Decimal):
            if value % 1 == 0:
                dict_detail[key] = int(value)
            else:
                dict_detail[key] = float(value)
        elif isinstance(dict_detail[key], dict):
            convert_decimal_to_number(dict_detail[key])
        elif isinstance(dict_detail[key], list):
            for item in dict_detail[key]:
                if isinstance(item, dict):
                    convert_decimal_to_number(item)
    return dict_detail
