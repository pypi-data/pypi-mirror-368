from boto3 import Session
from typing import Optional, Dict, List
from chainsaws.aws.mediapackagev2.mediapackagev2_exception import (
    MediaPackageV2CreateChannelGroupError,
    MediaPackageV2GetChannelGroupError,
    MediaPackageV2UpdateChannelGroupError,
    MediaPackageV2DeleteChannelGroupError,
    MediaPackageV2CreateChannelError,
    MediaPackageV2UpdateChannelError,
    MediaPackageV2GetChannelError,
    MediaPackageV2ListChannelGroupsError,   
    MediaPackageV2DeleteChannelError,
    MediaPackageV2ListChannelsError,
    MediaPackageV2ResetChannelStatsError,
    MediaPackageV2CreateHarvestJobError,
    MediaPackageV2GetHarvestJobError,
    MediaPackageV2ListHarvestJobsError,
    MediaPackageV2CancelHarvestJobError,
    MediaPackageV2CreateOriginEndpointError,
    MediaPackageV2ListOriginEndpointsError,
    MediaPackageV2GetOriginEndpointError,
    MediaPackageV2UpdateOriginEndpointError,
    MediaPackageV2DeleteOriginEndpointError,
    MediaPackageV2ResetOriginEndpointStateError,
    MediaPackageV2PutOriginEndpointPolicyError,
    MediaPackageV2GetOriginEndpointPolicyError,
    MediaPackageV2DeleteOriginEndpointPolicyError,
)
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
from chainsaws.aws.mediapackagev2.response.ChannelGroupResponse import (
    CreateChannelGroupResponse,
    GetChannelGroupResponse,
    UpdateChannelGroupResponse,
    ListChannelGroupsResponse,
)
from chainsaws.aws.mediapackagev2.response.ChannelResponse import (
    CreateChannelResponse,
    UpdateChannelResponse,
    GetChannelResponse,
    ListChannelsResponse,
    ResetChannelStatsResponse,
)
from chainsaws.aws.mediapackagev2.response.HarvestJobResponse import (
    HarvestedManifests,
    Destination,
    CreateHarvestJobResponse,
    GetHarvestJobResponse,
    ListHarvestJobsResponse,
    HarvestJobStatus,
)
from chainsaws.aws.mediapackagev2.response.OriginEndpointResponse import (
    CreateOriginEndpointResponse,
    ListOriginEndpointsResponse,
    GetOriginEndpointResponse,
    UpdateOriginEndpointResponse,
    ResetOriginEndpointStateResponse,
)
from chainsaws.aws.mediapackagev2.response.OriginEndpointPolicyResponse import (
    GetOriginEndpointPolicyResponse,
)
from datetime import datetime


class MediaPackageV2:
    def __init__(
        self,
        boto3_session: Session,
        channel_group_name: str,
        config: Optional[MediaPackageV2APIConfig] = None
    ) -> None:
        self.channel_group_name = channel_group_name
        self.config = config or MediaPackageV2APIConfig()
        self.client = boto3_session.client(
            service_name="mediapackagev2",
            region_name=self.config.region,
        )

    
    def create_channel_group(
            self,
            description: Optional[str] = None,
            tags: Optional[Dict[str, str]] = None
    ) -> CreateChannelGroupResponse:
        """
        Create a channel group.

        Args:
            channel_group_name: The name of the channel group.
            description: The description of the channel group.
            tags: The tags of the channel group.

        Returns:
            CreateChannelGroupResponse: The response from the create_channel_group operation.
        """
        try:
            response = self.client.create_channel_group(
                ChannelGroupName=self.channel_group_name,
                Description=description,
                Tags=tags,
            )
        except Exception as e:
            raise MediaPackageV2CreateChannelGroupError(channel_group_name=self.channel_group_name, reason=str(e)) from e

        return response


    def get_channel_group(self) -> GetChannelGroupResponse:
        """
        Get a channel group.

        Args:
            channel_group_name: The name of the channel group.
        """
        try:
            response = self.client.get_channel_group(
                ChannelGroupName=self.channel_group_name,
            )
        except Exception as e:
            raise MediaPackageV2GetChannelGroupError(channel_group_name=self.channel_group_name, reason=str(e)) from e

        return response


    def list_channel_groups(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListChannelGroupsResponse:
        """
        List channel groups.    

        Args:
            max_results: The maximum number of channel groups to return.
            next_token: The token to use to get the next page of results.
        """
        params = dict(
            ChannelGroupName=self.channel_group_name,
        )
        if max_results is not None:
            params["MaxResults"] = max_results
        if next_token is not None:
            params["NextToken"] = next_token

        try:
            response = self.client.list_channel_groups(
                **params,
            )
        except Exception as e:
            raise MediaPackageV2ListChannelGroupsError(reason=str(e)) from e
        
        return {
            "Items": response["Items"],
            "NextToken": response.get("NextToken", None),
        }


    def update_channel_group(self, description: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> UpdateChannelGroupResponse:
        """
        Update a channel group. Cannot update the channel group name.

        Args:
            channel_group_name: The name of the channel group.
            description: The description of the channel group.
            tags: The tags of the channel group.
        """
        try:
            response = self.client.update_channel_group(
                ChannelGroupName=self.channel_group_name,
                Description=description,
                Tags=tags,
            )
        except Exception as e:
            raise MediaPackageV2UpdateChannelGroupError(channel_group_name=self.channel_group_name, reason=str(e)) from e

        return response
    

    def delete_channel_group(self) -> None:
        """
        Delete a channel group.

        Args:
            channel_group_name: The name of the channel group.
        """
        try:
            self.client.delete_channel_group(ChannelGroupName=self.channel_group_name)
        except Exception as e:
            raise MediaPackageV2DeleteChannelGroupError(channel_group_name=self.channel_group_name, reason=str(e)) from e
        
    
    def create_channel(
            self,
            channel_name: str,
            description: Optional[str] = None,
            input_type: ChannelInputType = "HLS",
            input_switch_configuration: Optional[InputSwitchConfiguration] = None,
            output_header_configuration: Optional[OutputHeaderConfiguration] = None,
            tags: Optional[Dict[str, str]] = None
    ) -> CreateChannelResponse:
        """
        Create a channel.

        Args:
            channel_group_name: The name of the channel group.
            channel_name: The name of the channel.
            description: The description of the channel.
            input_type: The input type of the channel.
            input_switch_configuration: The input switch configuration (CMAF only).
            output_header_configuration: The output header configuration (CMAF only).
            tags: The tags of the channel.
        """
        try:
            params = dict(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                Description=description,
                InputType=input_type,
                Tags=tags,
            )
            if input_type == "CMAF":
                if input_switch_configuration is not None:
                    params["InputSwitchConfiguration"] = input_switch_configuration
                if output_header_configuration is not None:
                    params["OutputHeaderConfiguration"] = output_header_configuration
            response = self.client.create_channel(**params)
        except Exception as e:
            raise MediaPackageV2CreateChannelError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e

        return response
    

    def update_channel(
        self,
        channel_name: str,
        description: Optional[str] = None,
        etag: Optional[str] = None,
        input_switch_configuration: Optional[InputSwitchConfiguration] = None,
        output_header_configuration: Optional[OutputHeaderConfiguration] = None,
    ) -> UpdateChannelResponse:
        try:
            params = dict(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                Description=description,
                ETag=etag,
            )
            if input_switch_configuration is not None:
                params["InputSwitchConfiguration"] = input_switch_configuration
            if output_header_configuration is not None:
                params["OutputHeaderConfiguration"] = output_header_configuration
            response = self.client.update_channel(**params)
        except Exception as e:
            raise MediaPackageV2UpdateChannelError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e
        
        return response


    def get_channel(
        self,
        channel_name: str,
    ) -> GetChannelResponse:
        """
        Get a channel.
        """
        try:
            response = self.client.get_channel(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
            )
        except Exception as e:
            raise MediaPackageV2GetChannelError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e
        
        return response
    

    def delete_channel(
        self,
        channel_name: str,
    ) -> None:
        """
        Delete a channel.
        """
        try:
            self.client.delete_channel(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
            )
        except Exception as e:
            raise MediaPackageV2DeleteChannelError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e


    def list_channels(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListChannelsResponse:
        """
        List channels.
        """
        params = dict(
            ChannelGroupName=self.channel_group_name,
        )
        if max_results is not None:
            params["MaxResults"] = max_results
        if next_token is not None:
            params["NextToken"] = next_token

        try:
            response = self.client.list_channels(
                **params,
            )
        except Exception as e:
            raise MediaPackageV2ListChannelsError(channel_group_name=self.channel_group_name, reason=str(e)) from e
        
        return {
            "Items": response["Items"],
            "NextToken": response.get("NextToken", None),
        }
    

    def reset_channel_stats(
        self,
        channel_name: str,
    ) -> ResetChannelStatsResponse:
        """
        Reset channel stats.

        Args:
            channel_group_name: The name of the channel group.
            channel_name: The name of the channel.

        Returns:
            ResetChannelStatsResponse: The response from the reset_channel_stats operation.
        """
        try:
            response = self.client.reset_channel_stats(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
            )
        except Exception as e:
            raise MediaPackageV2ResetChannelStatsError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e
        
        return response
    

    def create_harvest_job(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        start_time: datetime,
        end_time: datetime,
        description: str = None,
        harvested_manifests: HarvestedManifests = None,
        destination: Destination = None,
        client_token: str = None,
        harvest_job_name: str = None,
        tags: dict[str, str] = None,
    ) -> CreateHarvestJobResponse:
        """
        Create a harvest job.

        Args:
            channel_name: The name of the channel.
            origin_endpoint_name: The name of the origin endpoint.
            start_time: The start time of the harvest job.
            end_time: The end time of the harvest job.
            description: The description of the harvest job.
            harvested_manifests: The harvested manifests of the harvest job.
            destination: The destination of the harvest job.
            client_token: The client token of the harvest job.
            harvest_job_name: The name of the harvest job.
            tags: The tags of the harvest job.
        """
        try:
            params = dict(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
                ScheduleConfiguration={
                    "StartTime": start_time,
                    "EndTime": end_time,
                },
            )

            if description is not None:
                params["Description"] = description
            if harvested_manifests is not None:
                params["HarvestedManifests"] = harvested_manifests
            if destination is not None:
                params["Destination"] = destination
            if client_token is not None:
                params["ClientToken"] = client_token
            if harvest_job_name is not None:
                params["HarvestJobName"] = harvest_job_name
            if tags is not None:
                params["Tags"] = tags

            response = self.client.create_harvest_job(**params)
            return response
        except Exception as e:
            raise MediaPackageV2CreateHarvestJobError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e
        

    def get_harvest_job(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        harvest_job_name: str,
    ) -> GetHarvestJobResponse:
        """
        Get a harvest job.
        """
        try:
            response = self.client.get_harvest_job(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
                HarvestJobName=harvest_job_name,
            )
        except Exception as e:
            raise MediaPackageV2GetHarvestJobError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, harvest_job_name=harvest_job_name, reason=str(e)) from e
        
        return response
    

    def list_harvest_jobs(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        status: Optional[HarvestJobStatus] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListHarvestJobsResponse:
        """
        List harvest jobs.

        Args:
            channel_name: The name of the channel.
            origin_endpoint_name: The name of the origin endpoint.
            status: The status of the harvest jobs.
            max_results: The maximum number of harvest jobs to return.
        """

        params = dict(
            ChannelGroupName=self.channel_group_name,
            ChannelName=channel_name,
            OriginEndpointName=origin_endpoint_name,
        )
        if status is not None:
            params["Status"] = status

        if max_results is not None:
            params["MaxResults"] = max_results
        if next_token is not None:
            params["NextToken"] = next_token

        try:
            response = self.client.list_harvest_jobs(
                **params,
            )

            return {
                "Items": response["Items"],
                "NextToken": response.get("NextToken", None),
            }
        except Exception as e:
            raise MediaPackageV2ListHarvestJobsError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, status=status, reason=str(e)) from e
        

    def cancel_harvest_job(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        harvest_job_name: str,
        etag: str
    ) -> None:
        """
        Cancel a harvest job.

        Args:
            channel_group_name: The name of the channel group.
            channel_name: The name of the channel.
            origin_endpoint_name: The name of the origin endpoint.
            harvest_job_name: The name of the harvest job.
            etag: The etag of the harvest job.
        """
        try:
            self.client.cancel_harvest_job(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
                HarvestJobName=harvest_job_name,
                ETag=etag,
            )
        except Exception as e:
            raise MediaPackageV2CancelHarvestJobError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, harvest_job_name=harvest_job_name, reason=str(e)) from e
        

    def create_origin_endpoint(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        container_type: OriginEndpointContainerType,
        segment: OriginEndpointSegment = None,
        description: Optional[str] = None,
        startover_window_seconds: Optional[int] = None,
        hls_manifests: Optional[List[HLSManifests]] = None,
        ll_hls_manifests: Optional[List[HLSManifests]] = None,
        # TODO: Add DashManifests
        endpoint_error_configuration: Optional[ForceEndpointErrorConfiguration] = None,
        etag: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> CreateOriginEndpointResponse:
        """
        Create an origin endpoint.

        Args:
            channel_group_name: The name of the channel group.
            channel_name: The name of the channel.
            origin_endpoint_name: The name of the origin endpoint.
            container_type: The type of container.
            segment: The segment of the origin endpoint.
            description: The description of the origin endpoint.
        """
        params = {
            "ChannelGroupName": self.channel_group_name,
            "ChannelName": channel_name,
            "OriginEndpointName": origin_endpoint_name,
            "ContainerType": container_type,
        }
        if description is not None:
            params["Description"] = description
        if startover_window_seconds is not None:
            params["StartoverWindowSeconds"] = startover_window_seconds
        if hls_manifests is not None:
            params["HlsManifests"] = hls_manifests
        if ll_hls_manifests is not None:
            params["LowLatencyHlsManifests"] = ll_hls_manifests
        if segment is not None:
            params["Segment"] = segment
        if endpoint_error_configuration is not None:
            params["EndpointErrorConfiguration"] = endpoint_error_configuration
        if etag is not None:
            params["ETag"] = etag
        if tags is not None:
            params["Tags"] = tags

        try:
            response = self.client.create_origin_endpoint(**params)
            return response
        except Exception as e:
            raise MediaPackageV2CreateOriginEndpointError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        

    def list_origin_endpoints(
        self,
        channel_name: str,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListOriginEndpointsResponse:
        """
        List origin endpoints.
        """
        params = dict(
            ChannelGroupName=self.channel_group_name,
            ChannelName=channel_name,
        )
        if max_results is not None:
            params["MaxResults"] = max_results
        if next_token is not None:
            params["NextToken"] = next_token
        try:
            response = self.client.list_origin_endpoints(
                **params,
            )

            return {
                "Items": response["Items"],
                "NextToken": response.get("NextToken", None),
            }
        except Exception as e:
            raise MediaPackageV2ListOriginEndpointsError(channel_group_name=self.channel_group_name, channel_name=channel_name, reason=str(e)) from e
    

    def get_origin_endpoint(
        self,
        channel_name: str,  
        origin_endpoint_name: str,
    ) -> GetOriginEndpointResponse:
        """
        Get an origin endpoint.
        """
        try:
            response = self.client.get_origin_endpoint(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
            )
        except Exception as e:
            raise MediaPackageV2GetOriginEndpointError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        
        return response
    

    def update_origin_endpoint(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        segment: OriginEndpointSegment = None,
        startover_window_seconds: Optional[int] = None,
        hls_manifests: Optional[List[HLSManifests]] = None,
        ll_hls_manifests: Optional[List[HLSManifests]] = None,
        # TODO: Add DashManifests
        endpoint_error_configuration: Optional[ForceEndpointErrorConfiguration] = None,
        etag: Optional[str] = None,
    ) -> UpdateOriginEndpointResponse:
        """
        Update an origin endpoint.
        """
        try:
            response = self.client.update_origin_endpoint(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
                Segment=segment,
                StartoverWindowSeconds=startover_window_seconds,
                HlsManifests=hls_manifests,
                LowLatencyHlsManifests=ll_hls_manifests,
                EndpointErrorConfiguration=endpoint_error_configuration,
                ETag=etag,
            )
        except Exception as e:
            raise MediaPackageV2UpdateOriginEndpointError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        
        return response
    

    def delete_origin_endpoint(
        self,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> None:
        """
        Delete an origin endpoint.
        """
        try:
            self.client.delete_origin_endpoint(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
            )
        except Exception as e:
            raise MediaPackageV2DeleteOriginEndpointError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
    

    def reset_origin_endpoint_state(
        self,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> ResetOriginEndpointStateResponse:
        """
        Reset the state of an origin endpoint.
        """
        try:
            response = self.client.reset_origin_endpoint_state(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
            )

            return response
        except Exception as e:
            raise MediaPackageV2ResetOriginEndpointStateError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
    

    def put_origin_endpoint_policy(
        self,
        channel_name: str,
        origin_endpoint_name: str,
        policy: str,    
    ) -> None:
        """
        Put an origin endpoint policy.
        """
        try:
            self.client.put_origin_endpoint_policy(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
                Policy=policy,
            )
        except Exception as e:
            raise MediaPackageV2PutOriginEndpointPolicyError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        

    def get_origin_endpoint_policy(
        self,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> GetOriginEndpointPolicyResponse:
        """
        Get an origin endpoint policy.
        """
        try:
            response = self.client.get_origin_endpoint_policy(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
            )
        except Exception as e:
            raise MediaPackageV2GetOriginEndpointPolicyError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        
        return response
    

    def delete_origin_endpoint_policy(
        self,
        channel_name: str,
        origin_endpoint_name: str,
    ) -> None:
        """
        Delete an origin endpoint policy.
        """
        try:
            self.client.delete_origin_endpoint_policy(
                ChannelGroupName=self.channel_group_name,
                ChannelName=channel_name,
                OriginEndpointName=origin_endpoint_name,
            )
        except Exception as e:
            raise MediaPackageV2DeleteOriginEndpointPolicyError(channel_group_name=self.channel_group_name, channel_name=channel_name, origin_endpoint_name=origin_endpoint_name, reason=str(e)) from e
        