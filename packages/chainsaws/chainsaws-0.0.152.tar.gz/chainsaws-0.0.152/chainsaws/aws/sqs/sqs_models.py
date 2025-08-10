from typing import Literal, TypedDict
from chainsaws.aws.shared.config import APIConfig

class SQSAPIConfig(APIConfig):
    pass

class MessageAttributesValue(TypedDict):
  StringValue: str
  BinaryValue: bytes
  StringListValues: list[str]
  BinaryListValues: list[bytes]
  DataType: Literal["String", "Number", "Binary"]