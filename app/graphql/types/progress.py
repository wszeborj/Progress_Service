import strawberry
from datetime import datetime
from typing import Optional
from enum import Enum

from ...models.progress import Progress as ProgressModel, ProgressStatus as ProgressStatusEnum


@strawberry.enum
class ProgressStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@strawberry.type
class Progress:
    id: int
    user_id: int
    course_id: int
    status: ProgressStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    completion_percentage: float
    total_time_spent: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model: ProgressModel) -> "Progress":
        """Convert SQLAlchemy model to Strawberry GraphQL type."""
        return cls(
            id=model.id,
            user_id=model.user_id,
            course_id=model.course_id,
            status=ProgressStatus(model.status.value),
            started_at=model.started_at,
            completed_at=model.completed_at,
            last_accessed_at=model.last_accessed_at,
            completion_percentage=model.completion_percentage,
            total_time_spent=model.total_time_spent,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
