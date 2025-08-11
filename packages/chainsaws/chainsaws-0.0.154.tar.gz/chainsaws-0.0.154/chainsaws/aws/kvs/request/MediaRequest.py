from typing import TypedDict, Literal, Optional
from datetime import datetime

class GetMediaStartSelector(TypedDict):
    StartSelectorType: Literal['FRAGMENT_NUMBER','SERVER_TIMESTAMP','PRODUCER_TIMESTAMP','NOW','EARLIEST','CONTINUATION_TOKEN']
    AfterFragmentNumber: Optional[str]
    StartTimestamp: Optional[datetime]
    ContinuationToken: Optional[str]