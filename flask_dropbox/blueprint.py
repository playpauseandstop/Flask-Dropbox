from flask import Blueprint

from .views import callback, logout


__all__ = ('DropboxBlueprint', )


class DropboxBlueprint(Blueprint):
    """
    Blueprint to support work with Dropbox API in Flask projects.
    """
    def __init__(self, dropbox, **kwargs):
        """
        Initialize blueprint instance and add all necessary URL to it.
        """
        # Initialize blueprint instance
        defaults = {'name': 'dropbox',
                    'import_name': __name__}
        defaults.update(kwargs)

        super(DropboxBlueprint, self).__init__(**defaults)

        # Add URLs to the blueprint
        url_defaults = {'dropbox': dropbox}
        url_map = {'/callback': callback, '/logout': logout}

        for url, view_func in url_map.items():
            self.add_url_rule(url, defaults=url_defaults, view_func=view_func)
