from unittest import TestCase

from google_photos_api_client._album_api import GooglePhotosAlbumAPIClient
from google_photos_api_client.google_photos_api import GooglePhotosAPIServiceBuilder


class TestGooglePhotosAlbumAPI(TestCase):

    def setUp(self):
        service_builder = GooglePhotosAPIServiceBuilder()
        self.service = service_builder.get_service()
        self.album_api = GooglePhotosAlbumAPIClient(self.service)

    def tearDown(self):
        self.service.close()

    def test_list(self):
        for album_page, _ in self.album_api.list():
            for album in album_page:
                print(album.title)
                self.assertIsNotNone(album)
