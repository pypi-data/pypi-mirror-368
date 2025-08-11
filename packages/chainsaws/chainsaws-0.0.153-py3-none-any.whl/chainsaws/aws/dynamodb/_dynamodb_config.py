from typing import Final

# DynamoDB Sort Key configuration
# Total number of characters for sort key string
SORT_KEY_LENGTH: Final[int] = 20
# Number of decimal places in sort key (base 10)
SORT_KEY_DECIMAL_PLACES: Final[int] = 16

# DynamoDB Sort Key numeric range limits (base64 encoded)
SORT_KEY_MAX_HALF_VALUE: Final[int] = 664613997892457936451903530140172288
SORT_KEY_MAX_VALUE: Final[int] = SORT_KEY_MAX_HALF_VALUE * 2

# DynamoDB encoding and partition constants
DYNAMODB_BASE64_CHARSET: Final[str] = "+/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
PARTITION_KEY_META_INFO: Final[str] = "meta-info#partition"
DELIMITER: Final[str] = "|"
