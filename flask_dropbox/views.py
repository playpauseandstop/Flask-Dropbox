from dropbox.rest import ErrorResponse
from flask import current_app, redirect, render_template, request, session

from .compat import OAuthToken
from .settings import DROPBOX_REQUEST_TOKEN_KEY
from .utils import safe_url_for


def callback():
    """
    Process response for "Login" try from Dropbox API.

    If all OK - redirects to ``DROPBOX_LOGIN_REDIRECT`` url.

    Could render template with error message on:

    * oAuth token is not provided
    * oAuth token is not equal to request token
    * Error response from Dropbox API

    Default template to render is ``'dropbox/callback.html'``, you could
    overwrite it with ``DROPBOX_CALLBACK_TEMPLATE`` config var.
    """
    # Initial vars
    dropbox = current_app.extensions['dropbox']
    template = dropbox.DROPBOX_CALLBACK_TEMPLATE or 'dropbox/callback.html'

    # Get oAuth token from Dropbox
    oauth_token = request.args.get('oauth_token')

    if not oauth_token:
        return render_template(template, error_oauth_token=True)

    # oAuth token **should** be equal to stored request token
    try:
        key, secret = session.get(DROPBOX_REQUEST_TOKEN_KEY) or (None, None)
    except ValueError:
        return render_template(template, error_request_token=True)

    if oauth_token != key:
        return render_template(template, error_not_equal_tokens=True)

    # Do login with current request token
    try:
        dropbox.login(OAuthToken(key, secret))
    except ErrorResponse as e:
        return render_template(template, error_response=True, error=e)

    # Redirect to resulted page
    redirect_to = safe_url_for(dropbox.DROPBOX_LOGIN_REDIRECT or '/')
    return redirect(redirect_to)


def logout():
    """
    Logout current user from Dropbox.

    If all OK - redirects to ``DROPBOX_LOGOUT_REDIRECT`` url.
    """
    dropbox = current_app.extensions['dropbox']
    dropbox.logout()

    redirect_to = safe_url_for(dropbox.DROPBOX_LOGOUT_REDIRECT or '/')
    return redirect(redirect_to)
