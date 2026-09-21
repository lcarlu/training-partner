from datetime import date

from app.domain.entities import TrainingPlan
from app.infrastructure.db.repositories import SqlPlanRepository


class PlanService:
    def __init__(self, repo: SqlPlanRepository):
        self.repo = repo

    def get_or_create_default(
        self, default_race_date: date, default_target_time_seconds: int | None
    ) -> TrainingPlan:
        plan = self.repo.get_current()
        if plan is not None:
            return plan
        return self.repo.upsert(
            TrainingPlan(
                id=None,
                name="Marathon",
                race_date=default_race_date,
                target_time_seconds=default_target_time_seconds,
            )
        )

    def update_plan(self, plan: TrainingPlan) -> TrainingPlan:
        return self.repo.upsert(plan)
