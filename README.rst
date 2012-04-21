=============
Flask-Dropbox
=============

Add support of Dropbox API to the Flask applications.

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

Usage
=====

``app.py``::

    from flask import Flask
    from flask.ext.dropbox import Dropbox, DropboxBlueprint

    import settings


    app = Flask(__name__)
    app.config.from_object(settings)

    dropbox = Dropbox(app)
    dropbox_blueprint = DropboxBlueprint(dropbox)
    app.register_blueprint(dropbox_blueprint, url_prefix='/dropbox')

``settings.py``::

    SECRET_KEY = 'some-secret-key'
    DROPBOX_KEY = 'dropbox-app-key'
    DROPBOX_SECRET = 'dropbox-app-secret'
    DROPBOX_ACCESS_TYPE = 'app_folder'

``views.py``::

    from flask import url_for
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

0.1.1
-----

+ Check that access token is the instance of ``oauth.OAuthToken`` class and if
  it exists in session.

0.1
---

* Initial release.
