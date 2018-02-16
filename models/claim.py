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
                    Gift)

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

    accepted = Column(
                Boolean,
                default=False)

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