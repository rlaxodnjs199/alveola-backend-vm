from os import walk
from typing import List, Dict


def _get_top_level_subdirectories(path: str) -> List[str]:
    for _, dirs, _ in walk(path):
        return dirs


def parse_subdirectories_in_path(path: str) -> List[Dict]:
    subdirs = _get_top_level_subdirectories(path)
    ct_scan_list = []

    for subdir in subdirs:
        dict = {}
        _, date, project, worker = subdir.split("_")
        dict["acquisition_date"] = date
        dict["project"] = project
        dict["worker"] = worker
        ct_scan_list.append(dict)

    return ct_scan_list


def deidentify_dicom(path: str):
    return
