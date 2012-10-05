from flask import Blueprint

try:
    from flask.ext.babel import Babel
except ImportError:
    BABEL_SUPPORTED = False
else:
    BABEL_SUPPORTED = True

from .views import callback, logout


__all__ = ('DropboxBlueprint', )


class DropboxBlueprint(Blueprint):
    """
    Blueprint to support work with Dropbox API in Flask projects.
    """
    def __init__(self, **kwargs):
        """
        Initialize blueprint instance and add all necessary URL to it.
        """
        # Initialize blueprint instance
        defaults = {'name': 'dropbox',
                    'import_name': __name__,
                    'template_folder': 'templates'}
        defaults.update(kwargs)

        super(DropboxBlueprint, self).__init__(**defaults)

        # Add URLs to the blueprint
        url_map = {'/callback': callback, '/logout': logout}

        for url, view_func in url_map.items():
            self.add_url_rule(url, view_func=view_func)

        if not BABEL_SUPPORTED:
            @self.app_context_processor
            def inject_underscore():
                return {'_': lambda s: s}
