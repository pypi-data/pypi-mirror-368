import base64
from collections.abc import Iterator
from decimal import Decimal
from numbers import Number
from typing import Any, ParamSpec, TypeVar
import logging

from chainsaws.aws.dynamodb._dynamodb_config import (
    DELIMITER,
    DYNAMODB_BASE64_CHARSET,
    SORT_KEY_DECIMAL_PLACES,
    SORT_KEY_LENGTH,
    SORT_KEY_MAX_HALF_VALUE,
    SORT_KEY_MAX_VALUE,
)

P = ParamSpec("P")
R = TypeVar("R")


logger = logging.getLogger(__name__)


def encode_dict(
    obj: dict[str, Any] | list[Any] | Any,
) -> dict[str, Any] | list[Any] | Any:
    """Encode DynamoDB objects by converting Decimal types to native Python numbers.

    Args:
        obj: Object to encode (dict, list, or scalar value)
            - For dicts: Recursively encodes all values
            - For lists: Recursively encodes all elements
            - For scalars: Converts Decimal to int/float

    Returns:
        Encoded object with same structure but converted number types

    Examples:
        >>> encode_dict({'count': Decimal('10'), 'price': Decimal('19.99')})
        {'count': 10, 'price': 19.99}

        >>> encode_dict([Decimal('1'), Decimal('2.5')])
        [1, 2.5]

        >>> encode_dict({'items': [{'qty': Decimal('5')}]})
        {'items': [{'qty': 5}]}

    """
    def _cast_number(value: Any) -> Any:
        """Cast a value to appropriate number type if needed.

        Args:
            value: Value to cast

        Returns:
            - dict -> recursively encoded
            - list -> recursively encoded
            - bool -> unchanged boolean
            - Number -> int if whole number, float if decimal
            - other -> unchanged value

        """
        if isinstance(value, dict | list):
            return encode_dict(value)

        if isinstance(value, bool):
            return value

        if isinstance(value, Number):
            # Use modulo to check if it's a whole number
            return int(value) if value % 1 == 0 else float(value)

        return value

    if isinstance(obj, dict):
        return {
            key: _cast_number(value)
            for key, value in obj.items()
        }
    if isinstance(obj, list):
        return [_cast_number(value) for value in obj]
    return obj


def decode_dict(dict_obj: dict | list | Any) -> dict | list | Any:
    """Recursively convert float numbers to Decimal in nested dictionaries and lists.

    This function traverses through nested dictionaries and lists, converting any float
    values to Decimal for DynamoDB compatibility. The conversion is done recursively
    to handle arbitrary levels of nesting.

    Args:
        dict_obj: Input object to process. Can be:
            - Dictionary: All float values will be converted to Decimal
            - List: All float values in the list and nested structures will be converted
            - Other types: Returned as-is

    Returns:
        Union[Dict, List, Any]: The input structure with all float values converted to Decimal

    Examples:
        >>> decode_dict({'a': 1.0, 'b': {'c': 2.5}})
        {'a': Decimal('1.0'), 'b': {'c': Decimal('2.5')}}

        >>> decode_dict([1.0, {'a': 2.5}])
        [Decimal('1.0'), {'a': Decimal('2.5')}]

        >>> decode_dict('not a dict')
        'not a dict'

    """
    def cast_number(v):
        if isinstance(v, dict):
            return decode_dict(v)
        if isinstance(v, list):
            return decode_dict(v)
        if isinstance(v, float):
            return Decimal(str(v))
        return v

    if isinstance(dict_obj, dict):
        return {k: cast_number(v) for k, v in dict_obj.items()}
    if isinstance(dict_obj, list):
        return [cast_number(v) for v in dict_obj]
    return dict_obj


def has_sub_tuple(tuple_list: list[tuple], sub_tuple: tuple) -> bool:
    """Check if any tuple in the list contains sub_tuple as a prefix.

    Args:
        tuple_list: List of tuples to search in
        sub_tuple: Tuple to search for as a prefix

    Returns:
        bool: True if sub_tuple is a prefix of any tuple in the list

    """
    return any(
        all(t[i] == s for i, s in enumerate(sub_tuple))
        for t in tuple_list
        if len(sub_tuple) <= len(t)
    )


def is_sub_tuple(tup: tuple, sub_tuple: tuple) -> bool:
    """Check if sub_tuple is a prefix of tup.

    Args:
        tup: Main tuple to check against
        sub_tuple: Potential prefix tuple

    Returns:
        bool: True if sub_tuple is a prefix of tup

    """
    if len(sub_tuple) > len(tup):
        return False

    return all(tup[i] == sub_tuple[i] for i in range(len(sub_tuple)))


def get_item(tup: tuple, index: int, default: Any = None) -> Any:
    """Safely get item from tuple at index with default value.

    Args:
        tup: Tuple to get item from
        index: Index to retrieve
        default: Default value if index out of range

    Returns:
        Any: Item at index or default value

    """
    return tup[index] if len(tup) > index else default


def divide_chunks(data: list | dict, chunk_size: int) -> Iterator[list | dict]:
    """Split list or dictionary into chunks of specified size.

    Args:
        data: List or dictionary to split
        chunk_size: Size of each chunk

    Yields:
        Iterator of chunks

    """
    if isinstance(data, list):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    elif isinstance(data, dict):
        items = list(data.items())
        for i in range(0, len(items), chunk_size):
            yield dict(items[i:i + chunk_size])


def convert_int_to_custom_base64(number: int) -> str:
    """Convert integer to custom base64 string for sort key ordering.

    Args:
        number: Integer to convert

    Returns:
        str: Custom base64 representation

    """
    letters = []
    base = 64

    while True:
        letters.append(DYNAMODB_BASE64_CHARSET[number % base])
        number //= base
        if number == 0:
            break

    return "".join(reversed(letters))


def convert_custom_base64_to_int(custom_base64: str) -> int:
    """Convert custom base64 string back to integer.

    Args:
        custom_base64: Custom base64 string to convert

    Returns:
        int: Original integer value

    """
    base = 64
    return sum(
        DYNAMODB_BASE64_CHARSET.index(c) * pow(base, power)
        for power, c in enumerate(reversed(custom_base64))
    )


def str_to_base64_str(text: str) -> str:
    """Convert string to URL-safe base64 encoding.

    Args:
        text: String to encode

    Returns:
        str: Base64 encoded string

    """
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("utf-8")


def base64_str_to_str(b64_string: str) -> str:
    """Convert URL-safe base64 string back to original string.

    Args:
        b64_string: Base64 encoded string

    Returns:
        str: Original decoded string

    """
    return base64.urlsafe_b64decode(b64_string.encode("utf-8")).decode("utf-8")


def unsigned_number(number: int | float | Decimal) -> int:
    """Convert number to unsigned format for base64 conversion.

    Shifts negative numbers to positive range for sort key ordering.
    Valid range: -8.834235323891921e+55 to +8.834235323891921e+55

    Args:
        number: Number to convert

    Returns:
        int: Unsigned number

    Raises:
        ValueError: If number is outside valid range

    """
    scaled = int(Decimal(number) * Decimal(10) ** SORT_KEY_DECIMAL_PLACES)
    shifted = scaled + SORT_KEY_MAX_HALF_VALUE

    if not (0 <= shifted < SORT_KEY_MAX_VALUE):
        msg = "Number must be between -8.834235323891921e+55 and +8.834235323891921e+55"
        raise ValueError(
            msg,
        )

    return shifted


def merge_pk_sk(partition_key: str, sort_key: str) -> str:
    """Merge partition key and sort key with escape handling.

    Args:
        partition_key: Partition key
        sort_key: Sort key

    Returns:
        str: Merged key with escaped delimiters

    """
    return (
        partition_key.replace("&", "-&") +
        "&" +
        sort_key.replace("&", "-&")
    )


def split_pk_sk(merged_id: str) -> tuple[str, str]:
    """Split merged key back into partition key and sort key.

    Args:
        merged_id: Merged key string in format 'partition_key&sort_key'
                 where & is the delimiter

    Returns:
        Tuple[str, str]: (partition_key, sort_key)

    Raises:
        ValueError: If merged_id is invalid or doesn't contain the delimiter
    """
    keys = []
    prev_char = None
    buffer = []

    for char in merged_id:
        if char == "&" and prev_char != "-":
            keys.append("".join(buffer).replace("-&", "&"))
            buffer = []
        else:
            buffer.append(char)
        prev_char = char

    if buffer:
        keys.append("".join(buffer).replace("-&", "&"))

    if len(keys) != 2:
        msg = f"pk, sk parse failed. Invalid item_id format: {merged_id}."
        raise ValueError(msg)

    return keys[0], keys[1]


def convert_if_number_to_decimal(value: Any) -> Any:
    """Convert numeric values to Decimal for DynamoDB compatibility.

    Args:
        value: Value to potentially convert

    Returns:
        Any: Converted value or original if not numeric

    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    return value


def find_proper_index(
    partition_object: dict[str, Any],
    pk_field: str,
    sk_field: str | None = None,
) -> tuple[str | None, str, str]:
    """Find the appropriate index for querying.

    If sk_field is None, returns the first index that matches pk_field.
    If sk_field is provided, strictly searches for an exact match of both fields.

    Args:
        partition_object: Partition configuration object
        pk_field: Partition key field name
        sk_field: Sort key field name (optional)

    Returns:
        Tuple of (index_name, pk_name, sk_name)
        index_name will be None for main table, otherwise GSI name
        pk_name and sk_name are the key names for the chosen index

    """

    logger.debug(f"find_proper_index: {partition_object}, pk_field:: {
                 pk_field}, sk_field: {sk_field}")

    index_name = None
    pk_name = "_pk"
    sk_name = "_sk"
    if sk_field:
        # Strict search with both fields
        # Check main table first
        if pk_field == partition_object["_pk_field"] and sk_field == partition_object["_sk_field"]:
            index_name = None
        else:
            indexes = partition_object.get("indexes", [])
            for index in indexes:
                if pk_field == index["_pk_field"] and sk_field == index["_sk_field"]:
                    # Exact match found
                    index_name = index["index_name"]
                    pk_name = index["pk_name"]
                    sk_name = index["sk_name"]
                    break
            if not index_name:
                # No matching index found
                message = "pk_field & sk_field pair must be one of \n"
                message += f"0. pk: <{partition_object['_pk_field']}> & sk: <{
                    partition_object['_sk_field']}>\n"
                field_pairs = [f"{idx + 1}. pk: <{index['_pk_field']}> & sk: <{
                    index['_sk_field']}>" for idx, index in enumerate(indexes)]
                message += "\n".join(field_pairs)
                raise Exception(message)

    elif pk_field == partition_object["_pk_field"]:
        # Match on main table
        index_name = None
    else:
        indexes = partition_object.get("indexes", [])
        for index in indexes:
            if pk_field == index["_pk_field"]:
                # Found matching index
                index_name = index["index_name"]
                pk_name = index["pk_name"]
                sk_name = index["sk_name"]
                break
        # No match found in main table or indexes
        if not index_name:
            message = "pk_field & sk_field pair must be one of \n"
            message += f"0. pk: <{partition_object['_pk_field']}> & sk: <{
                partition_object['_sk_field']}>\n"
            field_pairs = [f"{idx + 1}. pk: <{index['_pk_field']}> & sk: <{index['_sk_field']}>" for idx, index in
                           enumerate(indexes)]
            message += "\n".join(field_pairs)
            raise Exception(message)

    return index_name, pk_name, sk_name


def pop_system_keys(item: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove internal system keys from item.

    Args:
        item: Dictionary to process

    Returns:
        Copy of item with system keys removed

    Note:
        Removes primary keys (_pk, _sk) and GSI keys (_pk1 through _pk5, _sk1 through _sk5)

    """
    if not item or not isinstance(item, dict):
        return item

    system_keys = ["_pk", "_sk"]
    system_keys.extend(
        f"_{key}{i}"
        for key in ("pk", "sk")
        for i in range(1, 21)
    )

    # Create copy and remove keys
    result = item.copy()
    for key in system_keys:
        result.pop(key, None)
    return result


def format_value(value: Any) -> str:
    """Format value for use as sort key with consistent ordering.

    Args:
        value: Value to format (number or string)

    Returns:
        Formatted string value

    Note:
        - Numbers are right-justified with prefix 'D'
        - Strings are terminated with delimiter and prefix 'S'
        - Numbers are converted to custom base64 for proper sorting
        - String length is padded to SORT_KEY_LENGTH for numbers

    """
    if isinstance(value, int | float | Decimal):
        # Handle numeric values
        base64_value = convert_int_to_custom_base64(unsigned_number(value))
        return "D" + base64_value.rjust(SORT_KEY_LENGTH)
    # Handle string values
    return f"S{str(object=value)}{DELIMITER}"
