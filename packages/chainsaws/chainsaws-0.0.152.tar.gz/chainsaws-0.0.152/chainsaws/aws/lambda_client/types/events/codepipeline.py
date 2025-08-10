"""CodePipeline event types for AWS Lambda."""

from typing import List, TypedDict


class Configuration(TypedDict):
    """Lambda function configuration in CodePipeline.

    Args:
        FunctionName (str): The name or ARN of the Lambda function.
        UserParameters (str): Custom parameters passed to the function.
    """
    FunctionName: str
    UserParameters: str


class ActionConfiguration(TypedDict):
    """Configuration for the pipeline action.

    Args:
        configuration (Configuration): The function configuration details.
    """
    configuration: Configuration


class S3Location(TypedDict):
    """S3 location information for artifacts.

    Args:
        bucketName (str): The name of the S3 bucket.
        objectKey (str): The key of the object in the bucket.
    """
    bucketName: str
    objectKey: str


class ArtifactLocation(TypedDict):
    """Location information for pipeline artifacts.

    Args:
        type (str): The type of artifact location (usually "S3").
        s3Location (S3Location): The S3 location details.
    """
    type: str
    s3Location: S3Location


class Artifact(TypedDict, total=False):
    """Pipeline artifact information.

    Args:
        name (str): The name of the artifact.
        revision (str): The revision ID of the artifact.
        location (ArtifactLocation): Where the artifact is stored.
    """
    name: str
    revision: str
    location: ArtifactLocation


class ArtifactCredentials(TypedDict):
    """Temporary credentials for accessing artifacts.

    Args:
        accessKeyId (str): AWS access key ID.
        secretAccessKey (str): AWS secret access key.
        sessionToken (str): AWS session token.
        expirationTime (int): When the credentials expire.
    """
    accessKeyId: str
    secretAccessKey: str
    sessionToken: str
    expirationTime: int


class EncryptionKey(TypedDict):
    """KMS encryption key information.

    Args:
        id (str): The ID or ARN of the encryption key.
        type (str): The type of encryption key.
    """
    id: str
    type: str


class Data(TypedDict, total=False):
    """Job data for the CodePipeline action.

    Args:
        actionConfiguration (ActionConfiguration): Configuration for the action.
        inputArtifacts (List[Artifact]): Input artifacts for the action.
        outputArtifacts (List[Artifact]): Output artifacts from the action.
        artifactCredentials (ArtifactCredentials): Credentials for accessing artifacts.
        encryptionKey (EncryptionKey): Key for artifact encryption.
        continuationToken (str): Token for continuing a job.
    """
    actionConfiguration: ActionConfiguration
    inputArtifacts: List[Artifact]
    outputArtifacts: List[Artifact]
    artifactCredentials: ArtifactCredentials
    encryptionKey: EncryptionKey
    continuationToken: str


class CodePipelineJob(TypedDict):
    """Information about a CodePipeline job.

    Args:
        id (str): The ID of the job.
        accountId (str): The AWS account ID where the job is running.
        data (Data): The job data.

    Reference:
        https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html
    """
    id: str
    accountId: str
    data: Data


class CodePipelineEvent(TypedDict):
    """Event sent to Lambda functions by CodePipeline.

    Args:
        CodePipeline_job (CodePipelineJob): The job information.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/services-codepipeline.html
    """
    CodePipeline_job: CodePipelineJob
