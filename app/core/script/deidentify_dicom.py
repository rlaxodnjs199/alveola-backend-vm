import os
from typing import List, Dict
from fastapi import HTTPException
from pydicom import Dataset, dcmread
from app.core.config import settings


def execute(ct_scan: Dict):
    def _get_raw_dcm_dir_path(ct_scan: Dict):
        try:
            raw_dcm_dir_path = f"{settings.RAW_CT_PATH}/"
            raw_dcm_dir_path += (
                "DCM_{acquisition_date}_{project}_{participant_id}_{worker}".format(
                    **ct_scan
                )
            )
        except:
            raise HTTPException(status_code=400, detail="Raw CT folder syntax error")
        return raw_dcm_dir_path

    def _get_dcm_paths_from_dir(dcm_dir: str):
        for base, _, files in os.walk(dcm_dir):
            for file in files:
                yield os.path.join(base, file)

    def _get_patient_id_from_dir(raw_dcm_dir: str) -> str:
        return os.path.basename(raw_dcm_dir).split("_")[-2]

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

    def _save_dcm_slice(
        deid_dcm: Dataset,
        deid_dcm_dirname: str,
        deid_dcm_filename: str,
        deid_dcm_basedir=settings.DEID_CT_PATH,
    ):
        if not os.path.exists(f"{deid_dcm_basedir}/{deid_dcm_dirname}"):
            os.makedirs(f"{deid_dcm_basedir}/{deid_dcm_dirname}")

        try:
            deid_dcm.save_as(
                f"{deid_dcm_basedir}/{deid_dcm_dirname}/{deid_dcm_filename}"
            )
        except:
            raise HTTPException(
                status_code=400,
                detail=f"Error occurred while saving de-identified CT scan on path: {deid_dcm_basedir}/{deid_dcm_dirname}/{deid_dcm_filename}",
            )

        return

    raw_dcm_dir_path = _get_raw_dcm_dir_path(ct_scan)
    try:
        patient_id = _get_patient_id_from_dir(raw_dcm_dir_path)
        deid_dcm_dirname = os.path.basename(raw_dcm_dir_path)
        for raw_dcm_path in _get_dcm_paths_from_dir(raw_dcm_dir_path):
            deid_dcm = _deidentify_dcm_slice(raw_dcm_path, patient_id)
            deid_dcm_filename = os.path.basename(raw_dcm_path)
            _save_dcm_slice(deid_dcm, deid_dcm_dirname, deid_dcm_filename)
    except:
        raise HTTPException(
            status_code=400,
            detail=f"Error occurred while de-identifying CT scan on path: {raw_dcm_dir_path}",
        )

    return {"msg": "Dicom deidentification succeeded"}
