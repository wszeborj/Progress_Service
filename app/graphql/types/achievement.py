import strawberry
from datetime import datetime
from typing import Optional

from ...models.achievement import Achievement as AchievementModel


@strawberry.type
class Achievement:
    id: int
    user_id: int
    achievement_type: str
    achievement_name: str
    description: Optional[str]
    earned_at: datetime
    metadata: Optional[str] = strawberry.field(description="JSON string with extra data")

    @classmethod
    def from_model(cls, model: AchievementModel) -> "Achievement":
        """Convert SQLAlchemy model to Strawberry GraphQL type."""
        return cls(
            id=model.id,
            user_id=model.user_id,
            achievement_type=model.achievement_type,
            achievement_name=model.achievement_name,
            description=model.description,
            earned_at=model.earned_at,
            metadata=model.metadata,
        )

