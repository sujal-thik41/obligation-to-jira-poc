from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.session import Base

class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String, nullable=False)
    obligated_party = Column(String, nullable=True)
    action = Column(Text, nullable=True)
    is_mandatory = Column(String, nullable=True)
    clause_text = Column(Text, nullable=True)
    clause_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
