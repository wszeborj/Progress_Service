from typing import List, Dict, Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.certificate import CourseCertificate
from ..models.progress import Progress
from ..models.progress import ProgressStatus
from ..models.achievement import Achievement


class ProgressService:

    @staticmethod
    async def user_course_stats(
        db: AsyncSession, user_id: int, course_id: int
    ) -> Dict[str, Any]:
        query = select(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.course_id == course_id
            )
        )
        result = await db.execute(query)
        progress = result.scalar_one_or_none()

        if not progress:
            return {
                "status": ProgressStatus.NOT_STARTED.value,
                "completion_percentage": 0.0,
                "total_time_spent": 0,
            }

        return {
            "status": progress.status.value,
            "completion_percentage": progress.completion_percentage,
            "total_time_spent": progress.total_time_spent,
        }

    @staticmethod
    async def generate_certificate_if_eligible(
        db: AsyncSession, user_id: int, course_id: int
    ) -> Optional[CourseCertificate]:
        existing_cert_query = select(CourseCertificate).where(
            and_(
                CourseCertificate.user_id == user_id,
                CourseCertificate.course_id == course_id,
            )
        )
        existing_cert_result = await db.execute(existing_cert_query)
        existing_cert = existing_cert_result.scalar_one_or_none()
        
        if existing_cert:
            return existing_cert

        stats = await ProgressService.user_course_stats(db, user_id, course_id)
        if stats["completion_percentage"] >= 100.0 or stats["status"] == ProgressStatus.COMPLETED.value:
            certificate = CourseCertificate(
                user_id=user_id,
                course_id=course_id,
            )
            db.add(certificate)
            await db.commit()
            await db.refresh(certificate)
            return certificate

        return None

    @staticmethod
    async def get_user_progress(
        db: AsyncSession, user_id: int, course_id: Optional[int] = None
    ) -> List[Progress]:
        query = select(Progress).where(Progress.user_id == user_id)
        if course_id:
            query = query.where(Progress.course_id == course_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_completed_courses(
        db: AsyncSession, user_id: int
    ) -> List[int]:
        query = select(Progress.course_id).where(
            and_(
                Progress.user_id == user_id,
                Progress.status == ProgressStatus.COMPLETED
            )
        ).distinct()
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_statistics(
        db: AsyncSession, user_id: int
    ) -> Dict[str, Any]:
        # Total completed courses
        completed_query = select(func.count()).select_from(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.status == ProgressStatus.COMPLETED
            )
        )
        total_completed_courses = (await db.execute(completed_query)).scalar() or 0

        # Total courses in progress
        in_progress_query = select(func.count()).select_from(Progress).where(
            and_(
                Progress.user_id == user_id,
                Progress.status == ProgressStatus.IN_PROGRESS
            )
        )
        total_courses_in_progress = (await db.execute(in_progress_query)).scalar() or 0

        # Total courses with any progress
        total_courses_query = select(func.count()).select_from(Progress).where(
            Progress.user_id == user_id
        )
        total_courses = (await db.execute(total_courses_query)).scalar() or 0

        # Total certificates
        certs_query = select(func.count()).select_from(CourseCertificate).where(
            CourseCertificate.user_id == user_id
        )
        total_certificates = (await db.execute(certs_query)).scalar() or 0

        # Total achievements
        achievements_query = select(func.count()).select_from(Achievement).where(
            Achievement.user_id == user_id
        )
        total_achievements = (await db.execute(achievements_query)).scalar() or 0

        # Total time spent
        time_query = select(func.sum(Progress.total_time_spent)).where(
            Progress.user_id == user_id
        )
        total_time = (await db.execute(time_query)).scalar() or 0

        # Average completion
        avg_query = select(func.avg(Progress.completion_percentage)).where(
            Progress.user_id == user_id
        )
        avg_completion = (await db.execute(avg_query)).scalar() or 0.0

        return {
            "total_completed_courses": total_completed_courses,
            "total_courses_in_progress": total_courses_in_progress,
            "total_courses": total_courses,
            "total_certificates": total_certificates,
            "total_achievements": total_achievements,
            "total_time_spent": total_time,
            "average_completion": float(avg_completion) if avg_completion else 0.0,
        }

    @staticmethod
    async def get_user_certificates(
        db: AsyncSession, user_id: int, course_id: Optional[int] = None
    ) -> List[CourseCertificate]:

        query = select(CourseCertificate).where(CourseCertificate.user_id == user_id)
        if course_id:
            query = query.where(CourseCertificate.course_id == course_id)
        query = query.order_by(CourseCertificate.earned_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_achievements(
        db: AsyncSession, user_id: int
    ) -> List[Achievement]:
        query = select(Achievement).where(
            Achievement.user_id == user_id
        ).order_by(Achievement.earned_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def add_achievement(
        db: AsyncSession,
        user_id: int,
        achievement_type: str,
        achievement_name: str,
        description: Optional[str] = None,
        metadata: Optional[str] = None,
    ) -> Achievement:
        achievement = Achievement(
            user_id=user_id,
            achievement_type=achievement_type,
            achievement_name=achievement_name,
            description=description,
            metadata=metadata,
        )
        db.add(achievement)
        await db.commit()
        await db.refresh(achievement)
        return achievement
