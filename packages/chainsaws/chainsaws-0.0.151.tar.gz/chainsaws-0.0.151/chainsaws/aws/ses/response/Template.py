from typing_extensions import TypedDict, NotRequired


class Template(TypedDict):
    """SES template details."""

    TemplateName: str
    SubjectPart: NotRequired[str]
    TextPart: NotRequired[str]
    HtmlPart: NotRequired[str]
