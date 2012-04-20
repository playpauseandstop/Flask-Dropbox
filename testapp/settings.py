# Dropbox settings
DROPBOX_KEY = 'please, set proper value in settings_local.py'
DROPBOX_SECRET = 'please, set proper value in settings_local.py'
DROPBOX_ACCESS_TYPE = 'app_folder'

# Default secret key for Flask session
SECRET_KEY = 'Hj+&G\xfc\x1b\x8fVg\n\x14\xcd\xe1j\xab\xe9f\xd6\xe2o(\x8a\x0e'


try:
    from settings_local import *
except ImportError:
    pass
