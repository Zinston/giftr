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
                   jsonify)

# Bind database
engine = create_engine('sqlite:///giftr.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
c = DBSession()

# Bind Flask
app = Flask(__name__)


if __name__ == '__main__':
    app.debug = True
    app.run(port=8080)