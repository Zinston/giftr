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
                   jsonify)

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

# Bind Flask
app = Flask(__name__)


# ROUTES
# Client routes
# Gifts
@app.route('/gifts', methods=['GET', 'POST'])
def cr_gifts():
    if request.method == 'GET':
        gifts = c.query(Gift).all()

        html = "<html><body>"

        form = "<form method='POST' action='/gifts'>"
        form += "<input type='text' name='name' placeholder='name'>"
        form += "<input type='submit'>"
        form += "</form>"
        html += form

        html += "<ul>"
        for gift in gifts:
            html += "<li>%s</li>" % gift.name
        html += "</ul></body></html>"
        return html

    if request.method == 'POST':
        gift = Gift(name=request.form['name'])
        c.add(gift)
        c.commit()
        return redirect(url_for('rud_gifts', g_id=gift.id))


@app.route('/gifts/<int:g_id>', methods=['GET', 'UPDATE', 'DELETE'])
def rud_gifts(g_id):
    return 'GET, UPDATE or DELETE gift %s' % g_id


# Claims
@app.route('/gifts/<int:g_id>/claims', methods=['GET', 'POST'])
def cr_claims(g_id):
    return 'GET or POST claims on gift %s' % g_id


@app.route('/gifts/<int:g_id>/claims/<int:c_id>', methods=['GET', 'UPDATE', 'DELETE'])
def rud_claims(g_id, c_id):
    return 'GET, UPDATE or DELETE claim %s on gift %s' % (g_id, c_id)


# Users
@app.route('/users', methods=['GET', 'POST'])
def cr_users():
    return 'GET or POST users'


@app.route('/users/<int:u_id>', methods=['GET', 'UPDATE', 'DELETE'])
def rud_users(u_id):
    return 'GET, UPDATE or DELETE user %s' % u_id


# Categories
@app.route('/categories', methods=['GET', 'POST'])
def cr_categories():
    return 'GET or POST categories'


@app.route('/categories/<int:c_id>', methods=['GET', 'UPDATE', 'DELETE'])
def rud_categories(c_id):
    return 'GET, UPDATE or DELETE category %s' % c_id


if __name__ == '__main__':
    app.debug = True
    app.run(port=8080)
