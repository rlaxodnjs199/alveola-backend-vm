import os
from typing import List, Dict
from fastapi import HTTPException


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