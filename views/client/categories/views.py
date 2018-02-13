#!/usr/bin/env python

"""Define routes for CRUD operations on categories."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Category)

from flask import (request,
                   redirect,
                   url_for,
                   render_template,
                   flash,
                   session,
                   Blueprint)

# For making decorators
from functools import wraps

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

categories_blueprint = Blueprint('categories', __name__, template_folder='templates')  # noqa


# DECORATORS
def login_required(f):
    """Redirect to login page if the user is not logged in (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to see that page.')
            return redirect(url_for('login.show'))
        return f(*args, **kwargs)
    return decorated_function


# ROUTES

@categories_blueprint.route('/categories', methods=['GET'])
def get():
    """Render all categories in the database."""
    categories = c.query(Category).all()

    return render_template('categories.html',
                           categories=categories)


@categories_blueprint.route('/categories/<int:cat_id>', methods=['GET'])
def get_byid(cat_id):
    """Render a category of id cat_id.

    Argument:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('category.html',
                           category=category)


@categories_blueprint.route('/categories/add', methods=['GET'])
@login_required
def add_get():
    """Render form to add a category.

    Login required.
    """
    return render_template('add_category.html')


@categories_blueprint.route('/categories/add', methods=['POST'])
@login_required
def add_post():
    """Add a category to the database with POST.

    Login required.
    """
    category = Category(name=request.form.get('name'),
                        picture=request.form.get('picture'),
                        description=request.form.get('description'))

    c.add(category)
    c.commit()

    flash("The category \"%s\" was successfully added." % category.name)

    return redirect(url_for('categories.get_byid',
                            cat_id=category.id))


@categories_blueprint.route('/categories/<int:cat_id>/edit', methods=['GET'])
@login_required
def edit_get(cat_id):
    """Render edit form for a category of id cat_id.

    Login required.

    Arguments:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('edit_category.html',
                           category=category)


@categories_blueprint.route('/categories/<int:cat_id>/edit', methods=['POST'])
@login_required
def edit_post(cat_id):
    """Edit a category of id cat_id with POST.

    Login required.

    Argument:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    category.name = request.form.get('name')
    category.picture = request.form.get('picture')
    category.description = request.form.get('description')

    c.add(category)
    c.commit()

    flash("The category \"%s\" was successfully edited." % category.name)

    return redirect(url_for('categories.get_byid',
                            cat_id=category.id))


@categories_blueprint.route('/categories/<int:cat_id>/delete', methods=['GET'])
@login_required
def delete_get(cat_id):
    """Render delete form for a category of id cat_id.

    Login required.

    Arguments:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('delete_category.html',
                           category=category)


@categories_blueprint.route('/categories/<int:cat_id>/delete', methods=['POST'])  # noqa
@login_required
def delete_post(cat_id):
    """Delete a category of id cat_id with POST.

    Login required.

    Argument:
    cat_id (int): the id of the desired category.
    """
    print cat_id
    category = c.query(Category).filter_by(id=cat_id).first()

    c.delete(category)
    c.commit()

    flash("The category \"%s\" was successfully deleted." % category.name)

    return redirect(url_for('categories.get'))
