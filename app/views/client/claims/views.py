#!/usr/bin/env python

"""Define routes for CRUD operations on claims."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Gift,
                    Claim)

from flask import (request,
                   redirect,
                   url_for,
                   render_template,
                   flash,
                   session,
                   Blueprint,
                   current_app)

# For making decorators
from functools import wraps

# For sending emails
from flask_mail import Mail, Message

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

claims_blueprint = Blueprint('claims', __name__, template_folder='templates')

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


def include_claim(f):
    """Take a c_id kwarg and return a claim object (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        c_id = kwargs['c_id']
        claim = c.query(Claim).filter_by(id=c_id).one_or_none()
        if not claim:
            flash('There\'s no claim here.')
            return redirect(url_for('claims.get'))
        # pass along the claim object to the next function
        kwargs['claim'] = claim
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


def creator_required(f):
    """Take a claim kwarg and redirect to claims.getbyid if user is not that claim's creator (decorator)."""  # noqa
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claim = kwargs['claim']

        if claim.creator_id != session.get('user_id'):
            flash('You have to be the creator of that claim to see that page.')
            return redirect(url_for('claims.get_byid',
                                    c_id=claim.id))
        return f(*args, **kwargs)
    return decorated_function


def gift_creator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claim = kwargs['claim']

        if claim.gift.creator_id != session.get('user_id'):
            flash('You have to be the creator of that gift to accept a claim on it.')
            return redirect(url_for('claims.get_byid',
                                    c_id=claim.id))
        return f(*args, **kwargs)
    return decorated_function


def open_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if kwargs.get('claim'):
            claim = kwargs['claim']
            gift = claim.gift
        elif kwargs.get('gift'):
            gift = kwargs['gift']

        if not gift.open:
            flash('You cannot do this anymore. The gift has been promised.')
            return redirect(url_for('gifts.get'))
        return f(*args, **kwargs)
    return decorated_function


# ROUTES

@claims_blueprint.route('/gifts/claims', methods=['GET'])
def get_all():
    """Render all claims in the database."""
    claims = c.query(Claim).all()

    return render_template('claims.html',
                           claims=claims)


@claims_blueprint.route('/gifts/<int:g_id>/claims', methods=['GET'])
def get(g_id):
    """Render all claims on a gift of id g_id.

    Argument:
    g_id (int): the id of the desired gift.
    """
    claims = c.query(Claim).filter_by(gift_id=g_id).all()
    gift = c.query(Gift).filter_by(id=g_id).first()

    return render_template('claims.html',
                           gift=gift,
                           claims=claims)


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>', methods=['GET'])
@include_claim
def get_byid(g_id, c_id, claim):
    """Render a claim of id c_id on a gift of id g_id.

    Login required.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    claim (object): generally passed through the @include_claim decorator,
                    contains a claim object of id c_id.
    """
    return render_template('claim.html',
                           claim=claim)


@claims_blueprint.route('/gifts/<int:g_id>/claims/add', methods=['GET'])
@login_required
@include_gift
@open_required
def add_get(g_id, gift):
    """Render form to add a claim on a gift of id g_id.

    Login required.
    One has to NOT be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    if gift.creator_id == session.get('user_id'):
        flash('You cannot claim your own gift ;-)')
        return redirect(url_for('gifts.get_byid',
                                g_id=gift.id))

    return render_template('add_claim.html',
                           gift=gift)


@claims_blueprint.route('/gifts/<int:g_id>/claims/add', methods=['POST'])
@login_required
@include_gift
@open_required
def add_post(g_id, gift):
    """Add a claim on a gift of id g_id to the database with POST.

    Login required.
    One has to NOT be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    if gift.creator_id == session.get('user_id'):
        flash('You cannot claim your own gift ;-)')
        return redirect(url_for('gifts.get_byid',
                                g_id=gift.id))

    claim = Claim(message=request.form.get('message'),
                  gift_id=g_id,
                  creator_id=session.get('user_id'))

    c.add(claim)
    c.commit()

    flash("Congratulations! You successfully claimed %s." % claim.gift.name)

    return redirect(url_for('claims.get_byid',
                            g_id=g_id,
                            c_id=claim.id))


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>/edit', methods=['GET'])  # noqa
@login_required
@include_claim
@creator_required
@open_required
def edit_get(g_id, c_id, claim):
    """Render edit form for a claim of id c_id on a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    claim (object): generally passed through the @include_claim decorator,
                    contains a claim object of id c_id.
    """
    return render_template('edit_claim.html',
                           claim=claim)


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>/edit', methods=['POST'])  # noqa
@login_required
@include_claim
@creator_required
@open_required
def edit_post(g_id, c_id, claim):
    """Edit a claim of id c_id on a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    claim (object): generally passed through the @include_claim decorator,
                    contains a claim object of id c_id.
    """
    claim.message = request.form.get('message')

    c.add(claim)
    c.commit()

    flash("Your claim on %s was successfully edited." % claim.gift.name)

    return redirect(url_for('claims.get_byid',
                            g_id=g_id,
                            c_id=c_id))


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>/delete', methods=['GET'])  # noqa
@login_required
@include_claim
@creator_required
@open_required
def delete_get(g_id, c_id, claim):
    """Render delete form for a claim with c_id on a gift with g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    claim (object): generally passed through the @include_claim decorator,
                    contains a claim object of id c_id.
    """
    return render_template('delete_claim.html',
                           claim=claim)


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>/delete', methods=['POST'])  # noqa
@login_required
@include_claim
@creator_required
@open_required
def delete_post(g_id, c_id, claim):
    """Delete a claim of id c_id on a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    claim (object): generally passed through the @include_claim decorator,
                    contains a claim object of id c_id.
    """
    gift_name = claim.gift.name

    c.delete(claim)
    c.commit()

    flash("Your claim on %s was successfully deleted." % gift_name)

    return redirect(url_for('claims.get',
                            g_id=g_id))


@claims_blueprint.route('/gifts/<int:g_id>/claims/<int:c_id>/accept', methods=['POST'])  # noqa
@login_required
@include_claim
@gift_creator_required
@open_required
def accept_post(g_id, c_id, claim):
    #claim.accepted = True
    #c.add(claim)

    #ift = claim.gift
    #gift.open = False
    #c.add(gift)

    #c.commit()

    giver_name = session.get('username')
    giver_email = session.get('email')
    claimer_name = claim.creator.name
    claimer_email = claim.creator.email

    message = """Hi %s and %s,\n
                 \n
                 Here's a mail to put you guys in contact so you can organize the
                 picking up of %s's gift.\n
                 \n
                 Thanks for using Giftr,\n
                 \n
                 Giftr""" % (giver_name, claimer_name, giver_name)
    msg = Message("Hello",
                  sender="Giftr <giftr@gmail.com>",
                  recipients=[claimer_email, giver_email])
    mail.send(msg)

    flash("You accepted %s's claim on your gift." % claim.creator.name)

    return redirect(url_for('claims.get',
                            g_id=g_id))

