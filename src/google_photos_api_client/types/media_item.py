from enum import Enum
from typing import Optional

from google_photos_api_client.types.status import Status

__all__ = ['MediaItem', 'ContributorInfo', 'MediaMetadata', 'Photo', 'Video', 'VideoProcessingStatus',
           'NewMediaItemResult', 'NewMediaItem', 'SimpleMediaItem', 'MediaItemResult']


class VideoProcessingStatus(Enum):
    """Processing status of a video being uploaded to Google Photos."""
    # Video processing status is unknown.
    UNSPECIFIED = 'UNSPECIFIED'

    # Video is being processed.
    # The user sees an icon for this video in the Google Photos app; however, it isn't playable yet.
    PROCESSING = 'PROCESSING'

    # Video processing is complete and it is now ready for viewing.
    # Important: attempting to download a video not in the READY state may fail.
    READY = 'READY'

    # Something has gone wrong and the video has failed to process.
    FAILED = 'FAILED'


class Video:
    """Metadata that is specific to a video, for example, fps and processing status.
    Some of these fields may be null or not included."""

    # Brand of the camera with which the video was taken.
    camera_make: Optional[str]

    # Model of the camera with which the video was taken.
    camera_model: Optional[str]

    # Frame rate of the video.
    fps: Optional[float]

    # Processing status of the video.
    status: Optional[VideoProcessingStatus]

    def __init__(self, video: dict):
        camera_make = video.get('cameraMake')
        self.camera_make = str(camera_make) if camera_make else None

        camera_model = video.get('cameraModel')
        self.camera_model = str(camera_model) if camera_model else None

        fps = video.get('fps')
        self.fps = float(fps) if fps else None

        status = video.get('status')
        self.status = VideoProcessingStatus(status) if status else None


class Photo:
    """Metadata that is specific to a photo, such as, ISO, focal length and exposure time. Some of these fields may
    be null or not included. """

    # Brand of the camera with which the photo was taken.
    camera_make: Optional[str]

    # Model of the camera with which the photo was taken.
    camera_model: Optional[str]

    # Focal length of the camera lens with which the photo was taken.
    focal_length: Optional[float]

    # Aperture f number of the camera lens with which the photo was taken.
    aperture_f_number: Optional[float]

    # ISO of the camera with which the photo was taken.
    iso_equivalent: Optional[int]

    # Exposure time of the camera aperture when the photo was taken.
    #
    # A duration in seconds with up to nine fractional digits, terminated by 's'. Example: "3.5s".
    #
    # See https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#google.protobuf.Duration
    # for more information on this string format
    exposure_time: Optional[str]

    def __init__(self, photo: dict):
        camera_make = photo.get('cameraMake')
        self.camera_make = str(camera_make) if camera_make else None

        camera_model = photo.get('cameraModel')
        self.camera_model = str(camera_model) if camera_model else None

        focal_length = photo.get('focalLength')
        self.focal_length = float(focal_length) if focal_length else None

        aperture_f_number = photo.get('apertureFNumber')
        self.aperture_f_number = float(aperture_f_number) if aperture_f_number else None

        iso_equivalent = photo.get('isoEquivalent')
        self.iso_equivalent = int(iso_equivalent) if iso_equivalent else None

        exposure_time = photo.get('exposureTime')
        self.exposure_time = str(exposure_time) if exposure_time else None
        if self.exposure_time and not self.exposure_time.endswith('s'):
            raise TypeError(f"{self.__class__.__name__}: Exposure time duration string must end with letter 's' for "
                            f"second.")


class MediaMetadata:
    """Metadata for a media item."""

    # Time when the media item was first created (not when it was uploaded to Google Photos).
    #
    # A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
    # Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".
    creation_time: str

    # Original width (in pixels) of the media item.
    width: str

    # Original height (in pixels) of the media item.
    height: str

    # Metadata for a photo media type.
    photo: Optional[Photo]

    # Metadata for a video media type.
    video: Optional[Video]

    def __init__(self, media_metadata: dict):
        self.creation_time = str(media_metadata['creationTime'])
        self.width = str(media_metadata['width'])
        self.height = str(media_metadata['height'])

        # Note: these two attributes (photo and video) are actually a union type. They are split in two for
        # convenience, but they are never both set. If both are specified, 'photo' takes precedence.
        photo = media_metadata.get('photo')
        self.photo = Photo(photo) if photo else None

        if self.photo is None:
            video = media_metadata.get('video')
            self.video = Video(video) if video else None

        if self.photo is None and self.video is None:
            raise TypeError(f'{self.__class__.__name__}: Either photo or video attribute need to be specified.')


class ContributorInfo:
    """Information about the user who added the media item. Note that this information is included only if the media
    item is within a shared album created by your app and you have the sharing scope."""

    # URL to the profile picture of the contributor.
    profile_picture_base_url: str

    # Display name of the contributor.
    display_name: str

    def __init__(self, contributor_info: dict):
        self.profile_picture_base_url = str(contributor_info['profilePictureBaseUrl'])
        self.display_name = str(contributor_info['displayName'])


class MediaItem:
    """Representation of a media item (such as a photo or video) in Google Photos."""
    # Identifier for the media item. This is a persistent identifier that can be used between sessions
    # to identify this media item.
    id: str

    # Description of the media item. This is shown to the user in the item's info section in the Google Photos app.
    description: str

    # Google Photos URL for the media item. This link is available to the user only if they're signed in.
    # When retrieved from an album search, the URL points to the item inside the album.
    product_url: str

    # A URL to the media item's bytes. This shouldn't be used as is. Parameters should be appended to this URL before
    # use. See the developer documentation for a complete list of supported parameters. For example, '=w2048-h1024'
    # will set the dimensions of a media item of type photo to have a width of 2048 px and height of 1024 px.
    base_url: str

    # MIME type of the media item. For example, image/jpeg.
    mime_type: str

    # Metadata related to the media item, such as, height, width, or creation time.
    media_metadata: MediaMetadata

    # Information about the user who created this media item.
    contributor_info: Optional[ContributorInfo]

    # Filename of the media item. This is shown to the user in the item's info section in the Google Photos app.
    filename: str

    def __init__(self, media_item: dict):
        self.id = str(media_item['id'])
        self.description = str(media_item['description'])
        self.product_url = str(media_item['productUrl'])
        self.base_url = str(media_item['baseUrl'])
        self.mime_type = str('mimeType')
        self.media_metadata = MediaMetadata(media_item['mediaMetadata'])

        contributor_info = media_item['contributorInfo']
        self.contributor_info = ContributorInfo(contributor_info) if contributor_info else None

        self.filename = str(media_item['filename'])


class SimpleMediaItem:
    """A simple media item to be created in Google Photos via an upload token."""

    # A simple media item to be created in Google Photos via an upload token.
    upload_token: str

    # File name with extension of the media item. This is shown to the user in Google Photos.
    # The file name specified during the byte upload process is ignored if this field is set.
    # The file name, including the file extension, shouldn't be more than 255 characters. This is an optional field.
    file_name: Optional[str]

    def __init__(self, simple_media_item: dict):
        self.upload_token = str(simple_media_item['upload_token'])

        file_name = simple_media_item.get('fileName')
        self.file_name = str(file_name) if file_name else None


class NewMediaItem:
    """New media item that's created in a user's Google Photos account."""

    # Description of the media item. This will be shown to the user in the item's info section in the Google Photos
    # app. This string shouldn't be more than 1000 characters.
    description: str

    # A new media item that has been uploaded via the included uploadToken.
    simple_media_item: SimpleMediaItem

    def __init__(self, new_media_item: dict):
        self.description = str(new_media_item['description'])
        if len(self.description) > 1000:
            raise TypeError(f'{self.__class__.__name__}: The description should not be longer than 1000 characters.')

        self.simple_media_item = SimpleMediaItem(new_media_item['simpleMediaItem'])


class NewMediaItemResult:
    """Result of creating a new media item."""

    # The upload token used to create this new media item.
    upload_token: str

    # If an error occurred during the creation of this media item, this field is populated with information related
    # to the error. For details regarding this field, see Status.
    status: Optional[Status]

    # Media item created with the upload token. It's populated if no errors occurred and the media item was created
    # successfully.
    media_item: Optional[MediaItem]

    def __init__(self, new_media_item_result: dict):
        self.upload_token = str(new_media_item_result['uploadToken'])

        status = new_media_item_result.get('status')
        self.status = Status(status) if status else None

        media_item = new_media_item_result.get('mediaItem')
        self.media_item = MediaItem(media_item) if media_item else None


class MediaItemResult:
    """Result of retrieving a media item."""

    # If an error occurred while accessing this media item, this field is populated with information related to the
    # error. For details regarding this field, see Status.
    status: Optional[Status]

    # Media item retrieved from the user's library. It's populated if no errors occurred and the media item was
    # fetched successfully.
    media_item: Optional[MediaItem]

    def __init__(self, media_item_result: dict):
        status = media_item_result.get('status')
        self.status = Status(status) if status else None

        media_item = media_item_result.get('mediaItem')
        self.media_item = MediaItem(media_item) if media_item else None
