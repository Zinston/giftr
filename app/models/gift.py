from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        DateTime,
                        Boolean)
from sqlalchemy.orm import relationship
from datetime import datetime

from models import (Base,
                    User,
                    Category)

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

    open = Column(
            Boolean,
            default=True)

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