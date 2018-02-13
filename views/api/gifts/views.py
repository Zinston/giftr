#!/usr/bin/env python

"""Define routes for gifts API."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Gift,
                    Claim,
                    Category)

from flask import (request,
                   jsonify,
                   Blueprint)

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

api_gifts_blueprint = Blueprint('api_gifts', __name__, template_folder='templates')  # noqa


# ROUTES

@api_gifts_blueprint.route('/api/gifts')
def get_gifts():
    """Return the gifts in json."""
    req_cat = request.args.get('cat')
    categories = c.query(Category).all()

    # If there is a valid int as query string,
    # filter the gifts by category
    try:
        req_cat = int(req_cat)
        if req_cat > 0 and req_cat <= len(categories):
            gifts = c.query(Gift).filter_by(category_id=req_cat).order_by(Gift.created_at.desc()).all()  # noqa
        else:
            gifts = c.query(Gift).order_by(Gift.created_at.desc()).all()
    except:
        gifts = c.query(Gift).order_by(Gift.created_at.desc()).all()

    # Serialize
    serialized_gifts = [gift.serialize for gift in gifts]

    # Jsonify
    return jsonify(gifts=serialized_gifts)


@api_gifts_blueprint.route('/api/gifts/<int:g_id>')
def get_gift(g_id):
    """Return a gift of id g_id in json.

    Argument:
    g_id (int): the desired gift.
    """
    # Query database
    gift = c.query(Gift).filter_by(id=g_id).first()
    claims = c.query(Claim).filter_by(gift_id=g_id).all()

    # Serialize
    serialized_gift = gift.serialize
    serialized_claims = [claim.serialize for claim in claims]

    # Append the items to the restaurant
    serialized_gift['claims'] = serialized_claims

    # Jsonify
    return jsonify({'gift': serialized_gift})
