from datetime import datetime
from sqlalchemy import select, update
from app.api.v1.scan import models
from app.core.config import settings
from app.db.pgsql.session import get_db


async def update_db_on_vida_import(
    pid: str, acquisition_date: datetime, vida_case_id: int
):
    vida_result_path = settings.VIDA_RESULT_PATH + vida_case_id
    stmt = (
        update(models.Scan)
        .where(models.Scan.pid == pid)
        .where(models.Scan.acquisition_date == acquisition_date)
        .values(models.Scan.vida_case_id == vida_case_id)
        .values(models.Scan.vida_result_path == vida_result_path)
        .execution_options(synchronize_session="fetch")
    )
    db = get_db()
    query_result = await db.execute(stmt)


def update_db_on_vida_processed():
    pass


def update_db_on_dl_segmented():
    pass
