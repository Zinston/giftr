#!/usr/bin/env python

"""Define routes for login procedures."""

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

login_blueprint = Blueprint('login', __name__, template_folder='templates')

# ROUTES

@login_blueprint.route('/login', methods=['GET'])
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


@login_blueprint.route('/gconnect', methods=['GET', 'POST'])
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
        # Current user is already connected.

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


@login_blueprint.route('/fbconnect', methods=['GET', 'POST'])
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


# HELPERS

def get_random_string():
    """Get a random string of 32 uppercase letters and digits."""
    choice = string.ascii_uppercase + string.digits
    chars = [random.choice(choice) for x in xrange(32)]
    return ''.join(chars)


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
