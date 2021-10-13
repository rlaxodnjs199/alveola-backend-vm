import os
import datetime
from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from app.api.v1.scan import schemas

from . import models


def _get_top_level_subdirectories(path: str) -> List[str]:
    for _, dirs, _ in os.walk(path):
        return dirs


def parse_subdirectories_in_path(path: str) -> List[Dict]:
    subdirs = _get_top_level_subdirectories(path)
    ct_scan_list = []
    try:
        for subdir in subdirs:
            dict = {}
            _, date, project, participant_id, worker = subdir.split("_")
            dict["acquisition_date"] = date
            dict["project"] = project
            dict["participant_id"] = participant_id
            dict["worker"] = worker

            ct_scan_list.append(dict)
    except:
        raise HTTPException(status_code=400, detail="Raw CT folder syntax error")

    return ct_scan_list


async def get_scan_list(db: AsyncSession):
    stmt = select(models.Scan)
    query_result = await db.execute(stmt)
    scan_list = [
        schemas.DeidScan.from_orm(scan) for scan in query_result.scalars().all()
    ]

    return scan_list


async def create_scan(deid_CT_scan: schemas.ScanCreate, db: AsyncSession):
    scan_to_insert = models.Scan(**deid_CT_scan)
    scan_to_insert.acquisition_date = datetime.datetime.strptime(
        scan_to_insert.acquisition_date, "%Y%m%d"
    ).date()
    db.add(scan_to_insert)
    await db.commit()
    await db.refresh(scan_to_insert)

    return scan_to_insert


def delete_scan():
    return


def update_scan():
    return
