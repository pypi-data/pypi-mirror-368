from typing import Optional, Dict, List, Literal

from chainsaws.aws.kvs.kvs_exception import KVSGetMediaForFragmentListError
from chainsaws.aws.kvs.kvs_models import KVSAPIConfig, KVSDataEndpointAPI
from chainsaws.aws.kvs._kvs_internal import KVS, KVSArchivedMedia, KVSVideoMedia
from chainsaws.aws.kvs.response.StreamResponse import (
    CreateStreamResponse, GetStreamResponse, ListStreamsResponse
)
from chainsaws.aws.kvs.response.ArchivedMediaResponse import (
    GetClipResponse, GetDashStreamingSessionUrlResponse, GetHlsStreamingSessionUrlResponse, GetMediaForFragmentListResponse, ListFragmentsResponse
)
from chainsaws.aws.kvs.response.DataPointResponse import GetDataEndpointResponse
from chainsaws.aws.kvs.request.StreamRequest import ListStreamNameCondition
from chainsaws.aws.kvs.request.ArchivedMediaRequest import (
    ClipFragmentSelector, DashFragmentSelector, HLSFragmentSelector, FragmentSelector
)
from chainsaws.aws.kvs.request.MediaRequest import GetMediaStartSelector
from chainsaws.aws.shared import session
from chainsaws.aws.kvs.response.MediaResponse import GetMediaResponse

class KVSAPI:
    def __init__(
        self,
        config: Optional[KVSAPIConfig] = None,
    ) -> None:
        self.config = config or KVSAPIConfig()
        self.boto3_session = session.get_boto_session(
            self.config.credentials if self.config.credentials else None,
        )
        self.kvs = KVS(
            boto3_session=self.boto3_session,
            config=self.config,
        )
        self._archived_media = None

    def create_stream(
        self,
        stream_name: str,
        data_retention_in_hours: int = 0,
        tags: Optional[Dict[str, str]] = None,
    ) -> CreateStreamResponse:
        return self.kvs.create_stream(
            stream_name=stream_name,
            data_retention_in_hours=data_retention_in_hours,
            tags=tags,
        )

    def update_stream(
        self,
        stream_name: str,
        stream_arn: str,
        current_version: str,
    ) -> None:
        return self.kvs.update_stream(
            stream_name=stream_name,
            stream_arn=stream_arn,
            current_version=current_version,
        )

    def delete_stream(
        self,
        stream_arn: str,
        current_version: Optional[str] = None,
    ) -> None:
        return self.kvs.delete_stream(
            stream_arn=stream_arn,
            current_version=current_version,
        )

    def get_stream(
        self,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
    ) -> GetStreamResponse:
        return self.kvs.get_stream(
            stream_arn=stream_arn,
            stream_name=stream_name,
        )

    def list_streams(
        self,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        stream_name_condition: Optional[ListStreamNameCondition] = None,
    ) -> ListStreamsResponse:
        return self.kvs.list_streams(
            max_results=max_results,
            next_token=next_token,
            stream_name_condition=stream_name_condition,
        )

    def update_data_retention(
        self,
        current_version: str,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
        data_retention_change_in_hours: int = 0,
        operation: Literal["increase", "decrease"] = "increase",
    ) -> None:
        return self.kvs.update_data_retention(
            current_version=current_version,
            stream_arn=stream_arn,
            stream_name=stream_name,
            data_retention_change_in_hours=data_retention_change_in_hours,
            operation=operation,
        )

    def get_data_endpoint(
        self,
        api_name: KVSDataEndpointAPI,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
    ) -> GetDataEndpointResponse:
        return self.kvs.get_data_endpoint(
            api_name=api_name,
            stream_arn=stream_arn,
            stream_name=stream_name,
        )

    def _get_archived_media(self, endpoint_url: str) -> KVSArchivedMedia:
        if self._archived_media is None or self._archived_media.endpoint_url != endpoint_url:
            self._archived_media = KVSArchivedMedia(
                boto3_session=self.boto3_session,
                endpoint_url=endpoint_url,
                config=self.config,
            )
            self._archived_media.endpoint_url = endpoint_url  # for caching
        return self._archived_media

    def get_clip(
        self,
        endpoint_url: str,
        clip_fragment_selector: ClipFragmentSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetClipResponse:
        archived_media = self._get_archived_media(endpoint_url)
        return archived_media.get_clip(
            clip_fragment_selector=clip_fragment_selector,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )

    def get_dash_streaming_session_url(
        self,
        endpoint_url: str,
        stream_arn: Optional[str] = None,
        stream_name: Optional[str] = None,
        playback_mode: Literal["LIVE", "LIVE_REPLAY", "ON_DEMAND"] = "LIVE",
        dash_fragment_selector: Optional[DashFragmentSelector] = None,
        display_fragment_timestamp: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        display_fragment_number: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        expires: Optional[int] = None,
        max_manifest_fragment_results: Optional[int] = None,
    ) -> GetDashStreamingSessionUrlResponse:
        archived_media = self._get_archived_media(endpoint_url)
        return archived_media.get_dash_streaming_session_url(
            stream_arn=stream_arn,
            stream_name=stream_name,
            playback_mode=playback_mode,
            dash_fragment_selector=dash_fragment_selector,
            display_fragment_timestamp=display_fragment_timestamp,
            display_fragment_number=display_fragment_number,
            expires=expires,
            max_manifest_fragment_results=max_manifest_fragment_results,
        )

    def get_hls_streaming_session_url(
        self,
        endpoint_url: str,
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
        archived_media = self._get_archived_media(endpoint_url)
        return archived_media.get_hls_streaming_session_url(
            stream_name=stream_name,
            stream_arn=stream_arn,
            playback_mode=playback_mode,
            hls_fragment_selector=hls_fragment_selector,
            container_format=container_format,
            discontinuity_mode=discontinuity_mode,
            display_fragment_timestamp=display_fragment_timestamp,
            expires=expires,
            max_media_playlist_fragment_results=max_media_playlist_fragment_results,
        )

    def get_media_for_fragment_list(
        self,
        endpoint_url: str,
        fragment_list: List[str],
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetMediaForFragmentListResponse:
        archived_media = self._get_archived_media(endpoint_url)
        return archived_media.get_media_for_fragment_list(
            fragment_list=fragment_list,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )


    def list_fragments(
        self,
        endpoint_url: str,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
        fragment_selector: Optional[FragmentSelector] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListFragmentsResponse:
        archived_media = self._get_archived_media(endpoint_url)
        return archived_media.list_fragments(
            stream_name=stream_name,
            stream_arn=stream_arn,
            fragment_selector=fragment_selector,
            max_results=max_results,
            next_token=next_token,
        )


    def get_hls_url_simple(
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
        """
        stream_name 또는 stream_arn만 넘기면 endpoint_url을 자동으로 얻어 HLS 세션 URL을 반환하는 헬퍼 메서드입니다.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        endpoint_resp = self.get_data_endpoint(
            api_name='GET_HLS_STREAMING_SESSION_URL',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']
        return self.get_hls_streaming_session_url(
            endpoint_url=endpoint_url,
            stream_name=stream_name,
            stream_arn=stream_arn,
            playback_mode=playback_mode,
            hls_fragment_selector=hls_fragment_selector,
            container_format=container_format,
            discontinuity_mode=discontinuity_mode,
            display_fragment_timestamp=display_fragment_timestamp,
            expires=expires,
            max_media_playlist_fragment_results=max_media_playlist_fragment_results,
        )


    def get_dash_url_simple(
        self,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
        playback_mode: Literal["LIVE", "LIVE_REPLAY", "ON_DEMAND"] = "LIVE",
        dash_fragment_selector: Optional[DashFragmentSelector] = None,
        display_fragment_timestamp: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        display_fragment_number: Optional[Literal["ALWAYS", "NEVER"]] = 'NEVER',
        expires: Optional[int] = None,
        max_manifest_fragment_results: Optional[int] = None,
    ) -> GetDashStreamingSessionUrlResponse:
        """
        stream_name 또는 stream_arn만 넘기면 endpoint_url을 자동으로 얻어 DASH 세션 URL을 반환하는 헬퍼 메서드입니다.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        endpoint_resp = self.get_data_endpoint(
            api_name='GET_DASH_STREAMING_SESSION_URL',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']
        return self.get_dash_streaming_session_url(
            endpoint_url=endpoint_url,
            stream_name=stream_name,
            stream_arn=stream_arn,
            playback_mode=playback_mode,
            dash_fragment_selector=dash_fragment_selector,
            display_fragment_timestamp=display_fragment_timestamp,
            display_fragment_number=display_fragment_number,
            expires=expires,
            max_manifest_fragment_results=max_manifest_fragment_results,
        )

    def get_clip_simple(
        self,
        clip_fragment_selector: ClipFragmentSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetClipResponse:
        """
        stream_name 또는 stream_arn만 넘기면 endpoint_url을 자동으로 얻어 Clip을 반환하는 헬퍼 메서드입니다.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        endpoint_resp = self.get_data_endpoint(
            api_name='GET_CLIP',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']
        return self.get_clip(
            endpoint_url=endpoint_url,
            clip_fragment_selector=clip_fragment_selector,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )

    def list_fragments_simple(
        self,
        fragment_selector: FragmentSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
    ) -> ListFragmentsResponse:
        """
        stream_name 또는 stream_arn만 넘기면 endpoint_url을 자동으로 얻어 fragment 목록을 반환하는 헬퍼 메서드입니다.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        
        endpoint_resp = self.get_data_endpoint(
            api_name='LIST_FRAGMENTS',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']

        return self.list_fragments(
            endpoint_url=endpoint_url,
            stream_name=stream_name,
            stream_arn=stream_arn,
            fragment_selector=fragment_selector,
            max_results=max_results,
            next_token=next_token,
        )

    def get_media(
        self,
        start_selector: GetMediaStartSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetMediaResponse:
        """
        Retrieve media from the stream using the specified start selector.
        Args:
            start_selector: Dictionary specifying the start selector (type, timestamp, etc).
            stream_name: Name of the KVS stream.
            stream_arn: ARN of the KVS stream.
        Returns:
            GetMediaResponse: The media response.
        Raises:
            KVSGetMediaError: If the media cannot be retrieved.
        """
        return self.kvs_media.get_media(
            start_selector=start_selector,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )

    def get_media_simple(
        self,
        start_selector: GetMediaStartSelector,
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetMediaResponse:
        """
        Helper to retrieve media from the stream using the specified start selector.
        Automatically resolves the endpoint_url using get_data_endpoint.
        Args:
            start_selector: Start selector for the media request.
            stream_name: Name of the KVS stream.
            stream_arn: ARN of the KVS stream.
        Returns:
            GetMediaResponse: The media response.
        Raises:
            KVSGetMediaError: If the media cannot be retrieved.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        endpoint_resp = self.get_data_endpoint(
            api_name='GET_MEDIA',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']
        kvs_media = KVSVideoMedia(
            boto3_session=self.boto3_session,
            endpoint_url=endpoint_url,
            config=self.config,
        )
        return kvs_media.get_media(
            start_selector=start_selector,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )
    

    def get_media_for_fragment_list_simple(
        self,
        fragment_list: List[str],
        stream_name: Optional[str] = None,
        stream_arn: Optional[str] = None,
    ) -> GetMediaForFragmentListResponse:
        """
        Helper to retrieve media for a fragment list.
        Automatically resolves the endpoint_url using get_data_endpoint.
        """
        if not stream_name and not stream_arn:
            raise ValueError("Either stream_name or stream_arn must be provided")
        if stream_name and stream_arn:
            raise ValueError("Only one of stream_name or stream_arn must be provided")
        if not fragment_list:
            raise KVSGetMediaForFragmentListError(reason="fragment_list must be provided")
        
        endpoint_resp = self.get_data_endpoint(
            api_name='GET_MEDIA_FOR_FRAGMENT_LIST',
            stream_name=stream_name,
            stream_arn=stream_arn
        )
        endpoint_url = endpoint_resp['DataEndpoint']

        return self.get_media_for_fragment_list(
            endpoint_url=endpoint_url,
            fragment_list=fragment_list,
            stream_name=stream_name,
            stream_arn=stream_arn,
        )