#!/usr/bin/env python

"""Serve the app's views on a webserver."""

from flask import (Flask,
                   request,
                   session,
                   abort)

import string
import random

import logging

# BLUEPRINTS
from views.client.gifts.views import gifts_blueprint
from views.client.claims.views import claims_blueprint
from views.client.categories.views import categories_blueprint
from views.client.users.views import users_blueprint

from views.auth.login.views import login_blueprint
from views.auth.logout.views import logout_blueprint

from views.api.gifts.views import api_gifts_blueprint
from views.api.categories.views import api_categories_blueprint

# DATABASE

import sys
from sqlalchemy import create_engine

from models import (Base,
                    User,
                    Gift,
                    Category,
                    Claim)

from flask_mail import Mail, Message

engine = create_engine('sqlite:///giftr.db')
Base.metadata.create_all(engine)


# Bind Flask
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')
mail = Mail()
mail.init_app(app)

# register the blueprints
app.register_blueprint(gifts_blueprint)
app.register_blueprint(claims_blueprint)
app.register_blueprint(categories_blueprint)
app.register_blueprint(users_blueprint)

app.register_blueprint(login_blueprint)
app.register_blueprint(logout_blueprint)

app.register_blueprint(api_gifts_blueprint)
app.register_blueprint(api_categories_blueprint)


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
