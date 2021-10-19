from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, validator


class Scan(BaseModel):
    project: str
    participant_id: str
    acquisition_date: date
    worker: str

    @validator("acquisition_date", pre=True)
    def parse_acquisition_date(cls, value):
        return datetime.strptime(value, "%Y%m%d").date()

    class Config:
        orm_mode = True


class ScanCreate(Scan):
    path: str
    folder_name: str
    in_or_ex: str
    timepoint: int


class DeidScan(Scan):
    created_at: datetime
    updated_at: Optional[datetime]
    status: str
    in_or_ex: str
    timepoint: int
