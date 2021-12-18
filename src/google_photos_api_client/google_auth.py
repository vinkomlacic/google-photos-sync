import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from python_settings import settings

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))


__all__ = ['GoogleApiAuthError', 'authenticate']


class GoogleApiAuthError(Exception):
    pass


def authenticate():
    """Creates the credentials object through using either the token file or by asking the user to log in.
    This function will return a credentials object or raise a GoogleApiAuthError.
    """
    credentials = None

    # If there is already a user token in the file system, use it
    if settings.TOKEN_FILE.exists():
        LOG.debug(f'Using token file to load credentials: {settings.TOKEN_FILE}.')
        credentials = Credentials.from_authorized_user_file(str(settings.TOKEN_FILE), settings.SCOPES)

    # If we loaded the credentials from the token, check if they are valid
    if credentials:
        # If the credentials are invalid, check if they can be refreshed
        if not credentials.valid:
            LOG.debug(f'Credentials from token file invalid.')
            # If credentials can be refreshed, refresh them
            if credentials.expired and credentials.refresh_token:
                LOG.debug(f'Credentials from token file expired, but they have a refresh token. Refreshing...')
                credentials.refresh(Request())
            # Otherwise, we have invalid credentials and we can't do anything about it
            # We delete them and let the user log in later.
            else:
                LOG.debug(f'Could not use credentials from the token file.')
                credentials = None

    # If credentials were not loaded in any of the previous steps, ask the user to log in
    if not credentials:
        LOG.debug(f'Asking the user to provide log in information.')
        flow = InstalledAppFlow.from_client_secrets_file(str(settings.CLIENT_SECRET_FILE), settings.SCOPES)
        credentials = flow.run_local_server(port=0)

    # Finally, check if any of the steps created the credentials
    # If yes, store the credentials in the token file
    if credentials:
        LOG.debug(f'Credentials successfully obtained. Saving to {settings.TOKEN_FILE}...')
        with settings.TOKEN_FILE.open('w') as token_file:
            token_file.write(credentials.to_json())
    # If no, raise an authentication error
    else:
        raise GoogleApiAuthError('Could not authenticate with Google API')

    return credentials
