from typing import Optional, TypedDict, TypeVar, List, Generic

T = TypeVar("T")

class PaginatedRequest(TypedDict):
    MaxResults: Optional[int]
    NextToken: Optional[str]


class PaginatedResponse(TypedDict, Generic[T]):
    Items: List[T]
    NextToken: Optional[str]