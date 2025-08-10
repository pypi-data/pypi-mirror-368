from typing import TypedDict, Literal, Dict, List, Optional


class LambdaVpcConfig(TypedDict):
    SubnetIds: List[str]
    SecurityGroupIds: List[str]
    VpcId: str
    Ipv6AllowedForDualStack: bool


class LambdaDeadLetterConfig(TypedDict):
    TargetArn: str


class LambdaEnvironmentError(TypedDict):
    ErrorCode: str
    Message: str


class LambdaEnvironment(TypedDict):
    Variables: Dict[str, str]
    Error: Optional[LambdaEnvironmentError]


class LambdaTracingConfig(TypedDict):
    Mode: Literal['Active', 'PassThrough']


class LambdaLayer(TypedDict):
    Arn: str
    CodeSize: int
    SigningProfileVersionArn: str
    SigningJobArn: str


class LambdaFileSystemConfig(TypedDict):
    Arn: str
    LocalMountPath: str


class LambdaImageConfigError(TypedDict):
    ErrorCode: str
    Message: str


class LambdaImageConfig(TypedDict):
    EntryPoint: List[str]
    Command: List[str]
    WorkingDirectory: str


class LambdaImageConfigResponse(TypedDict):
    ImageConfig: LambdaImageConfig
    Error: Optional[LambdaImageConfigError]


class LambdaEphemeralStorage(TypedDict):
    Size: int


class LambdaSnapStart(TypedDict):
    ApplyOn: Literal['PublishedVersions', 'None']
    OptimizationStatus: Literal['On', 'Off']


class LambdaRuntimeVersionConfigError(TypedDict):
    ErrorCode: str
    Message: str


class LambdaRuntimeVersionConfig(TypedDict):
    RuntimeVersionArn: str
    Error: Optional[LambdaRuntimeVersionConfigError]


class LambdaLoggingConfig(TypedDict):
    LogFormat: Literal['JSON', 'Text']
    ApplicationLogLevel: Literal['TRACE',
                                 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
    SystemLogLevel: Literal['DEBUG', 'INFO', 'WARN']
    LogGroup: str


class LambdaConfiguration(TypedDict):
    FunctionName: str
    FunctionArn: str
    Runtime: Literal['nodejs', 'nodejs4.3', 'nodejs6.10', 'nodejs8.10', 'nodejs10.x', 'nodejs12.x', 'nodejs14.x', 'nodejs16.x', 'java8', 'java8.al2', 'java11', 'python2.7', 'python3.6', 'python3.7', 'python3.8', 'python3.9', 'dotnetcore1.0', 'dotnetcore2.0', 'dotnetcore2.1',
                     'dotnetcore3.1', 'dotnet6', 'dotnet8', 'nodejs4.3-edge', 'go1.x', 'ruby2.5', 'ruby2.7', 'provided', 'provided.al2', 'nodejs18.x', 'python3.10', 'java17', 'ruby3.2', 'ruby3.3', 'python3.11', 'nodejs20.x', 'provided.al2023', 'python3.12', 'java21', 'python3.13', 'nodejs22.x']
    Role: str
    Handler: str
    CodeSize: int
    Description: str
    Timeout: int
    MemorySize: int
    LastModified: str
    CodeSha256: str
    Version: str
    VpcConfig: LambdaVpcConfig
    DeadLetterConfig: Optional[LambdaDeadLetterConfig]
    Environment: Optional[LambdaEnvironment]
    KMSKeyArn: Optional[str]
    TracingConfig: Optional[LambdaTracingConfig]
    MasterArn: Optional[str]
    RevisionId: str
    Layers: Optional[List[LambdaLayer]]
    State: Literal['Pending', 'Active', 'Inactive', 'Failed']
    StateReason: Optional[str]
    StateReasonCode: Optional[Literal['Idle', 'Creating', 'Restoring', 'EniLimitExceeded', 'InsufficientRolePermissions', 'InvalidConfiguration', 'InternalError', 'SubnetOutOfIPAddresses', 'InvalidSubnet', 'InvalidSecurityGroup', 'ImageDeleted',
                                      'ImageAccessDenied', 'InvalidImage', 'KMSKeyAccessDenied', 'KMSKeyNotFound', 'InvalidStateKMSKey', 'DisabledKMSKey', 'EFSIOError', 'EFSMountConnectivityError', 'EFSMountFailure', 'EFSMountTimeout', 'InvalidRuntime', 'InvalidZipFileException', 'FunctionError']]
    LastUpdateStatus: Optional[Literal['Successful', 'Failed', 'InProgress']]
    LastUpdateStatusReason: Optional[str]
    LastUpdateStatusReasonCode: Optional[Literal['EniLimitExceeded', 'InsufficientRolePermissions', 'InvalidConfiguration', 'InternalError', 'SubnetOutOfIPAddresses', 'InvalidSubnet', 'InvalidSecurityGroup', 'ImageDeleted', 'ImageAccessDenied',
                                                 'InvalidImage', 'KMSKeyAccessDenied', 'KMSKeyNotFound', 'InvalidStateKMSKey', 'DisabledKMSKey', 'EFSIOError', 'EFSMountConnectivityError', 'EFSMountFailure', 'EFSMountTimeout', 'InvalidRuntime', 'InvalidZipFileException', 'FunctionError']]
    FileSystemConfigs: Optional[List[LambdaFileSystemConfig]]
    PackageType: Literal['Zip', 'Image']
    ImageConfigResponse: Optional[LambdaImageConfigResponse]
    SigningProfileVersionArn: Optional[str]
    SigningJobArn: Optional[str]
    Architectures: List[Literal['x86_64', 'arm64']]
    EphemeralStorage: Optional[LambdaEphemeralStorage]
    SnapStart: Optional[LambdaSnapStart]
    RuntimeVersionConfig: Optional[LambdaRuntimeVersionConfig]
    LoggingConfig: Optional[LambdaLoggingConfig]


class LambdaCode(TypedDict):
    RepositoryType: str
    Location: str
    ImageUri: Optional[str]
    ResolvedImageUri: Optional[str]
    SourceKMSKeyArn: Optional[str]


class LambdaTagsError(TypedDict):
    ErrorCode: str
    Message: str


class LambdaConcurrency(TypedDict):
    ReservedConcurrentExecutions: int


class GetFunctionResponse(TypedDict):
    Configuration: LambdaConfiguration
    Code: LambdaCode
    Tags: Optional[Dict[str, str]]
    TagsError: Optional[LambdaTagsError]
    Concurrency: Optional[LambdaConcurrency]
