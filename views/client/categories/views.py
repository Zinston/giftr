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
                   jsonify,
                   g,
                   session,
                   make_response,
                   abort,
                   Blueprint)

# For making decorators
from functools import wraps

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

categories_blueprint = Blueprint('categories', __name__, template_folder='templates')

# DECORATORS
def login_required(f):
    """Redirect to login page if the user is not logged in (decorator)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to see that page.')
            return redirect(url_for('show_login'))
        return f(*args, **kwargs)
    return decorated_function

# ROUTES

@categories_blueprint.route('/categories', methods=['GET'])
def get_categories():
    """Render all claims in the database."""
    categories = c.query(Category).all()

    return render_template('categories.html',
                           categories=categories)


@categories_blueprint.route('/categories/add', methods=['GET'])
@login_required
def show_add_category():
    """Render form to add a category.

    Login required.
    """
    return render_template('add_category.html')


@categories_blueprint.route('/categories', methods=['POST'])
@login_required
def add_category():
    """Add a category to the database with POST.

    Login required.
    """
    category = Category(name=request.form.get('name'),
                        picture=request.form.get('picture'),
                        description=request.form.get('description'))

    c.add(category)
    c.commit()

    flash("The category \"%s\" was successfully added." % category.name)

    return redirect(url_for('get_category_byid',
                            cat_id=category.id))


@categories_blueprint.route('/categories/<int:cat_id>', methods=['GET'])
def get_category_byid(cat_id):
    """Render a category of id cat_id.

    Argument:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('category.html',
                           category=category)


@categories_blueprint.route('/categories/<int:cat_id>/edit', methods=['GET'])
@login_required
def show_edit_category(cat_id):
    """Render edit form for a category of id cat_id.

    Login required.

    Arguments:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('edit_category.html',
                           category=category)


@categories_blueprint.route('/categories/<int:cat_id>', methods=['POST'])
@login_required
def edit_category(cat_id):
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

    return redirect(url_for('get_category_byid',
                            cat_id=category.id))


@categories_blueprint.route('/categories/<int:cat_id>/delete', methods=['GET'])
@login_required
def show_delete_category(cat_id):
    """Render delete form for a category of id cat_id.

    Login required.

    Arguments:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('delete_category.html',
                           category=category)


@categories_blueprint.route('/categories/<int:cat_id>', methods=['POST'])
@login_required
def delete_category(cat_id):
    """Delete a category of id cat_id with POST.

    Login required.

    Argument:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    c.delete(category)
    c.commit()

    flash("The category \"%s\" was successfully deleted." % category.name)

    return redirect(url_for('get_categories'))