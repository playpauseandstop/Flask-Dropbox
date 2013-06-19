from dropbox.client import DropboxClient
from dropbox.session import DropboxSession
from flask import g, request, session as flask_session, url_for
from werkzeug.utils import cached_property, import_string

from .blueprint import DropboxBlueprint
from .compat import OAuthToken
from .settings import (
    ACCOUNT_INFO_CACHE_KEY, CLIENT_CACHE_KEY, DROPBOX_ACCESS_TOKEN_KEY,
    DROPBOX_REQUEST_TOKEN_KEY, SESSION_CACHE_KEY
)


__all__ = ('Dropbox', )


DROPBOX_CONFIGS = ('*DROPBOX_KEY', '*DROPBOX_SECRET', '*DROPBOX_ACCESS_TYPE',
                   'DROPBOX_CALLBACK_TEMPLATE', 'DROPBOX_CALLBACK_URL',
                   'DROPBOX_LOGIN_REDIRECT', 'DROPBOX_LOGOUT_REDIRECT',
                   'DROPBOX_CACHE_STORAGE')


class Dropbox(object):
    """
    Simple wrapper to Dropbox Python API.
    """
    def __init__(self, app=None):
        """
        Initialize wrapper, read Dropbox settings from application config and
        register ``dropbox`` var to the all application templates.
        """
        if app:
            self.init_app(app)

    @property
    def account_info(self):
        """
        Shortcut to ``self.client.account_info()`` method.

        Also stores result in instance cache to reduce network connections.
        """
        if not hasattr(self.cache_storage, ACCOUNT_INFO_CACHE_KEY):
            account_info = self.client.account_info()
            setattr(self.cache_storage, ACCOUNT_INFO_CACHE_KEY, account_info)
        return getattr(self.cache_storage, ACCOUNT_INFO_CACHE_KEY)

    @cached_property
    def cache_storage(self):
        """
        Cache storage. For versions 0.2 this storage was self, for later
        versions it should be configurable, but ``flask.g`` by default.
        """
        if self.DROPBOX_CACHE_STORAGE:
            if self.DROPBOX_CACHE_STORAGE == 'self':
                return self
            return (import_string(self.DROPBOX_CACHE_STORAGE)
                    if isinstance(self.DROPBOX_CACHE_STORAGE, basestring)
                    else self.DROPBOX_CACHE_STORAGE)
        return g

    @property
    def client(self):
        """
        Initialize Dropbox client instance or return it from instance cache.
        """
        if not hasattr(self.cache_storage, CLIENT_CACHE_KEY):
            assert self.is_authenticated, 'Please, login with Dropbox first.'

            key, secret = flask_session[DROPBOX_ACCESS_TOKEN_KEY]
            self.session.set_token(key, secret)
            client = DropboxClient(self.session)

            setattr(self.cache_storage, CLIENT_CACHE_KEY, client)
        return getattr(self.cache_storage, CLIENT_CACHE_KEY)

    def init_app(self, app):
        """
        Initialize Dropbox application for ``app`` Flask application by
        reading configuration values and applying its to current instance.
        """
        # Read Dropbox configuration
        for name in DROPBOX_CONFIGS:
            real_name = name.replace('*', '')
            value = app.config.get(real_name)

            if not value and name.startswith('*'):
                raise ValueError('Please, supply {0!r} config value first.'.
                                 format(real_name))

            setattr(self, real_name, value)

        # Register context processor
        @app.context_processor
        def inject_dropbox():
            return {'dropbox': self}

        # Store extension in application and application in current instance
        app.extensions['dropbox'] = self
        self.app = app

    @property
    def is_authenticated(self):
        """
        Check if current user logged in with Dropbox or not.
        """
        return DROPBOX_ACCESS_TOKEN_KEY in flask_session

    def login(self, request_token):
        """
        Grant access for Dropbox user to the site.
        """
        # Generate access token for current user
        access_token = self.session.obtain_access_token(request_token)
        flask_session[DROPBOX_ACCESS_TOKEN_KEY] = [access_token.key,
                                                   access_token.secret]

        # Remove available request token
        del flask_session[DROPBOX_REQUEST_TOKEN_KEY]

    @property
    def login_url(self):
        """
        Generate "Login with Dropbox" URL.
        """
        host_url = request.host_url
        callback_url = self.DROPBOX_CALLBACK_URL or url_for('dropbox.callback')

        if not callback_url.startswith(host_url):
            callback_url = '%s%s' % (host_url.rstrip('/'), callback_url)

        return self.session.build_authorize_url(self.request_token,
                                                oauth_callback=callback_url)

    def logout(self):
        """
        Revoke access for Dropbox user to the site.
        """
        if hasattr(self.cache_storage, ACCOUNT_INFO_CACHE_KEY):
            delattr(self.cache_storage, ACCOUNT_INFO_CACHE_KEY)
        if hasattr(self.cache_storage, CLIENT_CACHE_KEY):
            delattr(self.cache_storage, CLIENT_CACHE_KEY)
        if hasattr(self.cache_storage, SESSION_CACHE_KEY):
            delattr(self.cache_storage, SESSION_CACHE_KEY)
        if DROPBOX_ACCESS_TOKEN_KEY in flask_session:
            del flask_session[DROPBOX_ACCESS_TOKEN_KEY]

    @property
    def logout_url(self):
        """
        Generate "Logout" URL.
        """
        return url_for('dropbox.logout')

    def register_blueprint(self, *args, **kwargs):
        """
        Initialize and register dropbox blueprint for current application.
        """
        blueprint = DropboxBlueprint()
        self.app.register_blueprint(blueprint, *args, **kwargs)

    @property
    def request_token(self):
        """
        Generate Dropbox session request token and place it to Flask session.
        """
        request_token = self.session.obtain_request_token()
        flask_session[DROPBOX_REQUEST_TOKEN_KEY] = [request_token.key,
                                                    request_token.secret]
        return request_token

    @property
    def session(self):
        """
        Initialize or return already initialized ``DropboxSession`` instance.
        """
        if not hasattr(self.cache_storage, SESSION_CACHE_KEY):
            session = DropboxSession(self.DROPBOX_KEY,
                                     self.DROPBOX_SECRET,
                                     self.DROPBOX_ACCESS_TYPE)
            setattr(self.cache_storage, SESSION_CACHE_KEY, session)
        return getattr(self.cache_storage, SESSION_CACHE_KEY)


# Monkey-patch Dropbox SDK ``OAuthToken`` class to add support of pickling
# tokens. Without this monkey-patch all tries to save any token in Flask
# session will cause "TypeError: a class that defines __slots__ without
# defining __getstate__ cannot be pickled"
if hasattr(OAuthToken, '__slots__'):
    OAuthToken.__getstate__ = \
        lambda instance: dict([(key, getattr(instance, key))
                               for key in instance.__slots__])
    OAuthToken.__setstate__ = \
        lambda instance, data: [setattr(instance, key, value)
                                for key, value in data.iteritems()
                                if key in instance.__slots__]
