"""Setup a database with the app's models."""

# CONFIGURATION #

# to manipulate Python run-time environment:
import sys
# for Mapper code:
from sqlalchemy import Column, ForeignKey, Integer, String
# for Configuration code and Class code:
from sqlalchemy.ext.declarative import declarative_base
# for creating foreign key relationships:
from sqlalchemy.orm import relationship
# for Configuration code:
from sqlalchemy import create_engine

# for Class code
# lets SQLAlchemy know that our classes
# are special SQLAlchemy classes
# that correspond to tables in the db:
Base = declarative_base()


# CONFIGURATION #

# point to the database we'll use
# (will create a new file if it doesn't exist):
engine = create_engine('sqlite:///giftr.db')
# add all classes that extend the Base class
# as tables in the database:
Base.metadata.create_all(engine)
