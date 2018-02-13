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