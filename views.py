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
@app.route('/gifts', methods=['GET'])
def get_gifts():
    gifts = c.query(Gift).all()

    return render_template('gifts.html',
                           gifts=gifts)


@app.route('/gifts', methods=['POST'])
def add_gift():
    gift = Gift(name=request.form.get('name'),
                picture=request.form.get('picture'),
                description=request.form.get('description'))
    c.add(gift)
    c.commit()

    return redirect(url_for('get_gifts',
                            g_id=gift.id))


@app.route('/gifts/<int:g_id>', methods=['GET'])
def get_gift_byid(g_id):
    gift = c.query(Gift).filter_by(id=g_id).first()

    return render_template('gift.html',
                           gift=gift)

    
@app.route('/gifts/<int:g_id>/edit', methods=['POST'])
def edit_gift(g_id):
    gift = c.query(Gift).filter_by(id=g_id).first()

    gift.name = request.form.get('name')
    gift.picture = request.form.get('picture')
    gift.description = request.form.get('description')

    c.add(gift)
    c.commit()

    return redirect(url_for('get_gift_byid',
                            g_id=gift.id))


@app.route('/gifts/<int:g_id>/delete', methods=['POST'])
def delete_gift(g_id):
    gift = c.query(Gift).filter_by(id=g_id).first()

    c.delete(gift)
    c.commit()

    return redirect(url_for('get_gifts'))


# Claims
@app.route('/claims', methods=['GET'])
def get_all_claims():
    claims = c.query(Claim).all()

    return jsonify(claims)


@app.route('/gifts/<int:g_id>/claims', methods=['GET'])
def get_claims(g_id):
    claims = c.query(Claim).filter_by(gift_id=g_id).all()

    return jsonify(claims)


@app.route('/gifts/<int:g_id>/claims', methods=['POST'])
def add_claim(g_id):
    claim = Claim(message=request.form.get('message'),
                  gift_id=g_id)

    c.add(claim)
    c.commit()

    return redirect(url_for('get_claim_byid',
                            c_id=claim.id))


@app.route('/gifts/<int:g_id>/claims/<int:c_id>', methods=['GET'])
def get_claim_byid(g_id, c_id):
    claim = c.query(Claim).filter_by(claim_id=c_id).first()

    return jsonify(claim)


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/edit', methods=['POST'])
def edit_claim(g_id, c_id):
    claim = c.query(Claim).filter_by(claim_id=c_id).first()

    claim.message = request.form.get('message')

    c.add(claim)
    c.commit()

    return redirect(url_for('get_claim_byid', c_id=c_id))


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/delete', methods=['POST'])
def delete_claim(g_id, c_id):
    claim = c.query(Claim).filter_by(claim_id=c_id).first()

    c.delete(claim)
    c.commit()

    return redirect(url_for('get_claims'))


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
