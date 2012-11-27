#!/usr/bin/env python

import os

from app import manager


DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

DROPBOX_KEY = 'ot{5nllomksux\x86\x86'
DROPBOX_SECRET = 'q8ifzo\x7fzpsA\x83>or'


@manager.command
def settings_local():
    """
    Prepare local settings for Travis' environment.
    """
    decrypt = lambda val: ''.join([chr(ord(s) - i) for i, s in enumerate(val)])
    filename = rel('settings_local.py')

    if os.path.isfile(filename):
        print('ERROR: {0!r} already exists, exit...'.format(filename))
        return

    with open(filename, 'w+') as handler:
        handler.write("DROPBOX_KEY = '{0}'\n".format(decrypt(DROPBOX_KEY)))
        handler.write(
            "DROPBOX_SECRET = '{0}'\n".format(decrypt(DROPBOX_SECRET))
        )

    print('Local settings file created at {0!r}.'.format(filename))


if __name__ == '__main__':
    manager.run()
