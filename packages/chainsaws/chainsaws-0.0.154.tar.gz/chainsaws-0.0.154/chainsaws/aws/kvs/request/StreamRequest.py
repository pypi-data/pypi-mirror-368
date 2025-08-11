from typing import TypedDict, Literal

class ListStreamNameCondition(TypedDict):
    ComparisonOperator: Literal["BEGINS_WITH"]
    ComparisonValue: str