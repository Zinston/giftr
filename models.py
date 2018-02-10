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

from datetime import datetime

# for Class code
# lets SQLAlchemy know that our classes
# are special SQLAlchemy classes
# that correspond to tables in the db:
Base = declarative_base()


# CLASS #

class User(Base):
    """Database table for a user."""

    # TABLE #
    __tablename__ = 'user'
    # MAPPER #
    id = Column(
            Integer,
            primary_key=True)

    name = Column(
            String(80),
            nullable=False)

    email = Column(
                String(80),
                nullable=False)

    address = Column(
    			String(200))

    picture = Column(
                String(80))

    created_at = Column(
					Date,
					default=datetime.datetime.now())

    updated_at = Column(
					Date,
					onupdate=datetime.datetime.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'address': self.address,
            'id': self.id
        }


class Gift(Base):
	"""Database table for a gift."""

	# TABLE #
	__tablename__ = 'gift'
	# MAPPER#
	id = Column(
            Integer,
            primary_key=True)

	name = Column(
			String(80),
			nullable=False)

	picture = Column(
				String(80))

	description = Column(
					String(140))

	created_at = Column(
					Date,
					default=datetime.datetime.now())

	updated_at = Column(
					Date,
					onupdate=datetime.datetime.now())

	creator_id = Column(
	                Integer,
	                ForeignKey('user.id'))

    creator = relationship(User)

    category_id = Column(
    				Integer,
    				ForeignKey('category.id'))

    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'creator_id': self.creator_id,
            'category_id': self.category_id,
            'id': self.id
        }


# CONFIGURATION #

# point to the database we'll use
# (will create a new file if it doesn't exist):
engine = create_engine('sqlite:///giftr.db')
# add all classes that extend the Base class
# as tables in the database:
Base.metadata.create_all(engine)
