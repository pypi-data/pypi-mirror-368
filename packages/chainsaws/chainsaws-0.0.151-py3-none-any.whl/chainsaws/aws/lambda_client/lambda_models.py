from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypedDict, NotRequired, Any, Literal, List, Dict

from chainsaws.aws.shared.config import APIConfig


@dataclass
class LambdaAPIConfig(APIConfig):
    """Configuration for LambdaAPI."""

InvocationType = Literal["RequestResponse", "Event", "DryRun"]
LambdaPackageType = Literal["Zip", "Image"]


class PythonRuntime(str, Enum):
    """Supported Python runtimes for Lambda functions."""

    PYTHON_313 = "python3.13"
    PYTHON_312 = "python3.12"
    PYTHON_311 = "python3.11"
    PYTHON_310 = "python3.10"
    PYTHON_39 = "python3.9"


@dataclass
class LambdaHandler:
    """Lambda function handler configuration.

    Defaults to "index", "handler" # index.handler

    Example:
        handler = LambdaHandler(module_path="app", function_name="handler")  # app.handler
        handler = LambdaHandler(module_path="src.functions.app", function_name="process_event")  # src.functions.app.process_event
    """

    # Module path (e.g., 'app' or 'src.functions.app')
    module_path: str = "index"
    # Function name (e.g., 'handler' or 'process_event')
    function_name: str = "handler"

    def __post_init__(self) -> None:
        """Validate the handler configuration after initialization."""
        self._validate_python_identifier(self.module_path)
        self._validate_python_identifier(self.function_name)

    @staticmethod
    def _validate_python_identifier(value: str) -> None:
        """Validate that the path components are valid Python identifiers."""
        for part in value.split("."):
            if not part.isidentifier():
                msg = f"'{part}' is not a valid Python identifier"
                raise ValueError(msg)

    def __str__(self) -> str:
        return f"{self.module_path}.{self.function_name}"


class FunctionConfiguration(TypedDict):
    """Lambda function configuration."""

    FunctionName: str
    FunctionArn: str
    Runtime: str
    Role: str
    Handler: str
    CodeSize: int
    Timeout: int
    MemorySize: int
    LastModified: str
    CodeSha256: str
    Version: str
    Description: NotRequired[str]
    Environment: NotRequired[Dict[str, Dict[str, str]]]
    TracingConfig: NotRequired[Dict[str, str]]
    RevisionId: NotRequired[str]
    State: NotRequired[str]
    LastUpdateStatus: NotRequired[str]
    PackageType: NotRequired[str]
    Architectures: NotRequired[List[str]]
    ImageConfigResponse: NotRequired[Dict[str, Any]]


class FunctionCode(TypedDict, total=False):
    """Lambda function code configuration.

    AWS Lambda API의 Code 파라미터와 일치하는 TypedDict입니다.
    total=False로 설정하여 모든 필드가 선택적이 되도록 합니다.

    Fields:
        ZipFile: ZIP 파일 바이트
        S3Bucket: S3 버킷 이름
        S3Key: S3 객체 키
        S3ObjectVersion: S3 객체 버전 ID
        ImageUri: 컨테이너 이미지 URI
    """

    ZipFile: bytes
    S3Bucket: str
    S3Key: str
    S3ObjectVersion: str
    ImageUri: str


@dataclass
class CreateFunctionRequest:
    """Request model for creating Lambda function."""

    function_name: str
    runtime: PythonRuntime
    role: str
    handler: str
    code: FunctionCode
    timeout: int = field(default=3)
    memory_size: int = field(default=128)
    description: Optional[str] = None
    publish: bool = False
    environment: Optional[Dict[str, Dict[str, str]]] = None
    tags: Optional[Dict[str, str]] = None
    architectures: List[str] = field(default_factory=lambda: ["x86_64"])
    package_type: str = field(default="Zip")
    image_uri: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the function configuration after initialization."""
        if not 1 <= self.timeout <= 900:
            raise ValueError("Timeout must be between 1 and 900 seconds")
        if not 128 <= self.memory_size <= 10240:
            raise ValueError("MemorySize must be between 128 and 10240 MB")
        if self.package_type not in ["Zip", "Image"]:
            raise ValueError("PackageType must be either 'Zip' or 'Image'")
        if self.package_type == "Image" and not self.image_uri:
            raise ValueError(
                "ImageUri is required when PackageType is 'Image'")

    def to_dict(self, exclude_none: bool = True) -> dict:
        """Convert the request to a dictionary format.

        Args:
            exclude_none: If True, exclude None values from the dictionary

        Returns:
            dict: Dictionary representation of the request
        """
        result = {
            "FunctionName": self.function_name,
            "Role": self.role,
            "PackageType": self.package_type,
            "Timeout": self.timeout,
            "MemorySize": self.memory_size,
            "Publish": self.publish,
            "Architectures": self.architectures,
        }

        if self.package_type == "Zip":
            result["Runtime"] = self.runtime
            result["Handler"] = self.handler
            if isinstance(self.code.get("ZipFile"), bytes):
                result["Code"] = {"ZipFile": self.code["ZipFile"]}
            elif self.code.get("S3Bucket") and self.code.get("S3Key"):
                result["Code"] = {
                    "S3Bucket": self.code["S3Bucket"],
                    "S3Key": self.code["S3Key"],
                }
                if self.code.get("S3ObjectVersion"):
                    result["Code"]["S3ObjectVersion"] = self.code["S3ObjectVersion"]
        else:  # Image
            result["Code"] = {"ImageUri": self.image_uri}

        if self.description:
            result["Description"] = self.description
        if self.environment:
            result["Environment"] = self.environment
        if self.tags:
            result["Tags"] = self.tags

        if exclude_none:
            return {k: v for k, v in result.items() if v is not None}
        return result


class TriggerType(Enum):
    """Supported Lambda trigger types."""

    API_GATEWAY = "apigateway"
    S3 = "s3"
    EVENTBRIDGE = "eventbridge"
    SNS = "sns"
    SQS = "sqs"
    DYNAMODB = "dynamodb"
