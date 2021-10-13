import datetime
from typing import Optional
from pydantic import BaseModel


class Scan(BaseModel):
    project: str
    participant_id: str
    acquisition_date: datetime.date
    worker: Optional[str]
    status: str

    class Config:
        orm_mode = True


class ScanCreate(Scan):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    path: str
