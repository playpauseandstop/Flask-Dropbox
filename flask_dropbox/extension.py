from dropbox.client import DropboxClient
from dropbox.session import DropboxSession
from flask import request, session as flask_session, url_for
from werkzeug.utils import cached_property

try:
    # For Dropbox SDK 1.4.1+
    from dropbox.session import OAuthToken
except ImportError:
    from oauth.oauth import OAuthToken

from .blueprint import DropboxBlueprint
from .settings import DROPBOX_ACCESS_TOKEN_KEY, DROPBOX_REQUEST_TOKEN_KEY


__all__ = ('Dropbox', )


DROPBOX_CONFIGS = ('*DROPBOX_KEY', '*DROPBOX_SECRET', '*DROPBOX_ACCESS_TYPE',
                   'DROPBOX_CALLBACK_TEMPLATE', 'DROPBOX_CALLBACK_URL',
                   'DROPBOX_LOGIN_REDIRECT', 'DROPBOX_LOGOUT_REDIRECT')


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
        if not hasattr(self, '_account_info_cache'):
            account_info = self.client.account_info()
            setattr(self, '_account_info_cache', account_info)
        return getattr(self, '_account_info_cache')

    @property
    def client(self):
        """
        Initialize Dropbox client instance or return it from instance cache.
        """
        if not hasattr(self, '_client_cache'):
            assert self.is_authenticated, 'Please, login with Dropbox first.'
            token = flask_session[DROPBOX_ACCESS_TOKEN_KEY]

            self.session.set_token(token.key, token.secret)
            client = DropboxClient(self.session)

            setattr(self, '_client_cache', client)
        return getattr(self, '_client_cache')

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
        db_session_key = flask_session.get(DROPBOX_ACCESS_TOKEN_KEY)
        return db_session_key and isinstance(db_session_key, OAuthToken)

    def login(self, request_token):
        """
        Grant access for Dropbox user to the site.
        """
        # Generate access token for current user
        access_token = self.session.obtain_access_token(request_token)
        flask_session[DROPBOX_ACCESS_TOKEN_KEY] = access_token

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
        # Do not forget to remove account info and client cache as well
        if hasattr(self, '_account_info_cache'):
            delattr(self, '_account_info_cache')

        if hasattr(self, '_client_cache'):
            delattr(self, '_client_cache')

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
        token = self.session.obtain_request_token()
        flask_session[DROPBOX_REQUEST_TOKEN_KEY] = token
        return token

    @cached_property
    def session(self):
        """
        Initialize or return already initialized ``DropboxSession`` instance.
        """
        return DropboxSession(self.DROPBOX_KEY,
                              self.DROPBOX_SECRET,
                              self.DROPBOX_ACCESS_TYPE)


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
