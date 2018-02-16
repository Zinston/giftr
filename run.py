#!/usr/bin/env python

"""Serve the app's views on a webserver."""

import os, string, random
from flask import request, session

from application import create_app

app = create_app()


# CSRF protection
# Source: http://flask.pocoo.org/snippets/3/
@app.before_request
def csrf_protect():
    """Check on every POST form submit for a hidden CSRF PROTECT token."""
    if request.method == "POST" and request.form:
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            log = 'CSRF Protection blocked a POST request.'
            log += '\nRequest was: ' + str(dict(request.form))
            log += '\nResponded with error 403.'
            logging.warning(log)
            abort(403)


def generate_csrf_token():
    """Return and store in session a random CSRF PROTECT token."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = get_random_string()
    return session['_csrf_token']


def get_random_string():
    """Get a random string of 32 uppercase letters and digits."""
    choice = string.ascii_uppercase + string.digits
    chars = [random.choice(choice) for x in xrange(32)]
    return ''.join(chars)


app.jinja_env.globals['csrf_token'] = generate_csrf_token


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(port=8080)
