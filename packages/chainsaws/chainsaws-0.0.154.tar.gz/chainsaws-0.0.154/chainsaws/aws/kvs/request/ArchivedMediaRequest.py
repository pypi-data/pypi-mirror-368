from typing import TypedDict, Literal

class TimestampRange(TypedDict):
    StartTimestamp: str
    EndTimestamp: str

class FragmentSelector(TypedDict):
    FragmentSelectorType: Literal["PRODUCER_TIMESTAMP", "SERVER_TIMESTAMP"]
    TimestampRange: TimestampRange


class ClipFragmentSelector(FragmentSelector):
    pass

class DashFragmentSelector(FragmentSelector):
    pass

class HLSFragmentSelector(FragmentSelector):
    pass