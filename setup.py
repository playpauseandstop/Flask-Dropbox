#!/usr/bin/env python

import os

from distutils.core import setup


DIRNAME = os.path.dirname(__file__)

readme = open(os.path.join(DIRNAME, 'README.rst'), 'r')
README = readme.read()
readme.close()


setup(
    name='Flask-Dropbox',
    version='0.2',
    description='Dropbox Python SDK support for Flask applications.',
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='https://github.com/playpauseandstop/Flask-Dropbox',
    install_requires=[
        'Flask',
        'dropbox',
    ],
    package_data={
        'flask_dropbox': [
            'templates/dropbox/*.html'
        ],
    },
    packages=[
        'flask_dropbox',
    ],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='flask dropbox',
    license='BSD License',
)
