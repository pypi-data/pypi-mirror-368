from typing import TypedDict

class PutRecordResponse(TypedDict):
    RecordId: str
    Encrypted: bool


class PutRecordBatchSuccessEntry(TypedDict):
    RecordId: str


class PutRecordBatchFailureEntry(TypedDict):
    ErrorCode: str
    ErrorMessage: str


class PutRecordBatchResponse(TypedDict):
    FailedPutCount: int
    RequestResponses: list[PutRecordBatchSuccessEntry | PutRecordBatchFailureEntry]