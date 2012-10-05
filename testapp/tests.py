#!/usr/bin/env python

import copy

try:
    import cPickle as pickle
except ImportError:
    import pickle

import unittest
import urllib

# Simple manipulation to use ``unittest2`` if current Python version is
# less than 2.7
if not hasattr(unittest.TestCase, 'assertIn'):
    import unittest2 as unittest

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from random import choice
from string import digits, letters

from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
from dropbox.session import DropboxSession
from flask import session, url_for
from flask.ext.dropbox import Dropbox, DropboxBlueprint
from flask.ext.dropbox.extension import OAuthToken
from flask.ext.dropbox.settings import DROPBOX_ACCESS_TOKEN_KEY, \
    DROPBOX_REQUEST_TOKEN_KEY
from flask.ext.dropbox.utils import safe_url_for
from mock import MagicMock
from werkzeug.routing import BuildError as RoutingBuildError

from testapp.app import app, dropbox


TEST_ACCOUNT_INFO = {
    'referral_link': 'https://www.dropbox.com/referrals/TI2MDQ0MDAzO',
    'display_name': 'Igor Davydenko',
    'uid': 604400,
    'country': 'UA',
    'quota_info': {
        'shared': 0,
        'quota': 5637144576,
        'normal': 4143008,
    },
    'email': 'playpauseandstop@gmail.com',
}
TEST_MEDIA = {
    'url': 'https://dl.dropbox.com/0/view/qlfzirhc4zrln/Apps/Lyrics/redis.pdf',
    'expires': 'Fri, 20 Apr 2012 19:58:37 +0000'
}
TEST_METADATA = {
    'hash': 'cad3db434d253eb9351c9ef4734eac0d',
    'thumb_exists': False,
    'bytes': 0,
    'path': '/',
    'is_dir': True,
    'icon': 'folder',
    'root': 'app_folder',
    'contents': [
        {
            'size': '200.9 KB',
            'rev': '19070b1ff3',
            'thumb_exists': False,
            'bytes': 205736,
            'modified': 'Fri, 20 Apr 2012 15:53:56 +0000',
            'mime_type': 'application/pdf',
            'path': '/redis.pdf',
            'is_dir': False,
            'icon': 'page_white_acrobat',
            'root': 'dropbox',
            'client_mtime': 'Fri, 20 Apr 2012 15:53:56 +0000',
            'revision': 1
        }
    ],
    'size': '0 bytes'
}
TEST_METADATA_EMPTY = {
    'hash': 'b00f9ab62e3bfe61736c6d249e729b41',
    'thumb_exists': False,
    'bytes': 0,
    'path': '/',
    'is_dir': True,
    'icon': 'folder',
    'root': 'app_folder',
    'contents': [],
    'size': '0 bytes'
}


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        key = ''.join(choice(letters + digits) for _ in range(12))
        secret = ''.join(choice(letters + digits) for _ in range(16))
        self.token = OAuthToken(key, secret)

    def tearDown(self):
        app.config['TESTING'] = False


class TestDropboxBlueprint(TestCase):

    def test_init(self):
        self.assertIn('dropbox', app.blueprints)
        self.assertEqual(app.blueprints['dropbox'].name, 'dropbox')

        name = 'dropbox_blueprint'
        import_name = DropboxBlueprint.__module__
        self.assertRaises(TypeError, DropboxBlueprint, name, import_name)

        blueprint = DropboxBlueprint(name=name,
                                     import_name=import_name)
        self.assertEqual(blueprint.name, name)

    def test_view_functions(self):
        self.assertIn('dropbox.callback', app.view_functions)
        self.assertIn('dropbox.logout', app.view_functions)

        with app.test_request_context():
            self.assertEqual(url_for('dropbox.callback'), '/dropbox/callback')
            self.assertEqual(url_for('dropbox.logout'), '/dropbox/logout')


class TestDropboxUtils(TestCase):

    def setUp(self):
        super(TestDropboxUtils, self).setUp()

        self.old_DROPBOX_KEY = app.config['DROPBOX_KEY']
        self.old_DROPBOX_SECRET = app.config['DROPBOX_SECRET']
        self.old_DROPBOX_ACCESS_TYPE = app.config['DROPBOX_ACCESS_TYPE']
        self.old_DROPBOX_CALLBACK_URL = app.config.get('DROPBOX_CALLBACK_URL')

    def tearDown(self):
        app.config['DROPBOX_KEY'] = self.old_DROPBOX_KEY
        app.config['DROPBOX_SECRET'] = self.old_DROPBOX_SECRET
        app.config['DROPBOX_ACCESS_TYPE'] = self.old_DROPBOX_ACCESS_TYPE
        app.config['DROPBOX_CALLBACK_URL'] = self.old_DROPBOX_CALLBACK_URL

        super(TestDropboxUtils, self).tearDown()

    def test_dropbox_callback_url(self):
        callback_url = 'http://localhost/dropbox-callback'
        quoted_url = urllib.urlencode({'oauth_callback': callback_url})

        app.config['DROPBOX_CALLBACK_URL'] = callback_url
        dropbox_obj = Dropbox(app)

        with app.test_request_context():
            self.assertIn(quoted_url, dropbox_obj.login_url)

    def test_dropbox_init(self):
        dropbox_obj = Dropbox(app)

        self.assertEqual(dropbox_obj.DROPBOX_KEY, app.config['DROPBOX_KEY'])
        self.assertEqual(
            dropbox_obj.DROPBOX_SECRET, app.config['DROPBOX_SECRET']
        )
        self.assertEqual(
            dropbox_obj.DROPBOX_ACCESS_TYPE, app.config['DROPBOX_ACCESS_TYPE']
        )

        request_token = dropbox_obj.session.obtain_request_token()

    def test_dropbox_init_missing_config(self):
        app.config['DROPBOX_KEY'] = ''
        self.assertRaises(ValueError, Dropbox, app)

        del app.config['DROPBOX_KEY']
        self.assertRaises(ValueError, Dropbox, app)

        app.config['DROPBOX_KEY'] = self.old_DROPBOX_KEY
        app.config['DROPBOX_SECRET'] = ''
        self.assertRaises(ValueError, Dropbox, app)

        del app.config['DROPBOX_SECRET']
        self.assertRaises(ValueError, Dropbox, app)

        app.config['DROPBOX_SECRET'] = self.old_DROPBOX_SECRET
        app.config['DROPBOX_ACCESS_TYPE'] = ''
        self.assertRaises(ValueError, Dropbox, app)

        del app.config['DROPBOX_ACCESS_TYPE']
        self.assertRaises(ValueError, Dropbox, app)

    def test_dropbox_init_wrong_config(self):
        app.config['DROPBOX_KEY'] = 'wrong-key'
        app.config['DROPBOX_SECRET'] = 'wrong-secret'
        app.config['DROPBOX_ACCESS_TYPE'] = 'wrong-access-type'

        dropbox_obj = Dropbox(app)
        self.assertRaises(AssertionError, getattr, dropbox_obj, 'session')

        app.config['DROPBOX_ACCESS_TYPE'] = choice(('app_folder', 'dropbox'))
        dropbox_obj = Dropbox(app)

        session = dropbox_obj.session
        self.assertRaises(ErrorResponse, session.obtain_request_token)

    def test_dropbox_login_url(self):
        with app.test_request_context():
            callback_url = url_for('dropbox.callback', _external=True)
            quoted_url = urllib.urlencode({'oauth_callback': callback_url})

            first_url = dropbox.login_url
            self.assertIn(quoted_url, first_url)

            second_url = dropbox.login_url
            self.assertIn(quoted_url, second_url)

            self.assertNotEqual(first_url, second_url)

    def test_dropbox_logout_not_logged_in(self):
        with app.test_request_context():
            self.assertNotIn(DROPBOX_ACCESS_TOKEN_KEY, session)
            dropbox.logout()
            self.assertNotIn(DROPBOX_ACCESS_TOKEN_KEY, session)

    def test_dropbox_logout_url(self):
        with app.test_request_context():
            self.assertEqual(url_for('dropbox.logout'), dropbox.logout_url)

    def test_register_blueprint(self):
        self.assertIn('dropbox', app.blueprints)
        old_blueprint = app.blueprints['dropbox']

        rules = filter(lambda rule: rule.endpoint.startswith('dropbox.'),
                       app.url_map._rules)
        self.assertEqual(len(rules), 2)

        dropbox_obj = Dropbox(app)
        self.assertRaises(AssertionError,
                          dropbox_obj.register_blueprint,
                          url_prefix='/dbox')

        del app.blueprints['dropbox']
        dropbox_obj.register_blueprint(url_prefix='/dbox')

        rules = filter(lambda rule: rule.endpoint.startswith('dropbox.'),
                       app.url_map._rules)
        self.assertEqual(len(rules), 4)

        self.assertIn('dropbox', app.blueprints)
        app.blueprints['dropbox'] = old_blueprint

    def test_safe_url_for(self):
        with app.test_request_context():
            self.assertEqual(url_for('home'), '/')
            self.assertRaises(RoutingBuildError, url_for, 'does_not_exist')
            self.assertEqual(safe_url_for('does_not_exist'), 'does_not_exist')

    def test_token_pickable(self):
        dump = pickle.dumps(self.token)
        token = pickle.loads(dump)

        self.assertEqual(self.token.key, token.key)
        self.assertEqual(self.token.secret, token.secret)


class TestDropboxViews(TestCase):

    def setUp(self):
        super(TestDropboxViews, self).setUp()
        self.filename = filename = 'redis.pdf'

        with app.test_request_context():
            self.delete_url = url_for('delete', filename=filename)
            self.download_url = url_for('download', filename=filename)
            self.home_url = url_for('home')
            self.files_url = url_for('files')
            self.media_url = url_for('media', filename=filename)
            self.success_url = url_for('success', filename=filename)
            self.upload_url = url_for('upload')

        self.old_build_authorize_url = DropboxSession.build_authorize_url

        dropbox_url = 'https://www.dropbox.com/login'
        DropboxSession.build_authorize_url = \
            MagicMock(return_value=dropbox_url)

        self.old_obtain_request_token = DropboxSession.obtain_request_token
        DropboxSession.obtain_request_token = \
            MagicMock(return_value=self.token)

    def tearDown(self):
        DropboxSession.build_authorize_url = self.old_build_authorize_url
        DropboxSession.obtain_request_token = self.old_obtain_request_token

        old_methods = ('account_info', 'file_delete', 'get_file_and_metadata',
                       'media', 'metadata')

        for method in old_methods:
            attr = 'old_' + method

            if hasattr(self, attr):
                setattr(DropboxClient, method, getattr(self, attr))

        with app.test_request_context():
            dropbox.logout()

        super(TestDropboxViews, self).tearDown()

    def test_callback(self):
        with app.test_request_context():
            callback_url = url_for('dropbox.callback')

        response = self.app.get(callback_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h3>Warning</h3>', response.data)
        self.assertIn(
            "Dropbox API didn't return valid oAuth token.", response.data
        )

        token = self.token.key
        response = self.app.get(callback_url + '?oauth_token=%s' % token[::-1])
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h3>Warning</h3>', response.data)
        self.assertIn(
            'Looks like, oAuth token from Dropbox API is broken.',
            response.data
        )

        response = self.app.get(callback_url + '?oauth_token=%s' % token)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h3>Warning</h3>', response.data)
        self.assertNotIn(
            'Looks like, oAuth token from Dropbox API is broken.',
            response.data
        )

    def test_delete(self):
        response = self.app.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/')

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        # Mock ``file_delete`` method
        self.old_file_delete = DropboxClient.file_delete
        DropboxClient.file_delete = MagicMock(return_value={})

        response = self.app.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'],
                         'http://localhost%s' % self.files_url)

    def test_download(self):
        response = self.app.get(self.download_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/')

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        # Mock ``get_file_and_metadata`` method
        self.old_get_file_and_metadata = DropboxClient.get_file_and_metadata
        data = StringIO(), TEST_METADATA['contents'][0]
        DropboxClient.get_file_and_metadata = MagicMock(return_value=data)

        response = self.app.get(self.download_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        self.assertEqual(response.data, '')

    def test_home(self):
        response = self.app.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login with Dropbox', response.data)

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        response = self.app.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Login with Dropbox', response.data)
        self.assertIn(self.files_url, response.data)
        self.assertIn(self.upload_url, response.data)

    def test_files(self):
        response = self.app.get(self.files_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/')

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        # Mock ``account_info`` method
        self.old_account_info = DropboxClient.account_info
        DropboxClient.account_info = MagicMock(return_value=TEST_ACCOUNT_INFO)

        # Mock ``metadata`` method
        self.old_metadata = DropboxClient.metadata
        DropboxClient.metadata = MagicMock(return_value=TEST_METADATA_EMPTY)

        response = self.app.get(self.files_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, <strong>Igor Davydenko</strong>!', response.data)
        self.assertIn('No files available.', response.data)

        # Remock ``metadata`` method
        DropboxClient.metadata = MagicMock(return_value=TEST_METADATA)

        response = self.app.get(self.files_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('No files available.', response.data)
        self.assertIn(self.media_url, response.data)
        self.assertIn(self.download_url, response.data)
        self.assertIn(self.delete_url, response.data)

    def test_media(self):
        response = self.app.get(self.media_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/')

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        # Mock ``media`` method
        self.old_media = DropboxClient.media
        DropboxClient.media = MagicMock(return_value=TEST_MEDIA)

        response = self.app.get(self.media_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], TEST_MEDIA['url'])

    def test_success(self):
        response = self.app.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<strong>%s</strong>' % self.filename, response.data)

    def test_upload(self):
        response = self.app.get(self.upload_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/')

        # ``Authenticate`` with Dropbox API
        with self.app.session_transaction() as sess:
            sess[DROPBOX_ACCESS_TOKEN_KEY] = self.token

        response = self.app.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Upload</button>', response.data)


if __name__ == '__main__':
    unittest.main()
