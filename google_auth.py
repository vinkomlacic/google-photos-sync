import logging
from pathlib import Path

from dotenv import dotenv_values
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

LOG = logging.getLogger('google_photos_sync.{}'.format(__name__))
CONF = dotenv_values('.env')


__all__ = ['authenticate']


class GoogleApiAuthError(Exception):
    pass


def get_scopes():
    """
    The scopes in the dotenv are listed as a comma-separated list. This function transforms it to a python list.

    :return: list of scope strings
    """
    scopes = CONF['SCOPES'].split(',')

    # Strip scopes of any possible whitespace and remove falsy values, if any
    scopes = [scope.strip() for scope in scopes if scope]

    return scopes


def authenticate():
    """Creates the credentials object through using either the token file or by asking the user to log in.
    This function will return a credentials object or raise a GoogleApiAuthError.
    """
    credentials = None
    token_file_path = Path(CONF['CREDENTIALS_DIR_PATH']) / Path(CONF['TOKEN_FILE_NAME'])
    scopes = get_scopes()

    # If there is already a user token in the file system, use it
    if token_file_path.exists():
        LOG.debug(f'Using token file to load credentials: {token_file_path}.')
        credentials = Credentials.from_authorized_user_file(token_file_path.name, scopes)

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
        client_secret_file_path = Path(CONF['CREDENTIALS_DIR_PATH']) / Path(CONF['CLIENT_SECRET_FILE_NAME'])
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file_path.name, scopes)
        credentials = flow.run_local_server(port=0)

    # Finally, check if any of the steps created the credentials
    # If yes, store the credentials in the token file
    if credentials:
        LOG.debug(f'Credentials successfully obtained. Saving to {token_file_path}...')
        with token_file_path.open('w') as token_file:
            token_file.write(credentials.to_json())
    # If no, raise an authentication error
    else:
        raise GoogleApiAuthError('Could not authenticate with Google API')

    return credentials
