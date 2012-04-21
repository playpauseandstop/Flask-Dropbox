=====================
Testing Flask-Dropbox
=====================

``Flask-Dropbox`` provides simple testapp to test ability of login with
Dropbox API, upload files, retrieve files metadata and some more.

Requirements
============

* `make <http://www.gnu.org/software/make/>`_

Bootstrap
=========

::

    $ make -C testapp/ bootstrap

Configuration
=============

Provide proper ``SECRET_KEY``, ``DROPBOX_KEY``, ``DROPBOX_SECRET`` and
``DROPBOX_ACCESS_TYPE`` values to ``testapp/settings_local.py`` file.

Feel free, to create some dummy app at `Dropbox developer site
<https://www.dropbox.com/developers>`_ and then populate Dropbox config
values.

Running test app
================

::

    $ make -C testapp/ server

By default, test app would be available at ``http://127.0.0.1:4354/``, you
could update this, by providing ``HOST`` and ``PORT`` env vars before ``make``.

Running tests
=============

::

    $ make -C testapp/ test
