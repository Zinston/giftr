from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models import Base

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
