#!/usr/bin/env python

"""Serve the app's views on a webserver."""

# For webserver
from BaseHTTPServer import (BaseHTTPRequestHandler,
                            HTTPServer)
import cgi  # Common Gateway Interface

# For CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    User,
                    Gift,
                    Claim,
                    Category)

from flask import (Flask,
                   request,
                   redirect,
                   url_for,
                   render_template,
                   flash,
                   jsonify,
                   g,
                   session,
                   make_response,
                   abort,
                   Blueprint)

# For OAuth
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)
import random
import string
import json
import requests
import httplib2

import logging

# For making decorators
from functools import wraps

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

# Bind Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')

# BLUEPRINTS
from views.client.gifts.views import gifts_blueprint
# register the blueprints
app.register_blueprint(gifts_blueprint)


# API Secrets and IDs
def get_google_client_id(json_file_name):
    """Get client id for Google OAuth2, from provided json file."""
    google_client_secrets_f = open(json_file_name, 'r')
    google_client_secrets = google_client_secrets_f.read()
    google_client_secrets_json = json.loads(google_client_secrets)
    return google_client_secrets_json['web']['client_id']


CLIENT_ID = get_google_client_id('google_client_secrets.json')


# DECORATORS


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


app.jinja_env.globals['csrf_token'] = generate_csrf_token


# ROUTES
# Client routes
# Gifts



# Claims



# Categories



# AUTH

# Log in


# Log out


# API Routes


# HELPERS

def create_user_from_session():
    """Add a user to database from session, return its database id."""
    # Create a new User in db with the info from the session
    new_user = User(name=session.get('username'),
                    email=session.get('email'),
                    picture=session.get('picture'))
    c.add(new_user)
    c.commit()

    # Get the new User, from their email
    user_id = get_user_id(session.get('email'))

    # Return the new User's id
    return user_id


def get_user_id(email):
    """Return a user's database id from their email address.

    Argument:
    email (str): the user's email address.
    """
    try:
        user = c.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_random_string():
    """Get a random string of 32 uppercase letters and digits."""
    choice = string.ascii_uppercase + string.digits
    chars = [random.choice(choice) for x in xrange(32)]
    return ''.join(chars)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(port=8080)
