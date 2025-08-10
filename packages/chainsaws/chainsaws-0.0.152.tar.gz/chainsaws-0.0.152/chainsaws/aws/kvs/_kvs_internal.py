from boto3 import Session
from typing import Optional, Dict, Literal, List

from chainsaws.aws.kvs.kvs_models import KVSAPIConfig, KVSDataEndpointAPI
from chainsaws.aws.kvs.kvs_exception import (
    KVSCreateStreamError,
    KVSUpdateStreamError,
    KVSDeleteStreamError,
    KVSGetStreamError,
    KVSListStreamsError,
    KVSGetDataEndpointError,
    KVSUpdateDataRetentionError,
    KVSGetClipError,
    KVSGetDashStreamingSessionUrlError,
    KVSGetHlsStreamingSessionUrlError,
    KVSGetMediaForFragmentListError,
    KVSListFragmentsError,
    KVSGetMediaError
  )
from chainsaws.aws.kvs.response.StreamResponse import (
    CreateStreamResponse,
    GetStreamResponse,
    ListStreamsResponse
)
from chainsaws.aws.kvs.response.ArchivedMediaResponse import (
    GetClipResponse,
    GetDashStreamingSessionUrlResponse,
    GetHlsStreamingSessionUrlResponse,
    GetMediaForFragmentListResponse,
    ListFragmentsResponse
)
from chainsaws.aws.kvs.response.DataPointResponse import GetDataEndpointResponse
from chainsaws.aws.kvs.request.StreamRequest import ListStreamNameCondition
from chainsaws.aws.kvs.request.ArchivedMediaRequest import (
    ClipFragmentSelector,
    DashFragmentSelector,
    HLSFragmentSelector,
    FragmentSelector
)
from chainsaws.aws.kvs.request.MediaRequest import GetMediaStartSelector
from chainsaws.aws.kvs.response.MediaResponse import GetMediaResponse

class KVS:
    def __init__(
        self,
        boto3_session: Session,
        config: Optional[KVSAPIConfig] = None
    ) -> None:
        self.config = config or KVSAPIConfig()
        self.kinesis_video_client = boto3_session.client(
            service_name="kinesisvideo",
            region_name=self.config.region,
        )

    
    def create_stream(
            self,
            stream_name: str,
            data_retention_in_hours: int = 0,
            tags: Optional[Dict[str, str]] = None,
        ) -> CreateStreamResponse:
        """
        Create a new KVS stream.

        Args:
            stream_name: The name of the stream to create.
            data_retention_in_hours: The number of hours to retain the stream data.
            tags: A dictionary of tags to add to the stream.

        Returns:
            CreateStreamResponse: The response from the KVS create stream operation.
        """
        try:
            params = dict(
                StreamName=stream_name,
                DataRetentionInHours=data_retention_in_hours,
            )

            if tags is not None:
                params["Tags"] = tags

            response = self.kinesis_video_client.create_stream(
                **params,
            )
            return response
        except Exception as e:
            raise KVSCreateStreamError(stream_name, str(e))
    

    def update_stream(
            self,
            stream_name: str,
            stream_arn: str,
            current_version: str,
        ) -> None:
        """
        Update an existing KVS stream.

        Args:
            stream_name: The name of the stream to update.
            stream_arn: The ARN of the stream to update.
            current_version: The current version of the stream. (REQUIRED)

        Returns:
            None
        """

        try:
            self.kinesis_video_client.update_stream(
                StreamName=stream_name,
                StreamARN=stream_arn,
                CurrentVersion=current_version,
            )
        except Exception as e:
            raise KVSUpdateStreamError(stream_name, str(e))
    

    def delete_stream(
          self,
          stream_arn: str,
          current_version: Optional[str] = None,
      ) -> None:
        """
        Delete an existing KVS stream.

        Args:
            stream_arn: The ARN of the stream to delete.
            current_version: The current version of the stream. Use as a safeguard to prevent accidental deletion. (OPTIONAL)
        """

        params = dict(
            StreamARN=stream_arn,
        )

        if current_version is not None:
            params["CurrentVersion"] = current_version

        try:
            self.kinesis_video_client.delete_stream(**params)
        except Exception as e:
            raise KVSDeleteStreamError(stream_arn, str(e))
        
    
    def get_stream(
        self,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
    ) -> GetStreamResponse:
        """
        Get information about a KVS stream.

        Args:
            stream_arn: The ARN of the stream to get.
            stream_name: The name of the stream to get. (OPTIONAL)
        """
        if not stream_arn and not stream_name:
            raise ValueError("Either stream_arn or stream_name must be provided")
        
        try:
            if stream_arn:
                response = self.kinesis_video_client.describe_stream(
                    StreamARN=stream_arn,
                )
            else:
                response = self.kinesis_video_client.describe_stream(
                    StreamName=stream_name,
                )
            return response
        except Exception as e:
            raise KVSGetStreamError(stream_arn, str(e))
        
      
    def list_streams(
          self,
          max_results: Optional[int] = None,
          next_token: Optional[str] = None,
          stream_name_condition: Optional[ListStreamNameCondition] = None,
      ) -> ListStreamsResponse:
        """
        List KVS streams.

        Args:
            max_results: The maximum number of streams to return.
            next_token: The token to use to get the next page of results.
            stream_name_condition: The condition to use to filter the streams.
        """
        try:
            params = dict()

            if max_results is not None:
                params["MaxResults"] = max_results
            if next_token is not None:
                params["NextToken"] = next_token
            if stream_name_condition is not None:
                params["StreamNameCondition"] = stream_name_condition

            response = self.kinesis_video_client.list_streams(
                **params,
            )

            return {
                "Items": response["StreamInfoList"],
                "NextToken": response.get("NextToken", None),
            }
        except Exception as e:
            raise KVSListStreamsError(str(e))
        

    def update_data_retention(
        self,
        current_version: str,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
        data_retention_change_in_hours: int = 0,
        operation: Literal["increase", "decrease"] = "increase",
    ) -> None:
        """
        Update the data retention for a KVS stream.

        Args:
            current_version: The current version of the stream.
            stream_arn: The ARN of the stream to update. (OPTIONAL)
            stream_name: The name of the stream to update. (OPTIONAL)
            data_retention_change_in_hours: The data retention change in hours.
            operation: The operation to perform.
        """
        if not stream_arn and not stream_name:
            raise ValueError("Either stream_arn or stream_name must be provided")
        
        data_retention_operation = 'INCREASE_DATA_RETENTION' if operation == 'increase' else 'DECREASE_DATA_RETENTION'

        try:
            if stream_arn:
                response = self.kinesis_video_client.update_data_retention(
                    StreamARN=stream_arn,
                    CurrentVersion=current_version,
                    Operation=data_retention_operation,
                    DataRetentionChangeInHours=data_retention_change_in_hours,
                )
            else:
                response = self.kinesis_video_client.update_data_retention(
                    StreamName=stream_name,
                    CurrentVersion=current_version,
                    Operation=data_retention_operation,
                    DataRetentionChangeInHours=data_retention_change_in_hours,
                )

            return response
        except Exception as e:
            raise KVSUpdateDataRetentionError(stream_arn, str(e))

    def get_data_endpoint(
        self,
        api_name: KVSDataEndpointAPI,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
    ) -> GetDataEndpointResponse:
        """
        Get the data endpoint for a KVS stream.

        Args:
            api_name: The API name to get the data endpoint for.
            stream_arn: The ARN of the stream to get the data endpoint for. (OPTIONAL)
            stream_name: The name of the stream to get the data endpoint for. (OPTIONAL)
        """
        if not stream_arn and not stream_name:
            raise ValueError("Either stream_arn or stream_name must be provided")
        
        try:
            if stream_arn:
                response = self.kinesis_video_client.get_data_endpoint(
                    StreamARN=stream_arn,
                    APIName=api_name,
                )
            else:
                response = self.kinesis_video_client.get_data_endpoint(
                    StreamName=stream_name,
                    APIName=api_name,
                )
            return response
        except Exception as e:
            raise KVSGetDataEndpointError(str(e))



class KVSArchivedMedia:
    def __init__(
        self,
        boto3_session: Session,
        endpoint_url: str,
        config: Optional[KVSAPIConfig] = None,
    ) -> None:
        self.config = config or KVSAPIConfig()
        self.kinesis_video_archived_media_client = boto3_session.client(
            service_name="kinesis-video-archived-media",
            region_name=self.config.region,
            endpoint_url=endpoint_url,
        )

      
    def get_clip(
        self,
        clip_fragment_selector: ClipFragmentSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetClipResponse:
        try:
            if not stream_arn and not stream_name:
                raise ValueError("Either stream_arn or stream_name must be provided")
            
            if not clip_fragment_selector:
                raise ValueError("clip_fragment_selector must be provided")
            
            if clip_fragment_selector['TimestampRange']['StartTimestamp'] >= clip_fragment_selector['TimestampRange']['EndTimestamp']:
                raise ValueError("StartTimestamp must be less than EndTimestamp")
            
            if stream_arn:
                response = self.kinesis_video_archived_media_client.get_clip(
                    StreamARN=stream_arn,
                    ClipFragmentSelector=clip_fragment_selector,
                )
            else:
                response = self.kinesis_video_archived_media_client.get_clip(
                    StreamName=stream_name,
                    ClipFragmentSelector=clip_fragment_selector,
                )

            return {
                "ContentType": response["ContentType"],
                "Payload": response["Payload"],
            }
        except Exception as e:
            raise KVSGetClipError(str(e))
        

    def get_dash_streaming_session_url(
        self,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
        playback_mode: Literal["LIVE", "LIVE_REPLAY", "ON_DEMAND"] = "LIVE",
        dash_fragment_selector: Optional[DashFragmentSelector] = None,
        display_fragment_timestamp: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        display_fragment_number: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        expires: Optional[int] = None,
        max_manifest_fragment_results: Optional[int] = None,
    ) -> GetDashStreamingSessionUrlResponse:
        if not stream_arn and not stream_name:
            raise ValueError("Either stream_arn or stream_name must be provided")

        if playback_mode == 'LIVE' and dash_fragment_selector["TimestampRange"] is not None:
            raise ValueError("TimestampRange is not supported for LIVE playback mode")
        
        if playback_mode == 'LIVE_REPLAY' and dash_fragment_selector["TimestampRange"] is None:
            raise ValueError("TimestampRange is required for LIVE_REPLAY playback mode")
        
        if playback_mode == 'ON_DEMAND' and dash_fragment_selector["TimestampRange"] is None:
            raise ValueError("TimestampRange is required for ON_DEMAND playback mode")
        
        if expires is not None and (expires < 300 or expires > 43200):
            raise ValueError("Expire time must be between 300 and 43200 seconds")
        
        params = dict()

        if stream_arn is not None:
            params["StreamARN"] = stream_arn
        if stream_name is not None:
            params["StreamName"] = stream_name
        if playback_mode is not None:
            params["PlaybackMode"] = playback_mode
        if dash_fragment_selector is not None:
            params["DashFragmentSelector"] = dash_fragment_selector
        if display_fragment_timestamp is not None:
            params["DisplayFragmentTimestamp"] = display_fragment_timestamp
        if display_fragment_number is not None:
            params["DisplayFragmentNumber"] = display_fragment_number
        if expires is not None:
            params["Expires"] = expires
        if max_manifest_fragment_results is not None:
            params["MaxManifestFragmentResults"] = max_manifest_fragment_results
            
        try :
            response = self.kinesis_video_archived_media_client.get_dash_streaming_session_url(
                **params,
            )

            return response
        except Exception as e:
            raise KVSGetDashStreamingSessionUrlError(str(e))

    
    def get_hls_streaming_session_url(
        self,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
        playback_mode: Literal["LIVE", "LIVE_REPLAY", "ON_DEMAND"] = "LIVE",
        hls_fragment_selector: Optional[HLSFragmentSelector] = None,
        container_format: Optional[Literal["FRAGMENTED_MP4", "MPEG_TS"]] = None,
        discontinuity_mode: Optional[Literal["ALWAYS", "NEVER", "ON_DISCONTINUITY"]] = None,
        display_fragment_timestamp: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        expires: Optional[int] = None,
        max_media_playlist_fragment_results: Optional[int] = None,
    ) -> GetHlsStreamingSessionUrlResponse:
        if not stream_arn and not stream_name:
            raise ValueError("Either stream_arn or stream_name must be provided")
        
        if expires is not None and (expires < 300 or expires > 43200):
            raise ValueError("Expire time must be between 300 and 43200 seconds")
        
        params = dict()

        if stream_arn is not None:
            params["StreamARN"] = stream_arn
        if stream_name is not None:
            params["StreamName"] = stream_name
        if playback_mode is not None:
            params["PlaybackMode"] = playback_mode
        if hls_fragment_selector is not None:
            params["HLSFragmentSelector"] = hls_fragment_selector
        if container_format is not None:
            params["ContainerFormat"] = container_format
        if discontinuity_mode is not None:
            params["DiscontinuityMode"] = discontinuity_mode
        if display_fragment_timestamp is not None:
            params["DisplayFragmentTimestamp"] = display_fragment_timestamp
        if expires is not None:
            params["Expires"] = expires
        if max_media_playlist_fragment_results is not None:
            params["MaxMediaPlaylistFragmentResults"] = max_media_playlist_fragment_results
        
        try:
            response = self.kinesis_video_archived_media_client.get_hls_streaming_session_url(
                **params,
            )

            return response
        except Exception as e:
            raise KVSGetHlsStreamingSessionUrlError(str(e))
        
    
    def get_media_for_fragment_list(
      self,
      fragment_list: List[str],
      stream_name: Optional[str] = None,
      stream_arn: Optional[str] = None,
    ) -> GetMediaForFragmentListResponse:
      if not stream_arn and not stream_name:
        raise ValueError("Either stream_arn or stream_name must be provided")
      
      if not fragment_list:
        raise ValueError("fragment_list must be provided")
      
      params = dict()

      if stream_arn is not None:
        params["StreamARN"] = stream_arn
      if stream_name is not None:
        params["StreamName"] = stream_name
      if fragment_list is not None:
        params["Fragments"] = fragment_list
      
      try:
        response = self.kinesis_video_archived_media_client.get_media_for_fragment_list(
          **params,
        )

        return response
      except Exception as e:
        raise KVSGetMediaForFragmentListError(str(e))
      

    def list_fragments(
        self,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
        fragment_selector: Optional[FragmentSelector] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListFragmentsResponse:
      if not stream_arn and not stream_name:
        raise ValueError("Either stream_arn or stream_name must be provided")
      
      if not fragment_selector:
        raise ValueError("fragment_selector must be provided")
      
      params = dict()

      if stream_arn is not None:
        params["StreamARN"] = stream_arn
      if stream_name is not None:
        params["StreamName"] = stream_name
      if fragment_selector is not None:
        params["FragmentSelector"] = fragment_selector
      if max_results is not None:
        params["MaxResults"] = max_results
      if next_token is not None:
        params["NextToken"] = next_token

      try:
        response = self.kinesis_video_archived_media_client.list_fragments(
          **params,
        )

        return response
      except Exception as e:
        raise KVSListFragmentsError(str(e))
      

class KVSVideoMedia:
    def __init__(
        self,
        boto3_session: Session,
        endpoint_url: str,
        config: Optional[KVSAPIConfig] = None,
    ) -> None:
        self.config = config or KVSAPIConfig()
        self.kinesis_video_media_client = boto3_session.client(
            service_name="kinesis-video-media",
            region_name=self.config.region,
            endpoint_url=endpoint_url,
        )

    def get_media(
        self,
        start_selector: GetMediaStartSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetMediaResponse:
      if not stream_arn and not stream_name:
        raise ValueError("Either stream_arn or stream_name must be provided")
      
      if not start_selector:
        raise ValueError("start_selector must be provided")
      
      if start_selector['StartSelectorType'] == 'PRODUCER_TIMESTAMP' or start_selector['StartSelectorType'] == 'SERVER_TIMESTAMP':
          if not start_selector['StartTimestamp']:
              raise ValueError("StartTimestamp must be provided")
      
      params = dict()

      if stream_arn is not None:
        params["StreamARN"] = stream_arn
      if stream_name is not None:
        params["StreamName"] = stream_name
      if start_selector is not None:
        params["StartSelector"] = start_selector

      try:
        response = self.kinesis_video_media_client.get_media(
          **params,
        )

        return response
      except Exception as e:
        raise KVSGetMediaError(str(e))