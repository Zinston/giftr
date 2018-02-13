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