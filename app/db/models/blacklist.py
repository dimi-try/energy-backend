from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.models.base import Base

class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    reason = Column(String, nullable=True)  # Причина добавления в черный список
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship(
        "User",
        back_populates="blacklist_entry",
        primaryjoin="foreign(Blacklist.user_id)==User.id",
        uselist=False
    )