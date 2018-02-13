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