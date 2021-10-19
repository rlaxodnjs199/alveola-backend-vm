import os
from typing import List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select, text
from app.api.v1.scan import schemas
from app.core.config import settings

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
    scan_to_insert = models.Scan(**deid_CT_scan.dict())
    db.add(scan_to_insert)
    await db.commit()
    await db.refresh(scan_to_insert)

    return {"msg": f"Add scan {deid_CT_scan.folder_name} success"}


def delete_scan():
    return


def update_scan():
    return
