from flask import url_for
from werkzeug.routing import BuildError as RoutingBuildError


__all__ = ('safe_url_for', )


def safe_url_for(url, *args, **kwargs):
    """
    Fail silently ``BuildError`` on calling original Flask's ``url_for``
    function.
    """
    try:
        return url_for(url, *args, **kwargs)
    except RoutingBuildError:
        return url
