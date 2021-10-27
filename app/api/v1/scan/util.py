import os
from typing import List, Dict
from operator import attrgetter

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
            _, date, project, pid, processed_by = subdir.split("_")
            dict["acquisition_date"] = date
            dict["project"] = project
            dict["pid"] = pid
            dict["processed_by"] = processed_by

            ct_scan_list.append(dict)
    except:
        raise HTTPException(status_code=400, detail="Raw CT folder syntax error")

    return ct_scan_list


def modify_acquisition_date_format(
    deid_CT_scan_list: schemas.DeidScan,
) -> List[schemas.DeidScan]:
    for scan in deid_CT_scan_list:
        scan.acquisition_date = scan.acquisition_date.strftime("%Y%m%d")
    return deid_CT_scan_list


async def get_scan_list(db: AsyncSession) -> List[schemas.DeidScan]:
    stmt = select(models.Scan)
    query_result = await db.execute(stmt)
    scans = modify_acquisition_date_format(query_result.scalars().all())
    scans.sort(key=attrgetter("acquisition_date"))
    return scans


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
