#!/usr/bin/env python

"""Define routes for CRUD operations on users."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Gift,
                    Claim,
                    User)

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

users_blueprint = Blueprint('users', __name__, template_folder='templates')


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


def include_user(f):
    """Take a u_id kwarg and return a user object (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        u_id = kwargs['u_id']
        user = c.query(User).filter_by(id=u_id).one_or_none()
        if not user:
            flash('There\'s no user here.')
            return redirect(url_for('gifts.get'))
        # pass along the gift object to the next function
        kwargs['user'] = user
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """Take a user id (u_id) and redirect to home if logged in user doesn't match that id (decorator)."""  # noqa
    @wraps(f)
    def decorated_function(*args, **kwargs):
        u_id = kwargs['u_id']

        if u_id != session.get('user_id'):
            flash('You can only do this for your own profile.')
            return redirect(url_for('gifts.get'))
        return f(*args, **kwargs)
    return decorated_function


# ROUTES

@users_blueprint.route('/users/<int:u_id>/profile', methods=['GET'])
@login_required
@include_user
def get_byid(u_id, user):
    """Render a user with id u_id's profile.

    Argument:
    u_id (int): the id of the desired user.
    user (object): generally passed through the @include_user decorator,
                   contains a user object of id u_id.
    """
    return render_template('user.html',
                           user=user)


@users_blueprint.route('/users/<int:u_id>/edit', methods=['GET'])
@login_required
def edit_get(u_id):
    """Render an edit form for the logged in user.

    Login required.

    Argument:
    u_id (int): the id of the desired user.
    """
    return render_template('edit_user.html')


@users_blueprint.route('/users/<int:u_id>/edit', methods=['POST'])
@login_required
@user_required
@include_user
def edit_post(u_id, user):
    """Edit a user of id u_id with POST.

    Login required.
    One has to be logged in as the requested user to access this.

    Arguments:
    u_id (int): the id of the desired user.
    user (object): generally passed through the @include_user decorator,
                   contains a user object of id u_id.
    """
    user.name = request.form.get('name')
    user.picture = request.form.get('picture')
    user.email = request.form.get('email')
    user.address = request.form.get('address')

    c.add(user)
    c.commit()

    session['username'] = user.name
    session['picture'] = user.picture
    session['email'] = user.email
    session['address'] = user.address

    flash("Your account was successfully edited.")

    return redirect(url_for('users.get_byid',
                            u_id=user.id))


@users_blueprint.route('/users/<int:u_id>/delete', methods=['GET'])
@login_required
def delete_get(u_id):
    """Render a delete form for the logged in user.

    Login required.

    Arguments:
    u_id (int): the id of the desired user.
    """
    return render_template('delete_user.html')


@users_blueprint.route('/users/<int:u_id>/delete', methods=['POST'])
@login_required
@include_user
@user_required
def delete_post(u_id, user):
    """Delete a user of id u_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    u_id (int): the id of the desired user.
    user (object): generally passed through the @include_user decorator,
                   contains a user object of id u_id.
    """
    # Delete the gifts of that user too
    user_gifts = c.query(Gift).filter_by(creator_id=user.id).all()
    for gift in user_gifts:
        # Delete the claims to that gift first
        claims = c.query(Claim).filter_by(gift_id=gift.id).all()
        for claim in claims:
            c.delete(claim)
        c.delete(gift)

    c.delete(user)
    c.commit()

    flash("Your account was successfully deleted.")

    return redirect(url_for('logout.disconnect'))
