class KVSException(Exception):
    """Base class for all KVS exceptions."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class KVSCreateStreamError(KVSException):
    """Exception raised for KVS stream creation errors."""

    def __init__(self, stream_name: str, reason: str) -> None:
        message = f"Failed to create stream '{stream_name}': {reason}"
        super().__init__(message)
        self.stream_name = stream_name
        self.reason = reason


class KVSUpdateStreamError(KVSException):
    """Exception raised for KVS stream update errors."""

    def __init__(self, stream_name: str, reason: str) -> None:
        message = f"Failed to update stream '{stream_name}': {reason}"
        super().__init__(message)
        self.stream_name = stream_name
        self.reason = reason


class KVSDeleteStreamError(KVSException):
    """Exception raised for KVS stream deletion errors."""

    def __init__(self, stream_arn: str, reason: str) -> None:
        message = f"Failed to delete stream '{stream_arn}': {reason}"
        super().__init__(message)
        self.stream_arn = stream_arn
        self.reason = reason


class KVSGetStreamError(KVSException):
    """Exception raised for KVS stream retrieval errors."""

    def __init__(self, stream_arn: str, reason: str) -> None:
        message = f"Failed to get stream '{stream_arn}': {reason}"
        super().__init__(message)
        self.stream_arn = stream_arn
        self.reason = reason


class KVSListStreamsError(KVSException):
    """Exception raised for KVS stream listing errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to list streams: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSUpdateDataRetentionError(KVSException):
    """Exception raised for KVS data retention update errors."""

    def __init__(self, stream_arn: str, reason: str) -> None:
        message = f"Failed to update data retention for stream '{stream_arn}': {reason}"
        super().__init__(message)
        self.stream_arn = stream_arn
        self.reason = reason

class KVSGetDataEndpointError(KVSException):
    """Exception raised for KVS data endpoint retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get data endpoint: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSGetClipError(KVSException):
    """Exception raised for KVS clip retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get clip: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSGetDashStreamingSessionUrlError(KVSException):
    """Exception raised for KVS DASH streaming session URL retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get DASH streaming session URL: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSGetHlsStreamingSessionUrlError(KVSException):
    """Exception raised for KVS HLS streaming session URL retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get HLS streaming session URL: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSGetMediaForFragmentListError(KVSException):
    """Exception raised for KVS media for fragment list retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get media for fragment list: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSListFragmentsError(KVSException):
    """Exception raised for KVS fragment listing errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to list fragments: {reason}"
        super().__init__(message)
        self.reason = reason


class KVSGetMediaError(KVSException):
    """Exception raised for KVS media retrieval errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to get media: {reason}"
        super().__init__(message)
        self.reason = reason    


