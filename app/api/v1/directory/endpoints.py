from typing import List, Dict
from fastapi import APIRouter, HTTPException, status

from app import config
from . import util

directory_router = directory = APIRouter(
    prefix="/ct-scans", tags=["ct-scans"], responses={404: {"description": "Not found"}}
)


@directory.get("/raw", response_model=List[Dict])
async def get_raw_ct_scan_list():
    return util.parse_subdirectories_in_path(config.RAW_CT_PATH)


@directory.get("/deid")
async def get_deid_ct_scan_list():
    return {"DEID_PATH": config.DEID_CT_PATH}


@directory.get("/vida-processed")
async def get_vida_processed_ct_scan_list():
    return {"VIDA_PROCESSED_PATH": config.VIDA_PROCESSED_CT_PATH}
