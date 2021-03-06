from flask import (Flask,
                   request,
                   session,
                   abort)

import string
import random
import json
import logging

# EMAIL

from flask_mail import Mail, Message
mail = Mail()

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

from application.models import (Base,
                    User,
                    Gift,
                    Category,
                    Claim)


def create_app():
    # App
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('flask.cfg')

    # Db
    engine = create_engine('sqlite:///giftr.db')
    Base.metadata.create_all(engine)

    # Email
    mail_secrets_f = open('mail_secrets.json', 'r')
    mail_secrets = mail_secrets_f.read()
    mail_secrets_json = json.loads(mail_secrets)
    app.config.update(
        MAIL_SERVER=mail_secrets_json['server'],
        MAIL_PORT=mail_secrets_json['port'],
        MAIL_USE_SSL=mail_secrets_json['use_ssl'],
        MAIL_USERNAME=mail_secrets_json['username'],
        MAIL_PASSWORD=mail_secrets_json['password']
    )
    mail.init_app(app)

    # Blueprints
    app.register_blueprint(gifts_blueprint)
    app.register_blueprint(claims_blueprint)
    app.register_blueprint(categories_blueprint)
    app.register_blueprint(users_blueprint)

    app.register_blueprint(login_blueprint)
    app.register_blueprint(logout_blueprint)

    app.register_blueprint(api_gifts_blueprint)
    app.register_blueprint(api_categories_blueprint)

    return app
