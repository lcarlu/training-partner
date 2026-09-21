import json
from datetime import date, datetime

from sqlmodel import Session, select

from app.domain.entities import JournalEntry as JournalEntryDomain
from app.domain.entities import TrainingPlan as TrainingPlanDomain
from app.infrastructure.db.models import JournalEntry as JournalEntryRow
from app.infrastructure.db.models import SyncLog as SyncLogRow
from app.infrastructure.db.models import TrainingPlan as TrainingPlanRow


def _journal_to_domain(row: JournalEntryRow) -> JournalEntryDomain:
    return JournalEntryDomain(
        id=row.id,
        day=row.day,
        sport=row.sport,
        planned_notes=row.planned_notes,
        actual_notes=row.actual_notes,
        rpe=row.rpe,
        mood=row.mood,
        linked_activity_id=row.linked_activity_id,
    )


class SqlJournalRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, since: date | None, until: date | None) -> list[JournalEntryDomain]:
        statement = select(JournalEntryRow)
        if since is not None:
            statement = statement.where(JournalEntryRow.day >= since)
        if until is not None:
            statement = statement.where(JournalEntryRow.day <= until)
        # `ty` doesn't yet model SQLAlchemy's descriptor protocol (class-level attribute access
        # returns an InstrumentedAttribute, not the annotated Python type) -- known false positive.
        statement = statement.order_by(JournalEntryRow.day.desc())  # ty: ignore[unresolved-attribute]
        rows = self.session.exec(statement).all()
        return [_journal_to_domain(row) for row in rows]

    def get(self, entry_id: str) -> JournalEntryDomain | None:
        row = self.session.get(JournalEntryRow, entry_id)
        return _journal_to_domain(row) if row else None

    def create(self, entry: JournalEntryDomain) -> JournalEntryDomain:
        row = JournalEntryRow(
            day=entry.day,
            sport=entry.sport,
            planned_notes=entry.planned_notes,
            actual_notes=entry.actual_notes,
            rpe=entry.rpe,
            mood=entry.mood,
            linked_activity_id=entry.linked_activity_id,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _journal_to_domain(row)

    def update(self, entry_id: str, entry: JournalEntryDomain) -> JournalEntryDomain | None:
        row = self.session.get(JournalEntryRow, entry_id)
        if row is None:
            return None
        row.day = entry.day
        row.sport = entry.sport
        row.planned_notes = entry.planned_notes
        row.actual_notes = entry.actual_notes
        row.rpe = entry.rpe
        row.mood = entry.mood
        row.linked_activity_id = entry.linked_activity_id
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _journal_to_domain(row)

    def delete(self, entry_id: str) -> bool:
        row = self.session.get(JournalEntryRow, entry_id)
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True


class SqlPlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_current(self) -> TrainingPlanDomain | None:
        # ty false positive, see the comment in SqlJournalRepository.list above.
        row = self.session.exec(
            select(TrainingPlanRow).order_by(TrainingPlanRow.id.desc())  # ty: ignore[unresolved-attribute]
        ).first()
        if row is None:
            return None
        return TrainingPlanDomain(
            id=row.id,
            name=row.name,
            race_date=row.race_date,
            target_time_seconds=row.target_time_seconds,
        )

    def upsert(self, plan: TrainingPlanDomain) -> TrainingPlanDomain:
        # ty false positive, see the comment in SqlJournalRepository.list above.
        row = self.session.exec(
            select(TrainingPlanRow).order_by(TrainingPlanRow.id.desc())  # ty: ignore[unresolved-attribute]
        ).first()
        if row is None:
            row = TrainingPlanRow(
                name=plan.name,
                race_date=plan.race_date,
                target_time_seconds=plan.target_time_seconds,
            )
        else:
            row.name = plan.name
            row.race_date = plan.race_date
            row.target_time_seconds = plan.target_time_seconds
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return TrainingPlanDomain(
            id=row.id,
            name=row.name,
            race_date=row.race_date,
            target_time_seconds=row.target_time_seconds,
        )


class SqlSyncLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_latest(self) -> SyncLogRow | None:
        return self.session.get(SyncLogRow, "latest")

    def record(
        self, started_at: datetime, finished_at: datetime, counts: dict[str, int]
    ) -> SyncLogRow:
        row = SyncLogRow(
            id="latest",
            started_at=started_at,
            finished_at=finished_at,
            counts_json=json.dumps(counts),
        )
        self.session.merge(row)
        self.session.commit()
        return row
