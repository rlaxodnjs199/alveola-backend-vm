import asyncio
from datetime import datetime
from sqlalchemy import select, update
from app.api.v1.scan import models
from app.core.config import settings
from app.db.pgsql.session import engine


async def update_db_on_vida_import(
    pid: str, acquisition_date: datetime, in_or_ex: str, vida_case_id: int
):
    vida_result_path = f"{settings.VIDA_RESULT_PATH}{vida_case_id}"
    stmt = (
        update(models.Scan)
        .where(models.Scan.pid == pid)
        .where(models.Scan.acquisition_date == acquisition_date)
        .where(models.Scan.in_or_ex == in_or_ex)
        .values(status="VIDA-Imported")
        .values(vida_case_id=vida_case_id)
        .values(vida_result_path=vida_result_path)
        .execution_options(synchronize_session="fetch")
    )

    async with engine.connect() as conn:
        await conn.execute(stmt)
        await conn.commit()


def update_db_on_vida_processed():
    pass


def update_db_on_dl_segmented():
    pass
