from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LearningStatistics:
    user_id: int
    total_completed_lessons: int
    total_courses_in_progress: int
    total_completed_courses: int
    total_certificates: int
    total_achievements: int
    total_time_spent_seconds: int
    average_completion_percentage: float
