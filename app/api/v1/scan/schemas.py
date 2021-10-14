from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class Scan(BaseModel):
    project: str
    participant_id: str
    acquisition_date: date
    worker: str

    class Config:
        orm_mode = True


class ScanCreate(Scan):
    path: str
    folder_name: str


class DeidScan(Scan):
    created_at: datetime
    updated_at: Optional[datetime]
    status: str
