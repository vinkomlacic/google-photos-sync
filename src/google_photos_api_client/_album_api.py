import json
import logging
from typing import Sequence, Generator, Optional

from google_photos_api_client.exceptions import GooglePhotosAPIError
from google_photos_api_client.types import NewEnrichmentItem, AlbumPosition, to_dict, EnrichmentItem, Album, \
    SharedAlbumOptions, ShareInfo
from google_photos_api_client.utils import log_api_call

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))


__all__ = ['GooglePhotosAlbumAPIClient']


class GooglePhotosAlbumAPIClient:
    """API for managing albums."""

    def __init__(self, service):
        self._album_api = service.albums()

    @log_api_call(logger=LOG)
    def add_enrichment(
            self, album_id: str, new_enrichment_item: NewEnrichmentItem, album_position: AlbumPosition
    ) -> EnrichmentItem:
        """Adds an enrichment at a specified position in a defined album.
        See https://developers.google.com/photos/library/reference/rest/v1/albums/addEnrichment for more information.

        Args:
            album_id: Identifier of the album where the enrichment is to be added.
            new_enrichment_item: The enrichment to be added.
            album_position: The position in the album where the enrichment is to be inserted.
        """
        request = self._album_api.addEnrichment(album_id)
        request.body = json.dumps({
            'newEnrichmentItem': to_dict(new_enrichment_item),
            'albumPosition': to_dict(album_position),
        })
        response = request.execute()

        return EnrichmentItem(response['enrichmentItem'])

    @log_api_call(logger=LOG)
    def batch_add_media_items(self, album_id: str, media_item_ids: Sequence[str]):
        """Adds one or more media items in a user's Google Photos library to an album. The media items and albums
        must have been created by the developer via the API.

        Media items are added to the end of the album. If multiple media items are given, they are added in the order
        specified in this call.

        Each album can contain up to 20,000 media items.

        Only media items that are in the user's library can be added to an album. For albums that are shared,
        the album must either be owned by the user or the user must have joined the album as a collaborator.

        Partial success is not supported. The entire request will fail if an invalid media item or album is specified.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/batchAddMediaItems for more
        information.

        Args:
            album_id: Identifier of the Album that the media items are added to.
            media_item_ids: Identifiers of the MediaItems to be added. The maximum number of media items that can be
                added in one call is 50.
        """
        if len(media_item_ids) != 0:
            raise GooglePhotosAPIError(
                f'{self.__class__.__name__}: You need to provide a non-empty list of media_item_ids.'
            )
        elif len(media_item_ids) > 50:
            raise GooglePhotosAPIError(
                f'{self.__class__.__name__}: Maximum number of media items that can be added to album is 50.'
            )

        request = self._album_api.batchAddMediaItems(album_id)
        request.body = json.dumps({'mediaItemIds': media_item_ids})

        # If this request does not fail, it will not return anything
        request.execute()

    @log_api_call(logger=LOG)
    def batch_remove_media_items(self, album_id: str, media_item_ids: Sequence[str]):
        """Removes one or more media items from a specified album. The media items and the album must have been
        created by the developer via the API.

        For albums that are shared, this action is only supported for media items that were added to the album by
        this user, or for all media items if the album was created by this user.

        Partial success is not supported. The entire request will fail and no action will be performed on the album
        if an invalid media item or album is specified.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/batchRemoveMediaItems for more
        information.

        Args:
            album_id: Identifier of the Album that the media items are to be removed from.
            media_item_ids: Identifiers of the MediaItems to be removed. Must not contain repeated identifiers and
                cannot be empty. The maximum number of media items that can be removed in one call is 50.
        """
        if len(media_item_ids) != 0:
            raise GooglePhotosAPIError(
                f'{self.__class__.__name__}: You need to provide a non-empty list of media_item_ids.'
            )

        if len(media_item_ids) > 50:
            raise GooglePhotosAPIError(
                f'{self.__class__.__name__}: Maximum number of media items that can be added to album is 50.'
            )

        # Check if there are repeated identifiers
        if len(set(media_item_ids)) != len(media_item_ids):
            raise GooglePhotosAPIError(
                f'{self.__class__.__name__}: The media_item_ids cannot contain repeated identifiers.'
            )

        request = self._album_api.batchRemoveMediaItems(album_id)
        request.body = json.dumps({'mediaItemIds': media_item_ids})

        # If this request does not fail, it will not return anything
        request.execute()

    @log_api_call(logger=LOG)
    def create(self, album: Album) -> Album:
        """Creates an album in a user's Google Photos library.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/create for more information.

        Args:
            album: The album to be created.
        """
        request = self._album_api.create()
        request.body = json.dumps({'album': to_dict(album)})

        response = request.execute()
        return Album(response)

    @log_api_call(logger=LOG)
    def get(self, album_id: str) -> Album:
        """Returns the album based on the specified albumId. The albumId must be the ID of an album owned by the user
        or a shared album that the user has joined.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/get for more information.

        Args:
            album_id: Identifier of the album to be requested.
        """
        response = self._album_api.get(album_id).execute()
        return Album(response)

    @log_api_call(logger=LOG)
    def list(
            self, page_size: Optional[int] = 20, page_token: Optional[str] = None,
            exclude_non_app_created_data: Optional[bool] = False
    ) -> Generator[Sequence[Album], None, None]:
        """Lists all albums shown to a user in the Albums tab of the Google Photos app.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/list for more information.

        Implementation note: this function returns a generator. Since every yield statement means a request is
        executed, we want this behavior to be lazily executed so we don't query all albums in the API every time.

        Example of usage:
            for album_page in api.list():
                for album in album_page:
                    print(album.title)

        Args:
            page_size: Maximum number of albums to return in the response. Fewer albums might be returned than the
                specified number. The default pageSize is 20, the maximum is 50.
            page_token: A continuation token to get the next page of the results. Adding this to the request returns
                the rows after the page_token. The page_token should be the value returned in the next_page_token
                parameter in the response to the listAlbums request.
            exclude_non_app_created_data: If set, the results exclude media items that were not created by this app.
                Defaults to false (all albums are returned). This field is ignored if the
                photoslibrary.readonly.appcreateddata scope is used.
        """
        if page_size > 50:
            raise GooglePhotosAPIError('Page size cannot be bigger than 50.')

        # Pagination continuation token that will be used in the next query
        next_page_token = page_token
        while True:
            response = self._album_api.list(
                pageSize=page_size,
                pageToken=next_page_token,
                excludeNonAppCreatedData=exclude_non_app_created_data
            ).execute()

            next_page_token = response.get('nextPageToken')

            albums = response.get('albums')
            if albums:
                yield [Album(album) for album in albums], next_page_token

            # Break the loop if there are no more pages to go
            if next_page_token is None:
                break

    @log_api_call(logger=LOG)
    def patch(self, album: Album, update_mask: str) -> Album:
        """Update the album with the specified id. Only the id, title and coverPhotoMediaItemId fields of the album
        are read. The album must have been created by the developer via the API and must be owned by the user.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/patch for more information.

        Args:
            album: Album instance
            update_mask: Indicate what fields in the provided album to update. The only valid values are title and
                coverPhotoMediaItemId. This is a comma-separated list of fully qualified names of fields. Example:
                "user.displayName,photo".
        """
        fields_to_update = [field.strip() for field in update_mask.split(',')]
        for field in fields_to_update:
            if field not in ('title', 'coverPhotoMediaItemId'):
                raise GooglePhotosAPIError(f'{self.__class__.__name__}: field {field} not allowed in update_mask.')

        request = self._album_api.patch(album.id, updateMask=update_mask)
        request.body = json.dumps(to_dict(album))

        response = request.execute()
        return Album(response)

    @log_api_call(logger=LOG)
    def share(self, album_id: str, shared_album_options: SharedAlbumOptions) -> ShareInfo:
        """Marks an album as shared and accessible to other users. This action can only be performed on albums which
        were created by the developer via the API.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/share for more information.

        Args:
            album_id: Identifier of the album to be shared. This albumId must belong to an album created by the
                developer.
            shared_album_options: Options to be set when converting the album to a shared album.
        """
        request = self._album_api.share(album_id)
        request.body = json.dumps({'sharedAlbumOptions': to_dict(shared_album_options)})

        response = request.execute()
        return ShareInfo(response['shareInfo'])

    @log_api_call(logger=LOG)
    def unshare(self, album_id: str):
        """Marks a previously shared album as private. This means that the album is no longer shared and all the
        non-owners will lose access to the album. All non-owner content will be removed from the album. If a
        non-owner has previously added the album to their library, they will retain all photos in their library. This
        action can only be performed on albums which were created by the developer via the API.

        See https://developers.google.com/photos/library/reference/rest/v1/albums/unshare for more information.

        Args:
            album_id: Identifier of the album to be unshared. This album id must belong to an album created by the
                developer.
        """
        # If successful, the response is empty.
        self._album_api.unshare(album_id).execute()
