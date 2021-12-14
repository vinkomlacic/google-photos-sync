import logging

from googleapiclient.discovery import build

from google_photos_api_client._album_api import GooglePhotosAlbumAPIClient
from google_photos_api_client._google_auth import authenticate, GoogleApiAuthError
from google_photos_api_client._media_item_api import GooglePhotosMediaItemAPIClient
from google_photos_api_client.exceptions import GooglePhotosAPIError

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))


__all__ = ['GooglePhotosAPIServiceBuilder', 'GooglePhotosAPIClient']


class GooglePhotosAPIServiceBuilder:
    """Responsible for authenticating and creating Google Photos API Service object for use with API client.

    Example:
        # Creates service and authenticates to Google
        service_builder = GooglePhotosAPIServiceBuilder()

        # Use service as context manager to automatically close it after use
        with service_builder.get_service() as service:
            client = GooglePhotosAPIClient(service)
            ...
    """
    SERVICE_NAME = 'photoslibrary'
    SERVICE_VERSION = 'v1'
    # We need to use a specific discovery service for Photos Library API because default discovery service does
    # not list Photos Library API.
    DISCOVERY_SERVICE_URL = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

    def __init__(self):
        try:
            LOG.debug('Trying to authenticate with Google...')
            self.credentials = authenticate()
            LOG.debug('Successfully authenticated.')

        except GoogleApiAuthError as error:
            raise GooglePhotosAPIError('Could not instantiate Google Photos API.') from error

    def get_service(self):
        """Returns a context manager."""
        try:
            return build(
                self.SERVICE_NAME, self.SERVICE_VERSION, credentials=self.credentials,
                discoveryServiceUrl=self.DISCOVERY_SERVICE_URL
            )
        except Exception as error:
            raise GooglePhotosAPIError('Could not build service.') from error


class GooglePhotosAPIClient:
    albums: GooglePhotosAlbumAPIClient
    media_items: GooglePhotosMediaItemAPIClient

    def __init__(self, service):
        self.albums = GooglePhotosAlbumAPIClient(service)
        self.media_items = GooglePhotosMediaItemAPIClient(service)
