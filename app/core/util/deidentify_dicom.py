import os
from typing import List, Union
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydicom import Dataset, dcmread
from app.core.config import settings
from app.api.v1.scan.schemas import Scan, ScanCreate


TLC_FOLDER_SYNTAX = "TLC"
FRC_FOLDER_SYNTAX = "RV"


async def execute(raw_CT_scan: Scan, db: AsyncSession) -> List[ScanCreate]:
    def _get_raw_dcm_dir_path(raw_CT_scan: Scan):
        try:
            raw_dcm_dir_path = f"{settings.RAW_CT_PATH}/"
            raw_dcm_dir_path += (
                "DCM_{acquisition_date}_{project}_{pid}_{worker}".format(
                    **raw_CT_scan.dict()
                )
            )
            raw_dcm_dir_path = raw_dcm_dir_path.replace("-", "")
        except:
            raise HTTPException(status_code=400, detail="Raw CT folder syntax error")
        return raw_dcm_dir_path

    def _yield_subdir_if_exists(dir: str):
        for subdir in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, subdir)):
                yield os.path.join(dir, subdir)

    def _get_dcm_paths_from_dir(dcm_dir: str):
        for base, _, files in os.walk(dcm_dir):
            for file in files:
                yield os.path.join(base, file)

    def _get_patient_id_from_dir(raw_dcm_dir: str) -> str:
        return os.path.basename(raw_dcm_dir).split("_")[-2]

    async def _is_scan_duplicate(
        folder_name: str, in_or_ex: str, db: AsyncSession
    ) -> Union[int, bool]:
        stmt = text(
            f"SELECT folder_name FROM {settings.DB_TABLE_SCAN} WHERE folder_name='{folder_name}' AND in_or_ex='{in_or_ex}'"
        )
        result = await db.execute(stmt)
        if result.scalars().all():
            return True
        return False

    async def _calc_scan_timepoint(
        project: str, pid: str, in_or_ex: str, db: AsyncSession
    ):
        stmt = text(
            f"SELECT MAX(timepoint) FROM {settings.DB_TABLE_SCAN} WHERE project='{project}' AND pid='{pid}' AND in_or_ex='{in_or_ex}'"
        )
        result = await db.execute(stmt)
        max_timepoint = result.scalars().first()
        if type(max_timepoint) == int:
            return max_timepoint + 1
        return 0

    def _deidentify_dcm_slice(dcm_path: str, patient_ID: str) -> Dataset:
        dicom_to_deidentify = dcmread(dcm_path)

        try:
            dicom_to_deidentify.PatientID = dicom_to_deidentify.PatientName = patient_ID
        except:
            print(f"{dcm_path}: PatientID or PatientName tag does not exist")
        try:
            dicom_to_deidentify.PatientBirthDate = (
                dicom_to_deidentify.PatientBirthDate[:-4] + "0101"
            )
        except:
            print(f"{dcm_path}: PatientBirthDate tag does not exist")

        tags_to_anonymize = [
            # 'PatientBirthDate',
            # 'PatientSex',
            # 'PatientAge',
            "InstitutionName",
            "InstitutionAddress",
            "InstitutionalDepartmentName",
            "ReferringPhysicianName",
            "ReferringPhysicianTelephoneNumbers",
            "ReferringPhysicianAddress",
            "PhysiciansOfRecord",
            "OperatorsName",
            "IssuerOfPatientID",
            "OtherPatientIDs",
            "OtherPatientNames",
            "OtherPatientIDsSequence",
            "PatientBirthName",
            # 'PatientSize',
            # 'PatientWeight',
            "PatientAddress",
            "PatientMotherBirthName",
            "CountryOfResidence",
            "RegionOfResidence",
            "CurrentPatientLocation",
            "PatientTelephoneNumbers",
            "SmokingStatus",
            "PregnancyStatus",
            "PatientReligiousPreference",
            "RequestingPhysician",
            "PerformingPhysicianName",
            "NameOfPhysiciansReadingStudy",
            "MilitaryRank",
            "EthnicGroup",
            "AdditionalPatientHistory",
            "PatientComments",
            "PersonName",
            "ScheduledPatientInstitutionResidence",
        ]
        for tag in tags_to_anonymize:
            if tag in dicom_to_deidentify:
                delattr(dicom_to_deidentify, tag)
        dicom_to_deidentify.remove_private_tags()

        return dicom_to_deidentify

    def _construct_deid_CT_scan(
        raw_CT_scan: Scan, deid_dcm_dirname: str, in_or_ex: str, timepoint: int
    ) -> ScanCreate:
        print(raw_CT_scan, deid_dcm_dirname, in_or_ex, timepoint)
        deid_CT_scan = ScanCreate(
            project=raw_CT_scan.project,
            pid=raw_CT_scan.pid,
            acquisition_date=raw_CT_scan.acquisition_date.strftime("%Y%m%d"),
            worker=raw_CT_scan.worker,
            folder_name=deid_dcm_dirname,
            path=f"{settings.DEID_CT_PATH}/{deid_dcm_dirname}",
            in_or_ex=in_or_ex,
            timepoint=timepoint,
        )

        return deid_CT_scan

    def _save_dcm_slice(
        deid_dcm: Dataset,
        deid_dcm_dirname: str,
        in_or_ex: str,
        deid_dcm_filename: str,
        deid_dcm_basedir=settings.DEID_CT_PATH,
    ):
        if not os.path.exists(f"{deid_dcm_basedir}/{deid_dcm_dirname}"):
            os.makedirs(f"{deid_dcm_basedir}/{deid_dcm_dirname}")

        if in_or_ex == "IN":
            if not os.path.exists(
                f"{deid_dcm_basedir}/{deid_dcm_dirname}/{TLC_FOLDER_SYNTAX}"
            ):
                os.makedirs(
                    f"{deid_dcm_basedir}/{deid_dcm_dirname}/{TLC_FOLDER_SYNTAX}"
                )
            try:
                deid_dcm.save_as(
                    f"{deid_dcm_basedir}/{deid_dcm_dirname}/{TLC_FOLDER_SYNTAX}/{deid_dcm_filename}"
                )
            except:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error occurred while saving de-identified CT scan on path: {deid_dcm_basedir}/{deid_dcm_dirname}/{TLC_FOLDER_SYNTAX}/{deid_dcm_filename}",
                )
        else:
            if not os.path.exists(
                f"{deid_dcm_basedir}/{deid_dcm_dirname}/{FRC_FOLDER_SYNTAX}"
            ):
                os.makedirs(
                    f"{deid_dcm_basedir}/{deid_dcm_dirname}/{FRC_FOLDER_SYNTAX}"
                )
            try:
                deid_dcm.save_as(
                    f"{deid_dcm_basedir}/{deid_dcm_dirname}/{FRC_FOLDER_SYNTAX}/{deid_dcm_filename}"
                )
            except:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error occurred while saving de-identified CT scan on path: {deid_dcm_basedir}/{deid_dcm_dirname}/{FRC_FOLDER_SYNTAX}/{deid_dcm_filename}",
                )
        return

    raw_dcm_dir_path = _get_raw_dcm_dir_path(raw_CT_scan)
    patient_id = _get_patient_id_from_dir(raw_dcm_dir_path)
    deid_dcm_dirname = os.path.basename(raw_dcm_dir_path)
    for raw_dcm_subdir_path in _yield_subdir_if_exists(raw_dcm_dir_path):
        in_or_ex = (
            "IN" if os.path.basename(raw_dcm_subdir_path) == TLC_FOLDER_SYNTAX else "EX"
        )
        if await _is_scan_duplicate(deid_dcm_dirname, in_or_ex, db):
            # raise HTTPException(
            #     status_code=400,
            #     detail=f"Scan {deid_dcm_dirname}:{in_or_ex} already exists",
            # )
            continue
        timepoint = await _calc_scan_timepoint(
            raw_CT_scan.project, raw_CT_scan.pid, in_or_ex, db
        )
        deid_CT_scan = _construct_deid_CT_scan(
            raw_CT_scan, deid_dcm_dirname, in_or_ex, timepoint
        )
        for raw_dcm_path in _get_dcm_paths_from_dir(raw_dcm_subdir_path):
            deid_dcm = _deidentify_dcm_slice(raw_dcm_path, patient_id)
            deid_dcm_filename = os.path.basename(raw_dcm_path)
            _save_dcm_slice(deid_dcm, deid_dcm_dirname, in_or_ex, deid_dcm_filename)

        yield deid_CT_scan
