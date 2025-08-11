"""Dictionary utility functions for data manipulation and transformation.

This module provides utility functions for working with dictionaries, including:
- Chunking dictionaries and lists
- Converting between decimal and numeric types recursively

Example:
    ```python
    from chainsaws.utils.dict_utils import divide_chunks, convert_number_to_decimal

    # Split dictionary into chunks
    data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    chunks = list(divide_chunks(data, chunk_size=2))
    # [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}]

    # Convert numeric values to Decimal
    data = {'price': 10.5, 'items': [{'cost': 2.5}]}
    decimal_data = convert_number_to_decimal(data)
    # {'price': Decimal('10.5'), 'items': [{'cost': Decimal('2.5')}]}
    ```

"""

from chainsaws.utils.dict_utils.dict_utils import (
    convert_decimal_to_number,
    convert_number_to_decimal,
    divide_chunks,
    CustomJSONEncoder
)

__all__ = [
    "convert_decimal_to_number",
    "convert_number_to_decimal",
    "divide_chunks",
    'CustomJSONEncoder'
]
