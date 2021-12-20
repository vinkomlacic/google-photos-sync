import json
from typing import Callable, Optional, Sequence


class MockGooglePhotoService:
    """Mock service used for unit testing. Instead of actually contacting the Google server, it will retrieve the
    data from test_resources/fake_google_photos_data.json."""

    def __init__(self, fake_data_json_file_name: str = 'fake_google_photos_data.json'):
        with open(fake_data_json_file_name) as file:
            self.data = json.load(file)
            self._album_api = AlbumMockService(self.data)
            self._media_item_api = MediaItemsMockService(self.data)
            self._shared_album_api = SharedAlbumsMockService(self.data)

    def albums(self):
        return self._album_api

    def media_items(self):
        return self._media_item_api

    def shared_albums(self):
        return self._shared_album_api


class MockRequest:
    """Mocks the request the regular service usually returns.

    To initialize this object, set the callback that will be called when calling execute. In this callable,
    you will have available the request object so you can retrieve the body of the request.
    """

    def __init__(self, create_response: Callable[['MockRequest'], dict]):
        self._body = None
        self._create_response = create_response

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, json_string):
        self._body = json.loads(json_string)

    def execute(self):
        return self._create_response(self)


########################################################################################################################
# Helper functions for making response callbacks
########################################################################################################################


def create_empty_response(mock_request: MockRequest) -> dict:
    return {}


def make_create_list_response_callback(
        items_with_id: Sequence[dict], output_array_name: str,
        page_size: Optional[int] = None, page_token: Optional[str] = None
) -> Callable[[MockRequest], dict]:
    page_size = page_size
    page_token = page_token

    def create_list_response(mock_request: MockRequest) -> dict:
        # We need this because after the reassignment we shadow the outer scope and lose
        # the variable. We get a syntax error without this.
        nonlocal page_token
        nonlocal page_size

        # If page token is not defined, try to find one in the request body
        if page_token is None:
            page_token = mock_request.body['pageToken']

        page_token = int(page_token) if page_token else 0

        if page_size is None:
            page_size = mock_request.body['pageSize']

        return {
            output_array_name: items_with_id[page_token:page_size],
            'nextPageToken': page_token + page_size
        }

    return create_list_response


def make_create_find_with_id_response_callback(
        items_with_id: Sequence[dict], item_id: str
) -> Callable[[MockRequest], dict]:

    def create_find_with_id_response(mock_request: MockRequest) -> dict:
        for item in items_with_id:
            if item['id'] == item_id:
                return item

        raise ValueError(f'There is no item with id of {item_id}')

    return create_find_with_id_response


########################################################################################################################
# Actual service mocks
########################################################################################################################


class AlbumMockService:

    def __init__(self, data):
        self._albums = data['albums']

    def add_enrichment(self, album_id: str) -> MockRequest:
        """Returns a random enrichment item."""
        def create_add_enrichment_response(mock_request: MockRequest) -> dict:
            return {'enrichmentItem': {'id': 'new ID'}}

        return MockRequest(create_add_enrichment_response)

    def batch_add_media_items(self, album_id: str) -> MockRequest:
        """Returns an empty response ({})."""
        return MockRequest(create_empty_response)

    def batch_remove_media_items(self, album_id: str) -> MockRequest:
        """Returns an empty response ({})."""
        return MockRequest(create_empty_response)

    def create(self) -> MockRequest:
        """Returns the request body."""
        def create_create_response(mock_request: MockRequest) -> dict:
            return mock_request.body

        return MockRequest(create_create_response)

    def get(self, album_id: str) -> MockRequest:
        """Returns the album with the specified ID in the fake data."""
        return MockRequest(make_create_find_with_id_response_callback(self._albums, album_id))

    def list(
            self, pageSize: Optional[int] = 20,
            pageToken: Optional[str] = None, excludeNonAppCreatedData: Optional[bool] = False
    ) -> MockRequest:
        """Returns the list response where integer version of the page token is used as the first slicing argument
        and page size is used as the second slicing argument."""
        return MockRequest(make_create_list_response_callback(
            self._albums, output_array_name='albums', page_size=pageSize, page_token=pageToken
        ))

    def patch(self, album_id: str, updateMask: Optional[str] = None) -> MockRequest:
        """Returns the same non-updated version of the existing album with the specified ID."""
        return MockRequest(make_create_find_with_id_response_callback(self._albums, album_id))

    def share(self, album_id: str) -> MockRequest:
        """Returns the share info dict as response.

        All of the options are set to True and the token is simply 'token'.
        """

        def create_share_response(mock_request: MockRequest) -> dict:
            return {
                'shareInfo': {
                    'sharedAlbumOptions': {
                        'isCollaborative': True,
                        'isCommentable': True,
                    },
                    'shareToken': 'token',
                    'isJoined': True,
                    'isOwned': True,
                    'isJoinable': True,
                },
            }

        return MockRequest(create_share_response)

    def unshare(self, album_id: str) -> MockRequest:
        """Returns empty response."""
        return MockRequest(create_empty_response)


class MediaItemsMockService:

    def __init__(self, data):
        self._media_items = data['mediaItems']

    def batch_create(self) -> MockRequest:
        """Returns the new media item results where each result has upload token value set as the description of the
        media item sent in the request.
        """
        def create_batch_create_response(mock_request: MockRequest) -> dict:
            new_media_items = mock_request.body['newMediaItems']
            return {
                'newMediaItemResults': [{
                    'uploadToken': new_media_item['description']
                } for new_media_item in new_media_items]
            }

        return MockRequest(create_batch_create_response)

    def batch_get(self, mediaItemIds: Sequence[str]) -> MockRequest:
        """Returns and empty media item result for every media item found in the fake data."""
        def create_batch_get_response(mock_request: MockRequest) -> dict:
            media_item_results = []

            for media_item in self._media_items:
                if media_item['id'] in mediaItemIds:
                    media_item_results.append({})

            return {'mediaItemResults': media_item_results}

        return MockRequest(create_batch_get_response)

    def get(self, media_item_id: str) -> MockRequest:
        """Returns the media item in the fake data specified by the ID."""
        return MockRequest(make_create_find_with_id_response_callback(self._media_items, media_item_id))

    def list(self, pageSize: Optional[int] = 25, pageToken: Optional[str] = None) -> MockRequest:
        """Returns the list response where integer version of the page token is used as the first slicing argument
        and page size is used as the second slicing argument."""
        return MockRequest(make_create_list_response_callback(
            self._media_items, output_array_name='mediaItems', page_size=pageSize, page_token=pageToken
        ))

    def patch(self, media_item_id: str) -> MockRequest:
        """Does not update anything.

        Returns the media item found in the fake data with the specified ID.
        """
        return MockRequest(make_create_find_with_id_response_callback(self._media_items, media_item_id))

    def search(self) -> MockRequest:
        """Mock replacement of the mediaItems.search method. Always returns all media items."""
        media_items = self._media_items['mediaItems']

        return MockRequest(make_create_list_response_callback(media_items, output_array_name='mediaItems'))


class SharedAlbumsMockService:

    def __init__(self, data):
        self._shared_albums = data['sharedAlbums']

    def get(self, share_token: str) -> MockRequest:
        """Returns the shared album from the fake data specified by the share token."""
        def create_get_response(mock_request: MockRequest) -> dict:
            for shared_album in self._shared_albums:
                if share_info := shared_album.get('shareInfo'):
                    if share_info['shareToken'] == share_token:
                        return shared_album

            raise ValueError(f'There is no album with share token of {share_token}')

        return MockRequest(create_get_response)

    def join(self):
        """Returns the shared album from the fake data specified by the share token."""
        def create_join_response(mock_request: MockRequest) -> dict:
            share_token = mock_request.body['shareToken']

            for shared_album in self._shared_albums:
                if share_info := shared_album.get('shareInfo'):
                    if share_info['shareToken'] == share_token:
                        return shared_album

            raise ValueError(f'There is no album with share token of {share_token}')

        return MockRequest(create_join_response)

    def leave(self, share_token: str) -> MockRequest:
        """Returns an empty response."""
        return MockRequest(create_empty_response)

    def list(
            self, pageSize: Optional[int] = 20, pageToken: Optional[str] = None,
            excludeNonAppCreatedData: Optional[bool] = False
    ) -> MockRequest:
        """Returns the list response where integer version of the page token is used as the first slicing argument
        and page size is used as the second slicing argument."""
        return MockRequest(make_create_list_response_callback(
            self._shared_albums, output_array_name='albums', page_size=pageSize, page_token=pageToken
        ))
