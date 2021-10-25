from sqlalchemy import Column, String, Date, DateTime, Integer
from sqlalchemy.sql import func
from app.db.pgsql.base_model import Base


class Scan(Base):
    __tablename__ = "scan"

    folder_name = Column(String, nullable=False, unique=True)
    project = Column(String, nullable=False)
    pid = Column(String, nullable=False)
    acquisition_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    worker = Column(String)
    status = Column(String, default="De-identified")
    in_or_ex = Column(String, nullable=False)
    timepoint = Column(Integer, nullable=False, default=0)
    path = Column(String)
    vida_case_id = Column(Integer)
