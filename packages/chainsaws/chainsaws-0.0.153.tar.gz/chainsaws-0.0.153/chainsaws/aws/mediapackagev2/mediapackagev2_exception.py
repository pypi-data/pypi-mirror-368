from chainsaws.aws.mediapackagev2.response.HarvestJobResponse import HarvestJobStatus


class MediaPackageV2Exception(Exception):
    """Base class for all MediaPackageV2 exceptions."""

    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        super().__init__(message, *args)


class MediaPackageV2CreateChannelGroupError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel group creation errors."""

    def __init__(self, channel_group_name: str, reason: str) -> None:
        message = f"Failed to create channel group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.reason = reason


class MediaPackageV2GetChannelGroupError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel group retrieval errors."""

    def __init__(self, channel_group_name: str, reason: str) -> None:
        message = f"Failed to get channel group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.reason = reason


class MediaPackageV2UpdateChannelGroupError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel group update errors."""

    def __init__(self, channel_group_name: str, reason: str) -> None:
        message = f"Failed to update channel group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.reason = reason


class MediaPackageV2DeleteChannelGroupError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel group deletion errors."""

    def __init__(self, channel_group_name: str, reason: str) -> None:
        message = f"Failed to delete channel group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.reason = reason


class MediaPackageV2CreateChannelError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel creation errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to create channel '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2ListChannelGroupsError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel group listing errors."""

    def __init__(self, reason: str) -> None:
        message = f"Failed to list channel groups: {reason}"
        super().__init__(message)
        self.reason = reason

class MediaPackageV2UpdateChannelError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel update errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to update channel '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2GetChannelError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel retrieval errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to get channel '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2DeleteChannelError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel deletion errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to delete channel '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2ListChannelsError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel listing errors."""

    def __init__(self, channel_group_name: str, reason: str) -> None:
        message = f"Failed to list channels in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.reason = reason


class MediaPackageV2ResetChannelStatsError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 channel stats reset errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to reset channel stats for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2CreateHarvestJobError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 harvest job creation errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to create harvest job for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2GetHarvestJobError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 harvest job retrieval errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, harvest_job_name: str, reason: str) -> None:
        message = f"Failed to get harvest job '{harvest_job_name}' for '{channel_name}' in group '{channel_group_name}' and origin endpoint '{origin_endpoint_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.harvest_job_name = harvest_job_name
        self.reason = reason


class MediaPackageV2ListHarvestJobsError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 harvest job listing errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, status: HarvestJobStatus, reason: str) -> None:
        message = f"Failed to list harvest jobs for '{channel_name}' in group '{channel_group_name}' and origin endpoint '{origin_endpoint_name}' with status '{status}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.status = status
        self.reason = reason


class MediaPackageV2CancelHarvestJobError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 harvest job cancellation errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, harvest_job_name: str, reason: str) -> None:
        message = f"Failed to cancel harvest job '{harvest_job_name}' for '{channel_name}' in group '{channel_group_name}' and origin endpoint '{origin_endpoint_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.harvest_job_name = harvest_job_name


class MediaPackageV2CreateOriginEndpointError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint creation errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to create origin endpoint '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2ListOriginEndpointsError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint listing errors."""

    def __init__(self, channel_group_name: str, channel_name: str, reason: str) -> None:
        message = f"Failed to list origin endpoints for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.reason = reason


class MediaPackageV2GetOriginEndpointError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint retrieval errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to get origin endpoint '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2UpdateOriginEndpointError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint update errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to update origin endpoint '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2DeleteOriginEndpointError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint deletion errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to delete origin endpoint '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2ResetOriginEndpointStateError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint state reset errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to reset origin endpoint state for '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2PutOriginEndpointPolicyError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint policy errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to put origin endpoint policy for '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2GetOriginEndpointPolicyError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint policy retrieval errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to get origin endpoint policy for '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason


class MediaPackageV2DeleteOriginEndpointPolicyError(MediaPackageV2Exception):
    """Exception raised for MediaPackageV2 origin endpoint policy deletion errors."""

    def __init__(self, channel_group_name: str, channel_name: str, origin_endpoint_name: str, reason: str) -> None:
        message = f"Failed to delete origin endpoint policy for '{origin_endpoint_name}' for '{channel_name}' in group '{channel_group_name}': {reason}"
        super().__init__(message)
        self.channel_group_name = channel_group_name
        self.channel_name = channel_name
        self.origin_endpoint_name = origin_endpoint_name
        self.reason = reason