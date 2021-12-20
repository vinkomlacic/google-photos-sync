from unittest import TestCase

from google_photos_api_client._media_item_api import GooglePhotosMediaItemAPIClient
from google_photos_api_client.google_photos_api import GooglePhotosAPIServiceBuilder


class TestGooglePhotosMediaItemAPI(TestCase):

    def setUp(self):
        service_builder = GooglePhotosAPIServiceBuilder()
        self.service = service_builder.build_service()
        self.media_item_api = GooglePhotosMediaItemAPIClient(self.service)

    def tearDown(self):
        self.service.close()

    def test_list(self):
        for media_item_page, _ in self.media_item_api.list():
            for media_item in media_item_page:
                print(media_item.description)
                self.assertIsNotNone(media_item)
