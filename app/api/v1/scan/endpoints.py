from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.scan import schemas

from app.core.config import settings
from app.core.script import deidentify
from app.db.pgsql.session import get_db
from . import util

scan_router = scan = APIRouter(
    prefix="/ct-scans", tags=["ct-scans"], responses={404: {"description": "Not found"}}
)


@scan.get("/raw", response_model=List[Dict])
async def get_raw_ct_scan_list():
    return util.parse_subdirectories_in_path(settings.RAW_CT_PATH)


@scan.get("/vida-processed")
async def get_vida_processed_ct_scan_list():
    return {"VIDA_PROCESSED_PATH": settings.VIDA_PROCESSED_CT_PATH}


@scan.get("/deid", response_model=List[schemas.DeidScan])
async def get_deid_CT_scan_list(db=Depends(get_db)):
    return await util.get_scan_list(db)


@scan.get("/deid/{scan_id}", response_model=schemas.Scan)
async def get_deid_scan_by_id(scan_id: int, db=Depends(get_db)):
    scan = util.get_scan_by_id(db, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail=f"Scan: {scan_id} was not found")
    return scan


@scan.post("/deid")
async def create_deid_CT_scan(raw_CT_scan: schemas.Scan, db=Depends(get_db)):
    deid_CT_scan_list = deidentify.execute(raw_CT_scan, db)
    async for deid_CT_scan in deid_CT_scan_list:
        await util.create_scan(deid_CT_scan, db)

    return {"msg": "success"}
