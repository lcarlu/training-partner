from datetime import date

from fastapi import APIRouter, HTTPException

from app.api.deps import JournalServiceDep
from app.api.schemas.journal import JournalEntryCreate, JournalEntryRead
from app.domain.entities import JournalEntry

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.get("", response_model=list[JournalEntryRead])
def list_entries(
    journal_service: JournalServiceDep,
    since: date | None = None,
    until: date | None = None,
) -> list[JournalEntryRead]:
    entries = journal_service.list_entries(since, until)
    return [JournalEntryRead.model_validate(e) for e in entries]


@router.post("", response_model=JournalEntryRead, status_code=201)
def create_entry(
    payload: JournalEntryCreate, journal_service: JournalServiceDep
) -> JournalEntryRead:
    entry = journal_service.create(JournalEntry(id=None, **payload.model_dump()))
    return JournalEntryRead.model_validate(entry)


@router.put("/{entry_id}", response_model=JournalEntryRead)
def update_entry(
    entry_id: str, payload: JournalEntryCreate, journal_service: JournalServiceDep
) -> JournalEntryRead:
    updated = journal_service.update(entry_id, JournalEntry(id=entry_id, **payload.model_dump()))
    if updated is None:
        raise HTTPException(status_code=404, detail="Entrée de journal introuvable")
    return JournalEntryRead.model_validate(updated)


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: str, journal_service: JournalServiceDep) -> None:
    if not journal_service.delete(entry_id):
        raise HTTPException(status_code=404, detail="Entrée de journal introuvable")
