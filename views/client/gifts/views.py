#!/usr/bin/env python

"""Define routes for CRUD operations on gifts."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    User,
                    Gift,
                    Claim,
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

gifts_blueprint = Blueprint('gifts', __name__, template_folder='templates')


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


def include_gift(f):
    """Take a g_id kwarg and return a gift object (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g_id = kwargs['g_id']
        gift = c.query(Gift).filter_by(id=g_id).one_or_none()
        if not gift:
            flash('There\'s no gift here.')
            return redirect(url_for('gifts.get'))
        # pass along the gift object to the next function
        kwargs['gift'] = gift
        return f(*args, **kwargs)
    return decorated_function


def include_categories(f):
    """Return an object with all categories (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        categories = c.query(Category).all()
        # pass along the categories object to the next function
        kwargs['categories'] = categories
        return f(*args, **kwargs)
    return decorated_function


def creator_required(f):
    """Take a gift kwarg and redirect to gifts.getbyid if user is not that gift's creator (decorator)."""  # noqa
    @wraps(f)
    def decorated_function(*args, **kwargs):
        gift = kwargs['gift']

        if gift.creator_id != session.get('user_id'):
            flash('You have to be the creator of that gift to see that page.')
            return redirect(url_for('gifts.get_byid',
                                    g_id=gift.id))
        return f(*args, **kwargs)
    return decorated_function


def open_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        gift = kwargs['gift']

        if not gift.open:
            flash('You cannot do this anymore. The gift has been promised.')
            return redirect(url_for('gifts.get'))
        return f(*args, **kwargs)
    return decorated_function


# ROUTES

@gifts_blueprint.route('/', methods=['GET'])
@gifts_blueprint.route('/gifts', methods=['GET'])
@include_categories
def get(categories):
    """Render all gifts or gifts of category id "cat" if query.

    Argument:
    categories (object): generally passed through the
                         @include_categories decorator,
                         contains all categories in the database.
    """
    req_cat = request.args.get('cat')

    # If there is a valid int as query string,
    # filter the gifts by category
    try:
        req_cat = int(req_cat)
        if req_cat > 0 and req_cat <= len(categories):
            gifts = c.query(Gift).filter_by(category_id=req_cat).order_by(Gift.created_at.desc()).all()  # noqa
            req_cat = c.query(Category).filter_by(id=req_cat).first()

            return render_template('gifts.html',
                                   gifts=gifts,
                                   categories=categories,
                                   req_cat=req_cat,
                                   page="gifts")
    except:
        pass

    gifts = c.query(Gift).order_by(Gift.created_at.desc()).all()

    return render_template('gifts.html',
                           categories=categories,
                           gifts=gifts,
                           page="gifts")


@gifts_blueprint.route('/gifts/<int:g_id>', methods=['GET'])
@include_gift
@include_categories
def get_byid(g_id, gift, categories):
    """Render a gift of id g_id.

    Login required.

    Arguments:
    g_id (int): the id of the desired gift.
    gift (object): generally passed through the @include_gift decorator,
                   contains a gift object of id g_id.
    categories (object): generally passed through the
                         @include_categories decorator,
                         contains all categories in the database.
    """
    return render_template('gift.html',
                           gift=gift,
                           categories=categories,
                           page="gift")


@gifts_blueprint.route('/gifts/user/<int:u_id>', methods=['GET'])
@include_categories
def get_byuserid(u_id, categories):
    """Render all gifts created by a user of id u_id.

    Arguments:
    u_id (int): the id of the desired user.
    categories (object): generally passed through the
                         @include_categories decorator,
                         contains all categories in the database.
    """
    gifts = c.query(Gift).filter_by(creator_id=u_id).order_by(Gift.created_at.desc()).all()  # noqa
    user = c.query(User).filter_by(id=u_id).first()

    return render_template('gifts.html',
                           gifts=gifts,
                           categories=categories,
                           user=user,
                           page="usergifts")


@gifts_blueprint.route('/gifts/add', methods=['GET'])
@login_required
@include_categories
def add_get(categories):
    """Render form to add a gift.

    Login required.

    Argument:
    categories (object): generally passed through the
                         @include_categories decorator,
                         contains all categories in the database.
    """
    return render_template('add_gift.html',
                           categories=categories)


@gifts_blueprint.route('/gifts/add', methods=['POST'])
@login_required
def add_post():
    """Add a gift to the database with POST.

    Login required.
    """
    gift = Gift(name=request.form.get('name'),
                picture=request.form.get('picture'),
                description=request.form.get('description'),
                category_id=request.form.get('category'),
                creator_id=session.get('user_id'))
    c.add(gift)
    c.commit()

    flash("Thanks for your generosity! %s was successfully added." % gift.name)

    return redirect(url_for('gifts.get_byid',
                            g_id=gift.id))


@gifts_blueprint.route('/gifts/<int:g_id>/edit', methods=['GET'])
@login_required
@include_gift
@creator_required
@open_required
@include_categories
def edit_get(g_id, gift, categories):
    """Render an edit form for a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    gift (object): generally passed through the @include_gift decorator,
                   contains a gift object of id g_id.
    categories (object): generally passed through the
                         @include_categories decorator,
                         contains all categories in the database.
    """
    return render_template('edit_gift.html',
                           gift=gift,
                           categories=categories)


@gifts_blueprint.route('/gifts/<int:g_id>/edit', methods=['POST'])
@login_required
@include_gift
@open_required
@creator_required
def edit_post(g_id, gift):
    """Edit a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    gift (object): generally passed through the @include_gift decorator,
                   contains a gift object of id g_id.
    """
    gift.name = request.form.get('name')
    gift.picture = request.form.get('picture')
    gift.description = request.form.get('description')
    gift.category_id = request.form.get('category')

    c.add(gift)
    c.commit()

    flash("%s was successfully edited." % gift.name)

    return redirect(url_for('gifts.get_byid',
                            g_id=gift.id))


@gifts_blueprint.route('/gifts/<int:g_id>/delete', methods=['GET'])
@login_required
@include_gift
@open_required
@creator_required
def delete_get(g_id, gift):
    """Render a delete form for a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    gift (object): generally passed through the @include_gift decorator,
                   contains a gift object of id g_id.
    """
    return render_template('delete_gift.html',
                           gift=gift)


@gifts_blueprint.route('/gifts/<int:g_id>/delete', methods=['POST'])
@login_required
@include_gift
@open_required
@creator_required
def delete_post(g_id, gift):
    """Delete a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    gift (object): generally passed through the @include_gift decorator,
                   contains a gift object of id g_id.
    """
    c.delete(gift)
    c.commit()

    # Delete the claims to that object too
    claims = c.query(Claim).filter_by(gift_id=gift.id).all()
    for claim in claims:
        c.delete(claim)
        c.commit()

    flash("%s was successfully deleted." % gift.name)

    return redirect(url_for('gifts.get'))
