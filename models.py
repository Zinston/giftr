"""Setup a database with the app's models."""

# CONFIGURATION #

# to manipulate Python run-time environment:
import sys
# for Mapper code:
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
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
                    DateTime,
                    default=datetime.now())

    updated_at = Column(
                    DateTime,
                    onupdate=datetime.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'address': self.address,
            'picture': self.picture,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


# CLASS #

class Category(Base):
    """Database table for a gift category."""

    # TABLE #
    __tablename__ = 'category'
    # MAPPER#
    id = Column(
            Integer,
            primary_key=True)

    name = Column(
            String(80),
            nullable=False)

    description = Column(
                    String(140))

    picture = Column(
                String(80))

    created_at = Column(
                    DateTime,
                    default=datetime.now())

    updated_at = Column(
                    DateTime,
                    onupdate=datetime.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'picture': self.picture,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


# CLASS #

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
                    DateTime,
                    default=datetime.now())

    updated_at = Column(
                    DateTime,
                    onupdate=datetime.now())

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
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'creator_id': self.creator_id,
            'category_id': self.category_id
        }


# CLASS #

class Claim(Base):
    """Database table for a claim on a gift."""

    # TABLE #
    __tablename__ = 'claim'
    # MAPPER#
    id = Column(
            Integer,
            primary_key=True)

    message = Column(
            String(140),
            nullable=False)

    created_at = Column(
                    DateTime,
                    default=datetime.now())

    updated_at = Column(
                    DateTime,
                    onupdate=datetime.now())

    gift_id = Column(
                    Integer,
                    ForeignKey('gift.id'))

    gift = relationship(Gift)

    creator_id = Column(
                    Integer,
                    ForeignKey('user.id'))

    creator = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'id': self.id,
            'message': self.message,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'gift_id': self.gift_id,
            'creator_id': self.creator_id
        }


# CONFIGURATION #

# point to the database we'll use
# (will create a new file if it doesn't exist):
engine = create_engine('sqlite:///giftr.db')
# add all classes that extend the Base class
# as tables in the database:
Base.metadata.create_all(engine)
