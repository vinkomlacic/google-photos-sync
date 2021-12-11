from enum import Enum
from typing import Optional


__all__ = ['Album', 'SharedAlbum', 'ShareInfo', 'SharedAlbumOptions']


class Album:
    """Representation of an album in Google Photos. Albums are containers for media items."""
    # Identifier for the album.
    # This is a persistent identifier that can be used between sessions to identify this album.
    id: str

    # Name of the album displayed to the user in their Google Photos account.
    # This string shouldn't be more than 500 characters.
    title: str

    # Google Photos URL for the album.
    # The user needs to be signed in to their Google Photos account to access this link.
    product_url: str

    # True if you can create media items in this album.
    # This field is based on the scopes granted and permissions of the album.
    # If the scopes are changed or permissions of the album are changed, this field is updated.
    is_writable: bool

    # The number of media items in the album.
    media_items_count: int

    # A URL to the cover photo's bytes. This shouldn't be used as is.
    # Parameters should be appended to this URL before use.
    # See the developer documentation for a complete list of supported parameters.
    # For example, '=w2048-h1024' sets the dimensions of the cover photo
    # to have a width of 2048 px and height of 1024 px.
    cover_photo_base_url: str

    # Identifier for the media item associated with the cover photo.
    cover_photo_media_item_id: str

    def __init__(self, album: dict):
        self.id = str(album['id'])

        self.title = str(album['title'])
        if len(self.title) > 500:
            raise TypeError(f'{self.__class__.__name__}: Title should not be longer than 500 characters.')

        self.product_url = str(album['productUrl'])
        self.is_writable = bool(album['isWritable'])
        self.media_items_count = int(album['mediaItemsCount'])
        self.cover_photo_base_url = str(album['coverPhotoBaseUrl'])
        self.cover_photo_media_item_id = str(album['coverPhotoMediaItemId'])


class SharedAlbumOptions:
    """Options that control the sharing of an album."""

    # True if the shared album allows collaborators (users who have joined the album) to add media items to it.
    # Defaults to false.
    is_collaborative: bool

    # True if the shared album allows collaborators (users who have joined the album) to add comments to the album.
    # Defaults to false
    is_commentable: bool

    def __init__(self, shared_album_options: dict):
        self.is_collaborative = bool(shared_album_options['isCollaborative'])
        self.is_commentable = bool(shared_album_options['isCommentable'])


class ShareInfo:
    """Information about albums that are shared. This information is only included if you created the album,
    it is shared and you have the sharing scope."""
    # Options that control whether someone can add media items to, or comment on a shared album.
    shared_album_options: SharedAlbumOptions

    # A link to the shared Google Photos album. Anyone with the link can view the contents of the album,
    # so it should be treated with care.
    #
    # The shareableUrl parameter is only returned if the album has link sharing turned on.
    # If a user is already joined to an album that isn't link-shared,
    # they can use the album's productUrl to access it instead.
    #
    # A shareableUrl is invalidated if the owner turns off link sharing in the Google Photos app,
    # or if the album is unshared.
    shareable_url: Optional[str]

    # A token that is used to join, leave, or retrieve the details of a shared album on behalf
    # of a user who isn't the owner.
    #
    # A shareToken is invalidated if the owner turns off link sharing in the Google Photos app,
    # or if the album is unshared.
    share_token: str

    # True if the user is joined to the album. This is always true for the owner of the album.
    is_joined: bool

    # True if the user owns the album.
    is_owned: bool

    # True if the album can be joined by users.
    is_joinable: bool

    def __init__(self, share_info: dict):
        self.shared_album_options = SharedAlbumOptions(shared_album_options=share_info['sharedAlbumOptions'])

        shareable_url = share_info.get('shareableUrl')
        self.shareable_url = str(shareable_url) if shareable_url else None

        self.share_token = str(share_info['shareToken'])
        self.is_joined = bool(share_info['isJoined'])
        self.is_owned = bool(share_info['isOwned'])
        self.is_joinable = bool(share_info['isJoinable'])


class SharedAlbum(Album):
    """Representation of an album in Google Photos. Albums are containers for media items.
    If an album has been shared by the application, it contains an extra shareInfo property."""
    # ... Inherited album properties ...

    #  Information related to shared albums. This field is only populated if the album is a shared album,
    #  the developer created the album and the user has granted the photoslibrary.sharing scope.
    share_info: Optional[ShareInfo]

    def __init__(self, shared_album: dict):
        super().__init__(shared_album)

        share_info = shared_album.get('shareInfo')
        self.share_info = ShareInfo(share_info) if share_info else None


class PositionType(Enum):
    """Possible positions in an album."""

    # Default value if this enum isn't set.
    POSITION_TYPE_UNSPECIFIED = 'POSITION_TYPE_UNSPECIFIED'
    FIRST_IN_ALBUM = 'FIRST_IN_ALBUM'
    LAST_IN_ALBUM = 'LAST_IN_ALBUM'
    AFTER_MEDIA_ITEM = 'AFTER_MEDIA_ITEM'
    AFTER_ENRICHMENT_ITEM = 'AFTER_ENRICHMENT_ITEM'


class AlbumPosition:
    """Specifies a position in an album."""

    # Type of position, for a media or enrichment item.
    position: PositionType

    # The media item to which the position is relative to. Only used when position type is AFTER_MEDIA_ITEM.
    relative_media_item_id: Optional[str]

    # The enrichment item to which the position is relative to. Only used when position type is AFTER_ENRICHMENT_ITEM.
    relative_enrichment_item_id: Optional[str]

    def __init__(self, album_position: dict):
        self.position = PositionType(album_position['position'])

        relative_media_item_id = album_position.get('relativeMediaItemId')
        self.relative_media_item_id = str(relative_media_item_id) if relative_media_item_id else None

        relative_enrichment_item_id = album_position.get('relativeEnrichmentItemId')
        self.relative_enrichment_item_id = str(relative_enrichment_item_id) if relative_enrichment_item_id else None

        if self.relative_media_item_id is None and self.relative_enrichment_item_id:
            raise TypeError(f'{self.__class__.__name__}: at least relative media item ID or relative enrichment item '
                            f'ID need to be specified')
