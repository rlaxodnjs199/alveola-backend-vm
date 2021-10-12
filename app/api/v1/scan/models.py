from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.sql import func
from app.db.pgsql.base_model import Base


class Scan(Base):
    __tablename__ = "scan"

    project = Column(String, nullable=False)
    participant_id = Column(String, nullable=False)
    acquisition_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    worker = Column(String)
    status = Column(String, default="De-identified")
