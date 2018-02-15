from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models import Base

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

    oauth_id = Column(
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