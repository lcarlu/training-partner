from datetime import date

from app.domain.entities import JournalEntry
from app.infrastructure.db.repositories import SqlJournalRepository


class JournalService:
    def __init__(self, repo: SqlJournalRepository):
        self.repo = repo

    def list_entries(self, since: date | None, until: date | None) -> list[JournalEntry]:
        return self.repo.list(since, until)

    def get(self, entry_id: str) -> JournalEntry | None:
        return self.repo.get(entry_id)

    def create(self, entry: JournalEntry) -> JournalEntry:
        return self.repo.create(entry)

    def update(self, entry_id: str, entry: JournalEntry) -> JournalEntry | None:
        return self.repo.update(entry_id, entry)

    def delete(self, entry_id: str) -> bool:
        return self.repo.delete(entry_id)
