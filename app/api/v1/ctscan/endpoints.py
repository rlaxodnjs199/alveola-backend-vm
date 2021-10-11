from typing import List, Dict
from fastapi import APIRouter

from app.core.config import settings
from . import util

CTscan_router = CTscan = APIRouter(
    prefix="/ct-scans", tags=["ct-scans"], responses={404: {"description": "Not found"}}
)


@CTscan.get("/raw", response_model=List[Dict])
async def get_raw_ct_scan_list():
    return util.parse_subdirectories_in_path(settings.RAW_CT_PATH)


@CTscan.get("/deid")
async def get_deid_ct_scan_list():
    return util.parse_subdirectories_in_path(settings.DEID_CT_PATH)


@CTscan.get("/vida-processed")
async def get_vida_processed_ct_scan_list():
    return {"VIDA_PROCESSED_PATH": settings.VIDA_PROCESSED_CT_PATH}

@CTscan.post("/de-identify")
async def deidentfy_raw_ct_scans(ct_scan: Dict):
    return util.deidentify_dicom(ct_scan)
