=============
Flask-Dropbox
=============

.. image:: https://travis-ci.org/playpauseandstop/Flask-Dropbox.png?branch=master
    :target: https://travis-ci.org/playpauseandstop/Flask-Dropbox

.. image:: https://img.shields.io/pypi/v/Flask-Dropbox.svg
    :target: https://crate.io/packages/Flask-Dropbox


Dropbox Python SDK support for Flask applications.

Requirements
============

* `Python <http://www.python.org/>`_ 2.6 or 2.7
* `Flask <http://flask.pocoo.org/>`_ 0.8 or higher
* `Dropbox Python SDK <http://pypi.python.org/pypi/dropbox>`_ 1.4 or higher

Installation
============

::

    $ pip install Flask-Dropbox

License
=======

``Flask-Dropbox`` is licensed under the `BSD License
<https://github.com/playpauseandstop/Flask-Dropbox/blob/master/LICENSE>`_.

Configuration
=============

SECRET_KEY
----------

**REQUIRED.** As token would be stored in Flask's `session
<http://flask.pocoo.org/docs/quickstart/#sessions>`_ instance, you need to
configure secret key for your application.

DROPBOX_KEY
-----------

**REQUIRED.** App key from Dropbox developer site.

DROPBOX_SECRET
--------------

**REQUIRED.** Secret key from Dropbox developer site.

DROPBOX_ACCESS_TYPE
-------------------

**REQUIRED.** Should be ``'dropbox'`` or ``'app_folder'`` as configured for
your app.

DROPBOX_CALLBACK_URL
--------------------

By default, you don't need to provide this setting, cause ``Flask-Dropbox``
will setup callback URL automaticly usign current host and type of request,
but if you don't trust us, you could to rewrite this setting manually.

DROPBOX_CALLBACK_TEMPLATE
-------------------------

Template to be used for showing errors while trying to process oAuth callback
from Dropbox API. By default: ``'dropbox/callback.html'``.

Next boolean vars could be sent to the template:

* ``error_oauth_token`` - Dropbox API didn't return oAuth token.
* ``error_not_equal_tokens`` - oAuth token from Dropbox API is not equal to
  request token stored in Flask session.
* ``error_response`` - Dropbox API returns ``ErrorResponse`` instance. Also
  actual exception as ``error`` var would be sent to the template too.

DROPBOX_LOGIN_REDIRECT
----------------------

Page to redirect to after user successfully logged in with Dropbox account. By
default: ``/``.

DROPBOX_LOGOUT_REDIRECT
-----------------------

Page to redirect to after user logged out from authenticated Dropbox session.
By default: ``/``.

DROPBOX_CACHE_STORAGE
---------------------

.. versionadded:: 0.3

Where to place account info, Dropbox client and Dropbox session instances. In
0.2 and lower all this info stored in ``flask_dropbox.Dropbox`` instance, which
isn't thread safe, but from 0.3 all these values stored to ``flask.g``. If you
need custom storage you can override this setting with object or string which
would be imported.

Usage
=====

``app.py``::

    from flask import Flask
    from flask.ext.dropbox import Dropbox, DropboxBlueprint

    import settings


    app = Flask(__name__)
    app.config.from_object(settings)

    dropbox = Dropbox(app)
    dropbox.register_blueprint(url_prefix='/dropbox')

``settings.py``::

    SECRET_KEY = 'some-secret-key'
    DROPBOX_KEY = 'dropbox-app-key'
    DROPBOX_SECRET = 'dropbox-app-secret'
    DROPBOX_ACCESS_TYPE = 'app_folder'

``views.py``::

    from flask import url_for, redirect, request
    from werkzeug import secure_filename

    from app import app, dropbox


    @app.route('/')
    def home():
        return u'Click <a href="%s">here</a> to login with Dropbox.' % \
               dropbox.login_url


    @app.route('/success/<path:filename>')
    def success(filename):
        return u'File successfully uploaded as /%s' % filename


    @app.route('/upload', methods=('GET', 'POST'))
    def upload():
        if not dropbox.is_authenticated:
            return redirect(url_for('home'))

        if request.method == 'POST':
            file_obj = request.files['file']

            if file_obj:
                client = dropbox.client
                filename = secure_filename(file.filename)

                # Actual uploading process
                result = client.put_file('/' + filename, file_obj.read())

                path = result['path'].lstrip('/')
                return redirect(url_for('success', filename=path))

        return u'<form action="" method="post">' \
               u'<input name="file" type="file">' \
               u'<input type="submit" value="Upload">' \
               u'</form>'

Bugs, feature requests?
=======================

If you found some bug in ``Flask-Dropbox`` library, please, add new issue to
the project's `GitHub issues
<https://github.com/playpauseandstop/Flask-Dropbox/issues>`_.

ChangeLog
=========

0.3
---

+ Flask 0.10 support
+ Store account info, Dropbox client and session in thread-safe ``flask.g``
  storage instead of ``flask_dropbox.Dropbox`` instance
+ Introduce ``DROPBOX_CACHE_STORAGE`` setting

0.2
---

+ Add ``init_app`` method to ``Dropbox`` extension class.
+ Do not send ``dropbox`` instance for initialization of ``DropboxBlueprint``
  class.
+ Use ``current_app.extensions['dropbox']`` statement in views for getting
  initialized ``Dropbox`` instance.

0.1.5
-----

+ Add ``register_blueprint`` shortcut to initialize ``DropboxBlueprint`` with
  default values in one line.
+ Move ``Dropbox`` class from ``flask.ext.dropbox.utils`` to
  ``flask.ext.dropbox.extension`` module. But mainly, it wouldn't affected to
  your code if you used ``from flask.ext.dropbox import Dropbox`` statements.

0.1.4
-----

+ Add ``dropbox`` library as install requirement in ``setup.py``.
+ Update project short description.

0.1.3
-----

+ Fix handling templates while installing via setup.py

0.1.2
-----

+ Add support of Dropbox SDK 1.4.1

0.1.1
-----

+ Check that access token is the instance of ``oauth.OAuthToken`` class if it
  exists in session.

0.1
---

* Initial release.
