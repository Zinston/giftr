#!/usr/bin/env python

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
                   jsonify,
                   g,
                   session,
                   make_response,
                   abort)

# For OAuth
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)
import random
import string
import json
import requests
import httplib2

# For making decorators
from functools import wraps

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

# Bind Flask
app = Flask(__name__)

# API Secrets and IDs
# Get client id for Google OAuth2, from json file
google_client_secrets_f = open('google_client_secrets.json', 'r')
google_client_secrets = google_client_secrets_f.read()
google_client_secrets_json = json.loads(google_client_secrets)
CLIENT_ID = google_client_secrets_json['web']['client_id']


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


# CSRF protection
# Source: http://flask.pocoo.org/snippets/3/
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = get_random_string()
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


# ROUTES
# Client routes
# Gifts
@app.route('/', methods=['GET'])
@app.route('/gifts', methods=['GET'])
def get_gifts():
    """Render all gifts or gifts of category id "cat" if query."""
    categories = c.query(Category).all()

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


@app.route('/gifts/add', methods=['GET'])
@login_required
def show_add_gift():
    """Render form to add a gift.

    Login required.
    """
    categories = c.query(Category).all()

    return render_template('add_gift.html',
                           categories=categories)


@app.route('/gifts/add', methods=['POST'])
@login_required
def add_gift():
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

    return redirect(url_for('get_gift_byid',
                            g_id=gift.id))


@app.route('/gifts/<int:g_id>', methods=['GET'])
def get_gift_byid(g_id):
    """Render a gift of id g_id.

    Login required.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()
    categories = c.query(Category).all()

    return render_template('gift.html',
                           gift=gift,
                           categories=categories,
                           page="gift")


@app.route('/gifts/<int:g_id>/edit', methods=['GET'])
@login_required
def show_edit_gift(g_id):
    """Render an edit form for a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id != session.get('user_id'):
        flash('You have to be the creator of that gift to see that page.')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    categories = c.query(Category).all()

    return render_template('edit_gift.html',
                           gift=gift,
                           categories=categories)


@app.route('/gifts/<int:g_id>/edit', methods=['POST'])
@login_required
def edit_gift(g_id):
    """Edit a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id != session.get('user_id'):
        flash('You have to be the creator of that gift to see that page.')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    gift.name = request.form.get('name')
    gift.picture = request.form.get('picture')
    gift.description = request.form.get('description')
    gift.category_id = request.form.get('category')

    c.add(gift)
    c.commit()

    flash("%s was successfully edited." % gift.name)

    return redirect(url_for('get_gift_byid',
                            g_id=gift.id))


@app.route('/gifts/<int:g_id>/delete', methods=['GET'])
@login_required
def show_delete_gift(g_id):
    """Render a delete form for a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id != session.get('user_id'):
        flash('You have to be the creator of that gift to see that page.')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    return render_template('delete_gift.html',
                           gift=gift)


@app.route('/gifts/<int:g_id>/delete', methods=['POST'])
@login_required
def delete_gift(g_id):
    """Delete a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id != session.get('user_id'):
        flash('You have to be the creator of that gift to see that page.')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    c.delete(gift)
    c.commit()

    # Delete the claims to that object too
    claims = c.query(Claim).filter_by(gift_id=gift.id).all()
    for claim in claims:
        c.delete(claim)
        c.commit()

    flash("%s was successfully deleted." % gift.name)

    return redirect(url_for('get_gifts'))


# Claims
@app.route('/gifts/claims', methods=['GET'])
def get_all_claims():
    """Render all claims in the database."""
    claims = c.query(Claim).all()

    return render_template('claims.html',
                           claims=claims)


@app.route('/gifts/<int:g_id>/claims', methods=['GET'])
def get_claims(g_id):
    """Render all claims on a gift of id g_id.

    Argument:
    g_id (int): the id of the desired gift.
    """
    claims = c.query(Claim).filter_by(gift_id=g_id).all()
    gift = c.query(Gift).filter_by(id=g_id).first()

    return render_template('claims.html',
                           gift=gift,
                           claims=claims)


@app.route('/gifts/<int:g_id>/claims/add', methods=['GET'])
@login_required
def show_add_claim(g_id):
    """Render form to add a claim on a gift of id g_id.

    Login required.
    One has to NOT be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id == session.get('user_id'):
        flash('You cannot claim your own gift ;-)')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    return render_template('add_claim.html',
                           gift=gift)


@app.route('/gifts/<int:g_id>/claims', methods=['POST'])
@login_required
def add_claim(g_id):
    """Add a claim on a gift of id g_id to the database with POST.

    Login required.
    One has to NOT be the creator of the gift to access this.

    Argument:
    g_id (int): the id of the desired gift.
    """
    gift = c.query(Gift).filter_by(id=g_id).first()

    if gift.creator_id == session.get('user_id'):
        flash('You cannot claim your own gift ;-)')
        return redirect(url_for('get_gift_byid',
                                g_id=gift.id))

    claim = Claim(message=request.form.get('message'),
                  gift_id=g_id,
                  creator_id=session.get('user_id'))

    c.add(claim)
    c.commit()

    flash("Congratulations! You successfully claimed %s." % claim.gift.name)

    return redirect(url_for('get_claim_byid',
                            g_id=g_id,
                            c_id=claim.id))


@app.route('/gifts/<int:g_id>/claims/<int:c_id>', methods=['GET'])
def get_claim_byid(g_id, c_id):
    """Render a claim of id c_id on a gift of id g_id.

    Login required.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    """
    claim = c.query(Claim).filter_by(id=c_id).first()

    return render_template('claim.html',
                           claim=claim)


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/edit', methods=['GET'])
@login_required
def show_edit_claim(g_id, c_id):
    """Render edit form for a claim of id c_id on a gift of id g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    """
    claim = c.query(Claim).filter_by(id=c_id).first()

    if claim.creator_id != session.get('user_id'):
        flash('You have to be the creator of that claim to see that page.')
        return redirect(url_for('get_claim_byid',
                                c_id=claim.id))

    return render_template('edit_claim.html',
                           claim=claim)


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/edit', methods=['POST'])
@login_required
def edit_claim(g_id, c_id):
    """Edit a claim of id c_id on a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    """
    claim = c.query(Claim).filter_by(id=c_id).first()

    if claim.creator_id != session.get('user_id'):
        flash('You have to be the creator of that claim to see that page.')
        return redirect(url_for('get_claim_byid',
                                c_id=claim.id))

    claim.message = request.form.get('message')

    c.add(claim)
    c.commit()

    flash("Your claim on %s was successfully edited." % claim.gift.name)

    return redirect(url_for('get_claim_byid',
                            g_id=g_id,
                            c_id=c_id))


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/delete', methods=['GET'])
@login_required
def show_delete_claim(g_id, c_id):
    """Render delete form for a claim with c_id on a gift with g_id.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    c_id (int): the id of the desired claim.
    """
    claim = c.query(Claim).filter_by(id=c_id).first()

    if claim.creator_id != session.get('user_id'):
        flash('You have to be the creator of that claim to see that page.')
        return redirect(url_for('get_claim_byid',
                                c_id=claim.id))

    return render_template('delete_claim.html',
                           claim=claim)


@app.route('/gifts/<int:g_id>/claims/<int:c_id>/delete', methods=['POST'])
@login_required
def delete_claim(g_id, c_id):
    """Delete a claim of id c_id on a gift of id g_id with POST.

    Login required.
    One has to be the creator of the gift to access this.

    Arguments:
    g_id (int): the id of the desired gift.
    """
    claim = c.query(Claim).filter_by(id=c_id).first()

    if claim.creator_id != session.get('user_id'):
        flash('You have to be the creator of that claim to see that page.')
        return redirect(url_for('get_claim_byid',
                                c_id=claim.id))

    gift_name = claim.gift.name

    c.delete(claim)
    c.commit()

    flash("Your claim on %s was successfully deleted." % gift_name)

    return redirect(url_for('get_claims',
                            g_id=g_id))


# Categories
@app.route('/categories', methods=['GET'])
def get_categories():
    """Render all claims in the database."""
    categories = c.query(Category).all()

    return render_template('categories.html',
                           categories=categories)


@app.route('/categories/add', methods=['GET'])
@login_required
def show_add_category():
    """Render form to add a category.

    Login required.
    """
    return render_template('add_category.html')


@app.route('/categories', methods=['POST'])
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


@app.route('/categories/<int:cat_id>', methods=['GET'])
def get_category_byid(cat_id):
    """Render a category of id cat_id.

    Argument:
    cat_id (int): the id of the desired category.
    """
    category = c.query(Category).filter_by(id=cat_id).first()

    return render_template('category.html',
                           category=category)


@app.route('/categories/<int:cat_id>/edit', methods=['GET'])
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


@app.route('/categories/<int:cat_id>', methods=['POST'])
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


@app.route('/categories/<int:cat_id>/delete', methods=['GET'])
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


@app.route('/categories/<int:cat_id>', methods=['POST'])
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


# AUTH

# Log in

@app.route('/login', methods=['GET'])
def show_login():
    """Render login page with a generated random state variable."""
    # If the user is already logged in, redirect them.
    if 'username' in session:
        flash("You're already logged in. Disconnect first.")
        return redirect(url_for('get_gifts'))

    state = get_random_string()

    # store that random string in the session
    session['state'] = state

    return render_template('login.html',
                           STATE=session['state'],
                           user='logging in')


@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    """Login and/or register a user using Google OAuth."""
    # Check if the posted STATE matches the session state
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # PART 1: Getting the credentials object
    # -------

    # Get the ONE-TIME-USE CODE sent through ajax
    code = request.data

    try:
        # Try and upgrade the authorization code into a CREDENTIALS OBJECT
        # (Exchange it via oauth2client.client)
        # The credentials object contains the ACCESS TOKEN for the server

        # 1. Create oauth_flow object with the client's SECRET KEY info in it
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json',
                                             scope='')
        # 2. Specify that this is the one-time code flow
        # the server will be sending off
        oauth_flow.redirect_uri = 'postmessage'
        # 3. Make the exchange, using the ONE-TIME-USE CODE
        # Exchanges an authorization code with a CREDENTIALS OBJECT
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        message = 'Failed to upgrade the authorization code.'
        response = make_response(json.dumps(message), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # PART 2: Verifying the validity of the credentials
    # -------

    # Have GOOGLE verify that the access token is valid

    # 1. Get ACCESS TOKEN from credentials
    access_token = credentials.access_token
    # 2. Get the URL for GOOGLE access token checking
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)  # noqa
    # 3. Create a json GET request with the URL
    # and store the result of that request in gapi_tokeninfo
    h = httplib2.Http()
    gapi_tokeninfo = json.loads(h.request(url, 'GET')[1])

    # Check if Google API's server's access token verification
    # returned an ERROR
    if gapi_tokeninfo.get('error') is not None:
        response = make_response(json.dumps(gapi_tokeninfo.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

        return response

    # If we get this far, the access token is VALID
    # Now we check if it's THE RIGHT ACCESS TOKEN

    # 1. Verify that the access token is used FOR THE INTENDED USER

    # Get the id of the token from the CREDENTIALS OBJECT
    gplus_id = credentials.id_token['sub']

    # Check that it matches the id of the token returned by Google API's server
    if gapi_tokeninfo['user_id'] != gplus_id:
        message = "Token's user ID doesn't match given user ID."
        response = make_response(json.dumps(message), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # 2. Verify that the access token is valid FOR THIS APP

    # Check that our client's id matches that of the token
    # returned by Google API's server
    if gapi_tokeninfo['issued_to'] != CLIENT_ID:
        message = "Token's client ID does not match this app's."
        response = make_response(json.dumps(message), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # 3. Verify that the user's NOT ALREADY LOGGED IN

    # Get the access token stored in the session if there is one
    stored_access_token = session.get('access_token')
    # Get the user id stored in the session if there is one
    stored_gplus_id = session.get('gplus_id')

    # Check if there is already an access token in the session
    # and if so, if the id of the token from the CREDENTIALS OBJECT
    # matches the id stored in the session
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        print 'Current user is already connected.'

        return make_response(render_template('login_success.html'))

    # PART 3: Log in
    # -------

    # If we get this far, the access token is VALID
    # and it's THE RIGHT ACCESS TOKEN.
    # The user can be successfully logged in

    # 1. Store the access token in the session
    session['access_token'] = access_token
    session['gplus_id'] = gplus_id

    # 2. Get user info from Google's API
    # Get the URL for GOOGLE'S API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    # Get the parameters to send with the request
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    # Send a GET request to Google's API
    userinfo = requests.get(userinfo_url, params=params)
    # Store the user's info in JSON from the response to the request
    userinfo_json = json.loads(userinfo.text)

    # 3. Store user info in the session
    session['username'] = userinfo_json['name']
    session['picture'] = userinfo_json['picture']
    session['email'] = userinfo_json['email']

    # Specify we used Google to sign in
    session['provider'] = 'google'

    # PART 4: Check if user needs to be registered
    # -------

    # 1. Get the user id from db if user exists
    user_id = get_user_id(session.get('email'))

    # 2. If it doesn't exist: create it and get his
    # newly created id
    if not user_id:
        user_id = create_user_from_session()
        flash('Welcom %s! You successfully signed up!' % session['username'])
    else:
        flash("""Welcome %s!
                 You were successfully logged in!""" % session['username'])

    # 3. Store the user id in the session
    session['user_id'] = user_id

    # Return html to place into the 'result' div
    return make_response(render_template('login_success.html'))


@app.route('/fbconnect', methods=['GET', 'POST'])
def fbconnect():
    """Login and/or register a user using Facebook OAuth."""
    # 1. Check if the posted STATE matches the session state
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # 2. Get the ACCESS TOKEN sent through ajax
    access_token = request.data

    # 3. Exchange client token for long-lived server-side token
    # with GET /oauth/access_token?grant_type=fb_exchange_token&client_id=
    # {app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    fb_info = json.loads(open('fb_client_secrets.json', 'r').read())
    app_id = fb_info['web']['app_id']
    app_secret = fb_info['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # 4. Use the long-lived token to get user info from API
    # extract access token from result
    token = eval(result).get('access_token')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email,picture' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['username'] = data['name']
    session['email'] = data['email']
    session['fb_id'] = data['id']
    session['picture'] = data['picture']['data']['url']

    # Specify we used Facebook to sign in
    session['provider'] = 'facebook'

    # 4. Check if user needs to be registered

    # 4.1. Get the user id from db if user exists
    user_id = get_user_id(session.get('email'))

    # 4.2. If it doesn't exist: create it and get his
    # newly created id
    if not user_id:
        user_id = create_user_from_session()
        flash('Welcom %s! You successfully signed up!' % session['username'])
    else:
        flash("""Welcome %s!
                 You were successfully logged in!""" % session['username'])

    # 4.3. Store the user id in the session
    session['user_id'] = user_id

    # Return html to place into the 'result' div
    return make_response(render_template('login_success.html'))


# Log out

@app.route('/disconnect')
def disconnect():
    """Redirect to appropriate disconnect function and clear session."""
    # If there's a user...
    if 'provider' in session:
        # If they logged in through GOOGLE
        if session['provider'] == 'google':
            # Revoke their Google access token
            gdisconnect()
            del session['gplus_id']

        # If they logged in through FACEBOOK
        if session['provider'] == 'facebook':
            # Revoke their Facebook access token
            fbdisconnect()
            del session['fb_id']

        # In any case, log them out...
        session.pop('username', None)
        session.pop('email', None)
        session.pop('picture', None)
        session.pop('user_id', None)
        session.pop('provider', None)
        session.pop('token', None)

        # Flash them
        flash("You have successfully logged out.")

        # Redirect them
        return redirect(url_for('get_gifts'))

    # If there's no user...
    else:
        # Flash them
        flash("You were not logged in to begin with...")

        # Redirect them
        return redirect(url_for('get_gifts'))


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect a user using Google OAuth."""
    # Disconnect = revoke a user's token and revoque their session

    # PART 1: Check that there is a user to disconnect
    # -------

    # Get the ACCESS TOKEN from the session
    token = session.get('access_token')

    # If there is none, then we have no user logged in
    if token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # PART 2: Disconnect user
    # -------

    # Have Google revoke the token

    # 2. Create a POST request with the URL
    # and store the json result of that request
    url = 'https://accounts.google.com/o/oauth2/revoke'
    params = {'token': token}
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    result = requests.post(url=url, params=params, headers=headers)

    # 3. Check if it's a success
    if result.status_code == '200':
        # 4. Send the response (DISCONNECT() TAKES CARE OF DELETING SESSION)
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    response = make_response(json.dumps('Could not revoke the token.'), 500)
    response.headers['Content-Type'] = 'application/json'

    return response


@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect a user using Facebook OAuth."""
    # PART 1: Check that there is a user to disconnect
    # -------

    # Get the ACCESS TOKEN from the session
    access_token = session.get('access_token')

    # If there is none, then we have no user logged in
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response

    # PART 2: Disconnect user
    # -------

    # Have Facebook revoke the permission

    # 1. Get the URL for FACEBOOK permissions
    fb_id = session['fb_id']
    url = 'https://graph.facebook.com/%s/permissions' % fb_id

    # 2. Create a DELETE request with the URL
    url = 'https://graph.facebook.com/%s/permissions' % fb_id
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    result = requests.delete(url=url, headers=headers)

    # 3. Check if it's a success
    if result.status_code == '200':
        # 4. Send the response (DISCONNECT() TAKES CARE OF DELETING SESSION)
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    response = make_response(json.dumps('Could not revoke the token.'), 500)
    response.headers['Content-Type'] = 'application/json'
    return response


# API Routes
@app.route('/api/gifts')
def api_get_gifts():
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


@app.route('/api/gifts/<int:g_id>')
def api_get_gift(g_id):
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


@app.route('/api/categories')
def api_get_categories():
    """Return the categories in json."""
    # Query database
    categories = c.query(Category).all()

    # Serialize
    serialized_categories = [cat.serialize for cat in categories]

    # Jsonify
    return jsonify({'categories': serialized_categories})


@app.route('/api/categories/<int:cat_id>')
def api_get_category(cat_id):
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


# HELPERS

def create_user_from_session():
    """Add a user to database from session, return its database id."""
    # Create a new User in db with the info from the session
    new_user = User(name=session.get('username'),
                    email=session.get('email'),
                    picture=session.get('picture'))
    c.add(new_user)
    c.commit()

    # Get the new User, from their email
    user_id = get_user_id(session.get('email'))

    # Return the new User's id
    return user_id


def get_user_id(email):
    """Return a user's database id from their email address.

    Argument:
    email (str): the user's email address.
    """
    try:
        user = c.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_random_string():
    """Get a random string of 32 uppercase letters and digits."""
    choice = string.ascii_uppercase + string.digits
    chars = [random.choice(choice) for x in xrange(32)]
    return ''.join(chars)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(port=8080)
