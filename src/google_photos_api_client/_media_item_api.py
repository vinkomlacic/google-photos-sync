import json
import logging
from typing import Sequence, Optional, Generator

from google_photos_api_client.exceptions import GooglePhotosAPIError
from google_photos_api_client.types import (
    AlbumPosition, to_dict, NewMediaItem, NewMediaItemResult, MediaItemResult, MediaItem, Filters
)
from google_photos_api_client.utils import log_api_call

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))


__all__ = ['GooglePhotosMediaItemAPIClient']


class GooglePhotosMediaItemAPIClient:
    """API for managing different media items like photos or videos."""

    def __init__(self, service):
        self._media_item_api = service.mediaItems()

    @log_api_call(logger=LOG)
    def batch_create(
            self, new_media_items: Sequence[NewMediaItem],
            album_position: Optional[AlbumPosition] = None, album_id: Optional[str] = None
    ) -> Sequence[NewMediaItemResult]:
        """Creates one or more media items in a user's Google Photos library. This is the second step for creating a
        media item. For details regarding Step 1, uploading the raw bytes to a Google Server, see Uploading media.

        This call adds the media item to the library. If an album id is specified, the call adds the media item to the
        album too. Each album can contain up to 20,000 media items. By default, the media item will be added to the end
        of the library or album.

        If an album id and position are both defined, the media item is added to the album at the specified position.

        If the call contains multiple media items, they're added at the specified position. If you are creating a media
        item in a shared album where you are not the owner, you are not allowed to position the media item. Doing so will
        result in a BAD REQUEST error.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate for more information.

        Args:
            new_media_items: List of media items to be created.
            album_position: Position in the album where the
                media items are added. If not specified, the media items are added to the end of the album (as per the
                default value, that is, LAST_IN_ALBUM). The request fails if this field is set and the albumId is not
                specified. The request will also fail if you set the field and are not the owner of the shared album.
            album_id: Identifier of the album where the media items are added. The media items are also added to
                the user's library.
        """
        request = self._media_item_api.batchCreate()
        body_dict = {'newMediaItems': [to_dict(new_media_item) for new_media_item in new_media_items]}
        if album_id:
            body_dict.update({'albumId': album_id})
        if album_id and album_position:
            body_dict.update({'albumPosition': to_dict(album_position)})

        if album_position and album_id is None:
            LOG.warning(f'Album position cannot be specified without album ID. Ignoring album position argument.')

        request.body = json.dumps(body_dict)

        response = request.execute()

        return [NewMediaItemResult(new_media_item_result) for new_media_item_result in response['newMediaItemResults']]

    @log_api_call(logger=LOG)
    def batch_get(self, media_item_ids: Sequence[str]) -> Sequence[MediaItemResult]:
        """Returns the list of media items for the specified media item identifiers. Items are returned in the same
        order as the supplied identifiers.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchGet for more information.

        Args: media_item_ids: Identifiers of the media items to be requested. Must not contain repeated identifiers
            and cannot be empty. The maximum number of media items that can be retrieved in one call is 50.
        """
        if len(media_item_ids) > 50:
            raise GooglePhotosAPIError(f'Media item IDs list cannot be longer than 50.')

        request = self._media_item_api.batchGet(mediaItemIds=media_item_ids)
        response = request.execute()

        return [MediaItemResult(media_item_result) for media_item_result in response['mediaItemResults']]

    @log_api_call(logger=LOG)
    def get(self, media_item_id: str) -> MediaItem:
        """Returns the media item for the specified media item identifier.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/get for more information.

        Args:
            media_item_id: Identifier of the media item to be requested.
        """
        response = self._media_item_api.get(media_item_id).execute()
        return MediaItem(response)

    @log_api_call(logger=LOG)
    def list(self, page_size: Optional[int] = 25, page_token: Optional[str] = None) -> Generator:
        """List all media items from a user's Google Photos library.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/list for more information.

        Implementation note: this function returns a generator. Since every yield statement means a request is
        executed, we want this behavior to be lazily executed so we don't query all albums in the API every time.

        Args:
            page_size: Maximum number of media items to return in the response. Fewer media items might be returned
                than the specified number. The default pageSize is 25, the maximum is 100.
            page_token: A continuation token to get the next page of the results. Adding this to the request returns
                the rows after the pageToken. The pageToken should be the value returned in the nextPageToken parameter
                in the response to the listMediaItems request.
        """
        if page_size > 100:
            raise GooglePhotosAPIError('Page size cannot be bigger than 100.')

        # Pagination continuation token that will be used in the next query
        next_page_token = page_token
        while True:
            response = self._media_item_api.list(
                pageSize=page_size,
                pageToken=next_page_token,
            ).execute()

            next_page_token = response.get('nextPageToken')

            media_items = response.get('mediaItems')
            if media_items:
                yield [MediaItem(media_item) for media_item in media_items], next_page_token

            # Break the loop if there are no more pages to go
            if next_page_token is None:
                break

    @log_api_call(logger=LOG)
    def patch(self, media_item: MediaItem, update_mask: str) -> MediaItem:
        """Update the media item with the specified id. Only the id and description fields of the media item are read.
        The media item must have been created by the developer via the API and must be owned by the user.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/patch for more information.

        Args:
            media_item: instance of MediaItem
            update_mask: Indicate what fields in the provided media item to update. The only valid value is description.
                This is a comma-separated list of fully qualified names of fields. Example: "user.displayName,photo".
        """
        if update_mask != 'description':
            raise GooglePhotosAPIError("The only valid value for update_mask is 'description'")

        request = self._media_item_api.patch(media_item.id)
        request.body = json.dumps(to_dict(media_item))

        response = request.execute()

        return MediaItem(response)

    def search(self, album_id: Optional[str] = None, page_size: Optional[int] = 25, page_token: Optional[str] = None,
               filters: Optional[Filters] = None, order_by: Optional[str] = None) -> Generator:
        """Searches for media items in a user's Google Photos library. If no filters are set, then all media items in
        the user's library are returned. If an album is set, all media items in the specified album are returned.

        If filters are specified, media items that match the filters from the user's library are listed.
        If you set both the album and the filters, the request results in an error.

        Implementation note: this function returns a generator. Since every yield statement means a request is
        executed, we want this behavior to be lazily executed so we don't query all albums in the API every time.

        See https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search for more information.

        Args:
            album_id: Identifier of an album. If populated, lists all media items in specified album.
                Can't set in conjunction with any filters.
            page_size: Maximum number of media items to return in the response. Fewer media items might be returned
                than the specified number. The default pageSize is 25, the maximum is 100.
            page_token: A continuation token to get the next page of the results. Adding this to the request returns
                the rows after the pageToken. The pageToken should be the value returned in the nextPageToken parameter
                in the response to the searchMediaItems request.
            filters: Filters to apply to the request. Can't be set in conjunction with an albumId.
            order_by: An optional field to specify the sort order of the search results. The orderBy field only works
                when a dateFilter is used. When this field is not specified, results are displayed newest first,
                oldest last by their creationTime. Providing MediaMetadata.creation_time displays search results in the
                opposite order, oldest first then newest last. To display results newest first then oldest last, include
                the desc argument as follows: MediaMetadata.creation_time desc. The only additional filters that can
                be used with this parameter are includeArchivedMedia and excludeNonAppCreatedData. No other filters are
                supported.
        """
        if album_id and filters:
            raise GooglePhotosAPIError('Album ID cannot be used in conjunction with filters.')

        if page_size > 100:
            raise GooglePhotosAPIError('Page size cannot be bigger than 100.')

        body_dict = {'pageSize': page_size}

        if album_id:
            body_dict.update({'albumId': album_id})

        if page_token:
            body_dict.update({'pageToken': page_token})

        if filters:
            body_dict.update({'filters': to_dict(filters)})

        if order_by:
            body_dict.update({'orderBy': order_by})

        next_page_token = page_token
        while True:
            request = self._media_item_api.search()
            body_dict.update({'pageToken': next_page_token})
            request.body = json.dumps(body_dict)

            response = request.execute()

            next_page_token = response.get('nextPageToken')
            if media_items := response.get('mediaItems'):
                yield [MediaItem(media_item) for media_item in media_items], next_page_token

            # Break the loop if there are no more pages to go
            if next_page_token is None:
                break
