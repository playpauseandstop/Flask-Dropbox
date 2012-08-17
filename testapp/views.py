from flask import (make_response, redirect, render_template, request, session,
                   url_for)
from werkzeug import secure_filename

from testapp.app import dropbox


def delete(filename):
    """
    Delete file from Dropbox.

    If user is not logged in - redirects to "Home" page.
    """
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    dropbox.client.file_delete('/' + filename)
    return redirect(url_for('files'))


def download(filename, media=False):
    """
    Download file from Dropbox.

    If user is not logged in - redirects to "Home" page.
    """
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    client = dropbox.client
    filename = '/' + filename

    if media:
        data = client.media(filename)
        return redirect(data['url'])

    file_obj, metadata = client.get_file_and_metadata(filename)

    response = make_response(''.join(file_obj.read()))
    response.headers['Content-Type'] = metadata['mime_type']
    return response


def home():
    """
    Home page.

    Show link for "Login with Dropbox" if user not logged in, and link to
    all files and upload pages if logged in.
    """
    return render_template('home.html')


def files():
    """
    All files page.

    List all files from Dropbox if user is logged in. If user is not logged
    in - redirects to "Home" page.
    """
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    client = dropbox.client
    data = client.metadata('/')
    info = dropbox.account_info

    for item in data['contents']:
        item['path'] = item['path'].lstrip('/')

    return render_template('files.html', data=data, info=info)


def session_clear():
    """
    Clear current Flask session and redirects to home page.
    """
    session.clear()
    return redirect(url_for('home'))


def session_dump():
    """
    Show current session dump.
    """
    items = list(session.items())

    response = make_response(
        u'\n'.join([u'%s => %r' % (key, value) for key, value in items])
    )
    response.mimetype = 'text/plain'

    return response


def success(filename):
    """
    Success page after file was uploaded to Dropbox.
    """
    return render_template('success.html', filename=filename)


def upload():
    """
    Upload file to Dropbox.

    If user not logged in - redirects to "Home" page.
    """
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        file_obj = request.files['file']

        if file_obj:
            client = dropbox.client
            filename = secure_filename(file_obj.filename)

            # Actual uploading process
            result = client.put_file('/' + filename, file_obj.read())

            path = result['path'].lstrip('/')
            return redirect(url_for('success', filename=path))

    return render_template('upload.html')
