import json
import logging
from typing import Generator, Sequence, Optional

from google_photos_api_client.exceptions import GooglePhotosAPIError
from google_photos_api_client.types import Album
from google_photos_api_client.utils import log_api_call

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))


__all__ = ['GooglePhotosSharedAlbumAPIClient']


class GooglePhotosSharedAlbumAPIClient:
    """API for managing shared albums. We actually deal with regular Album objects, only these ones contain the
    shareInfo property."""

    def __init__(self, service):
        self._shared_album_api = service.shared_albums()

    @log_api_call(logger=LOG)
    def get(self, share_token: str) -> Album:
        """Returns the album based on the specified shareToken.

        Args:
            share_token: Share token of the album to be requested.
        """
        response = self._shared_album_api.get(share_token).execute()

        return Album(response)

    @log_api_call(logger=LOG)
    def join(self, share_token: str) -> Album:
        """Joins a shared album on behalf of the Google Photos user.

        Args:
            share_token: Token to join the shared album on behalf of the user.
        """
        request = self._shared_album_api.join()
        request.body = json.dumps({'shareToken': share_token})

        response = request.execute()

        return Album(response['album'])

    @log_api_call(logger=LOG)
    def leave(self, share_token: str):
        """Leaves a previously-joined shared album on behalf of the Google Photos user. The user must not own this
        album.

        Args:
            share_token: Token to leave the shared album on behalf of the user.
        """
        request = self._shared_album_api.leave()
        request.body = json.dumps({'shareToken': share_token})

        # If successful, the response body is empty.
        request.execute()

    @log_api_call(logger=LOG)
    def list(
            self, page_size: Optional[int] = 20, page_token: Optional[str] = None,
            exclude_non_app_created_data: Optional[bool] = False
    ) -> Generator[Sequence[Album], None, None]:
        """Lists all shared albums available in the Sharing tab of the user's Google Photos app.


        See https://developers.google.com/photos/library/reference/rest/v1/sharedAlbums/list for more information.

        Implementation note: this function returns a generator. Since every yield statement means a request is
        executed, we want this behavior to be lazily executed so we don't query all albums in the API every time.

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
            response = self._shared_album_api.list(
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
