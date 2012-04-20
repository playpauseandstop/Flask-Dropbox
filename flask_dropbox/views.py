from flask import redirect, request, session, url_for

from .settings import DROPBOX_REQUEST_TOKEN_KEY
from .utils import safe_url_for


def callback(dropbox):
    """
    Process response for "Login" try from Dropbox API.

    If all OK - redirects to ``DROPBOX_LOGIN_REDIRECT`` url.

    Could show errors on:

    * Error response from Dropbox API
    * oAuth token is not provided
    * oAuth token is not equal to request token

    """
    # Get oAuth token from Dropbox
    oauth_token = request.args.get('oauth_token')

    if not oauth_token:
        raise ValueError('Please, supply "oauth_token" arg first.')

    # oAuth token **should** be equal to stored request token
    request_token = session.get(DROPBOX_REQUEST_TOKEN_KEY)

    if oauth_token != request_token.key:
        raise ValueError('Seems like oAuth token is broken.')

    # Do login with current request token
    dropbox.login(request_token)

    # Redirect to resulted page
    redirect_to = safe_url_for(dropbox.DROPBOX_LOGIN_REDIRECT or '/')
    return redirect(redirect_to)


def logout(dropbox):
    """
    Logout current user from Dropbox.

    If all OK - redirects to ``DROPBOX_LOGOUT_REDIRECT`` url.
    """
    dropbox.logout()

    redirect_to = safe_url_for(dropbox.DROPBOX_LOGOUT_REDIRECT or '/')
    return redirect(redirect_to)
