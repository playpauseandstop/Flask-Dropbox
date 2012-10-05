import os
import sys

from flask import Flask
from flask.ext.dropbox import Dropbox
from flask.ext.lazyviews import LazyViews
from flask.ext.script import Manager

import settings


# Initialize and configure Flask app
app = Flask(__name__)
app.config.from_object(settings)

# Setup Dropbox and script extensions
dropbox = Dropbox(app)
dropbox.register_blueprint(url_prefix='/dropbox')
manager = Manager(app)

# Add test project views
views = LazyViews(app, 'testapp.views')
views.add('/', 'home')
views.add('/delete/<path:filename>', 'delete')
views.add('/download/<path:filename>', 'download', endpoint='download')
views.add('/files', 'files')
views.add('/media/<path:filename>',
          'download',
          defaults={'media': True},
          endpoint='media')
views.add('/session/clear', 'session_clear')
views.add('/session/dump', 'session_dump')
views.add('/success/<path:filename>', 'success')
views.add('/upload', 'upload', methods=('GET', 'POST'))
