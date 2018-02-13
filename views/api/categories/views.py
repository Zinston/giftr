#!/usr/bin/env python

"""Define routes for categories API."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Category)

from flask import (jsonify,
                   Blueprint)

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

api_categories_blueprint = Blueprint('api_categories', __name__, template_folder='templates')  # noqa


# ROUTES

@api_categories_blueprint.route('/api/categories')
def get_categories():
    """Return the categories in json."""
    # Query database
    categories = c.query(Category).all()

    # Serialize
    serialized_categories = [cat.serialize for cat in categories]

    # Jsonify
    return jsonify({'categories': serialized_categories})


@api_categories_blueprint.route('/api/categories/<int:cat_id>')
def get_category(cat_id):
    """Return a category of id cat_id in json.

    Argument:
    cat_id (int): the desired category.
    """
    # Query database
    category = c.query(Category).filter_by(id=cat_id).first()

    # Serialize
    serialized_category = category.serialize

    # Jsonify
    return jsonify({'category': serialized_category})
