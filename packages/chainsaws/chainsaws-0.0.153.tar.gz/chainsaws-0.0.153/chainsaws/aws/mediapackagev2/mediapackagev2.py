from typing import Optional, Dict, List
from datetime import datetime

from chainsaws.aws.mediapackagev2.mediapackagev2_models import (
    MediaPackageV2APIConfig,
    ChannelInputType,
    InputSwitchConfiguration,
    OutputHeaderConfiguration,
    OriginEndpointSegment,
    OriginEndpointContainerType,
    HLSManifests,
    ForceEndpointErrorConfiguration
)
from chainsaws.aws.mediapackagev2._mediapackagev2_internal import MediaPackageV2
from chainsaws.aws.mediapackagev2.response.HarvestJobResponse import (
    HarvestJobStatus,
    HarvestedManifests,
    Destination
)
from chainsaws.aws.shared import session

class MediaPackageV2API:
    """
    High-level API for MediaPackageV2 operations.

    TODO: Add more methods for other operations and use cases.
    """

    def __init__(self, channel_group_name: str, config: Optional[MediaPackageV2APIConfig] = None) -> None:
        """
        Initialize the MediaPackageV2API Client.
        """
        self.channel_group_name = channel_group_name
        self.config = config or MediaPackageV2APIConfig()
        self.boto3_session = session.get_boto_session(
            credentials=self.config.credentials if self.config.credentials else None,
        )
        self.client = MediaPackageV2(
            boto3_session=self.boto3_session,
            channel_group_name=channel_group_name,
            config=self.config
        )

    # 채널 그룹 관련
    def create_channel_group(self, description: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        return self.client.create_channel_group(description=description, tags=tags)

    def get_channel_group(self):
        return self.client.get_channel_group()

    def list_channel_groups(self, max_results: Optional[int] = None, next_token: Optional[str] = None):
        return self.client.list_channel_groups(max_results=max_results, next_token=next_token)

    def update_channel_group(self, description: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        return self.client.update_channel_group(description=description, tags=tags)

    def delete_channel_group(self):
        return self.client.delete_channel_group()

    # 채널 관련
    def create_channel(
        self,
        channel_name: str,
        description: Optional[str] = None,
        input_type: ChannelInputType = "HLS",
        input_switch_configuration: Optional[InputSwitchConfiguration] = None,
        output_header_configuration: Optional[OutputHeaderConfiguration] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        return self.client.create_channel(
            channel_name=channel_name,
            description=description,
            input_type=input_type,
            input_switch_configuration=input_switch_configuration,
            output_header_configuration=output_header_configuration,
            tags=tags
        )

    def update_channel(
        self,
        channel_name: str,
        description: Optional[str] = None,
        etag: Optional[str] = None,
        input_switch_configuration: Optional[InputSwitchConfiguration] = None,
        output_header_configuration: Optional[OutputHeaderConfiguration] = None,
    ):
        return self.client.update_channel(
            channel_name=channel_name,
            description=description,
            etag=etag,
            input_switch_configuration=input_switch_configuration,
            output_header_configuration=output_header_configuration
        )

    def get_channel(self, channel_name: str):
        return self.client.get_channel(channel_name=channel_name)

    def delete_channel(self, channel_name: str):
        return self.client.delete_channel(channel_name=channel_name)

    def list_channels(self, max_results: Optional[int] = None, next_token: Optional[str] = None):
        return self.client.list_channels(max_results=max_results, next_token=next_token)

    def reset_channel_stats(self, channel_name: str):
        return self.client.reset_channel_stats(channel_name=channel_name)

    # Harvest Job 관련
    def create_harvest_job(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        start_time: datetime,
        end_time: datetime,
        harvested_manifests: HarvestedManifests,
        destination: Destination,
        description: Optional[str] = None,
        client_token: Optional[str] = None,
        harvest_job_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        return self.client.create_harvest_job(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            start_time=start_time,
            end_time=end_time,
            description=description,
            harvested_manifests=harvested_manifests,
            destination=destination,
            client_token=client_token,
            harvest_job_name=harvest_job_name,
            tags=tags
        )

    def get_harvest_job(self, channel_name: str, origin_endpoint_name: str, harvest_job_name: str):
        return self.client.get_harvest_job(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            harvest_job_name=harvest_job_name
        )

    def list_harvest_jobs(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        status: Optional[HarvestJobStatus] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ):
        return self.client.list_harvest_jobs(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            status=status,
            max_results=max_results,
            next_token=next_token
        )

    def cancel_harvest_job(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        harvest_job_name: str,
        etag: str
    ):
        return self.client.cancel_harvest_job(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            harvest_job_name=harvest_job_name,
            etag=etag
        )

    # Origin Endpoint 관련
    def create_origin_endpoint(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        container_type: OriginEndpointContainerType,
        segment: Optional[OriginEndpointSegment] = None,
        description: Optional[str] = None,
        startover_window_seconds: Optional[int] = None,
        hls_manifests: Optional[List[HLSManifests]] = None,
        ll_hls_manifests: Optional[List[HLSManifests]] = None,
        endpoint_error_configuration: Optional[ForceEndpointErrorConfiguration] = None,
        etag: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        return self.client.create_origin_endpoint(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            container_type=container_type,
            segment=segment,
            description=description,
            startover_window_seconds=startover_window_seconds,
            hls_manifests=hls_manifests,
            ll_hls_manifests=ll_hls_manifests,
            endpoint_error_configuration=endpoint_error_configuration,
            etag=etag,
            tags=tags
        )

    def list_origin_endpoints(self, channel_name: str, max_results: Optional[int] = None, next_token: Optional[str] = None):
        return self.client.list_origin_endpoints(channel_name=channel_name, max_results=max_results, next_token=next_token)

    def get_origin_endpoint(self, channel_name: str, origin_endpoint_name: str):
        return self.client.get_origin_endpoint(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name)

    def update_origin_endpoint(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        segment: Optional[OriginEndpointSegment] = None,
        startover_window_seconds: Optional[int] = None,
        hls_manifests: Optional[List[HLSManifests]] = None,
        ll_hls_manifests: Optional[List[HLSManifests]] = None,
        endpoint_error_configuration: Optional[ForceEndpointErrorConfiguration] = None,
        etag: Optional[str] = None,
    ):
        return self.client.update_origin_endpoint(
            channel_name=channel_name,
            origin_endpoint_name=origin_endpoint_name,
            segment=segment,
            startover_window_seconds=startover_window_seconds,
            hls_manifests=hls_manifests,
            ll_hls_manifests=ll_hls_manifests,
            endpoint_error_configuration=endpoint_error_configuration,
            etag=etag
        )

    def delete_origin_endpoint(self, channel_name: str, origin_endpoint_name: str):
        return self.client.delete_origin_endpoint(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name)

    def reset_origin_endpoint_state(self, channel_name: str, origin_endpoint_name: str):
        return self.client.reset_origin_endpoint_state(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name)

    # Origin Endpoint Policy 관련
    def put_origin_endpoint_policy(self, channel_name: str, origin_endpoint_name: str, policy: str):
        return self.client.put_origin_endpoint_policy(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, policy=policy)

    def get_origin_endpoint_policy(self, channel_name: str, origin_endpoint_name: str):
        return self.client.get_origin_endpoint_policy(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name)

    def delete_origin_endpoint_policy(self, channel_name: str, origin_endpoint_name: str):
        return self.client.delete_origin_endpoint_policy(channel_name=channel_name, origin_endpoint_name=origin_endpoint_name)