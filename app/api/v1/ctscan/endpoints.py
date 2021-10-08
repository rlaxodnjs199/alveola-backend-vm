from typing import List, Dict
from fastapi import APIRouter, HTTPException, status

from app import config
from . import util

CTscan_router = CTscan = APIRouter(
    prefix="/ct-scans", tags=["ct-scans"], responses={404: {"description": "Not found"}}
)


@CTscan.get("/raw", response_model=List[Dict])
async def get_raw_ct_scan_list():
    return util.parse_subdirectories_in_path(config.RAW_CT_PATH)


@CTscan.get("/deid")
async def get_deid_ct_scan_list():
    return {"DEID_PATH": config.DEID_CT_PATH}


@CTscan.get("/vida-processed")
async def get_vida_processed_ct_scan_list():
    return {"VIDA_PROCESSED_PATH": config.VIDA_PROCESSED_CT_PATH}

@CTscan.post("/de-identify")
async def deidentfy_raw_ct_scans(ct_scan_list: List[Dict]):
    print(ct_scan_list)
    return {'msg': 'success'}
