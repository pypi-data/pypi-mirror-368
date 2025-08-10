"""S3 Batch Operation event types for AWS Lambda."""

from typing import List, Literal, TypedDict

S3BatchResponseResultCode = Literal[
    "Succeeded",
    "TemporaryFailure",
    "PermanentFailure",
]


class S3BatchRequestJob(TypedDict):
    """Information about the S3 Batch Operations job.

    Args:
        id (str): The ID of the S3 Batch Operations job.
    """
    id: str


class S3BatchRequestTask(TypedDict, total=False):
    """Information about the task within an S3 Batch Operations job.

    Args:
        taskId (str): The identifier for this task.
        s3Key (str): The object key for this task.
        s3VersionId (str, optional): The version ID of the object if versioning is enabled.
        s3BucketArn (str): The ARN of the bucket containing the object.
    """
    taskId: str
    s3Key: str
    s3VersionId: str
    s3BucketArn: str


class S3BatchEvent(TypedDict):
    """The event passed to a Lambda function by S3 Batch Operations.

    Args:
        invocationSchemaVersion (str): Version of the event schema.
        invocationId (str): A unique ID for this invocation of the Lambda function.
        job (S3BatchRequestJob): Information about the S3 Batch Operations job.
        tasks (List[S3BatchRequestTask]): List of tasks to be processed.
    """
    invocationSchemaVersion: str
    invocationId: str
    job: S3BatchRequestJob
    tasks: List[S3BatchRequestTask]


class S3BatchResponseResult(TypedDict):
    """The result of processing a single task in the batch.

    Args:
        taskId (str): The identifier of the task this result is for.
        resultCode (S3BatchResponseResultCode): The status of the task processing.
        resultString (str): A description of the result.
    """
    taskId: str
    resultCode: S3BatchResponseResultCode
    resultString: str


class S3BatchResponse(TypedDict):
    """The response that must be returned by the Lambda function.

    Args:
        invocationSchemaVersion (str): Version of the response schema.
        treatMissingKeysAs (S3BatchResponseResultCode): How to handle missing keys.
        invocationId (str): The same invocationId that was received in the event.
        results (List[S3BatchResponseResult]): Results for each processed task.

    Reference:
        https://docs.aws.amazon.com/lambda/latest/dg/services-s3-batch.html
    """
    invocationSchemaVersion: str
    treatMissingKeysAs: S3BatchResponseResultCode
    invocationId: str
    results: List[S3BatchResponseResult]
