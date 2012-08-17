import os
import sys

from flask import Flask
from flask.ext.dropbox import Dropbox
from flask.ext.lazyviews import LazyViews

import settings


# Initialize and configure Flask app
app = Flask(__name__)
app.config.from_object(settings)

# Setup Dropbox support
dropbox = Dropbox(app)
dropbox.register_blueprint(url_prefix='/dropbox')

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


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000

    if len(sys.argv) == 2:
        mixed = sys.argv[1]

        try:
            host, port = mixed.split(':')
        except ValueError:
            port = mixed
    elif len(sys.argv) == 3:
        host, port = sys.argv[1:]

    try:
        port = int(port)
    except (TypeError, ValueError):
        print >> sys.stderr, 'Please, use proper digit value to the ' \
                             '``port`` argument.\nCannot convert %r to ' \
                             'integer.' % port

    app.debug = bool(int(os.environ.get('DEBUG', 1)))
    app.run(host=host, port=port)
