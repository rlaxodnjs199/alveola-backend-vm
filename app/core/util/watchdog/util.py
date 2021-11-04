from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api.v1.scan import models


async def update_db_on_vida_import(
    pid: str,
    acquisition_date: datetime,
    vida_case_id: int,
    vida_result_path: str,
    db: AsyncSession,
):
    stmt = (
        update(models.Scan)
        .where(models.Scan.pid == pid)
        .where(models.Scan.acquisition_date == acquisition_date)
        .values(models.Scan.vida_case_id == vida_case_id)
        .values(models.Scan.vida_result_path == vida_result_path)
        .execution_options(synchronize_session="fetch")
    )
    query_result = await db.execute(stmt)


def update_db_on_vida_processed():
    pass


def update_db_on_dl_segmented():
    pass
