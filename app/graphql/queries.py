import strawberry
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct

from ..models.progress import Progress as ProgressModel
from ..models.progress import ProgressStatus as ProgressStatusEnum
from ..models.achievement import Achievement as AchievementModel
from ..models.certificate import CourseCertificate as CertificateModel
from ..graphql.types.progress import Progress
from ..graphql.types.achievement import Achievement
from ..graphql.types.certificate import CourseCertificate
from ..graphql.types.statistics import LearningStatistics


@strawberry.type
class Query:
    @strawberry.field
    async def get_user_progress(
            self,
            user_id: int,
            info: strawberry.Info,
            course_id: Optional[int] = None
    ) -> List[Progress]:
        db_session: AsyncSession = info.context["db_session"]

        stmt = select(ProgressModel).where(ProgressModel.user_id == user_id)
        if course_id:
            stmt = stmt.where(ProgressModel.course_id == course_id)
        stmt = stmt.order_by(ProgressModel.last_accessed_at.desc())

        result = await db_session.execute(stmt)
        progresses = result.scalars().all()
        return [Progress.from_model(p) for p in progresses]

    @strawberry.field
    async def get_progress(
            self,
            user_id: int,
            course_id: int,
            info: strawberry.Info
    ) -> Optional[Progress]:
        db_session: AsyncSession = info.context["db_session"]

        stmt = select(ProgressModel).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.course_id == course_id
            )
        )
        result = await db_session.execute(stmt)
        progress = result.scalar_one_or_none()
        return Progress.from_model(progress) if progress else None

    @strawberry.field
    async def get_completed_courses(
            self,
            user_id: int,
            info: strawberry.Info
    ) -> List[int]:
        db_session: AsyncSession = info.context["db_session"]

        stmt = select(ProgressModel.course_id).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.status == ProgressStatusEnum.COMPLETED
            )
        ).distinct()

        result = await db_session.execute(stmt)
        course_ids = result.scalars().all()
        return list(course_ids)

    @strawberry.field
    async def get_user_achievements(
            self,
            user_id: int,
            info: strawberry.Info,
            achievement_type: Optional[str] = None
    ) -> List[Achievement]:

        db_session: AsyncSession = info.context["db_session"]
        stmt = select(AchievementModel).where(AchievementModel.user_id == user_id)
        if achievement_type:
            stmt = stmt.where(AchievementModel.achievement_type == achievement_type)
        stmt = stmt.order_by(AchievementModel.earned_at.desc())
        result = await db_session.execute(stmt)
        achievements = result.scalars().all()
        return [Achievement.from_model(a) for a in achievements]

    @strawberry.field
    async def get_user_certificates(
            self,
            user_id: int,
            info: strawberry.Info,
            course_id: Optional[int] = None
    ) -> List[CourseCertificate]:
        db_session: AsyncSession = info.context["db_session"]
        stmt = select(CertificateModel).where(CertificateModel.user_id == user_id)
        if course_id:
            stmt = stmt.where(CertificateModel.course_id == course_id)
        stmt = stmt.order_by(CertificateModel.earned_at.desc())
        result = await db_session.execute(stmt)
        certificates = result.scalars().all()
        return [CourseCertificate.from_model(c) for c in certificates]

    @strawberry.field
    async def get_certificate(
            self,
            user_id: int,
            course_id: int,
            info: strawberry.Info
    ) -> Optional[CourseCertificate]:

        db_session: AsyncSession = info.context["db_session"]
        stmt = select(CertificateModel).where(
            and_(
                CertificateModel.user_id == user_id,
                CertificateModel.course_id == course_id
            )
        )
        result = await db_session.execute(stmt)
        certificate = result.scalar_one_or_none()
        return CourseCertificate.from_model(certificate) if certificate else None

    @strawberry.field
    async def get_user_statistics(
            self,
            user_id: int,
            info: strawberry.Info
    ) -> LearningStatistics:
        db_session: AsyncSession = info.context["db_session"]

        # Total completed courses
        completed_courses_stmt = select(func.count()).select_from(ProgressModel).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.status == ProgressStatusEnum.COMPLETED
            )
        )
        completed_courses = (await db_session.execute(completed_courses_stmt)).scalar() or 0

        # Total courses in progress
        in_progress_stmt = select(func.count()).select_from(ProgressModel).where(
            and_(
                ProgressModel.user_id == user_id,
                ProgressModel.status == ProgressStatusEnum.IN_PROGRESS
            )
        )
        total_courses_in_progress = (await db_session.execute(in_progress_stmt)).scalar() or 0

        # Total certificates
        certs_stmt = select(func.count()).select_from(CertificateModel).where(
            CertificateModel.user_id == user_id
        )
        total_certificates = (await db_session.execute(certs_stmt)).scalar() or 0

        # Total achievements
        achievements_stmt = select(func.count()).select_from(AchievementModel).where(
            AchievementModel.user_id == user_id
        )
        total_achievements = (await db_session.execute(achievements_stmt)).scalar() or 0

        # Total time spent and average completion
        stats_stmt = select(
            func.sum(ProgressModel.total_time_spent).label("total_time"),
            func.avg(ProgressModel.completion_percentage).label("avg_completion")
        ).where(ProgressModel.user_id == user_id)
        stats_result = await db_session.execute(stats_stmt)
        stats_row = stats_result.first()
        total_time_spent = int(stats_row.total_time or 0) if stats_row else 0
        avg_completion = float(stats_row.avg_completion or 0.0) if stats_row else 0.0

        # For completed lessons, we'll use a placeholder since we don't have a lesson model
        # In a real system, you'd query a lessons table or join with course service
        total_completed_lessons = 0  # This would come from a lesson progress table

        return LearningStatistics(
            user_id=user_id,
            total_completed_lessons=total_completed_lessons,
            total_courses_in_progress=total_courses_in_progress,
            total_completed_courses=completed_courses,
            total_certificates=total_certificates,
            total_achievements=total_achievements,
            total_time_spent_seconds=total_time_spent,
            average_completion_percentage=avg_completion,
        )
