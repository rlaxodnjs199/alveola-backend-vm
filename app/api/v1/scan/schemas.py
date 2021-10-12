import datetime
from typing import Optional
from pydantic import BaseModel


class Scan(BaseModel):
    id: int
    project: str
    participant_id: str
    acquisition_date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime
    worker: Optional[str]
    status: str

    class Config:
        orm_mode = True
