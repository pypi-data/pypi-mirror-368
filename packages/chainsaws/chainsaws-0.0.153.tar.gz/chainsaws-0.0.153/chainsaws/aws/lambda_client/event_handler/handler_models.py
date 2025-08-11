"""Models for AWS Lambda handler utilities.

Defines request and response structures for Lambda functions.
"""
import json
import base64
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional, Dict, Union, TypeVar, Generic, TypedDict, BinaryIO, Iterator, Tuple, Protocol, runtime_checkable, Callable
from email.parser import Parser
from io import BytesIO

from chainsaws.utils.dict_utils import convert_decimal_to_number, CustomJSONEncoder

T = TypeVar('T')


class RequestContext(TypedDict, total=False):
    """AWS API Gateway request context."""
    identity: Dict[str, Any]
    request_id: Optional[str]
    domain_name: Optional[str]
    api_id: Optional[str]
    account_id: Optional[str]
    stage: Optional[str]

    @staticmethod
    def get_source_ip(identity: Dict[str, Any]) -> Optional[str]:
        """Get source IP address from request context."""
        return identity.get("sourceIp")


class ResponseHeaders(TypedDict, total=False):
    """API Gateway response headers."""
    Access_Control_Allow_Origin: str
    Access_Control_Allow_Headers: str
    Access_Control_Allow_Credentials: bool
    Access_Control_Allow_Methods: str
    Content_Type: str
    charset: str

    @staticmethod
    def default() -> 'ResponseHeaders':
        """Get default headers."""
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "*",
            "Content-Type": "application/json",
            "charset": "UTF-8"
        }


@dataclass
class HandlerConfig:
    """Configuration for Lambda handler decorator."""

    error_receiver: Optional[Callable[[str], Any]] = None
    content_type: str = "application/json"
    use_traceback: bool = True
    ignore_error_codes: list[int | str] = field(default_factory=list)


@dataclass
class ResponseMeta:
    """Response metadata."""
    rslt_cd: str = "S00000"
    rslt_msg: str = "Success"
    duration: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    traceback: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ResponseData(Generic[T]):
    """Generic response data wrapper."""
    data: T
    meta: ResponseMeta = field(default_factory=ResponseMeta)

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "data": self.data,
            "meta": self.meta.to_dict()
        }


@dataclass
class MultipartFile:
    """Represents a file from multipart/form-data."""
    filename: str
    content_type: str
    data: bytes
    headers: Dict[str, str]

    @property
    def size(self) -> int:
        """Get file size in bytes."""
        return len(self.data)

    def save(self, path: str) -> None:
        """Save file to disk.

        Args:
            path: Path to save the file
        """
        with open(path, 'wb') as f:
            f.write(self.data)

    def get_stream(self) -> BinaryIO:
        """Get file as binary stream.

        Returns:
            Binary stream of file data
        """
        return BytesIO(self.data)


class MultipartParser:
    """Parser for multipart/form-data."""

    def __init__(self, body: bytes, boundary: str):
        """Initialize parser.

        Args:
            body: Request body bytes
            boundary: Multipart boundary
        """
        self.body = body
        self.boundary = boundary.encode()

    def parse(self) -> Iterator[Tuple[Dict[str, str], bytes]]:
        """Parse multipart data.

        Yields:
            Tuple of (headers dict, content bytes)
        """
        parts = self.body.split(b'--' + self.boundary)

        # Skip preamble and epilogue
        for part in parts[1:-1]:
            # Remove leading \r\n and trailing --
            part = part.strip(b'\r\n-')
            if not part:
                continue

            # Split headers and content
            try:
                headers_raw, content = part.split(b'\r\n\r\n', 1)
            except ValueError:
                continue

            # Parse headers
            parser = Parser()
            headers = dict(parser.parsestr(headers_raw.decode()).items())

            yield headers, content


class MultipartData:
    """Handler for multipart/form-data."""

    def __init__(self, body: str, content_type: str):
        """Initialize multipart data handler.

        Args:
            body: Request body
            content_type: Content type header
        """
        self.body = body
        self.content_type = content_type
        self._files: Dict[str, MultipartFile] = {}
        self._fields: Dict[str, str] = {}
        self._parse()

    def _parse(self) -> None:
        """Parse multipart form data."""
        if not self.body:
            return

        # Get boundary from content type
        try:
            boundary = self.content_type.split('boundary=')[1].strip()
        except IndexError:
            raise ValueError("No boundary found in content type")

        # Decode body if base64 encoded
        body_bytes = base64.b64decode(
            self.body) if ';base64,' in self.body else self.body.encode()

        # Parse multipart data
        parser = MultipartParser(body_bytes, boundary)
        for headers, content in parser.parse():
            # Get content disposition
            disposition = headers.get('Content-Disposition', '')
            if not disposition.startswith('form-data'):
                continue

            # Parse content disposition
            params = dict(param.strip().split('=', 1)
                          for param in disposition.split(';')[1:])
            name = params.get('name', '').strip('"')
            if not name:
                continue

            filename = params.get('filename', '').strip('"')
            if filename:
                # This is a file
                self._files[name] = MultipartFile(
                    filename=filename,
                    content_type=headers.get(
                        'Content-Type', 'application/octet-stream'),
                    data=content,
                    headers=headers
                )
            else:
                # This is a form field
                self._fields[name] = content.decode()

    @property
    def files(self) -> Dict[str, MultipartFile]:
        """Get uploaded files.

        Returns:
            Dictionary of field name to MultipartFile
        """
        return self._files

    @property
    def fields(self) -> Dict[str, str]:
        """Get form fields.

        Returns:
            Dictionary of field name to value
        """
        return self._fields

    def get_file(self, name: str) -> Optional[MultipartFile]:
        """Get file by field name.

        Args:
            name: Form field name

        Returns:
            MultipartFile if found, None otherwise
        """
        return self._files.get(name)

    def get_field(self, name: str) -> Optional[str]:
        """Get field value by name.

        Args:
            name: Form field name

        Returns:
            Field value if found, None otherwise
        """
        return self._fields.get(name)


class LambdaEvent:
    """AWS Lambda event structure."""

    def __init__(
        self,
        body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        request_context: Optional[RequestContext] = None,
        **kwargs: Any
    ) -> None:
        self.body = body
        self.headers = headers or {}
        self.request_context = request_context or {}
        self.raw_event = kwargs

    @classmethod
    def from_dict(cls, event: Dict[str, Any]) -> 'LambdaEvent':
        """Create LambdaEvent from dictionary."""
        # 명시적으로 전달할 키들은 kwargs에서 제외
        event_copy = event.copy()
        for key in ['body', 'headers', 'requestContext']:
            event_copy.pop(key, None)

        return cls(
            body=event.get("body"),
            headers=event.get("headers", {}),
            request_context=event.get("requestContext", {}),
            **event_copy
        )

    @staticmethod
    def is_api_gateway_event(event: Dict[str, Any]) -> bool:
        """Check if the event is from API Gateway (REST or HTTP)."""
        request_context = event.get("requestContext", {})
        domain_name = request_context.get("domainName", "")
        is_execute_api_url = "execute-api" in domain_name

        # Check for HTTP API (v2)
        is_http_api = (
            is_execute_api_url and
            request_context.get("apiId") is not None and
            event.get("version") == "2.0" and
            request_context.get("accountId") != "anonymous"
        )

        # Check for REST API (v1)
        is_rest_api = (
            is_execute_api_url and
            request_context.get("apiId") is not None and
            request_context.get("stage") is not None and
            event.get("version") is None
        )

        return is_http_api or is_rest_api

    @staticmethod
    def is_alb_event(event: Dict[str, Any]) -> bool:
        """Check if event is from ALB."""
        return (
            isinstance(event, dict)
            and "requestContext" in event
            and "elb" in event.get("requestContext", {})
        )

    def get_json_body(self) -> Optional[Dict[str, Any]]:
        """Get JSON body from event."""
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return None

    def get_multipart_data(self) -> Optional[MultipartData]:
        """Get multipart form data from event.

        Returns:
            MultipartData if request is multipart/form-data, None otherwise
        """
        content_type = self.headers.get('content-type', '')
        if not content_type.startswith('multipart/form-data'):
            return None

        return MultipartData(self.body, content_type)


@dataclass
class LambdaResponse:
    """Lambda response formatter."""

    @staticmethod
    def is_lambda_response(response: dict) -> bool:
        """Check if the response is already a Lambda response format.

        Args:
            response: Response to check

        Returns:
            bool: True if response is already in Lambda response format
        """
        return (
            isinstance(response, dict) and
            "statusCode" in response and
            "body" in response and
            "headers" in response and
            "isBase64Encoded" in response
        )

    @staticmethod
    def create(
        body: Union[str, dict, list],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "application/json",
        status_description: Optional[str] = None,
        is_base64_encoded: bool = False,
        serialize: bool = True,
    ) -> dict:
        """Create Lambda response."""
        # 이미 Lambda response 형식이면 그대로 반환
        if isinstance(body, dict) and LambdaResponse.is_lambda_response(body):
            return body

        if not serialize:
            return body if isinstance(body, dict) else {"body": body}

        if isinstance(body, dict):
            body = convert_decimal_to_number(dict_detail=body)

        response = {
            "statusCode": status_code,
            "isBase64Encoded": is_base64_encoded,
        }

        # Add headers
        response["headers"] = headers or {"Content-Type": content_type}

        # Add status description for ALB Response
        if status_description:
            response["statusDescription"] = status_description

        response["body"] = json.dumps(
            obj={"data": body} if isinstance(body, (dict, list)) else {
                "data": str(body)},
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
            cls=CustomJSONEncoder
        )

        return response


@runtime_checkable
class OpenAPIRoute(Protocol):
    """Interface for routes that can be documented with OpenAPI"""

    @property
    def path(self) -> str:
        """Get route path"""
        ...

    @property
    def is_static(self) -> bool:
        """Check if route is static"""
        ...

    @property
    def _pattern(self) -> Any:
        """Get route pattern"""
        ...

    @property
    def cors(self) -> bool:
        """Check if route has CORS enabled"""
        ...

    @property
    def openapi_metadata(self) -> Dict[str, Any]:
        """Get OpenAPI metadata"""
        ...
