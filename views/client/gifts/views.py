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