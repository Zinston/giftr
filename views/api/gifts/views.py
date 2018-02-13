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