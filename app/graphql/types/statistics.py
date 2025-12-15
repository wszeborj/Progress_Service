import strawberry
from typing import List


@strawberry.type
class LearningStatistics:
    """Comprehensive learning statistics for a user."""
    user_id: int
    total_completed_lessons: int = strawberry.field(description="Total number of completed lessons")
    total_courses_in_progress: int = strawberry.field(description="Total number of courses with progress")
    total_completed_courses: int = strawberry.field(description="Total number of completed courses")
    total_certificates: int = strawberry.field(description="Total number of earned certificates")
    total_achievements: int = strawberry.field(description="Total number of achievements")
    total_time_spent_seconds: int = strawberry.field(description="Total time spent learning in seconds")
    average_completion_percentage: float = strawberry.field(description="Average completion percentage across all courses")


