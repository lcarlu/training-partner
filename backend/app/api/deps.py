from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_session
from app.infrastructure.db.repositories import (
    SqlJournalRepository,
    SqlPlanRepository,
    SqlSyncLogRepository,
)
from app.infrastructure.warehouse.reader import WarehouseReader
from app.services.journal_service import JournalService
from app.services.plan_service import PlanService

SessionDep = Annotated[Session, Depends(get_session)]


def get_journal_service(session: SessionDep) -> JournalService:
    return JournalService(SqlJournalRepository(session))


def get_plan_service(session: SessionDep) -> PlanService:
    return PlanService(SqlPlanRepository(session))


def get_sync_log_repository(session: SessionDep) -> SqlSyncLogRepository:
    return SqlSyncLogRepository(session)


def get_warehouse_reader() -> WarehouseReader:
    return WarehouseReader()


JournalServiceDep = Annotated[JournalService, Depends(get_journal_service)]
PlanServiceDep = Annotated[PlanService, Depends(get_plan_service)]
SyncLogRepositoryDep = Annotated[SqlSyncLogRepository, Depends(get_sync_log_repository)]
WarehouseReaderDep = Annotated[WarehouseReader, Depends(get_warehouse_reader)]
