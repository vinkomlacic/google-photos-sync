from pathlib import Path
from unittest import TestCase

from configuration import CONF
from google_auth import authenticate


class TestGoogleAuth(TestCase):

    def test_google_auth_authorization_screen(self):
        """Runs authentication. Deletes the token file beforehand to ensure that the authorization screen shows up."""
        token_file = Path(CONF['CREDENTIALS_DIR_PATH']) / Path(CONF['TOKEN_FILE_NAME'])
        if token_file.exists():
            token_file.unlink()

        # If authentication is successful, the function should return the credentials object
        self.assertIsNotNone(authenticate())

    def test_google_auth_from_token_file(self):
        """Tries to authenticate using the token file. If the token file does not exist, the authentication will run
        twice: once to create it, and once to use it.
        """
        # Assert token file exists
        token_file = Path(CONF['CREDENTIALS_DIR_PATH']) / Path(CONF['TOKEN_FILE_NAME'])
        if not token_file.exists():
            self.assertIsNotNone(authenticate())

        self.assertTrue(token_file.exists())

        # Authenticate using token file
        self.assertIsNotNone(authenticate())
