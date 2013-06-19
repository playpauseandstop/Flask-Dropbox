"""
====================
flask_dropbox.compat
====================

Code for support different Dropbox SDK versions.

"""

try:
    # For Dropbox SDK 1.4.1+
    from dropbox.session import OAuthToken
except ImportError:
    from oauth.oauth import OAuthToken
